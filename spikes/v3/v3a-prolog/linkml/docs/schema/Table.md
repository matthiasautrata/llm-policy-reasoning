---
search:
  boost: 10.0
---

# Class: Table 


_A physical table of the detail data._



<div data-search-exclude markdown="1">



URI: [slice:Table](https://example.org/llm-policy-reasoning/spike-v3/slice/Table)





```mermaid
 classDiagram
    class Table
    click Table href "../Table/"
      Table : columns
        
          
    
        
        
        Table --> "*" Column : columns
        click Column href "../Column/"
    

        
      Table : doc
        
      Table : id
        
      Table : name
        
      
```




<!-- no inheritance hierarchy -->

## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [id](id.md) | 1 <br/> [String](String.md) |  | direct |
| [name](name.md) | 0..1 <br/> [String](String.md) |  | direct |
| [doc](doc.md) | 0..1 <br/> [String](String.md) |  | direct |
| [columns](columns.md) | * <br/> [Column](Column.md) |  | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Slice](Slice.md) | [tables](tables.md) | range | [Table](Table.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Table |
| native | slice:Table |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Table
description: A physical table of the detail data.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
slots:
- id
- name
- doc
- columns
slot_usage:
  id:
    name: id
    pattern: ^table:[a-z_]+$

```
</details>

### Induced

<details>
```yaml
name: Table
description: A physical table of the detail data.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
slot_usage:
  id:
    name: id
    pattern: ^table:[a-z_]+$
attributes:
  id:
    name: id
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    identifier: true
    owner: Table
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
    pattern: ^table:[a-z_]+$
  name:
    name: name
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Table
    domain_of:
    - Table
    - Column
    range: string
  doc:
    name: doc
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Table
    domain_of:
    - Asset
    - Table
    - Column
    - Concept
    - Rule
    range: string
  columns:
    name: columns
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Table
    domain_of:
    - Table
    range: Column
    multivalued: true
    inlined: true
    inlined_as_list: true

```
</details></div>