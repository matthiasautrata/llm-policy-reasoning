(ns v3b.ops
  "V3b System A surface (CONTRACT.md): decide, why_not, claims, resolve_term, describe, fetch, add,
  with_hypothesis. Each op runs against one db value: main's, or a hypothesis's."
  (:require [v3b.engine :as e]
            [v3b.why :as why]
            [v3b.sql :as sql]
            [v3b.store :as store]))

(def ^:dynamic *db* nil)           ; the db value ops read (bound per op)
(defonce conn (atom nil))
(defonce opts (atom {:hypothesis :branch}))

(defn- ctx [op]
  (let [ix (store/index *db*)]
    {:ix ix :d (or (:as_of op) (:today ix)) :memo (atom {})}))

;; ------------------------------------------------------------------ decide

(defn- known-pred? [ix p]
  (or (some #(and (vector? (:head %)) (= p (e/pred-of (:head %)))) (:rules ix))
      (some #(= p (e/pred-of (:assertion %))) (:claims ix))))

(defn- scope [ix p]
  (if (some #(= (str "term:" (name p)) (:id %)) (:terms ix)) "UNDERDETERMINED" "OUT_OF_SCOPE"))

(defn- sub-nodes [x]
  (cond (map? x) (cons x (mapcat sub-nodes (keep x [:children :failed])))
        (sequential? x) (mapcat sub-nodes x)
        :else nil))

(defn- answer [c st v sides why]
  {:status st :value v :sides sides :why (vec why)
   :owners (vec (sort (distinct (for [n (sub-nodes why) :let [r (e/rule-by-id c (:id n))] :when r] (name (:owner r))))))
   :qualifier nil})

(defn- team-proofs [sups sn]
  (vec (for [s sups] (update (:proof s) :children into (filter #(= (:id s) (:winner %)) sn)))))

(defn- lexi [a b] (or (first (remove zero? (map compare a b))) (compare (count a) (count b))))
(defn- sides [& id-lists] (vec (sort lexi (distinct id-lists))))

(defn- incompatible [c g]
  (first (for [r (filter #(= :incompatible (:kind %)) (get-in c [:ix :rules]))
               :let [[_ p] (first (e/apply-rule c (assoc r :kind :strict) g))] :when p]
           [(:id r) (assoc p :goal [:neg g])])))

(defn- decide-ground [c g]
  (let [[st & more :as ev] (e/evaluate c g)]
    (case st
      :proven (let [[sups sn] more why (team-proofs sups sn)]
                (if-let [[iid inode] (incompatible c g)]
                  (answer c "CONFLICT" nil (sides (e/ids-of sups) [iid]) (conj why inode))
                  (answer c "ANSWER" true nil why)))
      :blocked (let [[sups un] more]
                 (answer c "CONFLICT" nil (sides (e/ids-of sups) (e/ids-of un)) (concat (map :proof sups) (map :proof un))))
      (answer c "ANSWER" false nil [(why/explain-not c g)]))))

(defn- vars-of [t] (distinct (filter e/lvar? (tree-seq vector? seq t))))

(defn- sups-of [[st & more]] (case st (:proven :blocked) (first more) :defeated (second more) []))

(defn- decide-open [c g]
  (let [vs (vars-of g)
        value (fn [inst] (let [s (e/unify g inst {}) xs (mapv #(e/subst % s) vs)] (if (= 1 (count xs)) (first xs) xs)))
        cands (->> (concat
                    (for [r (filter #(#{:strict :defeasible} (:kind %)) (get-in c [:ix :rules])) [_ p] (e/apply-rule c r g)] (:goal p))
                    (for [cl (get-in c [:ix :claims]) :when (e/in-force? cl (:d c)) :let [s (e/unify g (:assertion cl) {})] :when s]
                      (e/subst g s)))
                   (filter e/ground?) e/sort-terms)
        ges (for [gi cands] [gi (e/evaluate c gi)])
        won (filter #(= :proven (first (second %))) ges)]
    (if (get-in c [:ix :functional (e/pred-of g)])
      (cond
        (= 1 (count won)) (let [[gi [_ sups sn]] (first won)] (answer c "ANSWER" (value gi) nil (team-proofs sups sn)))
        (and (empty? won) (seq ges))
        (answer c "CONFLICT" nil
                (apply sides (for [[_ ev] ges :let [ss (sups-of ev)] :when (seq ss)] (e/ids-of ss)))
                (for [[_ ev] ges s (sups-of ev)] (:proof s)))
        (empty? won) (answer c "ANSWER" nil nil [(why/explain-not c g)])
        :else (assoc (answer c "CONFLICT" nil nil []) :value (mapv (comp value first) won)))
      (let [vws (for [[gi [_ sups sn]] won] [(value gi) (team-proofs sups sn)])]
        (answer c "ANSWER" (vec (e/sort-terms (map first vws))) nil (mapcat second vws))))))

(defn decide [c g]
  (let [p (e/pred-of g)]
    (cond (not (known-pred? (:ix c) p)) {:status (scope (:ix c) p) :value nil :sides nil :why [] :owners [] :qualifier nil}
          (e/ground? g) (decide-ground c g)
          :else (decide-open c g))))

(defn why-not [c g]
  (let [ev (when (e/ground? g) (e/evaluate c g))]
    (if (= :proven (first ev))
      {:status "ANSWER" :value true :why (team-proofs (second ev) (nth ev 2)) :why_not []}
      {:status "ANSWER" :value false :why_not [(why/explain-not c g)]})))

;; ------------------------------------------------------------------ claims

(defn- failing? [s] (not (#{"holds" "holds_with_qualifier"} (:standing s))))

(defn- own-standing [[st & more]]
  (case st
    (:proven :none) {:standing "holds" :defeater nil :qualifier [] :sides nil}
    :defeated {:standing "rebutted" :defeater (:id (first more)) :qualifier [] :sides nil}
    :blocked {:standing "contested" :defeater nil :qualifier [] :sides (sides (e/ids-of (first more)) (e/ids-of (second more)))}))

(defn- sub-standing [subs]
  (if-let [s (first (filter #(and (= "required" (:role %)) (failing? %)) subs))]
    {:standing "rebutted" :defeater (:defeater s) :qualifier [] :sides nil :via (:id s)}
    (let [q (vec (sort (for [s subs :when (and (= "supporting" (:role s)) (failing? s))] (:id s))))]
      (if (empty? q)
        {:standing "holds" :defeater nil :qualifier [] :sides nil}
        {:standing "holds_with_qualifier" :defeater nil :qualifier q :sides nil}))))

(defn standing [c cl]
  (let [subs (vec (for [s (get-in c [:ix :claims]) :when (= (:id cl) (:parent s))] (standing c s)))
        st (if-not (e/in-force? cl (:d c))
             {:standing "not_in_force" :defeater nil :qualifier [] :sides nil}
             (let [st0 (own-standing (e/evaluate c (:assertion cl)))]
               (if (= "holds" (:standing st0)) (sub-standing subs) st0)))]
    (merge {:id (:id cl) :about (:about cl) :assertion (:assertion cl) :asserted_by (:asserted_by cl)
            :asserted_at (:asserted_at cl) :valid_from (:valid_from cl) :valid_to (:valid_to cl)
            :backing (:backing cl) :modal (:qualifier cl) :role (some-> (:role cl) name)}
           st {:subclaims subs})))

;; ------------------------------------------------------------------ vocabulary, metadata

(defn resolve-term [c text]
  (let [ix (:ix c)
        ids (->> (store/terms-matching *db* (store/norm text))
                 (mapcat #(or (seq (store/term-see *db* %)) [%])) distinct sort)
        byid (into {} (map (juxt :id identity) (:terms ix)))]
    {:text text :status (case (count ids) 0 "none" 1 "concept" "several")
     :candidates (vec (for [id ids :let [t (byid id)]] {:term id :definition (:definition t) :owner (name (:owner t))}))}))

(defn describe [c a]
  (let [ix (:ix c)
        find (fn [k] (first (filter #(= a (:id %)) (k ix))))
        [k doc b] (or (when-let [x (find :assets)] [(name (:kind x)) (:doc x) nil])
                      (when-let [x (find :terms)] ["term" (:definition x) (:concept x)])
                      (when-let [x (find :concepts)]
                        [(name (:kind x)) (:doc x) {:concept (name (:name x)) :tables (:tables x [])
                                                    :params (mapv name (:params x [])) :sql (:sql x)}])
                      (when-let [x (find :tables)] ["table" (:doc x) nil])
                      (when-let [x (find :columns)] ["column" (:doc x) nil]))]
    {:status (if k "ANSWER" "OUT_OF_SCOPE") :asset a :kind k :doc doc :bindings b
     :claims (store/claims-about *db* a)}))

;; ------------------------------------------------------------------ dispatch

(declare run-op)

(defn- parse-goal [s] (store/read-edn s))

(defn- with-hypothesis [op]
  (let [recs (if (:add op) (store/read-edn (:add op)) [])
        w (vec (:withhold op))]
    (store/hypothesis-db @conn (:hypothesis @opts) w recs
                         (fn [db ids]
                           {:results (binding [*db* db] (mapv run-op (:ops op))) :added ids :withheld w}))))

(defn- do-op [op]
  (case (:op op)
    "decide" (decide (ctx op) (parse-goal (:goal op)))
    "why_not" (why-not (ctx op) (parse-goal (:goal op)))
    "claims" (let [c (ctx op)]
               {:asset (:asset op)
                :claims (vec (for [cl (get-in c [:ix :claims]) :when (and (= (:asset op) (:about cl)) (nil? (:parent cl)))]
                               (standing c cl)))})
    "resolve_term" (resolve-term (ctx op) (:text op))
    "describe" (describe (ctx op) (:asset op))
    "fetch" (let [{:keys [rows sql params truncated]} (sql/fetch (keyword (:concept op))
                                                                 (into (array-map) (map (fn [[k v]] [(name k) v])) (:filters op)))]
              {:concept (:concept op) :filters (:filters op) :rows rows :sql sql :params params
               :row_count (count rows) :truncated truncated})
    "add" (let [ids (store/add-records! @conn (store/read-edn (:edn op)) :ext)] {:added ids})
    "with_hypothesis" (with-hypothesis op)
    (throw (ex-info (str "unknown op " (:op op)) {}))))

(defn run-op [op]
  (sql/begin-op!)
  (let [t0 (System/nanoTime)
        r (binding [*db* (or *db* @@conn)]
            (try (do-op op)
                 (catch Exception ex {:status "ERROR" :error (str (.getSimpleName (class ex)) ": " (.getMessage ex))})))
        ms (/ (- (System/nanoTime) t0) 1e6)]
    (assoc r :ms ms :sql_log (if (= "with_hypothesis" (:op op)) [] (sql/take-log)))))
