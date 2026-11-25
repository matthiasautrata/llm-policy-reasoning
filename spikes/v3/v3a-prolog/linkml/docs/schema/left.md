---
search:
  boost: 5.0
---

# Slot: left 

<div data-search-exclude markdown="1">



URI: [slice:left](https://example.org/llm-policy-reasoning/spike-v3/slice/left)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Comparison](Comparison.md) | [:< a b] and friends: numbers or ISO dates |  no  |
| [Expr](Expr.md) | [:+ a b] or [:- a b]; exactly two operands |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Comparison](Comparison.md), [Expr](Expr.md) |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:left |
| native | slice:left |




## LinkML Source

<details>
```yaml
name: left
domain_of:
- Comparison
- Expr
range: string

```
</details></div>