(ns v3b.probe
  "V3b probes for PLAN §5.2 (not part of the acceptance test):

    clojure -M:probe

  1 who said it: attributes (:claim/asserted-by) vs transaction metadata (:tx/asserted-by)
  2 as-of on transaction time (d/as-of with a backdated :db/txInstant) vs valid time (attributes)
  3 history: C1 before/after the runtime extension, via d/as-of on a transaction id
  4 hypothesis cost: Datahike branch vs d/with, same question (Q11), n runs each"
  (:require [clojure.string :as str]
            [datahike.api :as d]
            [taoensso.timbre :as timbre]
            [v3b.ops :as ops]
            [v3b.sql :as sql]
            [v3b.store :as store]))

(def root (System/getProperty "v3b.root" "../../.."))
(defn- inst [s] (java.util.Date/from (java.time.Instant/parse (str s "T00:00:00Z"))))
(defn- ms [t0] (/ (- (System/nanoTime) t0) 1e6))
(defn- pct [xs p] (let [v (vec (sort xs))] (v (min (dec (count v)) (int (* p (count v)))))))

(defn- fresh! []
  (when @ops/conn (store/destroy! @ops/conn))
  (reset! ops/conn (store/create!))
  (let [s (store/load-file! @ops/conn (str root "/spikes/v3/shared/slice.edn"))]
    (doseq [c (:concepts s) :when (:sql c)] (sql/register! (:name c) (:sql c) (:params c [])))))

(defn who-said-it []
  (let [db @@ops/conn
        by-attr (sort (d/q '[:find [?id ...] :where [?e :claim/asserted-by :finance] [?e :rec/id ?id]] db))
        by-tx (sort (d/q '[:find [?id ...] :where [?e :claim/pred _ ?tx] [?tx :tx/asserted-by :finance] [?e :rec/id ?id]] db))]
    (println "1 who said it: claims by finance")
    (println "   attribute :claim/asserted-by   " by-attr)
    (println "   tx metadata :tx/asserted-by    " by-tx)
    (println "   differ:" (vec (sort (concat (remove (set by-tx) by-attr) (remove (set by-attr) by-tx))))
             "(a sub-claim is transacted with its parent, so the transaction names the parent's asserter)")))

(defn as-of-tx-time []
  (let [db @@ops/conn
        known (fn [date] (sort (d/q '[:find [?id ...] :where [?e :claim/pred] [?e :rec/id ?id] (not [?e :claim/parent _])]
                                    (d/as-of db (inst date)))))
        rules (fn [date] (count (d/q '[:find [?e ...] :where [?e :rule/kind]] (d/as-of db (inst date)))))
        valid (fn [date] (sort (d/q '[:find [?id ...] :in $ ?d
                                      :where [?e :claim/valid-from ?f] [(<= ?f ?d)] [?e :rec/id ?id] (not [?e :claim/parent _])
                                      (or-join [?e ?d] (not [?e :claim/valid-to _]) (and [?e :claim/valid-to ?t] [(<= ?d ?t)]))]
                                    db date)))]
    (println "2 as-of 2026-07-15 (Q10's date)")
    (println "   tx time  (d/as-of, txInstant = asserted_at): claims" (known "2026-07-15") "rules" (rules "2026-07-15"))
    (println "   valid time (attributes, in force on the date): claims" (valid "2026-07-15"))
    (println "   tx time 2026-06-01 (C4 asserted 01-02 but transacted after C3's 07-01):" (known "2026-06-01"))
    (println "   tx time 2026-08-02 (after C5's valid_from, before its asserted_at):" (known "2026-08-02"))
    (println "   tx instants in transaction order:"
             (->> (d/q '[:find ?tx ?t :where [?e :claim/pred _ ?tx] [?tx :db/txInstant ?t] (not [?e :claim/parent _])] db)
                  (sort-by first) (map #(subs (str (.toInstant ^java.util.Date (second %))) 0 10)) vec))))

(defn history []
  (let [t-before (:max-tx @@ops/conn)
        q {:op "claims" :asset "vendor:bolt" :as_of "2026-07-01"}
        st #(->> (:claims %) (filter (fn [c] (= "C1" (:id c)))) first :standing)
        before (ops/run-op q)
        _ (store/add-records! @ops/conn (store/read-edn (slurp (str root "/spikes/v3/shared/extension.edn"))) :ext)
        after (ops/run-op q)
        then (binding [ops/*db* (d/as-of @@ops/conn t-before)] (ops/run-op q))]
    (println "3 history: C1 on 2026-07-01")
    (println "   before extension:" (st before) "| after:" (st after) "| d/as-of tx" t-before "on the extended db:" (st then))))

(defn hypothesis-cost [n]
  (println (str "4 hypothesis cost (Q11: withhold R313, decide cost_centre_of e077 as of 2026-07-15), n=" n))
  (doseq [mode [:branch :with]]
    (swap! ops/opts assoc :hypothesis mode)
    (let [op {:op "with_hypothesis" :withhold ["R313"]
              :ops [{:op "decide" :goal "[:cost_centre_of \"e077\" ?c]" :as_of "2026-07-15"}]}
          r0 (ops/run-op op)
          ts (vec (for [_ (range n)] (let [t0 (System/nanoTime)] (ops/run-op op) (ms t0))))]
      (println (format "   %-7s status %s  p50 %.1f ms  p95 %.1f ms  (first run %.1f ms)"
                       (name mode) (-> r0 :results first :status) (pct ts 0.5) (pct ts 0.95) (:ms r0)))))
  (let [after (ops/run-op {:op "decide" :goal "[:cost_centre_of \"e077\" ?c]" :as_of "2026-07-15"})]
    (println "   base state afterwards:" (:status after) (:value after))))

(defn -main [& [n]]
  (timbre/merge-config! {:min-level :warn :appenders {:println (timbre/println-appender {:stream :std-err})}})
  (sql/configure! {:backend "duckdb" :duckdb "spikes/v3/shared/slice.duckdb" :fetch_limit 10000} root)
  (fresh!)
  (who-said-it)
  (as-of-tx-time)
  (history)
  (fresh!)
  (hypothesis-cost (parse-long (or n "50")))
  (store/destroy! @ops/conn)
  (shutdown-agents)
  (System/exit 0))
