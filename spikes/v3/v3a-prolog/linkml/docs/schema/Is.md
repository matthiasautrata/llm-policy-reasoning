---
search:
  boost: 10.0
---

# Class: Is 


_[:is ?x [:+ a b]]: arithmetic._



<div data-search-exclude markdown="1">



URI: [slice:Is](https://example.org/llm-policy-reasoning/spike-v3/slice/Is)





```mermaid
 classDiagram
    class Is
    click Is href "../Is/"
      Literal <|-- Is
        click Literal href "../Literal/"
      
      Is : expr
        
          
    
        
        
        Is --> "1" Expr : expr
        click Expr href "../Expr/"
    

        
      Is : type
        
      Is : var
        
          
    
        
        
        Is --> "1" Var : var
        click Var href "../Var/"
    

        
      
```





## Inheritance
* [Literal](Literal.md)
    * **Is**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [var](var.md) | 1 <br/> [Var](Var.md) |  | direct |
| [expr](expr.md) | 1 <br/> [Expr](Expr.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [Literal](Literal.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Is |
| native | slice:Is |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Is
description: '[:is ?x [:+ a b]]: arithmetic.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  var:
    name: var
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    domain_of:
    - Output
    - Is
    range: Var
    required: true
    inlined: true
  expr:
    name: expr
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Is
    range: Expr
    required: true
    inlined: true

```
</details>

### Induced

<details>
```yaml
name: Is
description: '[:is ?x [:+ a b]]: arithmetic.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  var:
    name: var
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    owner: Is
    domain_of:
    - Output
    - Is
    range: Var
    required: true
    inlined: true
  expr:
    name: expr
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Is
    domain_of:
    - Is
    range: Expr
    required: true
    inlined: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    designates_type: true
    owner: Is
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>