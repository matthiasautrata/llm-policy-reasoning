---
search:
  boost: 5.0
---

# Slot: concept_name 


_The concept's name as rules reference it in fetch literals._



<div data-search-exclude markdown="1">



URI: [slice:concept_name](https://example.org/llm-policy-reasoning/spike-v3/slice/concept_name)
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










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:concept_name |
| native | slice:concept_name |




## LinkML Source

<details>
```yaml
name: concept_name
description: The concept's name as rules reference it in fetch literals.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Concept
range: string

```
</details></div>