---
search:
  boost: 10.0
---

# Class: Str 

<div data-search-exclude markdown="1">



URI: [slice:Str](https://example.org/llm-policy-reasoning/spike-v3/slice/Str)





```mermaid
 classDiagram
    class Str
    click Str href "../Str/"
      RuleTerm <|-- Str
        click RuleTerm href "../RuleTerm/"
      
      Str : type
        
      Str : value
        
      
```





## Inheritance
* [RuleTerm](RuleTerm.md)
    * **Str**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [value](value.md) | 1 <br/> [String](String.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [RuleTerm](RuleTerm.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Str |
| native | slice:Str |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Str
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: RuleTerm
attributes:
  value:
    name: value
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Str
    - Int
    - Bool
    required: true

```
</details>

### Induced

<details>
```yaml
name: Str
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: RuleTerm
attributes:
  value:
    name: value
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Str
    domain_of:
    - Str
    - Int
    - Bool
    range: string
    required: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    designates_type: true
    owner: Str
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>