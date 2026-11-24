---
search:
  boost: 5.0
---

# Slot: columns 

<div data-search-exclude markdown="1">



URI: [slice:columns](https://example.org/llm-policy-reasoning/spike-v3/slice/columns)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Table](Table.md) | A physical table of the detail data |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Column](Column.md) |
| Domain Of | [Table](Table.md) |
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
| self | slice:columns |
| native | slice:columns |




## LinkML Source

<details>
```yaml
name: columns
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Table
range: Column
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>