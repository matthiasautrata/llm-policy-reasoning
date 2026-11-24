(ns v3b.why
  "V3b explanations (CONTRACT.md 'Why trees'), the same walk as V3a's why.pl.

  explain-not: an absent node for the goal whose children are, per candidate rule, a rule node with the
  body literals that held and `failed`: the first literal that did not (recursively explained for
  derived literals, a 0-row fetch, a false builtin, a NAF literal whose goal is provable) or, when the
  body held, the defeated_by node of the attacker that won (or blocked). In-force claims asserting the
  goal that were defeated appear as claim nodes with a defeated_by child. Bodies are followed along
  their first solution."
  (:require [v3b.engine :as e]))

(declare explain-not)

(defn defeat-node [ctx id [st & more]]
  (case st
    :defeated (let [[a] more]
                {:type "defeated_by" :id (:id a) :target id
                 :children (into [(:proof a)]
                                 (when-let [src (first (e/sup ctx (:id a) id))]
                                   [{:type "superior" :winner (:id a) :loser id :source src}]))})
    :blocked (let [[_ unbeaten] more a (first unbeaten)]
               {:type "defeated_by" :id (:id a) :target id :children [(:proof a)] :blocked true})
    nil))

(defn- failed-lit [ctx l s]
  (let [[op & args] l]
    (case op
      :fetch (let [[c f] args f2 (e/subst f s)]
               (if (e/ground? f2)
                 (let [[rows info fs] (e/fetch-rows c f2)]
                   (merge info {:type "fetch" :concept (name c) :filters fs :rows (count rows) :row nil}))
                 {:type "absent" :goal [:fetch c]}))
      :not (let [g (e/subst (first args) s)]
             {:type "absent" :goal [:not g] :children [(second (first (e/prove ctx g)))]})
      (:< :<= :> :>= := :is :as_of) {:type "fact" :goal (e/subst l s) :holds false}
      (explain-not ctx (e/subst l s)))))

(defn- walk-body
  "First solution of each literal in turn -> [s done failed-node-or-nil]."
  [ctx lits s]
  (loop [lits lits s s done []]
    (if (empty? lits)
      [s done nil]
      (if-let [[s2 k] (first (e/lit ctx (first lits) s))]
        (recur (rest lits) s2 (conj done k))
        [s done (failed-lit ctx (first lits) s)]))))

(defn- explain-rule [ctx r g ev]
  (let [{:keys [head] bd :body} (e/rename (select-keys r [:head :body]))]
    (when-let [s (e/unify head g {})]
      (let [[s2 done failed] (walk-body ctx bd s)]
        {:type "rule" :id (:id r) :goal (e/subst g s2) :children done
         :failed (or failed (defeat-node ctx (:id r) ev))}))))

(defn explain-not [ctx g]
  (let [ev (if (e/ground? g) (e/evaluate ctx g) [:none []])
        rs (for [r (get-in ctx [:ix :rules]) :when (#{:strict :defeasible} (:kind r))
                 :let [n (explain-rule ctx r g ev)] :when n] n)
        cs (when (and (e/ground? g) (not (#{:proven :none} (first ev))))
             (for [c (get-in ctx [:ix :claims])
                   :when (and (= (:assertion c) g) (e/in-force? c (:d ctx)))
                   :let [dn (defeat-node ctx (:id c) ev)] :when dn]
               (assoc (e/claim-proof c g) :children [dn])))]
    {:type "absent" :goal g :children (vec (concat rs cs))}))
