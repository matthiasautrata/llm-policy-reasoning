---
search:
  boost: 10.0
---

# Class: SubClaim 


_One level of nesting. A defeated required sub-claim rebuts its parent; a defeated supporting sub-claim leaves the parent holding with a qualifier that lists it._



<div data-search-exclude markdown="1">



URI: [slice:SubClaim](https://example.org/llm-policy-reasoning/spike-v3/slice/SubClaim)





```mermaid
 classDiagram
    class SubClaim
    click SubClaim href "../SubClaim/"
      ClaimCore <|-- SubClaim
        click ClaimCore href "../ClaimCore/"
      
      SubClaim : asserted_at
        
      SubClaim : asserted_by
        
          
    
        
        
        SubClaim --> "1" Owner : asserted_by
        click Owner href "../Owner/"
    

        
      SubClaim : assertion
        
          
    
        
        
        SubClaim --> "1" Literal : assertion
        click Literal href "../Literal/"
    

        
      SubClaim : backing
        
      SubClaim : id
        
      SubClaim : qualifier
        
          
    
        
        
        SubClaim --> "0..1" Modal : qualifier
        click Modal href "../Modal/"
    

        
      SubClaim : role
        
          
    
        
        
        SubClaim --> "1" SubClaimRole : role
        click SubClaimRole href "../SubClaimRole/"
    

        
      SubClaim : valid_from
        
      SubClaim : valid_to
        
      SubClaim : warrant
        
      
```





## Inheritance
* [ClaimCore](ClaimCore.md)
    * **SubClaim**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [role](role.md) | 1 <br/> [SubClaimRole](SubClaimRole.md) |  | direct |
| [id](id.md) | 1 <br/> [String](String.md) |  | [ClaimCore](ClaimCore.md) |
| [assertion](assertion.md) | 1 <br/> [Literal](Literal.md) | A literal, e | [ClaimCore](ClaimCore.md) |
| [asserted_by](asserted_by.md) | 1 <br/> [Owner](Owner.md) |  | [ClaimCore](ClaimCore.md) |
| [asserted_at](asserted_at.md) | 1 <br/> [date](date.md) |  | [ClaimCore](ClaimCore.md) |
| [valid_from](valid_from.md) | 1 <br/> [date](date.md) |  | [ClaimCore](ClaimCore.md) |
| [valid_to](valid_to.md) | 0..1 <br/> [date](date.md) |  | [ClaimCore](ClaimCore.md) |
| [warrant](warrant.md) | 0..1 <br/> [String](String.md) |  | [ClaimCore](ClaimCore.md) |
| [backing](backing.md) | 0..1 <br/> [String](String.md) |  | [ClaimCore](ClaimCore.md) |
| [qualifier](qualifier.md) | 0..1 <br/> [Modal](Modal.md) |  | [ClaimCore](ClaimCore.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Claim](Claim.md) | [subclaims](subclaims.md) | range | [SubClaim](SubClaim.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:SubClaim |
| native | slice:SubClaim |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: SubClaim
description: One level of nesting. A defeated required sub-claim rebuts its parent;
  a defeated supporting sub-claim leaves the parent holding with a qualifier that
  lists it.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: ClaimCore
slots:
- role
slot_usage:
  role:
    name: role
    required: true

```
</details>

### Induced

<details>
```yaml
name: SubClaim
description: One level of nesting. A defeated required sub-claim rebuts its parent;
  a defeated supporting sub-claim leaves the parent holding with a qualifier that
  lists it.
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: ClaimCore
slot_usage:
  role:
    name: role
    required: true
attributes:
  role:
    name: role
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - SubClaim
    range: SubClaimRole
    required: true
  id:
    name: id
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    identifier: true
    owner: SubClaim
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
    pattern: ^C[0-9]+(\.[0-9]+)?$
  assertion:
    name: assertion
    description: A literal, e.g. [:cost_centre_of "e077" "cc0078"].
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: Literal
    required: true
    inlined: true
  asserted_by:
    name: asserted_by
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: Owner
    required: true
  asserted_at:
    name: asserted_at
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: date
    required: true
  valid_from:
    name: valid_from
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: date
    required: true
  valid_to:
    name: valid_to
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: date
  warrant:
    name: warrant
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: string
    pattern: ^R[0-9]+$
  backing:
    name: backing
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: string
  qualifier:
    name: qualifier
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: SubClaim
    domain_of:
    - ClaimCore
    range: Modal

```
</details></div>