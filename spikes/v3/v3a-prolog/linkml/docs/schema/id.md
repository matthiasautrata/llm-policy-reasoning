---
search:
  boost: 5.0
---

# Slot: id 

<div data-search-exclude markdown="1">



URI: [slice:id](https://example.org/llm-policy-reasoning/spike-v3/slice/id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Asset](Asset.md) | Anything significant a claim can attach to that is not a table, column, conce... |  no  |
| [Table](Table.md) | A physical table of the detail data |  yes  |
| [Column](Column.md) | A column of a physical table |  yes  |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |  no  |
| [Term](Term.md) | A vocabulary term with a contrastive definition (X, as opposed to Y, differin... |  yes  |
| [CodeList](CodeList.md) | The admissible codes of an enumerated column |  no  |
| [Taxonomy](Taxonomy.md) | A two-level grouping over a code list |  no  |
| [Rule](Rule.md) | A rule envelope |  yes  |
| [ClaimCore](ClaimCore.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |  yes  |
| [Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |  no  |
| [Dimension](Dimension.md) | A concept whose kind is dimension |  no  |
| [Claim](Claim.md) |  |  no  |
| [SubClaim](SubClaim.md) | One level of nesting |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Asset](Asset.md), [Table](Table.md), [Column](Column.md), [Concept](Concept.md), [Term](Term.md), [CodeList](CodeList.md), [Taxonomy](Taxonomy.md), [Rule](Rule.md), [ClaimCore](ClaimCore.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:id |
| native | slice:id |




## LinkML Source

<details>
```yaml
name: id
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
identifier: true
domain_of:
- Asset
- Table
- Column
- Concept
- Term
- CodeList
- Taxonomy
- Rule
- ClaimCore
range: string
required: true

```
</details></div>