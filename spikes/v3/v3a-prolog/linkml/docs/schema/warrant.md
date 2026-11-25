---
search:
  boost: 5.0
---

# Slot: warrant 

<div data-search-exclude markdown="1">



URI: [slice:warrant](https://example.org/llm-policy-reasoning/spike-v3/slice/warrant)
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
| self | slice:warrant |
| native | slice:warrant |




## LinkML Source

<details>
```yaml
name: warrant
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: string
pattern: ^R[0-9]+$

```
</details></div>