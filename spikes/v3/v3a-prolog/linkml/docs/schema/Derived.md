---
search:
  boost: 10.0
---

# Class: Derived 


_[:pred arg ...]: another rule's head, or a claim._



<div data-search-exclude markdown="1">



URI: [slice:Derived](https://example.org/llm-policy-reasoning/spike-v3/slice/Derived)





```mermaid
 classDiagram
    class Derived
    click Derived href "../Derived/"
      Literal <|-- Derived
        click Literal href "../Literal/"
      
      Derived : args
        
          
    
        
        
        Derived --> "*" RuleTerm : args
        click RuleTerm href "../RuleTerm/"
    

        
      Derived : pred
        
      Derived : type
        
      
```





## Inheritance
* [Literal](Literal.md)
    * **Derived**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [pred](pred.md) | 1 <br/> [String](String.md) |  | direct |
| [args](args.md) | * <br/> [RuleTerm](RuleTerm.md) |  | direct |
| [type](type.md) | 1 <br/> [String](String.md) |  | [Literal](Literal.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Derived |
| native | slice:Derived |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Derived
description: '[:pred arg ...]: another rule''s head, or a claim.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  pred:
    name: pred
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    domain_of:
    - FunctionalPredicate
    - Rule
    - Derived
    required: true
    pattern: ^[a-z_]+$
  args:
    name: args
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    domain_of:
    - Derived
    range: RuleTerm
    multivalued: true
    inlined_as_list: true

```
</details>

### Induced

<details>
```yaml
name: Derived
description: '[:pred arg ...]: another rule''s head, or a claim.'
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: Literal
attributes:
  pred:
    name: pred
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    owner: Derived
    domain_of:
    - FunctionalPredicate
    - Rule
    - Derived
    range: string
    required: true
    pattern: ^[a-z_]+$
  args:
    name: args
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Derived
    domain_of:
    - Derived
    range: RuleTerm
    multivalued: true
    inlined: true
    inlined_as_list: true
  type:
    name: type
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    designates_type: true
    owner: Derived
    domain_of:
    - Literal
    - RuleTerm
    range: string
    required: true

```
</details></div>