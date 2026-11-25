---
search:
  boost: 5.0
---

# Slot: expr 

<div data-search-exclude markdown="1">



URI: [slice:expr](https://example.org/llm-policy-reasoning/spike-v3/slice/expr)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Is](Is.md) | [:is ?x [:+ a b]]: arithmetic |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Expr](Expr.md) |
| Domain Of | [Is](Is.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Is](Is.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:expr |
| native | slice:expr |




## LinkML Source

<details>
```yaml
name: expr
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
owner: Is
domain_of:
- Is
range: Expr
required: true
inlined: true

```
</details></div>