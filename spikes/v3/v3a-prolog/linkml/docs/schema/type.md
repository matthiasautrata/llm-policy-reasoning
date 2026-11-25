---
search:
  boost: 5.0
---

# Slot: type 

<div data-search-exclude markdown="1">



URI: [slice:type](https://example.org/llm-policy-reasoning/spike-v3/slice/type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Literal](Literal.md) | A literal of a rule head or body, or a claim assertion |  no  |
| [Derived](Derived.md) | [:pred arg  |  no  |
| [Fetch](Fetch.md) | [:fetch :concept {col term} {col ?var}]: a concept lookup; bound terms filter... |  no  |
| [Not](Not.md) | [:not literal]: the literal is not defeasibly provable |  no  |
| [Neg](Neg.md) | [:neg literal]: the complement (defeater heads, negative claims) |  no  |
| [Comparison](Comparison.md) | [:< a b] and friends: numbers or ISO dates |  no  |
| [Is](Is.md) | [:is ?x [:+ a b]]: arithmetic |  no  |
| [AsOf](AsOf.md) | [:as_of ?d]: the evaluation date |  no  |
| [RuleTerm](RuleTerm.md) | An argument of a literal (named RuleTerm because Term is the vocabulary class... |  no  |
| [Var](Var.md) |  |  no  |
| [Str](Str.md) |  |  no  |
| [Int](Int.md) |  |  no  |
| [Bool](Bool.md) |  |  no  |
| [Expr](Expr.md) | [:+ a b] or [:- a b]; exactly two operands |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Literal](Literal.md), [RuleTerm](RuleTerm.md) |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:type |
| native | slice:type |




## LinkML Source

<details>
```yaml
name: type
domain_of:
- Literal
- RuleTerm
range: string

```
</details></div>