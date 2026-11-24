---
search:
  boost: 5.0
---

# Slot: superior_to 

<div data-search-exclude markdown="1">



URI: [slice:superior_to](https://example.org/llm-policy-reasoning/spike-v3/slice/superior_to)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Rule](Rule.md) | A rule envelope |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Rule](Rule.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |


### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^R[0-9]+$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:superior_to |
| native | slice:superior_to |




## LinkML Source

<details>
```yaml
name: superior_to
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Rule
range: string
multivalued: true
pattern: ^R[0-9]+$

```
</details></div>