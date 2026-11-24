---
search:
  boost: 5.0
---

# Slot: groups 

<div data-search-exclude markdown="1">



URI: [slice:groups](https://example.org/llm-policy-reasoning/spike-v3/slice/groups)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Taxonomy](Taxonomy.md) | A two-level grouping over a code list |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [TaxonomyGroup](TaxonomyGroup.md) |
| Domain Of | [Taxonomy](Taxonomy.md) |
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
| self | slice:groups |
| native | slice:groups |




## LinkML Source

<details>
```yaml
name: groups
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
domain_of:
- Taxonomy
range: TaxonomyGroup
multivalued: true
inlined: true
inlined_as_list: true

```
</details></div>