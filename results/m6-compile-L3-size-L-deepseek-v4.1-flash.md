# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 3

152 scored records, 0 API errors left out. Cost $0.2181; prompt tokens 7,261,227, completion tokens 180,374 (reasoning 171,457); mean 9.8 s per call.
Providers: InferenceNet 144, CoreWeave 7, Baidu 1.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 152.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 76 | 95% (72/76) | 94% (68/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 76 | 100% (76/76) | 100% (72/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 0 | 40 | 92% (37/40) | 92% (37/40) | – | – | – | – | – | – | 0% (0/40) | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 1 | 56 | 98% (55/56) | 98% (55/56) | – | – | – | – | – | – | 0% (0/56) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 2 | 48 | 100% (48/48) | 100% (48/48) | – | – | – | – | – | – | 0% (0/48) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | None | 8 | 100% (8/8) | – | – | – | – | – | 100% (8/8) | 100% (8/8) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | L-s1 | 152 | 97% (148/152) | 97% (140/144) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/144) | 4 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | L-s1 | formal | 76 | 95% (72/76) | 47,022 | 987 | 1,045 | 8.6 | 15.5 | 73.6 | $0.00125 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | L-s1 | structured | 76 | 100% (76/76) | 48,521 | 1,269 | 1,328 | 11.0 | 32.8 | 41.9 | $0.00162 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 0 | – | 51% (35/68) | – | 79% (54/68) | – | 0% (0/68) | – | 0% (0/68) | 76 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 0 | – | 51% (37/72) | – | 85% (61/72) | – | 0% (0/72) | – | 0% (0/72) | 76 |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q11 | 8 | 100% (8/8) | – | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q17 | 8 | 100% (8/8) | – | ANSWER 8 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 140 | 0 | 0 | 0 | 0 | 4 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 8 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q01 | ANSWER 8 | 0 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q02 | ANSWER 8 | 0 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q03 | ANSWER 8 | 0 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q04 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q05 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q11 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q12 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q13 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q14 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q15 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q16 | ANSWER 8 | 1 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q17 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q21 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q22 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q23 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q24 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q25 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q26 | ANSWER 8 | 2 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q91 | OUT_OF_SCOPE 8 | None | 100% (8/8) | OUT_OF_SCOPE 8 |

## Compile mode

The model writes one to three plans (a Prolog goal over the material's predicates, with the readings it adopts); the engine validates and runs them (engine/compile.pl) and answers ANSWER if every run agrees, AMBIGUOUS if not. In the open configuration forks the plan leaves unfixed are expanded by the engine. Errors get one repair turn. First pass = the first reply alone; final = after repair. No run = no plan survived validation and execution (counted as unparsed). Text material is not offered compile mode.

| model | layer | config | prompt | repr | n | correct (first pass) | correct (final) | repaired | repair cleared errors | no run (final) | first reply status | plans per PLAN reply | PLAN replies with >1 plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 76 | 79% (60/76) | 95% (72/76) | 21% (16/76) | 75% (12/16) | 4 | PLAN 71, OUT_OF_SCOPE 4, PARSE 1 | 1.00 | 0% (0/71) |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 76 | 87% (66/76) | 100% (76/76) | 13% (10/76) | 100% (10/10) | 0 | PLAN 72, OUT_OF_SCOPE 4 | 1.00 | 0% (0/72) |

First-pass errors by kind (all compile records): V not bound 13, list as one value 7, not a predicate of the material 5, no JSON / no plan 1.

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 38 | 89% (34/38) |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 38 | 100% (38/38) |

