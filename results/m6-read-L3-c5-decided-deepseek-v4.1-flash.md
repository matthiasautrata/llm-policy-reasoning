# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

98 scored records, 0 API errors left out. Cost $0.4458; prompt tokens 1,018,580, completion tokens 705,579 (reasoning 697,727); mean 54.8 s per call.
Providers: InferenceNet 96, Baidu 2.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 84, length 14.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 26 | 85% (22/26) | 95% (19/20) | – | – | – | – | – | – | 0% (0/20) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 36 | 72% (26/36) | 89% (24/27) | – | – | – | – | – | – | 0% (0/27) | 6 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 36 | 75% (27/36) | 100% (27/27) | – | – | – | – | – | – | 0% (0/27) | 4 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 3 | 98 | 77% (75/98) | 95% (70/74) | – | – | – | – | – | – | 0% (0/74) | 14 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | 36 | 64% (23/36) | 85% (23/27) | – | – | – | – | – | – | 0% (0/27) | 12 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | 36 | 86% (31/36) | 100% (27/27) | – | – | – | – | – | – | 0% (0/27) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | 26 | 81% (21/26) | 100% (20/20) | – | – | – | – | – | – | 0% (0/20) | 1 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | formal | 12 | 67% (8/12) | 18,174 | 8,607 | 8,665 | 87.1 | 203.4 | 204.3 | $0.00565 | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | structured | 12 | 50% (6/12) | 19,164 | 9,036 | 9,079 | 58.2 | 122.3 | 122.9 | $0.00593 | 5 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | text | 12 | 75% (9/12) | 15,154 | 8,085 | 8,145 | 63.1 | 120.3 | 122.5 | $0.00519 | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | formal | 12 | 100% (12/12) | 8,004 | 6,517 | 6,638 | 48.9 | 104.6 | 134.3 | $0.00411 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | structured | 12 | 83% (10/12) | 7,062 | 6,777 | 6,862 | 38.5 | 79.0 | 82.7 | $0.00423 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | text | 12 | 75% (9/12) | 4,464 | 6,836 | 6,912 | 63.5 | 137.2 | 146.1 | $0.00426 | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | formal | 2 | 100% (2/2) | 7,996 | 1,648 | 1,788 | 10.9 | 11.8 | 11.8 | $0.00145 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | structured | 12 | 83% (10/12) | 7,062 | 6,588 | 6,642 | 46.9 | 86.0 | 92.7 | $0.00414 | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | text | 12 | 75% (9/12) | 4,464 | 5,423 | 5,556 | 39.4 | 69.8 | 76.2 | $0.00341 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 0 | – | 79% (15/19) | – | 89% (17/19) | – | 0% (0/19) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 0 | – | 75% (18/24) | – | 79% (19/24) | – | 0% (0/24) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 0 | – | 70% (19/27) | – | 74% (20/27) | – | 0% (0/27) | – | – | – |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 71 | 0 | 0 | 0 | 0 | 3 |
| CONFLICT | 8 | 0 | 5 | 0 | 0 | 11 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q33 | ANSWER 50 | 3 | 98% (49/50) | ANSWER 50 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q34 | ANSWER 24, CONFLICT 24 | 3 | 54% (26/48) | ANSWER 29, PARSE 14, CONFLICT 5 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 6 | 50% (3/6) | 0% (0/6) | 100% (6/6) | 0 | 0 | 0 | PARSE 3, CONFLICT 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 9 | 22% (2/9) | 0% (0/9) | 67% (6/9) | 0 | 3 | 0 | PARSE 4, ANSWER 3, CONFLICT 2 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 9 | 0% (0/9) | 0% (0/9) | 44% (4/9) | 0 | 5 | 0 | ANSWER 5, PARSE 4 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 9 | 89% (8/9) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 12 | 75% (9/12) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 12 | 92% (11/12) |

