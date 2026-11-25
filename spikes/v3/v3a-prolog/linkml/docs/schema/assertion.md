---
search:
  boost: 5.0
---

# Slot: assertion 


_A literal, e.g. [:cost_centre_of "e077" "cc0078"]._



<div data-search-exclude markdown="1">



URI: [slice:assertion](https://example.org/llm-policy-reasoning/spike-v3/slice/assertion)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Claim](Claim.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |  yes  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Literal](Literal.md) |
| Domain Of | [Claim](Claim.md) |










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
description: A literal, e.g. [:cost_centre_of "e077" "cc0078"].
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: Literal
inlined: true

```
</details></div>