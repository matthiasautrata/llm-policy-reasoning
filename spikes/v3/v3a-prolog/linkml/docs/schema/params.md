---
search:
  boost: 5.0
---

# Slot: params 

<div data-search-exclude markdown="1">



URI: [slice:params](https://example.org/llm-policy-reasoning/spike-v3/slice/params)
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
| self | slice:params |
| native | slice:params |




## LinkML Source

<details>
```yaml
name: params
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Concept
range: string
multivalued: true

```
</details></div>