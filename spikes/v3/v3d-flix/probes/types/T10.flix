// T10 wrong arity to a module function
mod TypeProbe { pub def t(a: Model.Goal, b: Model.Goal): Option[Engine.Subst] = Engine.unifyG(a, b) }
