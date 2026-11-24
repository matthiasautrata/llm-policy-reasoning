---
search:
  boost: 5.0
---

# Slot: values 

<div data-search-exclude markdown="1">



URI: [slice:values](https://example.org/llm-policy-reasoning/spike-v3/slice/values)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CodeList](CodeList.md) | The admissible codes of an enumerated column |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [CodeList](CodeList.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
| Multivalued | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:values |
| native | slice:values |




## LinkML Source

<details>
```yaml
name: values
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- CodeList
range: string
required: true
multivalued: true

```
</details></div>