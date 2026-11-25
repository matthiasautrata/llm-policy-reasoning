---
search:
  boost: 10.0
---

# Class: AsOf 


_[:as_of ?d]: the evaluation date._



<div data-search-exclude markdown="1">



URI: [slice:AsOf](https://example.org/llm-policy-reasoning/spike-v3/slice/AsOf)





```mermaid
 classDiagram
    class AsOf
    click AsOf href "../AsOf/"
      Literal <|-- AsOf
        click Literal href "../Literal/"
      
      AsOf : date
        
          
    
        
        
        AsOf --> "1" RuleTerm : date
        click RuleTerm href "../RuleTerm/"
    

        
      AsOf : type
        
      
```





## Inheritance
* [Literal](Literal.md)
    * **AsOf**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [date](date.md) | 1 <br/> [RuleTerm](RuleTerm.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [Literal](Literal.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:AsOf |
| native | slice:AsOf |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AsOf
description: '[:as_of ?d]: the evaluation date.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  date:
    name: date
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - AsOf
    range: RuleTerm
    required: true
    inlined: true

```
</details>

### Induced

<details>
```yaml
name: AsOf
description: '[:as_of ?d]: the evaluation date.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  date:
    name: date
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: AsOf
    domain_of:
    - AsOf
    range: RuleTerm
    required: true
    inlined: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    designates_type: true
    owner: AsOf
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>