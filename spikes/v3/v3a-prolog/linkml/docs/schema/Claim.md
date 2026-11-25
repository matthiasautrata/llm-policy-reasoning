---
search:
  boost: 10.0
---

# Class: Claim 

<div data-search-exclude markdown="1">



URI: [slice:Claim](https://example.org/llm-policy-reasoning/spike-v3/slice/Claim)





```mermaid
 classDiagram
    class Claim
    click Claim href "../Claim/"
      ClaimCore <|-- Claim
        click ClaimCore href "../ClaimCore/"
      
      Claim : about
        
      Claim : asserted_at
        
      Claim : asserted_by
        
          
    
        
        
        Claim --> "1" Owner : asserted_by
        click Owner href "../Owner/"
    

        
      Claim : assertion
        
          
    
        
        
        Claim --> "1" Literal : assertion
        click Literal href "../Literal/"
    

        
      Claim : backing
        
      Claim : id
        
      Claim : qualifier
        
          
    
        
        
        Claim --> "0..1" Modal : qualifier
        click Modal href "../Modal/"
    

        
      Claim : subclaims
        
          
    
        
        
        Claim --> "*" SubClaim : subclaims
        click SubClaim href "../SubClaim/"
    

        
      Claim : valid_from
        
      Claim : valid_to
        
      Claim : warrant
        
      
```





## Inheritance
* [ClaimCore](ClaimCore.md)
    * **Claim**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [about](about.md) | 1 <br/> [String](String.md) |  | direct |
| [subclaims](subclaims.md) | * <br/> [SubClaim](SubClaim.md) |  | direct |
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
| [Slice](Slice.md) | [claims](claims.md) | range | [Claim](Claim.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | slice:Claim |
| native | slice:Claim |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Claim
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: ClaimCore
slots:
- about
- subclaims
slot_usage:
  about:
    name: about
    required: true

```
</details>

### Induced

<details>
```yaml
name: Claim
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
is_a: ClaimCore
slot_usage:
  about:
    name: about
    required: true
attributes:
  about:
    name: about
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - Claim
    range: string
    required: true
    pattern: ^[a-z]+:[A-Za-z0-9_/]+$
  subclaims:
    name: subclaims
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - Claim
    range: SubClaim
    multivalued: true
    inlined: true
    inlined_as_list: true
  id:
    name: id
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    identifier: true
    owner: Claim
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
    owner: Claim
    domain_of:
    - ClaimCore
    range: Literal
    required: true
    inlined: true
  asserted_by:
    name: asserted_by
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: Owner
    required: true
  asserted_at:
    name: asserted_at
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: date
    required: true
  valid_from:
    name: valid_from
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: date
    required: true
  valid_to:
    name: valid_to
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: date
  warrant:
    name: warrant
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: string
    pattern: ^R[0-9]+$
  backing:
    name: backing
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: string
  qualifier:
    name: qualifier
    from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
    rank: 1000
    owner: Claim
    domain_of:
    - ClaimCore
    range: Modal

```
</details></div>