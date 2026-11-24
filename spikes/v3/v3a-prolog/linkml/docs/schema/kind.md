---
search:
  boost: 5.0
---

# Slot: kind 

<div data-search-exclude markdown="1">



URI: [slice:kind](https://example.org/llm-policy-reasoning/spike-v3/slice/kind)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Asset](Asset.md) | Anything significant a claim can attach to that is not a table, column, conce... |  yes  |
| [Concept](Concept.md) | A semantic-layer entry (measure, dimension, entity or hierarchy) bound to tab... |  yes  |
| [Rule](Rule.md) | A rule envelope |  yes  |
| [Measure](Measure.md) | A concept whose kind is measure (an aggregate over the detail data) |  no  |
| [Dimension](Dimension.md) | A concept whose kind is dimension |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Asset](Asset.md), [Concept](Concept.md), [Rule](Rule.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:kind |
| native | slice:kind |




## LinkML Source

<details>
```yaml
name: kind
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Asset
- Concept
- Rule
range: string

```
</details></div>