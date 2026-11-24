---
search:
  boost: 5.0
---

# Slot: valid_from 

<div data-search-exclude markdown="1">



URI: [slice:valid_from](https://example.org/llm-policy-reasoning/spike-v3/slice/valid_from)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ClaimCore](ClaimCore.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |  yes  |
| [Claim](Claim.md) |  |  no  |
| [SubClaim](SubClaim.md) | One level of nesting |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [ClaimCore](ClaimCore.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:valid_from |
| native | slice:valid_from |




## LinkML Source

<details>
```yaml
name: valid_from
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- ClaimCore
range: date

```
</details></div>