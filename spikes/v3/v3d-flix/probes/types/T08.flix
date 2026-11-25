// T8 a match arm on a result shape the callee never returns (connect returns Result, not Option)
mod TypeProbe { pub def t(cfg: Sql.Cfg): Unit \ IO = match Sql.connect(cfg) { case Some(_) => () case None => () } }
