(ns v3b.model
  "V3b model: Malli schemas for the slice and its runtime extensions, validated natively on the EDN the
  engine loads (rule heads and bodies included: the rule language is EDN data, so the schema can see into it).

    clojure -M:model    validate, negative tests, docs/slice.md, docs/why-node.schema.json"
  (:require [clojure.data.json :as json]
            [clojure.edn :as edn]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.walk]
            [malli.core :as m]
            [malli.error :as me]
            [malli.json-schema :as mjs]
            [malli.util :as mu]))

(def owner [:enum :finance :hr :procurement :compliance :risk :controller])
(def date [:re #"^\d{4}-\d{2}-\d{2}$"])
(def lvar [:and symbol? [:fn {:error/message "variables start with ?"} #(str/starts-with? (name %) "?")]])

(def registry
  {::term [:or lvar string? int? boolean? [:and vector? [:ref ::expr]]]
   ::expr [:catn [:op [:enum :+ :-]] [:a [:schema [:ref ::term]]] [:b [:schema [:ref ::term]]]]
   ::filters [:map-of keyword? ::term]
   ::literal [:orn
              [:fetch [:catn [:op [:= :fetch]] [:concept keyword?] [:filters ::filters] [:outputs [:map-of keyword? lvar]]]]
              [:not [:catn [:op [:= :not]] [:lit [:and vector? [:ref ::literal]]]]]
              [:neg [:catn [:op [:= :neg]] [:lit [:and vector? [:ref ::literal]]]]]
              [:cmp [:catn [:op [:enum :< :<= :> :>= :=]] [:a ::term] [:b ::term]]]
              [:is [:catn [:op [:= :is]] [:x lvar] [:e [:and vector? ::expr]]]]
              [:as_of [:catn [:op [:= :as_of]] [:x ::term]]]
              [:derived [:catn [:pred [:and keyword? [:not [:enum :fetch :not :neg :is :as_of :< :<= :> :>= :=]]]]
                         [:args [:* ::term]]]]]})

(defn- s [x] (m/schema x {:registry (merge (m/default-schemas) registry)}))

(def literal (s [:and vector? ::literal]))

(def rule-common [[:id keyword?] [:owner owner] [:doc string?] [:recorded_at date]
                  [:class [:enum :definition :material_inference :exception :entitlement :superiority :incompatibility]]
                  [:superior-to {:optional true} [:vector keyword?]]])

(def Rule
  (s [:multi {:dispatch :kind}
      [:superiority (into [:map {:closed true} [:kind [:= :superiority]] [:pred keyword?] [:order [:vector owner]]] rule-common)]
      [::m/default (into [:map {:closed true} [:kind [:enum :strict :defeasible :defeater :incompatible]]
                          [:head [:and vector? ::literal]] [:body [:vector [:and vector? ::literal]]]] rule-common)]]))

(def claim-core
  [[:id keyword?] [:assertion [:and vector? ::literal]] [:asserted_by owner] [:asserted_at date]
   [:valid_from date] [:valid_to {:optional true} [:maybe date]]
   [:backing {:optional true} string?] [:qualifier {:optional true} [:enum "certainly" "presumably"]]
   [:warrant {:optional true} keyword?] [:recorded_at date]])

;; Flat claims (PLAN-v3-integrity §1.1): every claim is top level with its own asserter and times; a parent
;; names its members by id. That the ids resolve is checked on the Slice (claim-links-resolve).
(def claim-id [:and keyword? [:fn {:error/message "a claim id (:C<n> or :C<n>.<m>)"} #(re-matches #"C[0-9]+(\.[0-9]+)?" (name %))]])
(def Claim (s (into [:map {:closed true} [:about [:re #"^[a-z]+:[A-Za-z0-9_/]+$"]]
                     [:depends_on {:optional true} [:vector claim-id]]
                     [:supports {:optional true} [:vector claim-id]]] claim-core)))

(def Column (s [:map {:closed true} [:id [:re #"^col:[a-z_]+/[a-z_]+$"]] [:name string?]
                [:type [:enum :id :int :enum :bool :date]] [:doc string?]]))
(def Table (s [:map {:closed true} [:id [:re #"^table:[a-z_]+$"]] [:name string?] [:doc string?] [:columns [:vector Column]]]))
(def Concept
  (s [:and [:map {:closed true} [:id [:re #"^(measure|dim|entity|hier):[a-z_]+$"]] [:name keyword?]
            [:kind [:enum :entity :dimension :hierarchy :measure]] [:tables [:vector [:re #"^table:"]]] [:doc string?]
            [:columns {:optional true} [:vector keyword?]] [:params {:optional true} [:vector keyword?]]
            [:sql {:optional true} string?] [:derived-by {:optional true} keyword?]
            [:additivity {:optional true} [:enum :additive :semi-additive :non-additive :unknown]]
            [:unsafe_dims {:optional true} [:vector keyword?]]]
      [:fn {:error/message "a concept has :sql or :derived-by"} #(or (:sql %) (:derived-by %))]
      [:fn {:error/message "a measure declares :additivity (PLAN-v3-integrity §1.3)"}
       #(or (not= :measure (:kind %)) (:additivity %))]
      [:fn {:error/message "a semi-additive measure names its :unsafe_dims"}
       #(or (not= :semi-additive (:additivity %)) (seq (:unsafe_dims %)))]]))
(def Term (s [:map {:closed true} [:id [:re #"^term:[a-z_]+$"]] [:label string?] [:synonyms [:vector string?]]
              [:owner owner] [:definition string?]
              [:concept {:optional true} [:re #"^(measure|dim|entity|hier):"]] [:see {:optional true} [:vector [:re #"^term:"]]]]))
(def Asset (s [:map {:closed true} [:id string?] [:kind [:enum :vendor :employee]] [:doc string?]]))

(def Slice
  (s [:and [:map {:closed true}
      [:slice/version int?] [:today date]
      [:assets [:vector Asset]] [:tables [:vector Table]] [:concepts [:vector Concept]] [:terms [:vector Term]]
      [:code-lists [:vector [:map [:id [:re #"^codes:"]] [:values [:vector string?]]]]]
      [:taxonomies [:vector [:map [:id string?] [:code-list string?] [:tree [:map-of string? [:vector string?]]]]]]
      [:functional [:map-of keyword? pos-int?]]
      [:rules [:vector Rule]] [:claims [:vector Claim]]]
      [:fn {:error/message "every :depends_on / :supports id names a claim of the slice"}
       (fn [x] (let [ids (set (map :id (:claims x)))]
                 (every? ids (mapcat #(concat (:depends_on %) (:supports %)) (:claims x)))))]]))

(def Extension (s [:vector [:or Rule Claim]]))

(defn errors [schema x] (some-> (m/explain schema x) me/humanize))

(defn validate!
  "Throws on a slice (map) or extension (vector) that does not conform."
  [label x]
  (when-let [e (errors (if (map? x) Slice Extension) x)]
    (throw (ex-info (str label ": " (pr-str e)) {:errors e}))))

;; ------------------------------------------------------------------ why nodes (CONTRACT.md "Why trees")

(def WhyNode
  "The common why shape, as Malli over the JSON the CLI prints (keys read as keywords). Open maps: a node
  may carry more than the contract names (fetch nodes carry ms; blocked defeats carry :blocked)."
  (m/schema
   [:schema {:registry
             {::goal [:vector any?]
              ::node [:multi {:dispatch :type}
                      ["rule" [:map [:type [:= "rule"]] [:id string?] [:goal ::goal]
                               [:children [:vector [:ref ::node]]] [:failed {:optional true} [:maybe [:ref ::node]]]]]
                      ["claim" [:map [:type [:= "claim"]] [:id string?] [:goal ::goal] [:asserted_by string?]
                                [:asserted_at string?] [:children [:vector [:ref ::node]]]]]
                      ["fetch" [:map [:type [:= "fetch"]] [:concept string?] [:filters map?] [:sql string?]
                                [:params vector?] [:rows int?] [:row {:optional true} [:maybe map?]]]]
                      ["fact" [:map [:type [:= "fact"]] [:goal ::goal] [:holds {:optional true} boolean?]]]
                      ["absent" [:map [:type [:= "absent"]] [:goal ::goal] [:children {:optional true} [:vector [:ref ::node]]]]]
                      ["defeated_by" [:map [:type [:= "defeated_by"]] [:id string?] [:target string?]
                                      [:children [:vector [:ref ::node]]] [:blocked {:optional true} boolean?]]]
                      ["superior" [:map [:type [:= "superior"]] [:winner string?] [:loser string?]
                                   [:source [:enum "explicit" "authority:R313" "later" "strict"]]]]]}}
    ::node]))

;; ------------------------------------------------------------------ instance docs (same layout as V3a's build.py)

(defn- nm [x] (if (keyword? x) (name x) (str x)))
(defn- esc [s] (str/replace (str s) "|" "\\|"))
(defn- csv [xs] (let [s (str/join ", " (map nm xs))] (if (str/blank? s) "—" s)))

(defn slice-md [s ext]
  (let [rules (concat (:rules s) (filter :kind ext))
        claims (concat (:claims s) (filter :assertion ext))
        claim-line (fn [c] (str "`" (pr-str (:assertion c)) "` — " (nm (:asserted_by c)) ", " (:asserted_at c)
                                ", in force " (:valid_from c) "–" (or (:valid_to c) "open")))]
    (str/join "\n"
              (concat
               ["# Procurement slice: model, vocabulary, rules, claims" ""
                (str "Evaluation date: " (:today s) ". Generated from `shared/slice.edn` by `v3b-clojure/src/v3b/model.clj`.") ""
                "## Tables" ""]
               (mapcat (fn [t] (concat [(str "### " (:name t) " (`" (:id t) "`)") "" (:doc t) ""
                                        "| column | type | meaning |" "|---|---|---|"]
                                       (for [c (:columns t)] (str "| " (:name c) " | " (nm (:type c)) " | " (esc (:doc c)) " |"))
                                       [""]))
                       (:tables s))
               ["## Semantic layer" "" "| concept | kind | parameters | columns | meaning |" "|---|---|---|---|---|"]
               (for [c (:concepts s)]
                 (str "| " (nm (:name c)) " | " (nm (:kind c)) " | " (csv (:params c)) " | " (csv (:columns c)) " | " (esc (:doc c)) " |"))
               ["" "## Vocabulary" ""]
               (for [t (:terms s)]
                 (str "- **" (:label t) "**" (when (seq (:synonyms t)) (str " (also: " (str/join ", " (:synonyms t)) ")"))
                      " — " (:definition t) (when (seq (:see t)) (str " See " (str/join ", " (:see t)) "."))
                      " *Owner: " (nm (:owner t)) ".*"))
               ["" "## Code lists" ""]
               (for [c (:code-lists s)] (str "- `" (:id c) "`: " (str/join ", " (:values c))))
               ["" "## Rules" "" "| id | kind | owner | rule |" "|---|---|---|---|"]
               (for [r rules]
                 (str "| " (nm (:id r)) " | " (nm (:kind r)) " | " (nm (:owner r)) " | " (esc (:doc r))
                      (when (seq (:superior-to r)) (str " Prevails over " (csv (:superior-to r)) ".")) " |"))
               ["" "## Claims" ""]
               (mapcat (fn [c] (cons (str "- **" (nm (:id c)) "** about `" (:about c) "`: " (claim-line c) "; "
                                          (:qualifier c "") "; backing: " (:backing c ""))
                                     (concat (for [x (:depends_on c)] (str "  - depends on " (nm x)))
                                             (for [x (:supports c)] (str "  - supported by " (nm x))))))
                       claims)
               [""]))))

;; ------------------------------------------------------------------ negative tests

(def negatives
  "Each mutation of the slice must be rejected; [label path-fn]. The first is the class rule LinkML
  declared but did not enforce (PLAN Decisions, LinkML model shape)."
  [["concept with neither :sql nor :derived-by" #(update-in % [:concepts 0] dissoc :sql :derived-by)]
   ["unknown owner on a rule" #(assoc-in % [:rules 0 :owner] :marketing)]
   ["rule variable without ?" #(assoc-in % [:rules 0 :head 1] 'cc)]
   ["fetch filters not a map" #(assoc-in % [:rules 0 :body 0 2] ["cc" '?c])]
   ["unknown arithmetic op in :is" #(update-in % [:rules 1 :body] conj '[:is ?x [:* 2 3]])]
   ["comparison with three arguments" #(update-in % [:rules 1 :body] conj '[:< ?x 1 2])]
   ["bad date in a claim" #(assoc-in % [:claims 0 :asserted_at] "2026-3-1")]
   ["unknown key on a claim (closed map)" #(assoc-in % [:claims 0 :confidence] 0.9)]
   ["depends_on member not a claim id" #(assoc-in % [:claims 0 :depends_on] [:R101])]
   ["superiority order with unknown owner" #(update % :rules conj {:id :R999 :kind :superiority :owner :controller
                                                                  :class :superiority :doc "x" :pred :p :order [:hr :sales]
                                                                  :recorded_at (get-in % [:rules 0 :recorded_at])})]
   ["rule kind unknown" #(assoc-in % [:rules 0 :kind] :presumption)]
   ["negated literal wrapping a non-literal" #(assoc-in % [:rules 0 :head] [:neg "x"])]
   ;; PLAN-v3-integrity §1.5
   ["nested :subclaims (claims are flat)" #(assoc-in % [:claims 0 :subclaims] [(get-in % [:claims 1])])]
   ["measure without :additivity"
    (fn [s] (update s :concepts (fn [cs] (let [i (first (keep-indexed #(when (= :measure (:kind %2)) %1) cs))]
                                           (update cs i dissoc :additivity)))))]
   ["dangling depends_on id" #(update-in % [:claims 0 :depends_on] conj :C9.9)]])

(defn -main [& [results]]
  (let [root (System/getProperty "v3b.root" "../../..")
        rd #(edn/read-string {:readers {'inst str}} (slurp (str root "/spikes/v3/shared/" %)))
        s (rd "slice.edn") ext (rd "extension.edn")
        out (io/file "docs")]
    (println "1 slice.edn:" (or (errors Slice s) "valid") "| extension.edn:" (or (errors Extension ext) "valid"))
    (let [rs (for [[label f] negatives] [label (some? (errors Slice (f s)))])]
      (println (str "2 negative tests: " (count (filter second rs)) "/" (count rs) " rejected"))
      (doseq [[label ok] rs :when (not ok)] (println "   NOT REJECTED:" label)))
    (.mkdirs out)
    (spit (io/file out "slice.md") (slice-md s ext))
    (spit (io/file out "why-node.schema.json") (json/write-str (mjs/transform WhyNode) :indent true :escape-slash false))
    (println "3 docs/slice.md," (count (str/split-lines (slurp (io/file out "slice.md")))) "lines; docs/why-node.schema.json")
    (when results
      (let [rs (json/read-str (slurp results) :key-fn keyword)
            trees (atom [])]
        (clojure.walk/postwalk (fn [x] (when (and (map? x) (vector? (:why x))) (swap! trees into (:why x)))
                                 (when (and (map? x) (vector? (:why_not x))) (swap! trees into (:why_not x))) x) rs)
        (let [bad (remove #(m/validate WhyNode %) @trees)]
          (println "4 why trees in" results ":" (count @trees) "roots," (count bad) "not conforming")
          (doseq [b (take 3 bad)] (println "  " (pr-str (me/humanize (m/explain WhyNode b))))))))))
