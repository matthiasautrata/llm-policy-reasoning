def main(): Unit \ IO = {
    let p = #{
        Q("a").
        P(x) :- Q(x), not R(x).
        R(x) :- Q(x), not P(x).
    };
    let r: Vector[String] = query p select x from P(x);
    println(r)
}
