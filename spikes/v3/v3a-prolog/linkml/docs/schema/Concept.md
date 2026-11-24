---
search:
  boost: 5.0
---

# Slot: concept 

<div data-search-exclude markdown="1">



URI: [slice:concept](https://example.org/llm-policy-reasoning/spike-v3/slice/concept)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Term](Term.md) | A vocabulary term with a contrastive definition (X, as opposed to Y, differin... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Term](Term.md) |
### Value Constraints

| Property | Value |
| --- | --- |
| Regex Pattern | `^(measure|dim|entity|hier):[a-z_]+$` |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:concept |
| native | slice:concept |




## LinkML Source

<details>
```yaml
name: concept
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Term
range: string
pattern: ^(measure|dim|entity|hier):[a-z_]+$

```
</details></div>