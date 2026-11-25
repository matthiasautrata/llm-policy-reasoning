---
search:
  boost: 5.0
---

# Slot: batch_sql 


_The set form of sql for its one required parameter $p, written IN ($p), with $p among the output columns (CONTRACT.md, Aggregates)._



<div data-search-exclude markdown="1">



URI: [slice:batch_sql](https://example.org/llm-policy-reasoning/spike-v3/slice/batch_sql)
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
| self | slice:batch_sql |
| native | slice:batch_sql |




## LinkML Source

<details>
```yaml
name: batch_sql
description: The set form of sql for its one required parameter $p, written IN ($p),
  with $p among the output columns (CONTRACT.md, Aggregates).
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Concept
range: string

```
</details></div>