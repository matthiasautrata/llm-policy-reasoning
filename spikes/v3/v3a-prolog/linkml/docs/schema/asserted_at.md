---
search:
  boost: 5.0
---

# Slot: asserted_at 

<div data-search-exclude markdown="1">



URI: [slice:asserted_at](https://example.org/llm-policy-reasoning/spike-v3/slice/asserted_at)
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
| Range | [date](date.md) |
| Domain Of | [ClaimCore](ClaimCore.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:asserted_at |
| native | slice:asserted_at |




## LinkML Source

<details>
```yaml
name: asserted_at
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- ClaimCore
range: date

```
</details></div>