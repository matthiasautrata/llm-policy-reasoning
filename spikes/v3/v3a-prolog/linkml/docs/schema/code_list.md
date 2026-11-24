---
search:
  boost: 5.0
---

# Slot: code_list 

<div data-search-exclude markdown="1">



URI: [slice:code_list](https://example.org/llm-policy-reasoning/spike-v3/slice/code_list)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Taxonomy](Taxonomy.md) | A two-level grouping over a code list |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Taxonomy](Taxonomy.md) |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^codes:[a-z_]+$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:code_list |
| native | slice:code_list |




## LinkML Source

<details>
```yaml
name: code_list
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Taxonomy
range: string
pattern: ^codes:[a-z_]+$

```
</details></div>