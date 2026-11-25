(ns v3b.cli
  "V3b CLI (CONTRACT.md): session script (JSON) on stdin -> {\"results\": [...], \"load_ms\": n} on stdout.
  Run from the repo root. Optional config key \"hypothesis\": \"branch\" (default) | \"with\"."
  (:gen-class)
  (:require [clojure.data.json :as json]
            [clojure.string :as str]
            [clojure.walk :as walk]
            [taoensso.timbre :as timbre]
            [v3b.gate :as gate]
            [v3b.model :as model]
            [v3b.ops :as ops]
            [v3b.sql :as sql]
            [v3b.store :as store]))

(defn- jsonable
  "Keywords -> names; logic variables -> their source name (\"?r\")."
  [x]
  (walk/prewalk (fn [v] (cond (keyword? v) (name v)
                              (symbol? v) (first (str/split (name v) #"#"))
                              :else v))
                x))

(declare run-loaded)

(defn run [script]
  (let [root (System/getProperty "v3b.root" (System/getProperty "user.dir"))
        cfg (:config script)
        t0 (System/nanoTime)]
    (sql/configure! cfg root)
    (when-let [h (:hypothesis cfg)] (swap! ops/opts assoc :hypothesis (keyword h)))
    (reset! ops/session {:root root :load (vec (:load script)) :added []})
    (if-let [v (seq (gate/violations root (vec (:load script)) [] []))]   ; before Malli and the store
      {:error {:op "load" :violations (vec v)} :results [] :load_ms (/ (- (System/nanoTime) t0) 1e6)}
      (run-loaded script root t0))))

(defn- run-loaded [script root t0]
  (do
    (reset! ops/conn (store/create!))
    (doseq [f (:load script)]
      (let [text (slurp (str root "/" f))]
        (model/validate! f (store/read-edn text))
        (when-let [s (store/load-file! @ops/conn (str root "/" f))]
          (doseq [c (:concepts s) :when (:sql c)] (sql/register! (:name c) (:sql c) (:params c []))))))
    (let [load-ms (/ (- (System/nanoTime) t0) 1e6)
          results (mapv ops/run-op (:ops script))
          conc (when (:concurrent script) (ops/run-concurrent (:concurrent script)))
          after (when (:after script) (mapv ops/run-op (:after script)))]
      (store/destroy! @ops/conn)
      (cond-> {:results results :load_ms load-ms} conc (assoc :concurrent conc) after (assoc :after after)))))

(defn -main [& _]
  (timbre/merge-config! {:min-level :warn
                         :appenders {:println (timbre/println-appender {:stream :std-err})}})
  (let [script (json/read-str (slurp *in*) :key-fn keyword)
        out (run script)]
    (json/write (jsonable out) *out*)
    (flush)
    (shutdown-agents)
    (System/exit 0)))
