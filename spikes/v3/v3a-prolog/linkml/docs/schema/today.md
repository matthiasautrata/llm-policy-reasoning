---
search:
  boost: 5.0
---

# Slot: today 

<div data-search-exclude markdown="1">



URI: [slice:today](https://example.org/llm-policy-reasoning/spike-v3/slice/today)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [Slice](Slice.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:today |
| native | slice:today |




## LinkML Source

<details>
```yaml
name: today
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Slice
range: date
required: true

```
</details></div>