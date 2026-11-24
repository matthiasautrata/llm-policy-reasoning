---
search:
  boost: 5.0
---

# Slot: subclaims 

<div data-search-exclude markdown="1">



URI: [slice:subclaims](https://example.org/llm-policy-reasoning/spike-v3/slice/subclaims)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Claim](Claim.md) |  |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SubClaim](SubClaim.md) |
| Domain Of | [Claim](Claim.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:subclaims |
| native | slice:subclaims |




## LinkML Source

<details>
```yaml
name: subclaims
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: SubClaim
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>