---
search:
  boost: 5.0
---

# Slot: code_lists 

<div data-search-exclude markdown="1">



URI: [slice:code_lists](https://example.org/llm-policy-reasoning/spike-v3/slice/code_lists)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Slice](Slice.md) | The whole slice, as authored in shared/slice |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [CodeList](CodeList.md) |
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
| self | slice:code_lists |
| native | slice:code_lists |




## LinkML Source

<details>
```yaml
name: code_lists
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Slice
range: CodeList
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>