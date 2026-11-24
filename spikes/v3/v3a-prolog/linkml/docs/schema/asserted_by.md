---
search:
  boost: 5.0
---

# Slot: asserted_by 

<div data-search-exclude markdown="1">



URI: [slice:asserted_by](https://example.org/llm-policy-reasoning/spike-v3/slice/asserted_by)
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
| Range | [Owner](Owner.md) |
| Domain Of | [ClaimCore](ClaimCore.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:asserted_by |
| native | slice:asserted_by |




## LinkML Source

<details>
```yaml
name: asserted_by
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- ClaimCore
range: Owner

```
</details></div>