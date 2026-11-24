---
search:
  boost: 5.0
---

# Slot: assertion 


_EDN literal, e.g. [:cost_centre_of "e077" "cc0078"]._



<div data-search-exclude markdown="1">



URI: [slice:assertion](https://example.org/llm-policy-reasoning/spike-v3/slice/assertion)
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
| Range | [String](String.md) |
| Domain Of | [ClaimCore](ClaimCore.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:assertion |
| native | slice:assertion |




## LinkML Source

<details>
```yaml
name: assertion
description: EDN literal, e.g. [:cost_centre_of "e077" "cc0078"].
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- ClaimCore
range: string

```
</details></div>