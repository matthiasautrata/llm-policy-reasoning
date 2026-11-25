///
/// V3d store: one immutable value. The slice's metadata (today, functional, assets, tables, columns,
/// concepts, terms) and the rules and claims in authoring order (claims flat, linked by id).
///
/// The running session holds the value in a Ref (Main); `add` replaces it. A hypothesis derives a new
/// value (records withheld, records added) and passes it down; the main value is untouched by
/// construction (as V3b's db value and V3c's struct).
///
pub mod Store {

    use Model.{Rule, Claim, Rec, Slice, TermRec}

    /// gate: what the integrity gate needs to re-check this value's rule base (load paths, EDN texts
    /// added since, ids withheld by enclosing hypotheses); carried in the value, so a hypothesis gets its own
    pub type alias GateIn = {load = List[String], added = List[String], withheld = List[String]}

    pub type alias Store = {meta = Slice, rules = List[Rule], claims = List[Claim], keys = Map[String, List[String]], gate = GateIn}

    /// resolve_term normalisation: lowercase, non-alphanumerics to spaces, collapse.
    pub def norm(s: String): String =
        String.map(c -> if (Char.isLetterOrDigit(c)) Char.toLowerCase(c) else ' ', s) |> String.words |> String.intercalate(" ")

    pub def recId(r: Rec): String = match r {
        case Rec.RRule(x) => x#id
        case Rec.RClaim(id, _) => id
    }

    /// Rule and claim records -> (store, ids in the order given). Rules first, then claims (as V3b).
    pub def addRecords(st: Store, recs: List[Rec]): (Store, List[String]) =
        let rs = List.filterMap(r -> match r { case Rec.RRule(x) => Some(x) case _ => None }, recs);
        let cs = List.flatMap(r -> match r { case Rec.RClaim(_, xs) => xs case _ => Nil }, recs);
        ({rules = st#rules ++ rs, claims = st#claims ++ cs | st}, List.map(recId, recs))

    pub def fromSlice(s: Slice): Store =
        let keys = List.toMap(List.map((t: TermRec) -> (t#id, List.distinct(List.map(norm, t#label :: t#synonyms))), s#terms));
        let st = {meta = {recs = Nil | s}, rules = Nil, claims = Nil, keys = keys, gate = {load = Nil, added = Nil, withheld = Nil}};
        fst(addRecords(st, s#recs))

    /// Withhold record ids (each record alone, as Datahike's retractEntity), then add records.
    pub def hypothesis(st: Store, withhold: List[String], recs: List[Rec]): (Store, List[String]) =
        let w = List.toSet(withhold);
        let st1 = {rules = List.filter(r -> not Set.memberOf(r#id, w), st#rules),
                   claims = List.filter(c -> not Set.memberOf(c#id, w), st#claims) | st};
        addRecords(st1, recs)

    pub def termsMatching(st: Store, key: String): List[String] =
        List.filterMap(t -> if (List.memberOf(key, Map.getWithDefault(t#id, Nil, st#keys))) Some(t#id) else None, st#meta#terms)

    pub def claimsAbout(st: Store, asset: String): List[String] =
        let linked = List.flatMap(c -> c#dependsOn ++ c#supports, st#claims);
        List.filterMap(c -> if (c#about == asset and not List.memberOf(c#id, linked)) Some(c#id) else None, st#claims)
}
