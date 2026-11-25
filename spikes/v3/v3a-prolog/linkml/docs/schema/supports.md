---
search:
  boost: 5.0
---

# Slot: supports 


_Claim ids that support this claim._



<div data-search-exclude markdown="1">



URI: [slice:supports](https://example.org/llm-policy-reasoning/spike-v3/slice/supports)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Claim](Claim.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Claim](Claim.md) |
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
| self | slice:supports |
| native | slice:supports |




## LinkML Source

<details>
```yaml
name: supports
description: Claim ids that support this claim.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: string
multivalued: true
pattern: ^C[0-9]+(\.[0-9]+)?$

```
</details></div>