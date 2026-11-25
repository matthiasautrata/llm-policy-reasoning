---
search:
  boost: 5.0
---

# Slot: recorded_at 


_When the record entered the store (provenance; no rule body reads it)._



<div data-search-exclude markdown="1">



URI: [slice:recorded_at](https://example.org/llm-policy-reasoning/spike-v3/slice/recorded_at)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Rule](Rule.md) | A rule envelope |  yes  |
| [Claim](Claim.md) | A Toulmin claim: an assertion about an asset by an asserter, in force from va... |  yes  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [date](date.md) |
| Domain Of | [Rule](Rule.md), [Claim](Claim.md) |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:recorded_at |
| native | slice:recorded_at |




## LinkML Source

<details>
```yaml
name: recorded_at
description: When the record entered the store (provenance; no rule body reads it).
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Rule
- Claim
range: date

```
</details></div>