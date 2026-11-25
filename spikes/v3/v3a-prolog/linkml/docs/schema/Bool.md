---
search:
  boost: 10.0
---

# Class: Bool 

<div data-search-exclude markdown="1">



URI: [slice:Bool](https://example.org/llm-policy-reasoning/spike-v3/slice/Bool)





```mermaid
 classDiagram
    class Bool
    click Bool href "../Bool/"
      RuleTerm <|-- Bool
        click RuleTerm href "../RuleTerm/"
      
      Bool : type
        
      Bool : value
        
      
```





## Inheritance
* [RuleTerm](RuleTerm.md)
    * **Bool**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [value](value.md) | 1 <br/> [Boolean](Boolean.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [RuleTerm](RuleTerm.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Bool |
| native | slice:Bool |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Bool
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
    range: boolean
    required: true

```
</details>

### Induced

<details>
```yaml
name: Bool
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: RuleTerm
attributes:
  value:
    name: value
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    owner: Bool
    domain_of:
    - Str
    - Int
    - Bool
    range: boolean
    required: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    designates_type: true
    owner: Bool
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>