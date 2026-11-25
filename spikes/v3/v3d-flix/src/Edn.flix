///
/// V3d EDN reader: a hand-written recursive-descent parser in Flix (no EDN library for Flix exists; the
/// Java ones (edn-java 0.7.1) would hand back java.util collections that need converting anyway).
///
/// Mapping (as V3b/V3c): keyword `:a` / `:ns/a` -> EKw("a") / EKw("ns/a"); symbol -> ESym (variables keep
/// their `?`); nil/true/false; integers (Int64), floats; strings with escapes; vector and list -> EVec;
/// map -> EMap (pairs, authoring order); set -> ESet; `#inst "2026-01-01"` -> the string. `;` comments,
/// commas, `#_` discard.
///
pub mod Edn {
    import java.lang.{Character => JChar}

    pub enum Edn with Eq, Order, ToString {
        case ENil
        case EBool(Bool)
        case EInt(Int64)
        case EFloat(Float64)
        case EStr(String)
        case EKw(String)
        case ESym(String)
        case EVec(List[Edn])
        case EMap(List[(Edn, Edn)])
        case ESet(List[Edn])
    }

    /// EDN text -> data, or an error naming the line.
    pub def read(text: String): Result[String, Edn] =
        let n = String.length(text);
        match skip(text, n, 0) {
            case Err(e) => Err(e)
            case Ok(i) => match form(text, n, i) {
                case Err(e) => Err(e)
                case Ok((x, j)) => match skip(text, n, j) {
                    case Err(e) => Err(e)
                    case Ok(k) => if (k == n) Ok(x) else err(text, k, "trailing input")
                }
            }
        }

    def err(text: String, i: Int32, msg: String): Result[String, a] =
        let line = 1 + List.count(c -> c == '\n', String.toList(String.slice(start = 0, end = Int32.min(i, String.length(text)), text)));
        let near = String.slice(start = i, end = Int32.min(i + 30, String.length(text)), text);
        Err("EDN line ${line}: ${msg} near \"${near}\"")

    def at(text: String, i: Int32): Char = String.charAt(i, text)

    def isWs(c: Char): Bool = c == ' ' or c == '\t' or c == '\n' or c == '\r' or c == ','

    def isSymStart(c: Char): Bool = Char.isLetter(c) or String.contains(substr = Char.toString(c), "*+!-_?<>=/.&%$")

    def isSymRest(c: Char): Bool = isSymStart(c) or Char.isDigit(c) or c == ':' or c == '#' or c == '\''

    /// whitespace, comments and #_ discards
    def skip(text: String, n: Int32, i: Int32): Result[String, Int32] =
        if (i >= n) Ok(i)
        else {
            let c = at(text, i);
            if (isWs(c)) skip(text, n, i + 1)
            else if (c == ';') skip(text, n, toEol(text, n, i))
            else if (c == '#' and i + 1 < n and at(text, i + 1) == '_')
                match skip(text, n, i + 2) {
                    case Err(e) => Err(e)
                    case Ok(j) => match form(text, n, j) {
                        case Err(e) => Err(e)
                        case Ok((_, k)) => skip(text, n, k)
                    }
                }
            else Ok(i)
        }

    def toEol(text: String, n: Int32, i: Int32): Int32 =
        if (i >= n or at(text, i) == '\n') i else toEol(text, n, i + 1)

    def form(text: String, n: Int32, i: Int32): Result[String, (Edn, Int32)] =
        if (i >= n) err(text, i, "unexpected end of input")
        else {
            let c = at(text, i);
            let d = if (i + 1 < n) at(text, i + 1) else ' ';
            if (Char.isDigit(c) or ((c == '-' or c == '+') and Char.isDigit(d))) number(text, n, i)
            else if (c == '"') str(text, n, i + 1, Nil)
            else if (c == ':') {
                let j = nameEnd(text, n, i + 1);
                if (j == i + 1) err(text, i, "empty keyword") else Ok((Edn.EKw(String.slice(start = i + 1, end = j, text)), j))
            }
            else if (c == '[') seq(text, n, i + 1, ']', Nil) |> Result.map(match (xs, j) -> (Edn.EVec(xs), j))
            else if (c == '(') seq(text, n, i + 1, ')', Nil) |> Result.map(match (xs, j) -> (Edn.EVec(xs), j))
            else if (c == '{') seq(text, n, i + 1, '}', Nil) |> Result.flatMap(match (xs, j) -> pairs(text, i, xs, Nil) |> Result.map(ps -> (Edn.EMap(ps), j)))
            else if (c == '#' and d == '{') seq(text, n, i + 2, '}', Nil) |> Result.map(match (xs, j) -> (Edn.ESet(xs), j))
            else if (c == '#' and String.startsWith(prefix = "#inst", String.sliceRight(start = i, text)))
                match skip(text, n, i + 5) {
                    case Err(e) => Err(e)
                    case Ok(j) => if (j < n and at(text, j) == '"') str(text, n, j + 1, Nil) else err(text, j, "#inst needs a string")
                }
            else if (isSymStart(c)) {
                let j = nameEnd(text, n, i);
                let s = String.slice(start = i, end = j, text);
                let x = match s {
                    case "nil" => Edn.ENil
                    case "true" => Edn.EBool(true)
                    case "false" => Edn.EBool(false)
                    case _ => Edn.ESym(s)
                };
                Ok((x, j))
            }
            else err(text, i, "unexpected character '${c}'")
        }

    def nameEnd(text: String, n: Int32, i: Int32): Int32 =
        if (i < n and isSymRest(at(text, i))) nameEnd(text, n, i + 1) else i

    def seq(text: String, n: Int32, i: Int32, close: Char, acc: List[Edn]): Result[String, (List[Edn], Int32)] =
        match skip(text, n, i) {
            case Err(e) => Err(e)
            case Ok(j) =>
                if (j >= n) err(text, j, "unclosed '${close}'")
                else if (at(text, j) == close) Ok((List.reverse(acc), j + 1))
                else match form(text, n, j) {
                    case Err(e) => Err(e)
                    case Ok((x, k)) => seq(text, n, k, close, x :: acc)
                }
        }

    def pairs(text: String, i: Int32, xs: List[Edn], acc: List[(Edn, Edn)]): Result[String, List[(Edn, Edn)]] = match xs {
        case Nil => Ok(List.reverse(acc))
        case k :: v :: rest => pairs(text, i, rest, (k, v) :: acc)
        case _ => err(text, i, "a map needs an even number of forms")
    }

    def digits(text: String, n: Int32, i: Int32): Int32 =
        if (i < n and Char.isDigit(at(text, i))) digits(text, n, i + 1) else i

    def number(text: String, n: Int32, i: Int32): Result[String, (Edn, Int32)] =
        let j0 = if (at(text, i) == '-' or at(text, i) == '+') i + 1 else i;
        let j1 = digits(text, n, j0);
        let (j2, frac) = if (j1 + 1 < n and at(text, j1) == '.' and Char.isDigit(at(text, j1 + 1))) (digits(text, n, j1 + 1), true) else (j1, false);
        let (j3, ex) =
            if (j2 < n and (at(text, j2) == 'e' or at(text, j2) == 'E')) {
                let k = if (j2 + 1 < n and (at(text, j2 + 1) == '-' or at(text, j2 + 1) == '+')) j2 + 2 else j2 + 1;
                let k2 = digits(text, n, k);
                if (k2 > k) (k2, true) else (j2, false)
            } else (j2, false);
        if (j3 < n and isSymRest(at(text, j3))) err(text, i, "bad number")
        else {
            let s = String.slice(start = i, end = j3, text);
            let s1 = if (String.startsWith(prefix = "+", s)) String.sliceRight(start = 1, s) else s;
            if (frac or ex)
                match Float64.fromString(s1) {
                    case Some(f) => Ok((Edn.EFloat(f), j3))
                    case None => err(text, i, "bad float")
                }
            else
                match Int64.fromString(s1) {
                    case Some(x) => Ok((Edn.EInt(x), j3))
                    case None => err(text, i, "bad integer")
                }
        }

    def str(text: String, n: Int32, i: Int32, acc: List[String]): Result[String, (Edn, Int32)] =
        if (i >= n) err(text, i, "unterminated string")
        else {
            let c = at(text, i);
            if (c == '"') Ok((Edn.EStr(String.flatten(List.reverse(acc))), i + 1))
            else if (c == '\\' and i + 1 < n) {
                let e = at(text, i + 1);
                match e {
                    case 'n' => str(text, n, i + 2, "\n" :: acc)
                    case 't' => str(text, n, i + 2, "\t" :: acc)
                    case 'r' => str(text, n, i + 2, "\r" :: acc)
                    case '"' => str(text, n, i + 2, "\"" :: acc)
                    case '\\' => str(text, n, i + 2, "\\" :: acc)
                    case 'u' if i + 5 < n =>
                        match Int32.parse(16, String.slice(start = i + 2, end = i + 6, text)) {
                            case Ok(cp) => str(text, n, i + 6, JChar.toString(cp) :: acc)
                            case Err(_) => err(text, i, "bad \\u escape")
                        }
                    case _ => err(text, i, "bad escape")
                }
            }
            else str(text, n, i + 1, Char.toString(c) :: acc)
        }
}
