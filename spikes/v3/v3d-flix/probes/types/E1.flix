// E1 (no V3c analog) an effect leak: SQL (IO) from a function declared pure
mod TypeProbe { import java.sql.{Connection => JConn}
    pub def t(c: JConn): Int32 = match Sql.runQuery(c, "SELECT 1", Nil) { case Ok(_) => 1 case _ => 0 } }
