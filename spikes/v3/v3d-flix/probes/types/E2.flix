// E2 (no V3c analog) a non-exhaustive match on a literal form
mod TypeProbe { pub def t(l: Model.Lit): String = match l { case Model.Lit.Derived(_) => "d" case Model.Lit.Fetch(_, _, _) => "f" } }
