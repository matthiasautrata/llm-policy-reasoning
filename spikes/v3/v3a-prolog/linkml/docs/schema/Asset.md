---
search:
  boost: 10.0
---

# Class: Asset 


_Anything significant a claim can attach to that is not a table, column, concept or term._



<div data-search-exclude markdown="1">



URI: [slice:Asset](https://example.org/llm-policy-reasoning/spike-v3/slice/Asset)





```mermaid
 classDiagram
    class Asset
    click Asset href "../Asset/"
      Asset : doc
        
      Asset : id
        
      Asset : kind
        
          
    
        
        
        Asset --> "1" AssetKind : kind
        click AssetKind href "../AssetKind/"
    

        
      
```




<!-- no inheritance hierarchy -->

## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [id](id.md) | 1 <br/> [String](String.md) |  | direct |
| [kind](kind.md) | 1 <br/> [AssetKind](AssetKind.md) |  | direct |
| [doc](doc.md) | 0..1 <br/> [String](String.md) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Slice](Slice.md) | [assets](assets.md) | range | [Asset](Asset.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Asset |
| native | slice:Asset |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Asset
description: Anything significant a claim can attach to that is not a table, column,
  concept or term.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
slots:
- id
- kind
- doc
slot_usage:
  kind:
    name: kind
    range: AssetKind
    required: true

```
</details>

### Induced

<details>
```yaml
name: Asset
description: Anything significant a claim can attach to that is not a table, column,
  concept or term.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
slot_usage:
  kind:
    name: kind
    range: AssetKind
    required: true
attributes:
  id:
    name: id
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    identifier: true
    owner: Asset
    domain_of:
    - Asset
    - Table
    - Column
    - Concept
    - Term
    - CodeList
    - Taxonomy
    - Rule
    - ClaimCore
    range: string
    required: true
  kind:
    name: kind
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Asset
    domain_of:
    - Asset
    - Concept
    - Rule
    range: AssetKind
    required: true
  doc:
    name: doc
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Asset
    domain_of:
    - Asset
    - Table
    - Column
    - Concept
    - Rule
    range: string

```
</details></div>