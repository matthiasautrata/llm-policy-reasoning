# Spike v3 System A slice

Physical model, semantic layer, vocabulary, rules and Toulmin claims of the spike v3 procurement slice. Detail data is not part of the model: it stays relational and is reached through fetch(concept, filters). Rule heads, bodies and claim assertions are structured (Literal and RuleTerm classes below), so the schema validates the rule language, not just the envelope.

URI: https://example.org/llm-policy-reasoning/spike-v3/slice

Name: slice



## Classes

| Class | Description |
| --- | --- |
| [Asset](Asset.md) | Anything significant a claim can attach to that is not a table, column, conce... |
| [Claim](Claim.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |
| [CodeList](CodeList.md) | The admissible codes of an enumerated column |
| [Column](Column.md) | A column of a physical table |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Dimension](Dimension.md) | A concept whose kind is dimension |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |
| [Filter](Filter.md) | One entry of a fetch filter map (compact form `column: term`) |
| [FunctionalPredicate](FunctionalPredicate.md) | A predicate whose first key_arity arguments are a key and whose last argument... |
| [Literal](Literal.md) | A literal of a rule head or body, or a claim assertion |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[AsOf](AsOf.md) | [:as_of ?d]: the evaluation date |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Comparison](Comparison.md) | [:< a b] and friends: numbers or ISO dates |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Derived](Derived.md) | [:pred arg  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Fetch](Fetch.md) | [:fetch :concept {col term} {col ?var}]: a concept lookup; bound terms filter... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Is](Is.md) | [:is ?x [:+ a b]]: arithmetic |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Neg](Neg.md) | [:neg literal]: the complement (defeater heads, negative claims) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Not](Not.md) | [:not literal]: the literal is not defeasibly provable |
| [Output](Output.md) | One entry of a fetch output map (compact form `column: ?var`) |
| [Rule](Rule.md) | A rule envelope |
| [RuleTerm](RuleTerm.md) | An argument of a literal (named RuleTerm because Term is the vocabulary class... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Bool](Bool.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Expr](Expr.md) | [:+ a b] or [:- a b]; exactly two operands |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Int](Int.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Str](Str.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Var](Var.md) |  |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |
| [Table](Table.md) | A physical table of the detail data |
| [Taxonomy](Taxonomy.md) | A two-level grouping over a code list |
| [TaxonomyGroup](TaxonomyGroup.md) |  |
| [Term](Term.md) | A vocabulary term with a contrastive definition (X, as opposed to Y, differin... |



## Slots

| Slot | Description |
| --- | --- |
| [about](about.md) |  |
| [additivity](additivity.md) |  |
| [args](args.md) |  |
| [asserted_at](asserted_at.md) |  |
| [asserted_by](asserted_by.md) |  |
| [assertion](assertion.md) | A literal, e |
| [assets](assets.md) |  |
| [backing](backing.md) |  |
| [body](body.md) | Literals, evaluated left to right |
| [claims](claims.md) |  |
| [code_list](code_list.md) |  |
| [code_lists](code_lists.md) |  |
| [column](column.md) |  |
| [column_type](column_type.md) |  |
| [columns](columns.md) |  |
| [columns_out](columns_out.md) | Output columns of the concept's rows |
| [concept](concept.md) |  |
| [concept_name](concept_name.md) | The concept's name as rules reference it in fetch literals |
| [concepts](concepts.md) |  |
| [conservative](conservative.md) |  |
| [date](date.md) |  |
| [definition](definition.md) |  |
| [depends_on](depends_on.md) | Claim ids this claim requires |
| [derived_by](derived_by.md) |  |
| [doc](doc.md) |  |
| [expr](expr.md) |  |
| [filters](filters.md) |  |
| [functional](functional.md) |  |
| [group](group.md) |  |
| [groups](groups.md) |  |
| [head](head.md) | A literal, e |
| [id](id.md) |  |
| [key_arity](key_arity.md) |  |
| [kind](kind.md) |  |
| [label](label.md) |  |
| [layer](layer.md) |  |
| [left](left.md) |  |
| [literal](literal.md) |  |
| [members](members.md) |  |
| [name](name.md) |  |
| [op](op.md) |  |
| [order](order.md) | Asserter authority, strongest first |
| [outputs](outputs.md) |  |
| [owner](owner.md) |  |
| [params](params.md) |  |
| [pred](pred.md) |  |
| [qualifier](qualifier.md) |  |
| [recorded_at](recorded_at.md) | When the record entered the store (provenance; no rule body reads it) |
| [right](right.md) |  |
| [rule_class](rule_class.md) |  |
| [rules](rules.md) |  |
| [see](see.md) |  |
| [sql](sql.md) |  |
| [superior_to](superior_to.md) |  |
| [supports](supports.md) | Claim ids that support this claim |
| [synonyms](synonyms.md) |  |
| [tables](tables.md) |  |
| [taxonomies](taxonomies.md) |  |
| [term](term.md) |  |
| [terms](terms.md) |  |
| [today](today.md) |  |
| [type](type.md) |  |
| [unsafe_dims](unsafe_dims.md) | Dimensions a semi-additive measure must not be summed over |
| [valid_from](valid_from.md) |  |
| [valid_to](valid_to.md) |  |
| [value](value.md) |  |
| [values](values.md) |  |
| [var](var.md) |  |
| [version](version.md) |  |
| [warrant](warrant.md) |  |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [Additivity](Additivity.md) |  |
| [ArithmeticOp](ArithmeticOp.md) |  |
| [AssetKind](AssetKind.md) |  |
| [ColumnType](ColumnType.md) |  |
| [ComparisonOp](ComparisonOp.md) |  |
| [ConceptKind](ConceptKind.md) |  |
| [Modal](Modal.md) |  |
| [Owner](Owner.md) |  |
| [RuleClass](RuleClass.md) |  |
| [RuleKind](RuleKind.md) |  |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
