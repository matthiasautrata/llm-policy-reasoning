# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 2

112 scored records, 0 API errors left out. Cost $0.1913; prompt tokens 1,532,600, completion tokens 405,701 (reasoning 391,821); mean 28.4 s per call.
Providers: DeepInfra 112.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 112.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | formal | 56 | 88% (49/56) | 100% (13/13) | 91% (39/43) | 84% (36/43) | – | – | – | – | 0% (0/13) | 1 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | structured | 56 | 95% (53/56) | 100% (13/13) | 100% (43/43) | 93% (40/43) | – | – | – | – | 0% (0/13) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | 1 | 96 | 90% (86/96) | 100% (10/10) | 95% (82/86) | 88% (76/86) | – | – | – | – | 0% (0/10) | 1 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | 2 | 16 | 100% (16/16) | 100% (16/16) | – | – | – | – | – | – | 0% (0/16) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | M-s1 | 28 | 89% (25/28) | 100% (6/6) | 95% (21/22) | 86% (19/22) | – | – | – | – | 0% (0/6) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s1 | 28 | 89% (25/28) | 100% (6/6) | 95% (21/22) | 86% (19/22) | – | – | – | – | 0% (0/6) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s2 | 28 | 93% (26/28) | 100% (8/8) | 100% (20/20) | 90% (18/20) | – | – | – | – | 0% (0/8) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s3 | 28 | 93% (26/28) | 100% (6/6) | 91% (20/22) | 91% (20/22) | – | – | – | – | 0% (0/6) | 1 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | M-s1 | formal | 14 | 86% (12/14) | 26,043 | 4,699 | 4,835 | 38.8 | 77.7 | 82.8 | $0.00233 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | M-s1 | structured | 14 | 93% (13/14) | 24,860 | 5,087 | 5,218 | 37.5 | 62.9 | 204.6 | $0.00250 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s1 | formal | 14 | 86% (12/14) | 10,923 | 3,837 | 3,973 | 32.0 | 74.8 | 92.4 | $0.00197 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s1 | structured | 14 | 93% (13/14) | 8,257 | 3,449 | 3,554 | 26.8 | 80.5 | 88.9 | $0.00161 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s2 | formal | 14 | 93% (13/14) | 10,924 | 3,295 | 3,418 | 25.0 | 46.6 | 94.7 | $0.00156 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s2 | structured | 14 | 93% (13/14) | 9,305 | 2,414 | 2,533 | 20.9 | 48.7 | 61.4 | $0.00118 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s3 | formal | 14 | 86% (12/14) | 10,363 | 2,774 | 2,908 | 25.1 | 61.7 | 66.5 | $0.00134 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | S-s3 | structured | 14 | 100% (14/14) | 8,797 | 2,432 | 2,540 | 21.1 | 39.6 | 58.4 | $0.00117 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | formal | 0 | – | 85% (11/13) | – | 100% (13/13) | – | 0% (0/13) | – | 0% (0/13) | 56 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | structured | 0 | – | 85% (11/13) | – | 92% (12/13) | – | 0% (0/13) | – | 0% (0/13) | 56 |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q11 | 16 | 100% (16/16) | – | AMBIGUOUS 16 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q17 | 16 | 81% (13/16) | – | AMBIGUOUS 13, ANSWER 3 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 26 | 0 | 0 | 0 | 0 | 0 |
| AMBIGUOUS | 3 | 82 | 0 | 0 | 0 | 1 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q11 | AMBIGUOUS 16 | 1 | 100% (16/16) | AMBIGUOUS 16 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q12 | AMBIGUOUS 16 | 1 | 62% (10/16) | AMBIGUOUS 16 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q13 | AMBIGUOUS 16 | 1 | 94% (15/16) | AMBIGUOUS 15, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q14 | AMBIGUOUS 8, ANSWER 8 | 1 | 100% (16/16) | AMBIGUOUS 8, ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q15 | AMBIGUOUS 14, ANSWER 2 | 1 | 100% (16/16) | AMBIGUOUS 14, ANSWER 2 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q17 | AMBIGUOUS 16 | 1 | 81% (13/16) | AMBIGUOUS 13, ANSWER 3 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | Q22 | ANSWER 16 | 2 | 100% (16/16) | ANSWER 16 |

## Compile mode

The model writes one to three plans (a Prolog goal over the material's predicates, with the readings it adopts); the engine validates and runs them (engine/compile.pl) and answers ANSWER if every run agrees, AMBIGUOUS if not. In the open configuration forks the plan leaves unfixed are expanded by the engine. Errors get one repair turn. First pass = the first reply alone; final = after repair. No run = no plan survived validation and execution (counted as unparsed). Text material is not offered compile mode.

| model | layer | config | prompt | repr | n | correct (first pass) | correct (final) | repaired | repair cleared errors | no run (final) | first reply status | plans per PLAN reply | PLAN replies with >1 plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | formal | 56 | 61% (34/56) | 88% (49/56) | 36% (20/56) | 95% (19/20) | 1 | PLAN 56 | 1.86 | 79% (44/56) |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | structured | 56 | 77% (43/56) | 95% (53/56) | 23% (13/56) | 92% (12/13) | 0 | PLAN 55, PARSE 1 | 1.85 | 78% (43/55) |

First-pass errors by kind (all compile records): V not bound 30, list as one value 28, too many plans 3, no JSON / no plan 1.

AMBIGUOUS keys in compile mode. Surfaced by the model: its plans fix some fork to different readings (it split on the question of interpretation itself). Engine only: AMBIGUOUS came from the engine expanding forks the plans left unfixed. Picked a reading: a single reading fixed for a fork the key depends on, so the engine did not expand it.

| model | layer | config | prompt | repr | n | AMBIGUOUS | readings right | surfaced by model | engine only | picked a reading | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | formal | 43 | 91% (39/43) | 84% (36/43) | 93% (40/43) | 0% (0/43) | 37% (16/43) | AMBIGUOUS 39, ANSWER 3, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | structured | 43 | 100% (43/43) | 93% (40/43) | 100% (43/43) | 0% (0/43) | 26% (11/43) | AMBIGUOUS 43 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | open | compile | formal | 0 | – |
| deepseek/deepseek-v4.1-flash | L2 | open | compile | structured | 0 | – |

