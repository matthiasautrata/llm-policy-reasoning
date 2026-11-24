---
search:
  boost: 5.0
---

# Slot: doc 

<div data-search-exclude markdown="1">



URI: [slice:doc](https://example.org/llm-policy-reasoning/spike-v3/slice/doc)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Asset](Asset.md) | Anything significant a claim can attach to that is not a table, column, conce... |  no  |
| [Table](Table.md) | A physical table of the detail data |  no  |
| [Column](Column.md) | A column of a physical table |  no  |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |  no  |
| [Rule](Rule.md) | A rule envelope |  no  |
| [Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |  no  |
| [Dimension](Dimension.md) | A concept whose kind is dimension |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Asset](Asset.md), [Table](Table.md), [Column](Column.md), [Concept](Concept.md), [Rule](Rule.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:doc |
| native | slice:doc |




## LinkML Source

<details>
```yaml
name: doc
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Asset
- Table
- Column
- Concept
- Rule
range: string

```
</details></div>