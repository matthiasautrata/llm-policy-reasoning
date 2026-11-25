---
search:
  boost: 5.0
---

# Slot: out 

<div data-search-exclude markdown="1">



URI: [slice:out](https://example.org/llm-policy-reasoning/spike-v3/slice/out)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Aggregate](Aggregate.md) | [:agg :sum ?x [literal  |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Var](Var.md) |
| Domain Of | [Aggregate](Aggregate.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Aggregate](Aggregate.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:out |
| native | slice:out |




## LinkML Source

<details>
```yaml
name: out
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
owner: Aggregate
domain_of:
- Aggregate
range: Var
required: true
inlined: true

```
</details></div>