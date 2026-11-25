---
search:
  boost: 5.0
---

# Slot: term 

<div data-search-exclude markdown="1">



URI: [slice:term](https://example.org/llm-policy-reasoning/spike-v3/slice/term)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Filter](Filter.md) | One entry of a fetch filter map (compact form `column: term`) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [RuleTerm](RuleTerm.md) |
| Domain Of | [Filter](Filter.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Filter](Filter.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:term |
| native | slice:term |




## LinkML Source

<details>
```yaml
name: term
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
owner: Filter
domain_of:
- Filter
range: RuleTerm
required: true
inlined: true

```
</details></div>