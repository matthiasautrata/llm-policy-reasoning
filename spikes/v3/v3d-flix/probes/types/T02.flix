// T2 (V3c: KeyError) wrong key on a SQL row map. Rows are Map[String, Value]: a misspelt key type-checks
mod TypeProbe { pub def t(row: Map[String, Model.Value]): Option[Model.Value] = Map.get("ancc", row) }
