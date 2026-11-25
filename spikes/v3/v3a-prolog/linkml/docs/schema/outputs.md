---
search:
  boost: 5.0
---

# Slot: outputs 

<div data-search-exclude markdown="1">



URI: [slice:outputs](https://example.org/llm-policy-reasoning/spike-v3/slice/outputs)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Fetch](Fetch.md) | [:fetch :concept {col term} {col ?var}]: a concept lookup; bound terms filter... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Output](Output.md) |
| Domain Of | [Fetch](Fetch.md) |
### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
| Multivalued | Yes |


### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Fetch](Fetch.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:outputs |
| native | slice:outputs |




## LinkML Source

<details>
```yaml
name: outputs
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
owner: Fetch
domain_of:
- Fetch
range: Output
required: true
multivalued: true
inlined: true

```
</details></div>