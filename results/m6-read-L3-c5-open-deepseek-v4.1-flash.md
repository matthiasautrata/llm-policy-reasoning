# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

70 scored records, 0 API errors left out. Cost $0.4714; prompt tokens 876,330, completion tokens 777,256 (reasoning 770,921); mean 75.6 s per call.
Providers: InferenceNet 68, Baidu 2.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 36, length 34.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 22 | 64% (14/22) | 67% (6/9) | 89% (8/9) | 89% (8/9) | – | – | – | – | 0% (0/9) | 8 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 24 | 42% (10/24) | 67% (6/9) | 44% (4/9) | 44% (4/9) | – | – | – | – | 0% (0/9) | 14 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 24 | 50% (12/24) | 67% (6/9) | 67% (6/9) | 67% (6/9) | – | – | – | – | 0% (0/9) | 12 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | 3 | 70 | 51% (36/70) | 67% (18/27) | 67% (18/27) | 67% (18/27) | – | – | – | – | 0% (0/27) | 34 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | M-s1 | 36 | 39% (14/36) | 50% (9/18) | 56% (5/9) | 56% (5/9) | – | – | – | – | 0% (0/18) | 22 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s1 | 34 | 65% (22/34) | 100% (9/9) | 72% (13/18) | 72% (13/18) | – | – | – | – | 0% (0/9) | 12 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | M-s1 | formal | 12 | 50% (6/12) | 18,814 | 11,544 | 11,619 | 98.6 | 180.1 | 184.0 | $0.00707 | 6 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | M-s1 | structured | 12 | 25% (3/12) | 19,594 | 12,171 | 12,192 | 69.1 | 114.9 | 117.5 | $0.00751 | 9 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | M-s1 | text | 12 | 42% (5/12) | 15,308 | 11,712 | 11,783 | 87.7 | 167.1 | 168.9 | $0.00744 | 7 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s1 | formal | 10 | 80% (8/10) | 8,644 | 8,638 | 8,828 | 47.5 | 89.4 | 89.4 | $0.00544 | 2 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s1 | structured | 12 | 58% (7/12) | 7,490 | 10,948 | 11,033 | 78.4 | 125.9 | 130.2 | $0.00620 | 5 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | S-s1 | text | 12 | 58% (7/12) | 4,618 | 10,670 | 10,787 | 67.7 | 120.0 | 122.4 | $0.00653 | 5 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 0 | – | 100% (6/6) | – | 100% (6/6) | – | 0% (0/6) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 0 | – | 100% (6/6) | – | 100% (6/6) | – | 0% (0/6) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 0 | – | 100% (6/6) | – | 100% (6/6) | – | 0% (0/6) | – | – | – |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 18 | 0 | 0 | 0 | 0 | 9 |
| AMBIGUOUS | 0 | 18 | 0 | 0 | 0 | 9 |
| CONFLICT | 0 | 0 | 0 | 0 | 0 | 16 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | Q33 | ANSWER 18, AMBIGUOUS 18 | 3 | 89% (32/36) | ANSWER 18, AMBIGUOUS 14, PARSE 4 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | Q34 | CONFLICT 16, ANSWER 9, AMBIGUOUS 9 | 3 | 12% (4/34) | PARSE 30, AMBIGUOUS 4 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 4 | 0% (0/4) | 0% (0/4) | 100% (4/4) | 0 | 0 | 0 | PARSE 4 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 6 | 0% (0/6) | 0% (0/6) | 100% (6/6) | 0 | 0 | 0 | PARSE 6 |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 6 | 0% (0/6) | 0% (0/6) | 100% (6/6) | 0 | 0 | 0 | PARSE 6 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | base | formal | 7 | 86% (6/7) |
| deepseek/deepseek-v4.1-flash | L3 | open | base | structured | 8 | 88% (7/8) |
| deepseek/deepseek-v4.1-flash | L3 | open | base | text | 8 | 75% (6/8) |

