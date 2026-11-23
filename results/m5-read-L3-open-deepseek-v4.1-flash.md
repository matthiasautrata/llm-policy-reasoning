# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

72 scored records, 0 API errors left out. Cost $0.0235; prompt tokens 691,950, completion tokens 24,358 (reasoning 21,471); mean 3.6 s per call.
Providers: DeepInfra 68, Baidu 4.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 72.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 24 | 100% (24/24) | 100% (22/22) | 100% (2/2) | 100% (2/2) | – | – | – | – | 0% (0/22) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 24 | 100% (24/24) | 100% (22/22) | 100% (2/2) | 100% (2/2) | – | – | – | – | 0% (0/22) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 24 | 100% (24/24) | 100% (22/22) | 100% (2/2) | 100% (2/2) | – | – | – | – | 0% (0/22) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | 3 | 72 | 100% (72/72) | 100% (66/66) | 100% (6/6) | 100% (6/6) | – | – | – | – | 0% (0/66) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | M-s1 | 18 | 100% (18/18) | 100% (15/15) | 100% (3/3) | 100% (3/3) | – | – | – | – | 0% (0/15) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s1 | 18 | 100% (18/18) | 100% (18/18) | – | – | – | – | – | – | 0% (0/18) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s2 | 18 | 100% (18/18) | 100% (18/18) | – | – | – | – | – | – | 0% (0/18) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s3 | 18 | 100% (18/18) | 100% (15/15) | 100% (3/3) | 100% (3/3) | – | – | – | – | 0% (0/15) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 0 | – | 50% (11/22) | – | 50% (11/22) | – | 0% (0/22) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 0 | – | 82% (18/22) | – | 82% (18/22) | – | 0% (0/22) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 0 | – | 55% (12/22) | – | 59% (13/22) | – | 0% (0/22) | – | – | – |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 66 | 0 | 0 | 0 | 0 | 0 |
| AMBIGUOUS | 0 | 6 | 0 | 0 | 0 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | Q31 | ANSWER 24 | 3 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | Q32 | ANSWER 18, AMBIGUOUS 6 | 3 | 100% (24/24) | ANSWER 18, AMBIGUOUS 6 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | Q35 | ANSWER 24 | 3 | 100% (24/24) | ANSWER 24 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 0 | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 0 | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 0 | – |

