// V3d probes. Run from the repo root: java -jar spikes/v3/v3d-flix/probes/artifact/probes.jar <probe>
// probes (-Dprobe=...): typed (closures + provenance), reified, translate (runtime-built Fixpoint3 programs), negatives, lattice, all
import java.lang.{System => JSys}
import java.util.Properties
import org.duckdb.DuckDBDriver
import java.nio.file.Files
import java.io.File

def main(): Unit \ IO = {
    let which = Option.getWithDefault("all", Option.map(x -> x, Some(JSys.getProperty("probe", "all"))));
    let p = new Properties();
    discard p.setProperty("duckdb.read_only", "true");
    let conn = (new DuckDBDriver()).connect("jdbc:duckdb:spikes/v3/shared/slice.duckdb", p);
    if (which == "typed" or which == "all") { Typed.closure(conn); Typed.provenance(conn) } else ();
    if (which == "reified" or which == "all") Typed.reified(conn) else ();
    if (which == "translate" or which == "all") match Edn.read(Files.readString((new File("spikes/v3/shared/slice.edn")).toPath())) |> Result.flatMap(Model.load) {
        case Ok(Model.Loaded.LSlice(s)) => Translate.probe(conn, Store.fromSlice(s))
        case _ => println("slice did not load")
    } else ();
    if (which == "negatives" or which == "all") {
        // the 15 negatives (Model.negatives): each mutates the slice EDN; pass iff the unmodified slice loads and all 15 are rejected
        match Edn.read(Files.readString((new File("spikes/v3/shared/slice.edn")).toPath())) {
            case Err(e) => println("slice EDN did not parse: ${e}")
            case Ok(e) =>
                println("negatives: unmodified slice " + (match Model.load(e) { case Ok(_) => "loads" case Err(m) => "REJECTED ${m}" }));
                let n = List.foldLeft((acc, neg) -> {
                    let (name, f) = neg;
                    match Model.load(f(e)) {
                        case Ok(_) => { println("  NOT REJECTED  ${name}"); acc }
                        case Err(m) => { println("  rejected  ${name}: ${m}"); acc + 1 }
                    }
                }, 0, Model.negatives());
                println("negatives rejected: ${n}/${List.length(Model.negatives())}")
        }
    } else ();
    if (which == "lattice" or which == "all") { println("lattice:"); Lattice.probe() } else ();
    ()
}
