---
search:
  boost: 2.0
---


# Enum: Owner 



<div data-search-exclude markdown="1">

URI: [slice:Owner](https://example.org/llm-policy-reasoning/spike-v3/slice/Owner)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| finance | None |  |
| hr | None |  |
| procurement | None |  |
| compliance | None |  |
| risk | None |  |
| controller | None |  |




## Slots

| Name | Description |
| ---  | --- |
| [owner](owner.md) |  |
| [order](order.md) | Asserter authority, strongest first |
| [asserted_by](asserted_by.md) |  |










## Identifier and Mapping Information





### Schema Source


* from schema: https://example.org/llm-policy-reasoning/spike-v3/slice






## LinkML Source

<details>
```yaml
name: Owner
from_schema: https://example.org/llm-policy-reasoning/spike-v3/slice
rank: 1000
permissible_values:
  finance:
    text: finance
  hr:
    text: hr
  procurement:
    text: procurement
  compliance:
    text: compliance
  risk:
    text: risk
  controller:
    text: controller

```
</details>

</div>