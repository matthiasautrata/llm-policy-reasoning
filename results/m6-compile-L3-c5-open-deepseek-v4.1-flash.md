# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 3

45 scored records, 0 API errors left out. Cost $0.5326; prompt tokens 1,041,596, completion tokens 858,580 (reasoning 855,363); mean 128.4 s per call.
Providers: InferenceNet 44, Baidu 1.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 27, length 18.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 21 | 67% (14/21) | 67% (6/9) | 56% (5/9) | 56% (5/9) | – | – | – | – | 0% (0/9) | 7 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 24 | 54% (13/24) | 78% (7/9) | 33% (3/9) | 33% (3/9) | – | – | – | – | 0% (0/9) | 11 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | 3 | 45 | 60% (27/45) | 72% (13/18) | 44% (8/18) | 44% (8/18) | – | – | – | – | 0% (0/18) | 18 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | M-s1 | 24 | 54% (13/24) | 58% (7/12) | 33% (2/6) | 33% (2/6) | – | – | – | – | 0% (0/12) | 11 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | S-s1 | 21 | 67% (14/21) | 100% (6/6) | 50% (6/12) | 50% (6/12) | – | – | – | – | 0% (0/6) | 7 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | M-s1 | formal | 12 | 67% (8/12) | 29,319 | 17,476 | 17,609 | 111.9 | 228.1 | 238.2 | $0.01096 | 4 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | M-s1 | structured | 12 | 42% (5/12) | 35,632 | 23,964 | 24,013 | 156.7 | 312.2 | 327.8 | $0.01521 | 7 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | S-s1 | formal | 9 | 67% (6/9) | 13,542 | 16,484 | 16,534 | 105.4 | 201.7 | 201.7 | $0.01006 | 3 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | S-s1 | structured | 12 | 67% (8/12) | 11,692 | 17,477 | 17,526 | 133.9 | 241.6 | 256.0 | $0.01067 | 4 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 0 | – | 17% (1/6) | – | 100% (6/6) | – | 0% (0/6) | – | 0% (0/6) | 21 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 0 | – | 43% (3/7) | – | 57% (4/7) | – | 0% (0/7) | – | 0% (0/7) | 24 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 13 | 0 | 0 | 0 | 0 | 5 |
| AMBIGUOUS | 0 | 8 | 0 | 0 | 0 | 10 |
| CONFLICT | 0 | 0 | 6 | 0 | 0 | 3 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | Q33 | ANSWER 12, AMBIGUOUS 12 | 3 | 83% (20/24) | ANSWER 12, AMBIGUOUS 8, PARSE 4 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | Q34 | CONFLICT 9, ANSWER 6, AMBIGUOUS 6 | 3 | 33% (7/21) | PARSE 14, CONFLICT 6, ANSWER 1 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 3 | 100% (3/3) | 0% (0/3) | 100% (3/3) | 0 | 0 | 0 | CONFLICT 3 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 6 | 50% (3/6) | 0% (0/6) | 100% (6/6) | 0 | 0 | 0 | CONFLICT 3, PARSE 3 |

## Compile mode

The model writes one to three plans (a Prolog goal over the material's predicates, with the readings it adopts); the engine validates and runs them (engine/compile.pl) and answers ANSWER if every run agrees, AMBIGUOUS if not. In the open configuration forks the plan leaves unfixed are expanded by the engine. Errors get one repair turn. First pass = the first reply alone; final = after repair. No run = no plan survived validation and execution (counted as unparsed). Text material is not offered compile mode.

| model | layer | config | prompt | repr | n | correct (first pass) | correct (final) | repaired | repair cleared errors | no run (final) | first reply status | plans per PLAN reply | PLAN replies with >1 plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 21 | 52% (11/21) | 67% (14/21) | 48% (10/21) | 30% (3/10) | 7 | PARSE 10, PLAN 8, CONFLICT 3 | 1.25 | 25% (2/8) |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 24 | 42% (10/24) | 54% (13/24) | 58% (14/24) | 21% (3/14) | 11 | PARSE 14, PLAN 9, CONFLICT 1 | 1.56 | 33% (3/9) |

First-pass errors by kind (all compile records): no JSON / no plan 24.

AMBIGUOUS keys in compile mode. Surfaced by the model: its plans fix some fork to different readings (it split on the question of interpretation itself). Engine only: AMBIGUOUS came from the engine expanding forks the plans left unfixed. Picked a reading: a single reading fixed for a fork the key depends on, so the engine did not expand it.

| model | layer | config | prompt | repr | n | AMBIGUOUS | readings right | surfaced by model | engine only | picked a reading | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 9 | 56% (5/9) | 56% (5/9) | 56% (5/9) | 0% (0/9) | 44% (4/9) | AMBIGUOUS 5, PARSE 4 |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 9 | 33% (3/9) | 33% (3/9) | 33% (3/9) | 0% (0/9) | 33% (3/9) | PARSE 6, AMBIGUOUS 3 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | open | compile | formal | 7 | 86% (6/7) |
| deepseek/deepseek-v4.1-flash | L3 | open | compile | structured | 8 | 62% (5/8) |

