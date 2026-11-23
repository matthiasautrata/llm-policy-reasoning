# Read mode: z-ai/glm-5.3 at layer(s) 3

84 scored records, 0 API errors left out. Cost $0.3545; prompt tokens 1,622,138, completion tokens 54,622 (reasoning 40,127); mean 8.5 s per call.
Providers: Novita 84.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 84.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 42 | 95% (40/42) | 95% (37/39) | – | – | – | – | 100% (2/2) | 100% (2/2) | 0% (0/39) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | structured | 42 | 100% (42/42) | 100% (39/39) | – | – | – | – | 100% (2/2) | 100% (2/2) | 0% (0/39) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | 0 | 20 | 95% (19/20) | 95% (19/20) | – | – | – | – | – | – | 0% (0/20) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 1 | 28 | 96% (27/28) | 96% (27/28) | – | – | – | – | – | – | 0% (0/28) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 2 | 24 | 100% (24/24) | 100% (24/24) | – | – | – | – | – | – | 0% (0/24) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | 3 | 8 | 100% (8/8) | 100% (6/6) | – | – | – | – | – | – | 0% (0/6) | 0 |
| z-ai/glm-5.3 | L3 | decided | base | None | 4 | 100% (4/4) | – | – | – | – | – | 100% (4/4) | 100% (4/4) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | 84 | 98% (82/84) | 97% (76/78) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/78) | 0 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | formal | 42 | 95% (40/42) | 18,771 | 384 | 569 | 7.5 | 10.7 | 85.9 | $0.00362 | 0 |
| z-ai/glm-5.3 | L3 | decided | base | M-s1 | structured | 42 | 100% (42/42) | 19,851 | 571 | 732 | 9.5 | 9.9 | 174.1 | $0.00482 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 0 | – | 3% (1/37) | – | 5% (2/37) | – | 0% (0/37) | – | – | – |
| z-ai/glm-5.3 | L3 | decided | base | structured | 0 | – | 5% (2/39) | – | 5% (2/39) | – | 0% (0/39) | – | – | – |

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
| ANSWER | 78 | 0 | 0 | 0 | 0 | 0 |
| CONFLICT | 0 | 0 | 2 | 0 | 0 | 0 |
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
| z-ai/glm-5.3 | L3 | decided | base | Q33 | ANSWER 4 | 3 | 100% (4/4) | ANSWER 4 |
| z-ai/glm-5.3 | L3 | decided | base | Q34 | ANSWER 2, CONFLICT 2 | 3 | 100% (4/4) | ANSWER 2, CONFLICT 2 |
| z-ai/glm-5.3 | L3 | decided | base | Q91 | OUT_OF_SCOPE 4 | None | 100% (4/4) | OUT_OF_SCOPE 4 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 1 | 100% (1/1) | 0% (0/1) | 100% (1/1) | 0 | 0 | 0 | CONFLICT 1 |
| z-ai/glm-5.3 | L3 | decided | base | structured | 1 | 100% (1/1) | 0% (0/1) | 100% (1/1) | 0 | 0 | 0 | CONFLICT 1 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| z-ai/glm-5.3 | L3 | decided | base | formal | 0 | – |
| z-ai/glm-5.3 | L3 | decided | base | structured | 0 | – |

