(ns v3b.sql
  "V3b SQL boundary: concept bindings (from slice.edn) -> SQL, executed through JDBC on DuckDB or Postgres.

  Same binding layer as V3a's sql.py, so that differences are engine differences:
    - $name required parameters -> `?` placeholders; other filters wrap the template as
      SELECT * FROM (<sql>) t WHERE t.\"col\" = ? ... LIMIT fetch_limit + 1
    - @iso(x): DuckDB strftime(x, '%Y-%m-%d'), Postgres to_char(x, 'YYYY-MM-DD')
  A per-op cache avoids re-issuing a statement inside one op; the per-op log is the CLI's sql_log.
  The SQL text reported for Postgres has `?` rewritten to `%s` (and `%` doubled) so the shared checker
  can re-run it with psycopg; the statement executed is the JDBC one."
  (:require [clojure.string :as str])
  (:import [java.sql DriverManager ResultSet]
           [java.util Properties]))

;; cfg, connection and concept bindings are shared; the per-op cache and log are per thread (ThreadLocal), and
;; statements are serialised on the one connection, so concurrent ops (shared/isolation.py) do not mix logs.
(def ^:private state (atom {:cfg nil :con nil :concepts {}}))
(def ^:private ^ThreadLocal op-state (ThreadLocal/withInitial (reify java.util.function.Supplier (get [_] (atom {:cache {} :log []})))))
(defn- ostate [] (.get op-state))

(defn configure! [cfg root]
  (when-let [c (:con @state)] (.close ^java.sql.Connection c))
  (let [con (case (:backend cfg)
              "duckdb" (let [p (doto (Properties.) (.setProperty "duckdb.read_only" "true"))]
                         (DriverManager/getConnection (str "jdbc:duckdb:" root "/" (:duckdb cfg)) p))
              "postgres" (let [kv (into {} (for [part (str/split (:postgres cfg) #"\s+")
                                                 :let [[k v] (str/split part #"=" 2)]] [k v]))]
                           (DriverManager/getConnection
                            (str "jdbc:postgresql://" (get kv "host" "localhost") ":" (get kv "port" "5432")
                                 "/" (get kv "dbname"))
                            (doto (Properties.) (.setProperty "user" (get kv "user" (System/getProperty "user.name")))))))]
    (swap! state assoc :cfg cfg :con con)))

(defn register! [concept-name sql params]
  (swap! state assoc-in [:concepts concept-name] [sql (mapv name params)]))

(defn- dialect [sql]
  (if (= "duckdb" (get-in @state [:cfg :backend]))
    (str/replace sql #"@iso\(([^)]*)\)" "strftime($1, '%Y-%m-%d')")
    (str/replace sql #"@iso\(([^)]*)\)" "to_char($1, 'YYYY-MM-DD')")))

(defn build
  "concept name (keyword), filters {string value} -> [sql params limit]"
  [c filters]
  (let [[tmpl req] (or (get-in @state [:concepts c]) (throw (ex-info (str "unknown concept " c) {})))
        missing (remove #(contains? filters %) req)
        _ (when (seq missing) (throw (ex-info (str "fetch " (name c) ": required parameter(s) " (vec missing) " unbound") {})))
        params (transient [])
        sql (str/replace (dialect tmpl) #"\$([a-z_]+)" (fn [[_ p]] (conj! params (get filters p)) "?"))
        rest (remove (fn [[k _]] (some #{k} req)) filters)
        sql (if (seq rest)
              (str "SELECT * FROM (" sql ") t WHERE " (str/join " AND " (map (fn [[k _]] (str "t.\"" k "\" = ?")) rest)))
              sql)
        params (into (persistent! params) (map second rest))
        limit (long (get-in @state [:cfg :fetch_limit] 10000))]
    [(str sql " LIMIT " (inc limit)) params limit]))

(defn- reported [sql]
  (if (= "postgres" (get-in @state [:cfg :backend]))
    (-> sql (str/replace "%" "%%") (str/replace "?" "%s"))
    sql))

(defn- value [v]
  (cond (instance? java.math.BigDecimal v) (if (zero? (.scale ^java.math.BigDecimal v)) (long v) (double v))
        (instance? java.math.BigInteger v) (long v)
        (instance? Integer v) (long v)
        (instance? java.sql.Date v) (str v)
        :else v))

(defn fetch
  "-> {:rows [{string value}] :sql :params :truncated}"
  [c filters]
  (let [k [c filters]]
    (or (get-in @(ostate) [:cache k])
        (let [[sql params limit] (build c filters)
              ^java.sql.Connection con (:con @state)
              rows (locking con (with-open [ps (.prepareStatement con sql)]
                     (doseq [[i p] (map-indexed vector params)] (.setObject ps (int (inc i)) p))
                     (with-open [^ResultSet rs (.executeQuery ps)]
                       (let [md (.getMetaData rs) n (.getColumnCount md)
                             cols (mapv #(.getColumnLabel md (int %)) (range 1 (inc n)))]
                         (loop [acc (transient [])]
                           (if (.next rs)
                             (recur (conj! acc (into (array-map) (map (fn [i col] [col (value (.getObject rs (int i)))])
                                                                      (range 1 (inc n)) cols))))
                             (persistent! acc)))))))
              truncated (> (count rows) limit)
              rows (vec (take limit rows))
              out {:rows rows :sql (reported sql) :params params :truncated truncated}]
          (swap! (ostate) (fn [s] (-> s (assoc-in [:cache k] out)
                                   (update :log conj {:concept (name c) :sql (reported sql) :params params :rows (count rows)}))))
          out))))

(defn begin-op! [] (reset! (ostate) {:cache {} :log []}))
(defn take-log [] (:log @(ostate)))
