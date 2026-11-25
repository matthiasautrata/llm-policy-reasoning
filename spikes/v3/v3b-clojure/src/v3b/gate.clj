(ns v3b.gate
  "The shared integrity gate (PLAN-v3-integrity §2), run as a subprocess: shared/integrity.py reads
  {load, added, withhold} and prints {ok, violations, ms}. One implementation for every engine."
  (:require [clojure.data.json :as json]
            [clojure.java.shell :as sh]))

(defn violations
  "load: the session's load paths (relative to root); added: EDN texts added since; withhold: ids.
  -> a vector of violation maps (empty: admissible). INTEGRITY_GATE=off is honoured by integrity.py."
  [root load added withhold]
  (let [{:keys [exit out err]} (sh/sh (str root "/.venv/bin/python") (str root "/spikes/v3/shared/integrity.py")
                                      :in (json/write-str {:load load :added added :withhold withhold})
                                      :dir root)]
    (if (zero? exit)
      (:violations (json/read-str out :key-fn keyword))
      [{:violation "malformed-record" :members [] :message (str "integrity gate failed: " err)}])))
