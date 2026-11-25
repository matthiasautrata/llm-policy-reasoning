---
search:
  boost: 10.0
---

# Class: Taxonomy 


_A two-level grouping over a code list._



<div data-search-exclude markdown="1">



URI: [slice:Taxonomy](https://example.org/llm-policy-reasoning/spike-v3/slice/Taxonomy)





```mermaid
 classDiagram
    class Taxonomy
    click Taxonomy href "../Taxonomy/"
      Taxonomy : code_list
        
      Taxonomy : groups
        
          
    
        
        
        Taxonomy --> "*" TaxonomyGroup : groups
        click TaxonomyGroup href "../TaxonomyGroup/"
    

        
      Taxonomy : id
        
      
```




<!-- no inheritance hierarchy -->

## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [id](id.md) | 1 <br/> [String](String.md) |  | direct |
| [code_list](code_list.md) | 0..1 <br/> [String](String.md) |  | direct |
| [groups](groups.md) | * <br/> [TaxonomyGroup](TaxonomyGroup.md) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Slice](Slice.md) | [taxonomies](taxonomies.md) | range | [Taxonomy](Taxonomy.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Taxonomy |
| native | slice:Taxonomy |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Taxonomy
description: A two-level grouping over a code list.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
slots:
- id
- code_list
- groups

```
</details>

### Induced

<details>
```yaml
name: Taxonomy
description: A two-level grouping over a code list.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
attributes:
  id:
    name: id
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    identifier: true
    owner: Taxonomy
    domain_of:
    - Asset
    - Table
    - Column
    - Concept
    - Term
    - CodeList
    - Taxonomy
    - Rule
    - Claim
    range: string
    required: true
  code_list:
    name: code_list
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Taxonomy
    domain_of:
    - Taxonomy
    range: string
    pattern: ^codes:[a-z_]+$
  groups:
    name: groups
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Taxonomy
    domain_of:
    - Taxonomy
    range: TaxonomyGroup
    multivalued: true
    inlined: true
    inlined_as_list: true

```
</details></div>