---
search:
  boost: 10.0
---

# Class: Neg 


_[:neg literal]: the complement (defeater heads, negative claims)._



<div data-search-exclude markdown="1">



URI: [slice:Neg](https://example.org/llm-policy-reasoning/spike-v3/slice/Neg)





```mermaid
 classDiagram
    class Neg
    click Neg href "../Neg/"
      Literal <|-- Neg
        click Literal href "../Literal/"
      
      Neg : literal
        
          
    
        
        
        Neg --> "1" Literal : literal
        click Literal href "../Literal/"
    

        
      Neg : type
        
      
```





## Inheritance
* [Literal](Literal.md)
    * **Neg**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [literal](literal.md) | 1 <br/> [Literal](Literal.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [Literal](Literal.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Neg |
| native | slice:Neg |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Neg
description: '[:neg literal]: the complement (defeater heads, negative claims).'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  literal:
    name: literal
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    domain_of:
    - Not
    - Neg
    range: Literal
    required: true
    inlined: true

```
</details>

### Induced

<details>
```yaml
name: Neg
description: '[:neg literal]: the complement (defeater heads, negative claims).'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  literal:
    name: literal
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    owner: Neg
    domain_of:
    - Not
    - Neg
    range: Literal
    required: true
    inlined: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    designates_type: true
    owner: Neg
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>