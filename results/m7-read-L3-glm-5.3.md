# Read mode: z-ai/glm-5.3 at layer(s) 3

140 scored records, 0 API errors left out. Cost $0.8025; prompt tokens 2,137,262, completion tokens 219,432 (reasoning 176,922); mean 19.4 s per call.
Providers: Novita 140.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 139, length 1.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 70 | 90% (63/70) | 95% (55/58) | – | – | – | – | 100% (2/2) | 100% (2/2) | 0% (0/58) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | structured | 70 | 90% (63/70) | 100% (58/58) | – | – | – | – | 100% (2/2) | 100% (2/2) | 0% (0/58) | 1 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | 0 | 20 | 95% (19/20) | 95% (19/20) | – | – | – | – | – | – | 0% (0/20) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 1 | 28 | 96% (27/28) | 96% (27/28) | – | – | – | – | – | – | 0% (0/28) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 2 | 24 | 100% (24/24) | 100% (24/24) | – | – | – | – | – | – | 0% (0/24) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 3 | 64 | 81% (52/64) | 98% (43/44) | – | – | – | – | – | – | 0% (0/44) | 1 |
| z-ai/glm-5.3 | L3 | decided | base | None | 4 | 100% (4/4) | – | – | – | – | – | 100% (4/4) | 100% (4/4) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | 92 | 96% (88/92) | 98% (82/84) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/84) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s1 | 16 | 75% (12/16) | 92% (11/12) | – | – | – | – | – | – | 0% (0/12) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s2 | 16 | 88% (14/16) | 100% (12/12) | – | – | – | – | – | – | 0% (0/12) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s3 | 16 | 75% (12/16) | 100% (8/8) | – | – | – | – | – | – | 0% (0/8) | 1 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | formal | 46 | 93% (43/46) | 18,771 | 577 | 790 | 9.9 | 15.6 | 85.9 | $0.00446 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | structured | 46 | 98% (45/46) | 19,851 | 767 | 958 | 11.8 | 15.4 | 174.1 | $0.00562 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s1 | formal | 8 | 75% (6/8) | 7,925 | 1,775 | 2,219 | 27.4 | 94.1 | 94.1 | $0.00577 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s1 | structured | 8 | 75% (6/8) | 7,090 | 2,519 | 3,025 | 37.4 | 155.2 | 155.2 | $0.00728 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s2 | formal | 8 | 100% (8/8) | 7,927 | 2,119 | 2,629 | 32.8 | 100.4 | 100.4 | $0.00657 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s2 | structured | 8 | 75% (6/8) | 7,092 | 1,811 | 2,384 | 27.6 | 56.9 | 56.9 | $0.00599 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s3 | formal | 8 | 75% (6/8) | 7,939 | 1,813 | 2,303 | 27.8 | 68.1 | 68.1 | $0.00593 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | S-s3 | structured | 8 | 75% (6/8) | 7,108 | 4,349 | 4,814 | 61.9 | 208.4 | 208.4 | $0.01081 | 1 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 0 | – | 7% (4/55) | – | 9% (5/55) | – | 2% (1/55) | – | – | – |
| z-ai/glm-5.3 | L3 | decided | base | structured | 0 | – | 9% (5/58) | – | 10% (6/58) | – | 3% (2/58) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | Q11 | 4 | 100% (4/4) | – | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q17 | 4 | 100% (4/4) | – | ANSWER 4 |

## Status confusion (rows: key, columns: model)

**z-ai/glm-5.3**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 116 | 0 | 0 | 0 | 0 | 0 |
| CONFLICT | 10 | 0 | 9 | 0 | 0 | 1 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 4 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | Q01 | ANSWER 4 | 0 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q02 | ANSWER 4 | 0 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q03 | ANSWER 4 | 0 | 75% (3/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q04 | ANSWER 4 | 0 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q05 | ANSWER 4 | 0 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q11 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q12 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q13 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q14 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q15 | ANSWER 4 | 1 | 75% (3/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q16 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q17 | ANSWER 4 | 1 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q21 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q22 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q23 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q24 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q25 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q26 | ANSWER 4 | 2 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q33 | ANSWER 28, CONFLICT 4 | 3 | 97% (31/32) | ANSWER 29, CONFLICT 3 |
| z-ai/glm-5.3 | L3 | decided | base | Q34 | ANSWER 16, CONFLICT 16 | 3 | 66% (21/32) | ANSWER 25, CONFLICT 6, PARSE 1 |
| z-ai/glm-5.3 | L3 | decided | base | Q91 | OUT_OF_SCOPE 4 | None | 100% (4/4) | OUT_OF_SCOPE 4 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 10 | 60% (6/10) | 0% (0/10) | 60% (6/10) | 0 | 4 | 0 | CONFLICT 6, ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | structured | 10 | 30% (3/10) | 0% (0/10) | 40% (4/10) | 0 | 6 | 0 | ANSWER 6, CONFLICT 3, PARSE 1 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 16 | 75% (12/16) |
| z-ai/glm-5.3 | L3 | decided | base | structured | 16 | 88% (14/16) |

