---
search:
  boost: 5.0
---

# Slot: literal 

<div data-search-exclude markdown="1">



URI: [slice:literal](https://example.org/llm-policy-reasoning/spike-v3/slice/literal)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Not](Not.md) | [:not literal]: the literal is not defeasibly provable |  no  |
| [Neg](Neg.md) | [:neg literal]: the complement (defeater heads, negative claims) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Not](Not.md), [Neg](Neg.md) |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:literal |
| native | slice:literal |




## LinkML Source

<details>
```yaml
name: literal
domain_of:
- Not
- Neg
range: string

```
</details></div>