---
search:
  boost: 5.0
---

# Slot: depends_on 


_Claim ids this claim requires._



<div data-search-exclude markdown="1">



URI: [slice:depends_on](https://example.org/llm-policy-reasoning/spike-v3/slice/depends_on)
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
| self | slice:depends_on |
| native | slice:depends_on |




## LinkML Source

<details>
```yaml
name: depends_on
description: Claim ids this claim requires.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: string
multivalued: true
pattern: ^C[0-9]+(\.[0-9]+)?$

```
</details></div>