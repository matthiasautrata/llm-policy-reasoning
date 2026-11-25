// T3 (V3c: bad child spec; no supervisor in Flix) the defect hit here instead: a spawned thread touching the parent region Ref
mod TypeProbe { pub def t(st: Store.Store): Unit \ IO + Chan + NonDet = region rc { let r = Ref.fresh(rc, st); spawn { Ref.put(st, r) } @ rc } }
