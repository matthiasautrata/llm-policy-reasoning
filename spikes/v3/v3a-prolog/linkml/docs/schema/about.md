---
search:
  boost: 5.0
---

# Slot: about 

<div data-search-exclude markdown="1">



URI: [slice:about](https://example.org/llm-policy-reasoning/spike-v3/slice/about)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Claim](Claim.md) |  |  yes  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Claim](Claim.md) |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^[a-z]+:[A-Za-z0-9_/]+$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:about |
| native | slice:about |




## LinkML Source

<details>
```yaml
name: about
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Claim
range: string
pattern: ^[a-z]+:[A-Za-z0-9_/]+$

```
</details></div>