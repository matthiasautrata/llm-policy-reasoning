# Spike v3 System A slice

Physical model, semantic layer, vocabulary, rules and Toulmin claims of the spike v3 procurement slice. Detail data is not part of the model: it stays relational and is reached through fetch(concept, filters). Rule heads and bodies are EDN strings (the rule language is EDN data; LinkML holds the envelope).

URI: https://example.org/llm-policy-reasoning/spike-v3/slice

Name: slice



## Classes

| Class | Description |
| --- | --- |
| [Asset](Asset.md) | Anything significant a claim can attach to that is not a table, column, conce... |
| [ClaimCore](ClaimCore.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Claim](Claim.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[SubClaim](SubClaim.md) | One level of nesting |
| [CodeList](CodeList.md) | The admissible codes of an enumerated column |
| [Column](Column.md) | A column of a physical table |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Dimension](Dimension.md) | A concept whose kind is dimension |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |
| [FunctionalPredicate](FunctionalPredicate.md) | A predicate whose first key_arity arguments are a key and whose last argument... |
| [Rule](Rule.md) | A rule envelope |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |
| [Table](Table.md) | A physical table of the detail data |
| [Taxonomy](Taxonomy.md) | A two-level grouping over a code list |
| [TaxonomyGroup](TaxonomyGroup.md) |  |
| [Term](Term.md) | A vocabulary term with a contrastive definition (X, as opposed to Y, differin... |



## Slots

| Slot | Description |
| --- | --- |
| [about](about.md) |  |
| [asserted_at](asserted_at.md) |  |
| [asserted_by](asserted_by.md) |  |
| [assertion](assertion.md) | EDN literal, e |
| [assets](assets.md) |  |
| [backing](backing.md) |  |
| [body](body.md) | EDN vector of literals (see the slice |
| [claims](claims.md) |  |
| [code_list](code_list.md) |  |
| [code_lists](code_lists.md) |  |
| [column_type](column_type.md) |  |
| [columns](columns.md) |  |
| [columns_out](columns_out.md) | Output columns of the concept's rows |
| [concept](concept.md) |  |
| [concept_name](concept_name.md) | The concept's name as rules reference it in fetch literals |
| [concepts](concepts.md) |  |
| [conservative](conservative.md) |  |
| [definition](definition.md) |  |
| [derived_by](derived_by.md) |  |
| [doc](doc.md) |  |
| [functional](functional.md) |  |
| [group](group.md) |  |
| [groups](groups.md) |  |
| [head](head.md) | EDN literal, e |
| [id](id.md) |  |
| [key_arity](key_arity.md) |  |
| [kind](kind.md) |  |
| [label](label.md) |  |
| [layer](layer.md) |  |
| [members](members.md) |  |
| [name](name.md) |  |
| [order](order.md) | Asserter authority, strongest first |
| [owner](owner.md) |  |
| [params](params.md) |  |
| [pred](pred.md) |  |
| [qualifier](qualifier.md) |  |
| [role](role.md) |  |
| [rule_class](rule_class.md) |  |
| [rules](rules.md) |  |
| [see](see.md) |  |
| [sql](sql.md) |  |
| [subclaims](subclaims.md) |  |
| [superior_to](superior_to.md) |  |
| [synonyms](synonyms.md) |  |
| [tables](tables.md) |  |
| [taxonomies](taxonomies.md) |  |
| [terms](terms.md) |  |
| [today](today.md) |  |
| [valid_from](valid_from.md) |  |
| [valid_to](valid_to.md) |  |
| [values](values.md) |  |
| [version](version.md) |  |
| [warrant](warrant.md) |  |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [AssetKind](AssetKind.md) |  |
| [ColumnType](ColumnType.md) |  |
| [ConceptKind](ConceptKind.md) |  |
| [Modal](Modal.md) |  |
| [Owner](Owner.md) |  |
| [RuleClass](RuleClass.md) |  |
| [RuleKind](RuleKind.md) |  |
| [SubClaimRole](SubClaimRole.md) |  |


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
