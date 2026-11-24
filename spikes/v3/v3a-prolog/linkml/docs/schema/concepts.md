---
search:
  boost: 5.0
---

# Slot: concepts 

<div data-search-exclude markdown="1">



URI: [slice:concepts](https://example.org/llm-policy-reasoning/spike-v3/slice/concepts)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Concept](Concept.md) |
| Domain Of | [Slice](Slice.md) |
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
| self | slice:concepts |
| native | slice:concepts |




## LinkML Source

<details>
```yaml
name: concepts
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Slice
range: Concept
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>