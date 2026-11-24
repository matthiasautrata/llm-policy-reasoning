---
search:
  boost: 5.0
---

# Slot: tables 

<div data-search-exclude markdown="1">



URI: [slice:tables](https://example.org/llm-policy-reasoning/spike-v3/slice/tables)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |  no  |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |  yes  |
| [Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |  no  |
| [Dimension](Dimension.md) | A concept whose kind is dimension |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Table](Table.md) |
| Domain Of | [Slice](Slice.md), [Concept](Concept.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:tables |
| native | slice:tables |




## LinkML Source

<details>
```yaml
name: tables
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Slice
- Concept
range: Table
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>