---
search:
  boost: 5.0
---

# Slot: assets 

<div data-search-exclude markdown="1">



URI: [slice:assets](https://example.org/llm-policy-reasoning/spike-v3/slice/assets)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Asset](Asset.md) |
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
| self | slice:assets |
| native | slice:assets |




## LinkML Source

<details>
```yaml
name: assets
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Slice
range: Asset
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>