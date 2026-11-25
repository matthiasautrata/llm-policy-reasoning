(ns v3b.engine
  "V3b evaluator: the same defeasible logic as V3a's defeasible.pl, over EDN data as Clojure data.

  Literals are vectors [:pred arg ...]; [:neg L] is the complement; variables are symbols ?x. A body is
  evaluated left to right as a lazy sequence of substitutions. evaluate decides a ground literal:
    [:proven sups sup-nodes]       every applicable attacker is beaten by some applicable supporter
    [:defeated att sups sup-nodes] an unbeaten attacker is superior to every supporter
    [:blocked sups unbeaten]       ambiguity blocking
    [:none atts]                   no applicable supporter
  Supporters: strict/defeasible rules whose body holds, in-force claims. Attackers: the same for the
  complement and, for functional predicates, the same key with another value; defeaters attack only.
  Superiority: explicit :superior-to, strict over non-strict, asserter authority (a :superiority rule
  scoped to its :pred), later asserted_at for the same asserter. Memoised per op.

  ctx: {:ix store index, :d as-of date, :memo atom}"
  (:require [clojure.string :as str]
            [v3b.sql :as sql]))

;; ------------------------------------------------------------------ terms

(defn lvar? [x] (and (symbol? x) (str/starts-with? (name x) "?")))

(defn walk [t s] (if (and (lvar? t) (contains? s t)) (recur (get s t) s) t))

(defn unify [a b s]
  (when s
    (let [a (walk a s) b (walk b s)]
      (cond (lvar? a) (if (= a b) s (assoc s a b))
            (lvar? b) (assoc s b a)
            (and (vector? a) (vector? b))
            (when (= (count a) (count b))
              (reduce (fn [s [x y]] (or (unify x y s) (reduced nil))) s (map vector a b)))
            (and (map? a) (map? b)) (when (= a b) s)
            (or (boolean? a) (boolean? b)) (when (identical? a b) s)
            (and (number? a) (number? b)) (when (== a b) s)
            (= a b) s))))

(defn subst [t s]
  (let [t (walk t s)]
    (cond (vector? t) (mapv #(subst % s) t)
          (map? t) (into {} (map (fn [[k v]] [k (subst v s)])) t)
          :else t)))

(defn ground? [t]
  (cond (lvar? t) false
        (vector? t) (every? ground? t)
        (map? t) (every? ground? (vals t))
        :else true))

(def ^:private counter (atom 0))

(defn rename
  "Fresh variables for one use of a rule."
  [t]
  (let [n (swap! counter inc)
        r (fn r [x] (cond (lvar? x) (symbol (str (name x) "#" n))
                          (vector? x) (mapv r x)
                          (map? x) (into {} (map (fn [[k v]] [k (r v)])) x)
                          :else x))]
    (r t)))

(defn- rank [x] (cond (lvar? x) 0 (number? x) 1 (or (keyword? x) (boolean? x) (nil? x)) 2 (string? x) 3 :else 4))

(defn tcmp
  "A standard order of terms (variables < numbers < atoms < strings < vectors), lexicographic on vectors."
  [a b]
  (let [ra (rank a) rb (rank b)]
    (cond (not= ra rb) (compare ra rb)
          (vector? a) (or (first (remove zero? (map tcmp a b))) (compare (count a) (count b)))
          (= ra 2) (compare (str a) (str b))
          (= ra 0) (compare (name a) (name b))
          :else (compare a b))))

(defn sort-terms [xs] (sort tcmp (distinct xs)))

(defn pred-of [l] (if (= :neg (first l)) (recur (second l)) (first l)))

;; ------------------------------------------------------------------ store access

(defn in-force? [{:keys [valid_from valid_to]} d]
  (and (<= (compare valid_from d) 0) (or (nil? valid_to) (<= (compare d valid_to) 0))))

(defn- rules-of [ctx kinds] (filter #(kinds (:kind %)) (get-in ctx [:ix :rules])))
(defn- claims [ctx] (get-in ctx [:ix :claims]))
(defn rule-by-id [ctx id] (get-in ctx [:ix :rule id]))
(defn claim-by-id [ctx id] (get-in ctx [:ix :claim id]))

(def ^:private derivers #{:strict :defeasible})
(def ^:private attacking #{:strict :defeasible :defeater})

(defn claim-proof [c goal]
  {:type "claim" :id (:id c) :goal goal :asserted_by (:asserted_by c) :asserted_at (:asserted_at c) :children []})

;; ------------------------------------------------------------------ bodies

(declare prove evaluate)

(defn- ev [t s]
  (let [t (walk t s)]
    (cond (and (vector? t) (#{:+ :-} (first t)))
          (let [x (ev (nth t 1) s) y (ev (nth t 2) s)] (if (= :+ (first t)) (+ x y) (- x y)))
          (lvar? t) (throw (ex-info (str "unbound " t) {}))
          :else t)))

(def ^:private cmp-ops {:< neg? :<= (complement pos?) :> pos? :>= (complement neg?) := zero?})

(defn cmp-holds? [op a b]
  (let [x (ev a {}) y (ev b {})]
    ((cmp-ops op) (if (and (number? x) (number? y)) (compare (double x) (double y)) (tcmp x y)))))

(defn fetch-rows
  "Concept lookup with ground filters -> [rows node-info filters]."
  [c f]
  (when-not (ground? f) (throw (ex-info (str "fetch " (name c) ": filters not ground: " (pr-str f)) {})))
  (let [fs (into (array-map) (map (fn [[k v]] [(name k) v])) f)
        {:keys [rows sql params truncated]} (sql/fetch c fs)]
    [rows {:sql sql :params params :truncated truncated} fs]))

(defn lit
  "One body literal under substitution s -> lazy seq of [s' node]."
  [ctx l s]
  (let [[op & args] l]
    (case op
      :fetch (let [[c f o] args
                   [rows info fs] (fetch-rows c (subst f s))
                   n (count rows)]
               (for [row rows
                     :let [s2 (reduce (fn [s [col t]]
                                        (let [k (name col)]
                                          (if (contains? row k) (or (unify t (get row k) s) (reduced nil)) (reduced nil))))
                                      s o)]
                     :when s2]
                 [s2 (merge info {:type "fetch" :concept (name c) :filters fs :rows n :row row})]))
      :not (let [g (subst (first args) s)]
             (when (empty? (prove ctx g)) [[s {:type "absent" :goal g}]]))
      :as_of (when-let [s2 (unify (first args) (:d ctx) s)] [[s2 {:type "fact" :goal [:as_of (:d ctx)]}]])
      :is (let [[x e] args v (ev e s)]
            (when-let [s2 (unify x v s)] [[s2 {:type "fact" :goal [:is v (subst e s)]}]]))
      (:< :<= :> :>= :=)
      (let [a (subst (first args) s) b (subst (second args) s)]
        (when (cmp-holds? op a b) [[s {:type "fact" :goal [op a b]}]]))
      ;; derived literal
      (let [g (subst l s)]
        (for [[inst p] (prove ctx g) :let [s2 (unify l inst s)] :when s2] [s2 p])))))

(defn body
  "-> lazy seq of [s kids]"
  [ctx lits s]
  (if (empty? lits)
    [[s []]]
    (for [[s1 k] (lit ctx (first lits) s)
          [s2 ks] (body ctx (rest lits) s1)]
      [s2 (into [k] ks)])))

(defn apply-rule
  "Rule r concluding goal l: lazy seq of [s proof-node] (goal instantiated by the body)."
  [ctx r l]
  (let [{:keys [head] bd :body} (rename (select-keys r [:head :body]))]
    (when-let [s (unify head l {})]
      (for [[s2 kids] (body ctx bd s)]
        [s2 {:type "rule" :id (:id r) :goal (subst l s2) :children kids}]))))

;; ------------------------------------------------------------------ evaluation

(defn- candidates [ctx l]
  (concat
   (for [r (rules-of ctx derivers) [s _] (apply-rule ctx r l)] (subst l s))
   (for [c (claims ctx) :when (in-force? c (:d ctx)) :let [s (unify l (:assertion c) {})] :when s] (subst l s))))

(defn- with-children [p extra] (update p :children into extra))

(defn prove
  "L defeasibly provable: lazy seq of [ground-instance proof]."
  [ctx l]
  (let [proof (fn [g] (let [[st sups sn] (evaluate ctx g)]
                        (when (= st :proven) [g (with-children (:proof (first sups)) sn)])))]
    (if (ground? l)
      (keep proof [l])
      (keep proof (filter ground? (sort-terms (candidates ctx l)))))))

(defn supporters [ctx l]
  (concat
   (for [r (rules-of ctx derivers) :let [[_ p] (first (apply-rule ctx r l))] :when p]
     {:id (:id r) :kind (:kind r) :proof p})
   (for [c (claims ctx) :when (and (= (:assertion c) l) (in-force? c (:d ctx)))]
     {:id (:id c) :kind :claim :proof (claim-proof c l)})))

(defn rivals
  "[head diff]: diff nil, or [v v2] for a functional rival with key fixed and value v2 /= v."
  [ctx l]
  (if (= :neg (first l))
    [[(second l) nil]]
    (let [[p & args] l
          n (get-in ctx [:ix :functional p])]
      (cond-> [[[:neg l] nil]]
        (and n (= (count args) (inc n)))
        (conj (let [v2 (symbol (str "?rival#" (swap! counter inc)))]
                [(into [p] (concat (take n args) [v2])) [(last args) v2]]))))))

(defn- differs? [diff s] (or (nil? diff) (let [[v v2] diff] (not= v (subst v2 s)))))

(defn attackers [ctx l]
  (let [atts (for [[h diff] (rivals ctx l)
                   a (concat
                      (for [r (rules-of ctx attacking)
                            :let [[s p] (first (filter (fn [[s _]] (differs? diff s)) (apply-rule ctx r h)))]
                            :when p]
                        {:id (:id r) :kind (:kind r) :head (subst h s) :proof p})
                      (for [c (claims ctx) :when (in-force? c (:d ctx))
                            :let [s (unify h (:assertion c) {})]
                            :when (and s (differs? diff s))]
                        {:id (:id c) :kind :claim :head (:assertion c) :proof (claim-proof c (:assertion c))}))]
               a)]
    (vals (reduce (fn [m a] (if (contains? m (:id a)) m (assoc m (:id a) a))) (array-map) atts))))

(defn sup
  "Sources by which w is superior to l, in order: explicit, strict, authority:<id>, later."
  [ctx w l]
  (let [rw (rule-by-id ctx w) rl (rule-by-id ctx l) cw (claim-by-id ctx w) cl (claim-by-id ctx l)]
    (concat
     (when (and rw ((:superior-to rw) l)) ["explicit"])
     (when (and rw (= :strict (:kind rw)) (not (and rl (= :strict (:kind rl))))) ["strict"])
     (when (and cw cl (not= (:asserted_by cw) (:asserted_by cl))
                (= (pred-of (:assertion cw)) (pred-of (:assertion cl))))
       (for [r (rules-of ctx #{:superiority})
             :when (= (:pred r) (pred-of (:assertion cw)))
             :let [o (vec (:order r)) iw (.indexOf o (:asserted_by cw)) il (.indexOf o (:asserted_by cl))]
             :when (and (>= iw 0) (>= il 0) (< iw il))]
         (str "authority:" (:id r))))
     (when (and cw cl (= (:asserted_by cw) (:asserted_by cl)) (pos? (compare (:asserted_at cw) (:asserted_at cl))))
       ["later"]))))

(defn- sup1 [ctx w l] (first (sup ctx w l)))

(defn classify [ctx sups atts]
  (if (empty? sups)
    [:none atts]
    (let [beats (fn [a] (some #(sup1 ctx (:id %) (:id a)) sups))
          {beaten true unbeaten false} (group-by (comp boolean beats) atts)
          sn (vec (for [a beaten :let [s (first (filter #(sup1 ctx (:id %) (:id a)) sups))]]
                    {:type "superior" :winner (:id s) :loser (:id a) :source (sup1 ctx (:id s) (:id a))}))]
      (if (empty? unbeaten)
        [:proven sups sn]
        (if-let [a (first (filter (fn [a] (every? #(sup1 ctx (:id a) (:id %)) sups)) unbeaten))]
          [:defeated a sups (vec (for [s sups] {:type "superior" :winner (:id a) :loser (:id s) :source (sup1 ctx (:id a) (:id s))}))]
          [:blocked sups (vec unbeaten)])))))

(defn evaluate
  "Memoised per op. Re-entry guard (PLAN-v3-integrity §3.2): ctx carries the path of literals being
  evaluated; meeting one again means a dependency cycle the integrity gate did not stop
  (INTEGRITY_GATE=off). Throws ex-info {:defeat-cycle goal-path}, a backstop, not a semantics."
  [ctx l]
  (let [k [(:d ctx) l]]
    (or (get @(:memo ctx) k)
        (let [path (:path ctx [])
              i (first (keep-indexed (fn [i x] (when (= x k) i)) path))]
          (when i
            (throw (ex-info "defeat-cycle" {:defeat-cycle (conj (mapv second (subvec path i)) l)})))
          (let [ctx' (assoc ctx :path (conj path k))
                r (classify ctx' (vec (supporters ctx' l)) (vec (attackers ctx' l)))]
            (swap! (:memo ctx) assoc k r)
            r)))))

(defn ids-of [xs] (vec (sort (distinct (map :id xs)))))
