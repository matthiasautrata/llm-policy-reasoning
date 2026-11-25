---
search:
  boost: 5.0
---

# Slot: completeness 


_IR-005: completeness claims (predicate complete) for the scope of the rule's :not / measure fetch._



<div data-search-exclude markdown="1">



URI: [slice:completeness](https://example.org/llm-policy-reasoning/spike-v3/slice/completeness)
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
| Regex Pattern | `^C[0-9]+(\.[0-9]+)?$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:completeness |
| native | slice:completeness |




## LinkML Source

<details>
```yaml
name: completeness
description: 'IR-005: completeness claims (predicate complete) for the scope of the
  rule''s :not / measure fetch.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Rule
range: string
multivalued: true
pattern: ^C[0-9]+(\.[0-9]+)?$

```
</details></div>