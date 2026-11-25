(ns v3b.store
  "V3b store: every slice record (rules, claims, terms, concepts, tables, columns, assets) is a Datahike
  entity. The engine reads an in-memory index built from a db value; a hypothesis is a Datahike branch
  (or a speculative d/with db), so 'the state' is always one immutable db value.

  Each entity: :rec/id (unique), :rec/type, :rec/seq (authoring order), :rec/source (base|ext|hyp),
  :rec/edn (the record, pr-str) plus a few queryable attributes. Claims are transacted one per
  transaction, the transaction carrying who said it (:tx/asserted-by) and when (:db/txInstant backdated
  to asserted_at), so 'who said it' is answerable both from attributes and from transaction metadata."
  (:require [clojure.edn :as edn]
            [clojure.string :as str]
            [datahike.api :as d]
            [datahike.experimental.versioning :as v]))

(def schema
  (vec (for [[ident type & [card uniq]] [[:rec/id :string :one :identity] [:rec/type :keyword] [:rec/seq :long]
                                         [:rec/source :keyword] [:rec/edn :string]
                                         [:rule/kind :keyword] [:rule/owner :keyword] [:rule/head-pred :keyword]
                                         [:claim/pred :keyword] [:claim/about :string] [:claim/asserted-by :keyword]
                                         [:claim/asserted-at :string] [:claim/valid-from :string] [:claim/valid-to :string]
                                         [:claim/parent :string] [:claim/role :keyword]
                                         [:term/key :string :many] [:term/see :string :many]
                                         [:tx/asserted-by :keyword]]]
             (cond-> {:db/ident ident :db/valueType (keyword "db.type" (name type))
                      :db/cardinality (if (= card :many) :db.cardinality/many :db.cardinality/one)}
               uniq (assoc :db/unique :db.unique/identity)))))

(defn read-edn
  "EDN text -> data. #inst becomes its ISO string (dates compare as strings, as in V3a)."
  [text]
  (edn/read-string {:readers {'inst str}} text))

(defn norm
  "resolve_term normalisation: lowercase, non-alphanumerics to spaces, collapse."
  [s]
  (->> (str/split (str/replace (str/lower-case s) #"[^\p{L}\p{N}]" " ") #" ") (remove str/blank?) (str/join " ")))

(defn rid [x] (if (keyword? x) (name x) (str x)))

(defn pred-of [l] (if (= :neg (first l)) (recur (second l)) (first l)))

;; ------------------------------------------------------------------ connection

(defonce ^:private cfg (atom nil))

(defn create! []
  (let [dir (str (System/getProperty "java.io.tmpdir") "/v3b-" (random-uuid))
        c {:store {:backend :file :path dir :id (random-uuid)} :keep-history? true :schema-flexibility :write}]
    (d/create-database c)
    (reset! cfg c)
    (let [conn (d/connect c)]
      (d/transact conn schema)
      conn)))

(defn destroy! [conn]
  (d/release conn)
  (try (d/delete-database @cfg) (catch Exception _)))

(def ^:private seqno (atom 0))

(defn- ent [type id m src & {:as extra}]
  (merge {:rec/id id :rec/type type :rec/seq (swap! seqno inc) :rec/source src :rec/edn (pr-str m)} extra))

(defn- inst [s] (java.util.Date/from (java.time.Instant/parse (str s "T00:00:00Z"))))

(defn- claim-ents
  "Claims are flat (PLAN-v3-integrity §1.1): one entity per claim, with its own asserter, times and :about.
  Links (:depends_on, :supports) stay in the record's EDN; links/1 reads them. :claim/parent and
  :claim/role are no longer written (probe.clj's PLAN-v3 queries used them)."
  [m src]
  [(cond-> (ent :claim (rid (:id m)) m src)
     true (assoc :claim/pred (pred-of (:assertion m)) :claim/about (:about m)
                 :claim/asserted-by (:asserted_by m) :claim/asserted-at (:asserted_at m)
                 :claim/valid-from (:valid_from m))
     (:valid_to m) (assoc :claim/valid-to (:valid_to m)))])

(defn links
  "claim records -> {member-id [parent-id role]}; role \"required\" for :depends_on, \"supporting\" for :supports."
  [claims]
  (into {} (for [c claims [k role] [[:depends_on "required"] [:supports "supporting"]] x (k c)]
             [(rid x) [(rid (:id c)) role]])))

(defn link-order
  "claim record -> member ids in output order: depends_on, then supports."
  [c]
  (mapv rid (concat (:depends_on c) (:supports c))))

(defn- rule-ent [m src]
  (cond-> (ent :rule (rid (:id m)) m src)
    true (assoc :rule/kind (:kind m) :rule/owner (:owner m))
    (vector? (:head m)) (assoc :rule/head-pred (pred-of (:head m)))))

(defn add-records!
  "Rule and claim records -> transactions. One transaction for the rules; one per claim, carrying its
  asserter and assertion date as transaction metadata. -> ids in the order given."
  [conn recs src]
  (let [{claims true rules false} (group-by #(contains? % :assertion) recs)]
    (when (seq rules) (d/transact conn (mapv #(rule-ent % src) rules)))
    (doseq [c claims]
      (d/transact conn {:tx-data (claim-ents c src)
                        :tx-meta {:tx/asserted-by (:asserted_by c) :db/txInstant (inst (:asserted_at c))}}))
    (mapv (comp rid :id) recs)))

(defn load-slice! [conn s]
  (d/transact conn (into [(ent :slice "slice" (select-keys s [:today :functional :code-lists :taxonomies]) :base)]
                         (concat
                          (for [a (:assets s)] (ent :asset (:id a) a :base))
                          (for [t (:tables s)] (ent :table (:id t) (dissoc t :columns) :base))
                          (for [t (:tables s) c (:columns t)] (ent :column (:id c) c :base))
                          (for [c (:concepts s)] (ent :concept (:id c) c :base))
                          (for [t (:terms s)]
                            (cond-> (ent :term (:id t) t :base)
                              true (assoc :term/key (vec (distinct (map norm (cons (:label t) (:synonyms t))))))
                              (seq (:see t)) (assoc :term/see (:see t)))))))
  (add-records! conn (concat (:rules s) (:claims s)) :base))

(defn load-file! [conn path]
  (let [x (read-edn (slurp path))]
    (if (map? x) (do (load-slice! conn x) x) (do (add-records! conn x :ext) nil))))

;; ------------------------------------------------------------------ index (what the engine reads)

(defn- index* [db]
  (let [recs (->> (d/q '[:find ?seq ?type ?edn ?src
                         :where [?e :rec/seq ?seq] [?e :rec/type ?type] [?e :rec/edn ?edn] [?e :rec/source ?src]] db)
                  (sort-by first)
                  (map (fn [[_ t e src]] [t (assoc (read-edn e) ::source src)])))
        about (into {} (d/q '[:find ?id ?a :where [?e :claim/about ?a] [?e :rec/id ?id]] db))
        by-type (group-by first recs)
        slice (second (first (by-type :slice)))
        rules (vec (for [[_ m] (by-type :rule)]
                     (assoc m :id (rid (:id m)) :superior-to (set (map rid (:superior-to m))))))
        L (links (map second (by-type :claim)))
        claims (vec (for [[_ m] (by-type :claim) :let [id (rid (:id m)) [p role] (L id)]]
                      (assoc m :id id :parent p :about (about id) :role role :members (link-order m)
                             :valid_to (:valid_to m))))]
    {:today (:today slice) :functional (:functional slice)
     :rules rules :claims claims
     :rule (into {} (map (juxt :id identity) rules))
     :claim (into {} (map (juxt :id identity) claims))
     :concepts (mapv second (by-type :concept)) :terms (mapv second (by-type :term))
     :assets (mapv second (by-type :asset)) :tables (mapv second (by-type :table)) :columns (mapv second (by-type :column))}))

(def ^:private last-ix (atom [nil nil]))

(defn index
  "Index of a db value, cached for the last db seen (a hypothesis db replaces it for the nested ops)."
  [db]
  (let [[d0 ix] @last-ix]
    (if (identical? d0 db) ix (let [ix (index* db)] (reset! last-ix [db ix]) ix))))

;; ------------------------------------------------------------------ queries the ops ask the store directly

(defn terms-matching [db key]
  (d/q '[:find [?id ...] :in $ ?k :where [?e :term/key ?k] [?e :rec/id ?id]] db key))

(defn term-see [db id]
  (d/q '[:find [?s ...] :in $ ?id :where [?e :rec/id ?id] [?e :term/see ?s]] db id))

(defn claims-about
  "Top-level claim ids about an asset, in authoring order."
  [db asset]
  (let [L (links (map read-edn (d/q '[:find [?edn ...] :where [?e :rec/type :claim] [?e :rec/edn ?edn]] db)))]
    (->> (d/q '[:find ?seq ?id :in $ ?a
                :where [?e :claim/about ?a] [?e :rec/id ?id] [?e :rec/seq ?seq]] db asset)
         sort (map second) (remove L) vec)))

;; ------------------------------------------------------------------ hypotheses

(defn hypothesis-db
  "mode :branch: a Datahike branch of main, edited, read, then deleted. mode :with: d/with on the db value.
  f receives the hypothetical db; the main branch is never written."
  [conn mode withhold recs f]
  (let [retract (vec (for [w withhold :when (d/entity @conn [:rec/id w])] [:db/retractEntity [:rec/id w]]))]
    (case mode
      :branch
      (let [b (keyword (str "hyp-" (swap! seqno inc)))]
        (v/branch! conn :db b)
        (let [bc (d/connect (assoc @cfg :branch b))]
          (try
            (when (seq retract) (d/transact bc retract))
            (let [ids (add-records! bc recs :hyp)]
              (f @bc ids))
            (finally (d/release bc) (v/delete-branch! conn b)))))
      :with
      (let [db1 (if (seq retract) (:db-after (d/with @conn retract)) @conn)
            {claims true rules false} (group-by #(contains? % :assertion) recs)
            db2 (if (seq rules) (:db-after (d/with db1 (mapv #(rule-ent % :hyp) rules))) db1)
            db3 (reduce (fn [db c] (:db-after (d/with db (claim-ents c nil (:about c) :hyp)))) db2 claims)]
        (f db3 (mapv (comp rid :id) recs))))))
