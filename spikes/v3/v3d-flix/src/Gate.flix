///
/// The shared integrity gate (PLAN-v3-integrity §2), run as a subprocess: shared/integrity.py reads
/// {load, added, withhold} on stdin and prints {ok, violations, ms}. One implementation for every engine.
/// Paths are relative to the working directory (the repo root). The request and the answer go through
/// temp files (ProcessBuilder redirects), so no stream handling on the Flix side.
///
pub mod Gate {
    import java.lang.ProcessBuilder
    import java.io.{File => JFile}
    import java.io.FileWriter
    import java.nio.file.Files
    import java.lang.{Exception => JExn}

    use Util.Json.Json
    use Util.Json.Json.{JArray, JObject, JString}

    def strs(xs: List[String]): Json = Engine.jarr(List.map(JString, xs))

    def bad(m: String): List[Json] =
        Engine.obj(("violation", JString("malformed-record")) :: ("members", Engine.jarr(Nil)) ::
                   ("message", JString("integrity gate failed: ${m}")) :: Nil) :: Nil

    /// -> Nil (admissible) or the violation objects
    pub def violations(load: List[String], added: List[String], withhold: List[String]): List[Json] \ IO =
        let req = Util.Json.toCompactString(Engine.obj(("load", strs(load)) :: ("added", strs(added)) :: ("withhold", strs(withhold)) :: Nil));
        try {
            let fin = JFile.createTempFile("v3d-gate", ".json");
            let fout = JFile.createTempFile("v3d-gate", ".out");
            let w = new FileWriter(fin);
            w.write(req);
            w.close();
            let pb: ProcessBuilder = region rc { new ProcessBuilder(Array#{".venv/bin/python", "spikes/v3/shared/integrity.py"} @ rc) };
            discard pb.redirectInput(fin);
            discard pb.redirectOutput(fout);
            let p = pb.start();
            let code = p.waitFor();
            let out = Files.readString(fout.toPath());
            discard fin.delete();
            discard fout.delete();
            if (code != 0) bad("exit ${code}")
            else match Util.Json.parse(out) {
                case Ok(JObject(m)) => match Map.get("violations", m) {
                    case Some(JArray(v)) => Vector.toList(v)
                    case _ => bad(out)
                }
                case _ => bad(out)
            }
        } catch {
            case e: JExn => bad(e.getMessage())
        }
}
