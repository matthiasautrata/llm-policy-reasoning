---
search:
  boost: 5.0
---

# Slot: derived_by 

<div data-search-exclude markdown="1">



URI: [slice:derived_by](https://example.org/llm-policy-reasoning/spike-v3/slice/derived_by)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |  no  |
| [Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |  no  |
| [Dimension](Dimension.md) | A concept whose kind is dimension |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Concept](Concept.md) |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^R[0-9]+$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:derived_by |
| native | slice:derived_by |




## LinkML Source

<details>
```yaml
name: derived_by
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Concept
range: string
pattern: ^R[0-9]+$

```
</details></div>