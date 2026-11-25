---
search:
  boost: 10.0
---

# Class: Int 

<div data-search-exclude markdown="1">



URI: [slice:Int](https://example.org/llm-policy-reasoning/spike-v3/slice/Int)





```mermaid
 classDiagram
    class Int
    click Int href "../Int/"
      RuleTerm <|-- Int
        click RuleTerm href "../RuleTerm/"
      
      Int : type
        
      Int : value
        
      
```





## Inheritance
* [RuleTerm](RuleTerm.md)
    * **Int**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [value](value.md) | 1 <br/> [Integer](Integer.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [RuleTerm](RuleTerm.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Int |
| native | slice:Int |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Int
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: RuleTerm
attributes:
  value:
    name: value
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    domain_of:
    - Str
    - Int
    - Bool
    range: integer
    required: true

```
</details>

### Induced

<details>
```yaml
name: Int
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: RuleTerm
attributes:
  value:
    name: value
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    owner: Int
    domain_of:
    - Str
    - Int
    - Bool
    range: integer
    required: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    designates_type: true
    owner: Int
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>