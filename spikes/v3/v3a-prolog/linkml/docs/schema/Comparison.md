---
search:
  boost: 10.0
---

# Class: Comparison 


_[:< a b] and friends: numbers or ISO dates._



<div data-search-exclude markdown="1">



URI: [slice:Comparison](https://example.org/llm-policy-reasoning/spike-v3/slice/Comparison)





```mermaid
 classDiagram
    class Comparison
    click Comparison href "../Comparison/"
      Literal <|-- Comparison
        click Literal href "../Literal/"
      
      Comparison : left
        
          
    
        
        
        Comparison --> "1" RuleTerm : left
        click RuleTerm href "../RuleTerm/"
    

        
      Comparison : op
        
          
    
        
        
        Comparison --> "1" ComparisonOp : op
        click ComparisonOp href "../ComparisonOp/"
    

        
      Comparison : right
        
          
    
        
        
        Comparison --> "1" RuleTerm : right
        click RuleTerm href "../RuleTerm/"
    

        
      Comparison : type
        
      
```





## Inheritance
* [Literal](Literal.md)
    * **Comparison**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [op](op.md) | 1 <br/> [ComparisonOp](ComparisonOp.md) |  | direct |
| [left](left.md) | 1 <br/> [RuleTerm](RuleTerm.md) |  | direct |
| [right](right.md) | 1 <br/> [RuleTerm](RuleTerm.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [Literal](Literal.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Comparison |
| native | slice:Comparison |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Comparison
description: '[:< a b] and friends: numbers or ISO dates.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  op:
    name: op
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Comparison
    - Aggregate
    - Expr
    range: ComparisonOp
    required: true
  left:
    name: left
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Comparison
    - Expr
    range: RuleTerm
    required: true
    inlined: true
  right:
    name: right
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Comparison
    - Expr
    range: RuleTerm
    required: true
    inlined: true

```
</details>

### Induced

<details>
```yaml
name: Comparison
description: '[:< a b] and friends: numbers or ISO dates.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  op:
    name: op
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Comparison
    domain_of:
    - Comparison
    - Aggregate
    - Expr
    range: ComparisonOp
    required: true
  left:
    name: left
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Comparison
    domain_of:
    - Comparison
    - Expr
    range: RuleTerm
    required: true
    inlined: true
  right:
    name: right
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Comparison
    domain_of:
    - Comparison
    - Expr
    range: RuleTerm
    required: true
    inlined: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    designates_type: true
    owner: Comparison
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>