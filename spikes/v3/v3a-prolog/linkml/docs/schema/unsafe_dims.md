---
search:
  boost: 5.0
---

# Slot: unsafe_dims 


_Dimensions a semi-additive measure must not be summed over._



<div data-search-exclude markdown="1">



URI: [slice:unsafe_dims](https://example.org/llm-policy-reasoning/spike-v3/slice/unsafe_dims)
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
| self | slice:unsafe_dims |
| native | slice:unsafe_dims |




## LinkML Source

<details>
```yaml
name: unsafe_dims
description: Dimensions a semi-additive measure must not be summed over.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Concept
range: string
multivalued: true

```
</details></div>