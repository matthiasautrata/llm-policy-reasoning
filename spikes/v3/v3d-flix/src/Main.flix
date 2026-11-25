//
// V3d CLI (CONTRACT.md): session script (JSON) on stdin -> {"results": [...], "load_ms": n} on stdout.
// Paths in `load` and the DuckDB file are relative to the working directory (the repo root).
// `concurrent`: each op list runs in its own thread on its own JDBC connection; results stamped with
// t_start / t_end (epoch ms). Main state: a Ref holding the Store value.
//
import java.nio.file.Files
import java.io.File
import java.lang.{System => JSys}

use Util.Json.Json
use Util.Json.Json.{JArray, JObject, JString, JNumber}

def slurp(p: String): String \ IO = Files.readString((new File(p)).toPath())

def cfgOf(j: Json, concepts: Map[String, (String, List[String])]): Sql.Cfg =
    {backend = Option.getWithDefault("duckdb", Ops.getStr("backend", j)),
     duckdb = Option.getWithDefault("", Ops.getStr("duckdb", j)),
     postgres = Option.getWithDefault("dbname=spike_v3", Ops.getStr("postgres", j)),
     limit = match Ops.get("fetch_limit", j) { case Some(JNumber(n)) => Option.getWithDefault(10000, BigDecimal.tryToInt32(n)) case _ => 10000 },
     concepts = concepts}

/// load files in order: a slice (map) replaces the store, an extension (vector) is added
def loadAll(files: List[String]): Result[String, Store.Store] \ IO =
    List.foldLeft((acc, f) -> Result.flatMap(st0 -> {
        let text = slurp(f);
        match Edn.read(text) |> Result.flatMap(Model.load) {
            case Err(e) => Err("${f}: ${e}")
            case Ok(Model.Loaded.LSlice(s)) => Ok(Some(Store.fromSlice(s)))
            case Ok(Model.Loaded.LExt(recs)) => match st0 {
                case Some(st) => Ok(Some(fst(Store.addRecords(st, recs))))
                case None => Err("${f}: an extension before the slice")
            }
        }
    }, acc), Ok(None), files) |> Result.flatMap(o -> match o { case Some(s) => Ok(s) case None => Err("no slice loaded") })

def conceptsOf(st: Store.Store): Map[String, (String, List[String])] =
    List.filterMap(c -> match c#source {
        case Model.Source.Sql(sql) => Some((c#name, (sql, c#params)))
        case _ => None
    }, st#meta#concepts) |> List.toMap

def strs(j: List[Json]): List[String] = List.filterMap(x -> match x { case JString(s) => Some(s) case _ => None }, j)

def die(msg: String): Unit \ IO = {
    JSys.err.println(msg);
    JSys.exit(1)
}

def main(): Unit \ IO + Chan + NonDet = region rc {
    let script = match Util.Json.parse(slurp("/dev/stdin")) {
        case Ok(j) => j
        case Err(e) => { die("bad script: ${e}"); Util.Json.Json.JNull }
    };
    let cfgJ = Option.getWithDefault(Util.Json.Json.JNull, Ops.get("config", script));
    let t0 = JSys.nanoTime();
    match loadAll(strs(Ops.getList("load", script))) {
        case Err(e) => die(e)
        case Ok(st) =>
            let cfg = cfgOf(cfgJ, conceptsOf(st));
            match Sql.connect(cfg) {
                case Err(e) => die(e)
                case Ok(conn) =>
                    let main = Ref.fresh(rc, st);
                    let env = {cfg = cfg, conn = conn};
                    let loadMs = Int64.toFloat64(JSys.nanoTime() - t0) / 1000000.0;
                    let results = List.map(op -> Ops.runOp(env, main, op), Ops.getList("ops", script));
                    let conc = match Ops.get("concurrent", script) {
                        case Some(JArray(lists)) =>
                            // spawn allows IO, NonDet, Chan only: a thread cannot touch this region's Ref, so each
                            // thread gets its own Ref holding the store value as it was when the threads started
                            let snap = Ref.get(main);
                            let rxs = Vector.toList(lists) |> List.map(l -> {
                                let (tx, rx): (Sender[List[Json]], Receiver[List[Json]]) = Channel.buffered(1);
                                spawn {
                                    let out: List[Json] = region tr {
                                        let tmain = Ref.fresh(tr, snap);
                                        match Sql.connect(cfg) {
                                            case Err(e) => Util.Json.Json.JString(e) :: Nil
                                            case Ok(c2) =>
                                                let env2 = {cfg = cfg, conn = c2};
                                                List.map(op -> {
                                                    let a = JSys.currentTimeMillis();
                                                    let r = Ops.runOp(env2, tmain, op);
                                                    Ops.merge(r, ("t_start", Engine.jint(a)) :: ("t_end", Engine.jint(JSys.currentTimeMillis())) :: Nil)
                                                }, match l { case JArray(v) => Vector.toList(v) case _ => Nil })
                                        }
                                    };
                                    Channel.send(out, tx)
                                } @ rc;
                                rx
                            });
                            Some(Engine.jarr(List.map(rx -> Engine.jarr(Channel.recv(rx)), rxs)))
                        case _ => None
                    };
                    let after = match Ops.get("after", script) {
                        case Some(JArray(v)) => Some(Engine.jarr(List.map(op -> Ops.runOp(env, main, op), Vector.toList(v))))
                        case _ => None
                    };
                    let out = Engine.obj(("results", Engine.jarr(results)) :: ("load_ms", Ops.jfloat(loadMs)) ::
                        (match conc { case Some(c) => ("concurrent", c) :: Nil case None => Nil }) ++
                        (match after { case Some(a) => ("after", a) :: Nil case None => Nil }));
                    JSys.out.print(Util.Json.toCompactString(out));
                    JSys.out.flush()
            }
    }
}
