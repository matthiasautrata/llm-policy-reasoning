// T1 (V3c: BadMapError) a function's tuple result used as a record
mod TypeProbe { pub def t(st: Store.Store, recs: List[Model.Rec]): List[Model.Rule] = Store.addRecords(st, recs)#rules }
