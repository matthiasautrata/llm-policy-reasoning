///
/// V3d model: the slice and its runtime extensions as Flix ADTs, and the conversion EDN -> ADT that is
/// also the validator ("parse, don't validate"). A value of these types is valid by construction where
/// the type can say so (owners, kinds, classes, roles, arities, ?variables, arithmetic ops, a concept
/// source, the shape of [:neg l] and of :fetch); what types cannot say (ISO dates, id formats, closed
/// maps, positive integers) is checked explicitly in the conversion.
///
/// The conversion returns the first error with its path (V3c listed all of them).
///
pub mod Model {

    use Edn.Edn
    use Edn.Edn.{ENil, EBool, EInt, EFloat, EStr, EKw, ESym, EVec, EMap, ESet}

    // ------------------------------------------------------------------ the rule language

    pub enum Value with Eq, Order, ToString {
        case VStr(String)
        case VInt(Int64)
        case VBool(Bool)
        case VNull
    }

    pub enum ArOp with Eq, Order, ToString { case Plus, case Minus }

    pub enum Term with Eq, Order, ToString {
        case Var(String)
        case Val(Value)
        case Ar(ArOp, Term, Term)
    }

    /// A derived literal: a head, a claim's assertion, a body literal that is proved.
    pub enum Goal with Eq, Order, ToString {
        case Pos(String, List[Term])
        case Neg(Goal)
    }

    pub enum CmpOp with Eq, Order, ToString { case Lt, case Le, case Gt, case Ge, case Equ }

    pub enum Lit with Eq, Order, ToString {
        case Derived(Goal)
        /// concept, filters {col term}, outputs {col ?var} (the ?var's name)
        case Fetch(String, List[(String, Term)], List[(String, String)])
        case Not(Goal)
        case Cmp(CmpOp, Term, Term)
        /// [:is ?x [op a b]]
        case Is(String, ArOp, Term, Term)
        case AsOf(Term)
    }

    pub enum Kind with Eq, Order, ToString { case Strict, case Defeasible, case Defeater, case Incompatible }

    pub enum Owner with Eq, Order, ToString { case Finance, case Hr, case Procurement, case Compliance, case Risk, case Controller }

    pub enum Class with Eq, Order, ToString {
        case Definition, case MaterialInference, case Exception, case Entitlement, case Superiority, case Incompatibility
    }

    pub enum Role with Eq, Order, ToString { case Required, case Supporting }

    /// A rule is either a logic rule or a superiority order between asserters (scoped to a predicate).
    pub enum Form with Eq, ToString {
        case Logic(Kind, Goal, List[Lit])
        case Order(String, List[Owner])
    }

    pub type alias Rule = {id = String, owner = Owner, cls = Class, doc = String, superiorTo = List[String], form = Form}

    /// A claim, sub-claims flattened in authoring order (parent first); `about` is the top claim's.
    pub type alias Claim = {id = String, about = String, parent = Option[String], role = Option[Role], assertion = Goal,
                            assertedBy = Owner, assertedAt = String, validFrom = String, validTo = Option[String],
                            backing = Option[String], modal = Option[String], warrant = Option[String]}

    pub enum Source with Eq, ToString { case Sql(String), case DerivedBy(String) }

    pub type alias Concept = {id = String, name = String, kind = String, tables = List[String], doc = String,
                              columns = List[String], params = List[String], source = Source}

    pub type alias TermRec = {id = String, label = String, synonyms = List[String], owner = Owner, definition = String,
                              concept = Option[String], see = List[String]}

    pub type alias Asset = {id = String, kind = String, doc = String}

    pub type alias Table = {id = String, name = String, doc = String}

    pub type alias Column = {id = String, name = String, kind = String, doc = String}

    /// A record of an extension (or of the slice's :rules / :claims): a rule, or a top claim with its sub-claims.
    pub enum Rec {
        case RRule(Rule)
        case RClaim(String, List[Claim])
    }

    pub type alias Slice = {today = String, assets = List[Asset], tables = List[Table], columns = List[Column],
                            concepts = List[Concept], terms = List[TermRec], functional = Map[String, Int32],
                            recs = List[Rec]}

    pub enum Loaded {
        case LSlice(Slice)
        case LExt(List[Rec])
    }

    pub def predOf(g: Goal): String = match g {
        case Goal.Pos(p, _) => p
        case Goal.Neg(h) => predOf(h)
    }

    // ------------------------------------------------------------------ conversion helpers

    type alias R[a] = Result[String, a]

    def fail(path: String, msg: String): R[a] = Err("${path}: ${msg}")

    def kw(path: String, e: Edn): R[String] = match e {
        case EKw(k) => Ok(k)
        case _ => fail(path, "a keyword")
    }

    def str(path: String, e: Edn): R[String] = match e {
        case EStr(s) => Ok(s)
        case _ => fail(path, "a string")
    }

    def re(rx: String, path: String, e: Edn): R[String] = match e {
        case EStr(s) if String.isMatch(regex = rx, s) => Ok(s)
        case _ => fail(path, "should match ${rx}")
    }

    def date(path: String, e: Edn): R[String] = re("\\d{4}-\\d{2}-\\d{2}", path, e)

    def vec(path: String, f: (String, Edn) -> R[a], e: Edn): R[List[a]] = match e {
        case EVec(xs) => Result.traverse(match (i, x) -> f("${path}[${i}]", x), List.zipWithIndex(xs) |> List.map(match (i, x) -> (i, x)))
        case _ => fail(path, "a vector")
    }

    def oneOf(path: String, xs: List[(String, a)], e: Edn): R[a] = match e {
        case EKw(k) => match List.find(match (n, _) -> n == k, xs) {
            case Some((_, v)) => Ok(v)
            case None => fail(path, "should be one of ${String.intercalate(", ", List.map(fst, xs))}")
        }
        case _ => fail(path, "a keyword")
    }

    def owner(path: String, e: Edn): R[Owner] =
        oneOf(path, ("finance", Owner.Finance) :: ("hr", Owner.Hr) :: ("procurement", Owner.Procurement) ::
                    ("compliance", Owner.Compliance) :: ("risk", Owner.Risk) :: ("controller", Owner.Controller) :: Nil, e)

    def cls(path: String, e: Edn): R[Class] =
        oneOf(path, ("definition", Class.Definition) :: ("material_inference", Class.MaterialInference) ::
                    ("exception", Class.Exception) :: ("entitlement", Class.Entitlement) ::
                    ("superiority", Class.Superiority) :: ("incompatibility", Class.Incompatibility) :: Nil, e)

    def kind(path: String, e: Edn): R[Kind] =
        oneOf(path, ("strict", Kind.Strict) :: ("defeasible", Kind.Defeasible) :: ("defeater", Kind.Defeater) ::
                    ("incompatible", Kind.Incompatible) :: Nil, e)

    def role(path: String, e: Edn): R[Role] =
        oneOf(path, ("required", Role.Required) :: ("supporting", Role.Supporting) :: Nil, e)

    def enumKw(xs: List[String], path: String, e: Edn): R[String] = oneOf(path, List.map(x -> (x, x), xs), e)

    /// A closed map: every key a keyword among `allowed`; -> the pairs by key name.
    def closed(path: String, allowed: List[String], e: Edn): R[Map[String, Edn]] = match e {
        case EMap(ps) => List.foldLeft((acc, p) -> Result.flatMap(m -> match p {
                case (EKw(k), v) if List.memberOf(k, allowed) => Ok(Map.insert(k, v, m))
                case (EKw(k), _) => fail("${path}.${k}", "disallowed key")
                case (k, _) => fail(path, "keyword keys, not ${k}")
            }, acc), Ok(Map.empty()), ps)
        case _ => fail(path, "a map")
    }

    /// An open map: keyword keys; other keys are ignored.
    def open(path: String, e: Edn): R[Map[String, Edn]] = match e {
        case EMap(ps) => Ok(List.foldLeft((m, p) -> match p {
                case (EKw(k), v) => Map.insert(k, v, m)
                case _ => m
            }, Map.empty(), ps))
        case _ => fail(path, "a map")
    }

    def req(path: String, k: String, f: (String, Edn) -> R[a], m: Map[String, Edn]): R[a] = match Map.get(k, m) {
        case Some(v) => f("${path}.${k}", v)
        case None => fail("${path}.${k}", "missing required key")
    }

    /// optional key; nil counts as absent
    def opt(path: String, k: String, f: (String, Edn) -> R[a], m: Map[String, Edn]): R[Option[a]] = match Map.get(k, m) {
        case Some(ENil) => Ok(None)
        case Some(v) => f("${path}.${k}", v) |> Result.map(Some)
        case None => Ok(None)
    }

    def optList(path: String, k: String, f: (String, Edn) -> R[a], m: Map[String, Edn]): R[List[a]] =
        opt(path, k, (p, e) -> vec(p, f, e), m) |> Result.map(Option.getWithDefault(Nil))

    // ------------------------------------------------------------------ terms and literals

    pub def isVarName(s: String): Bool = String.startsWith(prefix = "?", s) and String.length(s) > 1

    def term(path: String, e: Edn): R[Term] = match e {
        case ESym(s) if isVarName(s) => Ok(Term.Var(s))
        case EStr(s) => Ok(Term.Val(Value.VStr(s)))
        case EInt(i) => Ok(Term.Val(Value.VInt(i)))
        case EBool(b) => Ok(Term.Val(Value.VBool(b)))
        case EVec(_) => expr(path, e) |> Result.map(match (op, a, b) -> Term.Ar(op, a, b))
        case _ => fail(path, "a term: ?variable, string, integer, boolean or [:+|:- a b]")
    }

    def expr(path: String, e: Edn): R[(ArOp, Term, Term)] = match e {
        case EVec(EKw(o) :: a :: b :: Nil) if o == "+" or o == "-" =>
            forM (x <- term("${path}[1]", a); y <- term("${path}[2]", b))
                yield (if (o == "+") ArOp.Plus else ArOp.Minus, x, y)
        case _ => fail(path, "an expression [:+|:- a b]")
    }

    def var(path: String, e: Edn): R[String] = match e {
        case ESym(s) if isVarName(s) => Ok(s)
        case _ => fail(path, "a ?variable")
    }

    def reserved(): List[String] = "fetch" :: "not" :: "neg" :: "is" :: "as_of" :: "<" :: "<=" :: ">" :: ">=" :: "=" :: Nil

    def terms(path: String, i: Int32, xs: List[Edn]): R[List[Term]] =
        Result.traverse(match (j, x) -> term("${path}[${i + j}]", x), List.zipWithIndex(xs))

    /// a goal: [:pred term ...] or [:neg goal]
    pub def goal(path: String, e: Edn): R[Goal] = match e {
        case EVec(EKw("neg") :: l :: Nil) => match l {
            case EVec(_) => goal("${path}[1]", l) |> Result.map(Goal.Neg)
            case _ => fail("${path}[1]", "a literal (vector)")
        }
        case EVec(EKw(p) :: args) if not List.memberOf(p, reserved()) => terms(path, 1, args) |> Result.map(ts -> Goal.Pos(p, ts))
        case EVec(EKw(p) :: _) => fail(path, ":${p}: wrong arity or shape")
        case _ => fail(path, "a literal [:pred arg ...]")
    }

    def cmpOp(o: String): Option[CmpOp] = match o {
        case "<" => Some(CmpOp.Lt)
        case "<=" => Some(CmpOp.Le)
        case ">" => Some(CmpOp.Gt)
        case ">=" => Some(CmpOp.Ge)
        case "=" => Some(CmpOp.Equ)
        case _ => None
    }

    def pairsOf(path: String, f: (String, Edn) -> R[a], e: Edn, what: String): R[List[(String, a)]] = match e {
        case EMap(ps) => Result.traverse(match (k, v) -> match k {
                case EKw(n) => f("${path}.${n}", v) |> Result.map(x -> (n, x))
                case _ => fail(path, "keyword keys")
            }, ps)
        case _ => fail(path, "${what}: a map")
    }

    def lit(path: String, e: Edn): R[Lit] = match e {
        case EVec(EKw("fetch") :: c :: f :: o :: Nil) =>
            forM (cn <- kw("${path}[1]", c);
                  fs <- pairsOf("${path}[2]", term, f, "filters");
                  os <- pairsOf("${path}[3]", var, o, "outputs"))
                yield Lit.Fetch(cn, fs, os)
        case EVec(EKw("not") :: l :: Nil) => match l {
            case EVec(_) => goal("${path}[1]", l) |> Result.map(Lit.Not)
            case _ => fail("${path}[1]", "a literal (vector)")
        }
        case EVec(EKw(o) :: a :: b :: Nil) if Option.nonEmpty(cmpOp(o)) =>
            forM (x <- term("${path}[1]", a); y <- term("${path}[2]", b))
                yield Lit.Cmp(Option.getWithDefault(CmpOp.Equ, cmpOp(o)), x, y)
        case EVec(EKw("is") :: x :: ex :: Nil) =>
            forM (v <- var("${path}[1]", x); (op, a, b) <- expr("${path}[2]", ex)) yield Lit.Is(v, op, a, b)
        case EVec(EKw("as_of") :: x :: Nil) => term("${path}[1]", x) |> Result.map(Lit.AsOf)
        case _ => goal(path, e) |> Result.map(Lit.Derived)
    }

    // ------------------------------------------------------------------ records

    def rule(path: String, e: Edn): R[Rule] = {
        let isSup = match open(path, e) {
            case Ok(m) => Map.get("kind", m) == Some(EKw("superiority"))
            case Err(_) => false
        };
        if (isSup)
            forM (m <- closed(path, "id" :: "kind" :: "owner" :: "doc" :: "class" :: "pred" :: "order" :: "superior-to" :: Nil, e);
                  id <- req(path, "id", kw, m); o <- req(path, "owner", owner, m); d <- req(path, "doc", str, m);
                  c <- req(path, "class", cls, m); p <- req(path, "pred", kw, m);
                  ord <- req(path, "order", (q, x) -> vec(q, owner, x), m);
                  sup <- optList(path, "superior-to", kw, m))
                yield {id = id, owner = o, cls = c, doc = d, superiorTo = sup, form = Form.Order(p, ord)}
        else
            forM (m <- closed(path, "id" :: "kind" :: "owner" :: "doc" :: "class" :: "head" :: "body" :: "superior-to" :: Nil, e);
                  id <- req(path, "id", kw, m); o <- req(path, "owner", owner, m); d <- req(path, "doc", str, m);
                  c <- req(path, "class", cls, m); k <- req(path, "kind", kind, m);
                  h <- req(path, "head", goal, m);
                  b <- req(path, "body", (q, x) -> vec(q, lit, x), m);
                  sup <- optList(path, "superior-to", kw, m))
                yield {id = id, owner = o, cls = c, doc = d, superiorTo = sup, form = Form.Logic(k, h, b)}
    }

    def claimCore(): List[String] =
        "id" :: "assertion" :: "asserted_by" :: "asserted_at" :: "valid_from" :: "valid_to" :: "backing" :: "qualifier" :: "warrant" :: Nil

    /// a claim (top: about, subclaims; sub: role) -> itself and its sub-claims, flattened
    def claim(path: String, about0: Option[String], parent: Option[String], e: Edn): R[List[Claim]] = {
        let keys = match parent {
            case None => "about" :: "subclaims" :: claimCore()
            case Some(_) => "role" :: claimCore()
        };
        forM (m <- closed(path, keys, e);
              id <- req(path, "id", kw, m);
              about <- (match about0 {
                  case Some(a) => Ok(a)
                  case None => req(path, "about", (q, x) -> re("[a-z]+:[A-Za-z0-9_/]+", q, x), m)
              });
              rl <- (match parent {
                  case Some(_) => req(path, "role", role, m) |> Result.map(Some)
                  case None => Ok(None)
              });
              a <- req(path, "assertion", goal, m);
              by <- req(path, "asserted_by", owner, m);
              at <- req(path, "asserted_at", date, m);
              vf <- req(path, "valid_from", date, m);
              vt <- opt(path, "valid_to", date, m);
              bk <- opt(path, "backing", str, m);
              q <- opt(path, "qualifier", (p, x) -> match x {
                  case EStr("certainly") => Ok("certainly")
                  case EStr("presumably") => Ok("presumably")
                  case _ => fail(p, "should be one of [\"certainly\", \"presumably\"]")
              }, m);
              w <- opt(path, "warrant", kw, m);
              subs <- optList(path, "subclaims", (p, x) -> claim(p, Some(about), Some(id), x), m))
            yield {id = id, about = about, parent = parent, role = rl, assertion = a, assertedBy = by, assertedAt = at,
                   validFrom = vf, validTo = vt, backing = bk, modal = q, warrant = w} :: List.flatten(subs)
    }

    def record(path: String, e: Edn): R[Rec] = match open(path, e) {
        case Ok(m) if Map.memberOf("kind", m) => rule(path, e) |> Result.map(Rec.RRule)
        case Ok(m) if Map.memberOf("assertion", m) =>
            claim(path, None, None, e) |> Result.map(cs -> Rec.RClaim(List.head(cs) |> Option.map(c -> c#id) |> Option.getWithDefault(""), cs))
        case _ => fail(path, "a rule or claim record")
    }

    // ------------------------------------------------------------------ the slice

    def column(path: String, e: Edn): R[Column] =
        forM (m <- closed(path, "id" :: "name" :: "type" :: "doc" :: Nil, e);
              id <- req(path, "id", (q, x) -> re("col:[a-z_]+/[a-z_]+", q, x), m);
              n <- req(path, "name", str, m);
              t <- req(path, "type", (q, x) -> enumKw("id" :: "int" :: "enum" :: "bool" :: "date" :: Nil, q, x), m);
              d <- req(path, "doc", str, m))
            yield {id = id, name = n, kind = t, doc = d}

    def table(path: String, e: Edn): R[(Table, List[Column])] =
        forM (m <- closed(path, "id" :: "name" :: "doc" :: "columns" :: Nil, e);
              id <- req(path, "id", (q, x) -> re("table:[a-z_]+", q, x), m);
              n <- req(path, "name", str, m);
              d <- req(path, "doc", str, m);
              cs <- req(path, "columns", (q, x) -> vec(q, column, x), m))
            yield ({id = id, name = n, doc = d}, cs)

    def concept(path: String, e: Edn): R[Concept] =
        forM (m <- closed(path, "id" :: "name" :: "kind" :: "tables" :: "doc" :: "columns" :: "params" :: "sql" :: "derived-by" :: Nil, e);
              id <- req(path, "id", (q, x) -> re("(measure|dim|entity|hier):[a-z_]+", q, x), m);
              n <- req(path, "name", kw, m);
              k <- req(path, "kind", (q, x) -> enumKw("entity" :: "dimension" :: "hierarchy" :: "measure" :: Nil, q, x), m);
              ts <- req(path, "tables", (q, x) -> vec(q, (q2, y) -> re("table:.*", q2, y), x), m);
              d <- req(path, "doc", str, m);
              cols <- optList(path, "columns", kw, m);
              ps <- optList(path, "params", kw, m);
              sql <- opt(path, "sql", str, m);
              db <- opt(path, "derived-by", kw, m);
              src <- (match (sql, db) {
                  case (Some(s), _) => Ok(Source.Sql(s))
                  case (None, Some(r)) => Ok(Source.DerivedBy(r))
                  case (None, None) => fail(path, "a concept has :sql or :derived-by")
              }))
            yield {id = id, name = n, kind = k, tables = ts, doc = d, columns = cols, params = ps, source = src}

    def termRec(path: String, e: Edn): R[TermRec] =
        forM (m <- closed(path, "id" :: "label" :: "synonyms" :: "owner" :: "definition" :: "concept" :: "see" :: Nil, e);
              id <- req(path, "id", (q, x) -> re("term:[a-z_]+", q, x), m);
              l <- req(path, "label", str, m);
              syn <- req(path, "synonyms", (q, x) -> vec(q, str, x), m);
              o <- req(path, "owner", owner, m);
              d <- req(path, "definition", str, m);
              c <- opt(path, "concept", (q, x) -> re("(measure|dim|entity|hier):.*", q, x), m);
              see <- optList(path, "see", (q, x) -> re("term:.*", q, x), m))
            yield {id = id, label = l, synonyms = syn, owner = o, definition = d, concept = c, see = see}

    def asset(path: String, e: Edn): R[Asset] =
        forM (m <- closed(path, "id" :: "kind" :: "doc" :: Nil, e);
              id <- req(path, "id", str, m);
              k <- req(path, "kind", (q, x) -> enumKw("vendor" :: "employee" :: Nil, q, x), m);
              d <- req(path, "doc", str, m))
            yield {id = id, kind = k, doc = d}

    def codeList(path: String, e: Edn): R[Unit] =
        forM (m <- open(path, e);
              _ <- req(path, "id", (q, x) -> re("codes:.*", q, x), m);
              _ <- req(path, "values", (q, x) -> vec(q, str, x), m))
            yield ()

    def taxonomy(path: String, e: Edn): R[Unit] =
        forM (m <- open(path, e);
              _ <- req(path, "id", str, m);
              _ <- req(path, "code-list", str, m);
              _ <- req(path, "tree", (q, x) -> match x {
                  case EMap(ps) => Result.traverse(match (k, v) -> forM (_ <- str(q, k); _ <- vec(q, str, v)) yield (), ps) |> Result.map(_ -> ())
                  case _ => fail(q, "a map")
              }, m))
            yield ()

    def functional(path: String, e: Edn): R[Map[String, Int32]] =
        pairsOf(path, (q, x) -> match x {
            case EInt(n) if n > 0i64 => Ok(Int64.clampToInt32(min = 1, max = 1000, n))
            case _ => fail(q, "a positive integer")
        }, e, "functional") |> Result.map(List.toMap)

    def slice(e: Edn): R[Slice] =
        let path = "slice";
        forM (m <- closed(path, "slice/version" :: "today" :: "assets" :: "tables" :: "concepts" :: "terms" :: "code-lists" ::
                                "taxonomies" :: "functional" :: "rules" :: "claims" :: Nil, e);
              _ <- req(path, "slice/version", (q, x) -> match x { case EInt(_) => Ok(()) case _ => fail(q, "an integer") }, m);
              today <- req(path, "today", date, m);
              assets <- req(path, "assets", (q, x) -> vec(q, asset, x), m);
              tcs <- req(path, "tables", (q, x) -> vec(q, table, x), m);
              concepts <- req(path, "concepts", (q, x) -> vec(q, concept, x), m);
              terms <- req(path, "terms", (q, x) -> vec(q, termRec, x), m);
              _ <- req(path, "code-lists", (q, x) -> vec(q, codeList, x), m);
              _ <- req(path, "taxonomies", (q, x) -> vec(q, taxonomy, x), m);
              fun <- req(path, "functional", functional, m);
              rules <- req(path, "rules", (q, x) -> vec(q, rule, x), m);
              claims <- req(path, "claims", (q, x) -> vec(q, (p, y) -> claim(p, None, None, y), x), m))
            yield {today = today, assets = assets, tables = List.map(fst, tcs), columns = List.flatMap(snd, tcs),
                   concepts = concepts, terms = terms, functional = fun,
                   recs = List.map(Rec.RRule, rules) ++ List.map(cs -> Rec.RClaim(List.head(cs) |> Option.map(c -> c#id) |> Option.getWithDefault(""), cs), claims)}

    /// A map is a slice; a vector is an extension.
    pub def load(e: Edn): R[Loaded] = match e {
        case EMap(_) => slice(e) |> Result.map(Loaded.LSlice)
        case EVec(_) => vec("ext", record, e) |> Result.map(Loaded.LExt)
        case _ => Err("a slice (map) or an extension (vector)")
    }

    pub def records(e: Edn): R[List[Rec]] = vec("records", record, e)

    // ------------------------------------------------------------------ negative tests (the same 12 as V3a-V3c)

    enum Key { case I(Int32), case K(String) }

    /// update the EDN at a path of vector indices and map keys
    def upd(path: List[Key], f: Edn -> Edn, e: Edn): Edn = match (path, e) {
        case (Nil, _) => f(e)
        case (Key.I(i) :: rest, EVec(xs)) => EVec(List.mapWithIndex((j, x) -> if (j == i) upd(rest, f, x) else x, xs))
        case (Key.K(k) :: rest, EMap(ps)) => EMap(List.map(match (pk, v) -> if (pk == EKw(k)) (pk, upd(rest, f, v)) else (pk, v), ps))
        case _ => e
    }

    def setNth(i: Int32, v: Edn, e: Edn): Edn = match e {
        case EVec(xs) => EVec(List.mapWithIndex((j, x) -> if (j == i) v else x, xs))
        case _ => e
    }

    def append(v: Edn, e: Edn): Edn = match e {
        case EVec(xs) => EVec(xs ++ (v :: Nil))
        case _ => e
    }

    def dropKeys(ks: List[String], e: Edn): Edn = match e {
        case EMap(ps) => EMap(List.filter(match (k, _) -> match k { case EKw(n) => not List.memberOf(n, ks) case _ => true }, ps))
        case _ => e
    }

    def putKey(k: String, v: Edn, e: Edn): Edn = match e {
        case EMap(ps) => EMap(ps ++ ((EKw(k), v) :: Nil))
        case _ => e
    }

    def v(s: String): Edn = ESym(s)

    pub def negatives(): List[(String, Edn -> Edn)] =
        let rule0 = Key.K("rules") :: Key.I(0) :: Nil;
        let rule1 = Key.K("rules") :: Key.I(1) :: Nil;
        ("concept with neither :sql nor :derived-by", upd(Key.K("concepts") :: Key.I(0) :: Nil, dropKeys("sql" :: "derived-by" :: Nil))) ::
        ("unknown owner on a rule", upd(rule0 ++ (Key.K("owner") :: Nil), _ -> EKw("marketing"))) ::
        ("rule variable without ?", upd(rule0 ++ (Key.K("head") :: Nil), setNth(1, ESym("cc")))) ::
        ("fetch filters not a map", upd(rule0 ++ (Key.K("body") :: Key.I(0) :: Nil), setNth(2, EVec(EStr("cc") :: v("?c") :: Nil)))) ::
        ("unknown arithmetic op in :is", upd(rule1 ++ (Key.K("body") :: Nil), append(EVec(EKw("is") :: v("?x") :: EVec(EKw("*") :: EInt(2i64) :: EInt(3i64) :: Nil) :: Nil)))) ::
        ("comparison with three arguments", upd(rule1 ++ (Key.K("body") :: Nil), append(EVec(EKw("<") :: v("?x") :: EInt(1i64) :: EInt(2i64) :: Nil)))) ::
        ("bad date in a claim", upd(Key.K("claims") :: Key.I(0) :: Key.K("asserted_at") :: Nil, _ -> EStr("2026-3-1"))) ::
        ("unknown key on a claim (closed map)", upd(Key.K("claims") :: Key.I(0) :: Nil, putKey("confidence", EFloat(0.9)))) ::
        ("sub-claim role not required/supporting", upd(Key.K("claims") :: Key.I(0) :: Key.K("subclaims") :: Key.I(0) :: Key.K("role") :: Nil, _ -> EKw("optional"))) ::
        ("superiority order with unknown owner", upd(Key.K("rules") :: Nil, append(EMap(
            (EKw("id"), EKw("R999")) :: (EKw("kind"), EKw("superiority")) :: (EKw("owner"), EKw("controller")) ::
            (EKw("class"), EKw("superiority")) :: (EKw("doc"), EStr("x")) :: (EKw("pred"), EKw("p")) ::
            (EKw("order"), EVec(EKw("hr") :: EKw("sales") :: Nil)) :: Nil)))) ::
        ("rule kind unknown", upd(rule0 ++ (Key.K("kind") :: Nil), _ -> EKw("presumption"))) ::
        ("negated literal wrapping a non-literal", upd(rule0 ++ (Key.K("head") :: Nil), _ -> EVec(EKw("neg") :: EStr("x") :: Nil))) :: Nil
}
