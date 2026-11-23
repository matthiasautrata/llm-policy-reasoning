# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 3

96 scored records, 0 API errors left out. Cost $0.2996; prompt tokens 1,196,840, completion tokens 468,332 (reasoning 462,343); mean 39.8 s per call.
Providers: InferenceNet 93, Baidu 3.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 96.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 48 | 98% (47/48) | 97% (32/33) | – | – | – | – | – | – | 0% (0/33) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 48 | 90% (43/48) | 88% (29/33) | – | – | – | – | – | – | 0% (0/33) | 4 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 3 | 96 | 94% (90/96) | 92% (61/66) | – | – | – | – | – | – | 0% (0/66) | 5 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | 24 | 88% (21/24) | 89% (16/18) | – | – | – | – | – | – | 0% (0/18) | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | 24 | 100% (24/24) | 100% (18/18) | – | – | – | – | – | – | 0% (0/18) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s2 | 24 | 92% (22/24) | 89% (16/18) | – | – | – | – | – | – | 0% (0/18) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s3 | 24 | 96% (23/24) | 92% (11/12) | – | – | – | – | – | – | 0% (0/12) | 1 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | formal | 12 | 92% (11/12) | 22,060 | 4,318 | 4,382 | 26.6 | 44.3 | 79.2 | $0.00296 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | structured | 12 | 83% (10/12) | 23,251 | 6,206 | 6,284 | 49.0 | 104.1 | 114.5 | $0.00401 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | formal | 12 | 100% (12/12) | 9,458 | 3,435 | 3,479 | 44.4 | 114.7 | 126.1 | $0.00228 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | structured | 12 | 100% (12/12) | 9,131 | 5,134 | 5,191 | 44.5 | 92.8 | 93.8 | $0.00327 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s2 | formal | 12 | 100% (12/12) | 9,494 | 3,681 | 3,779 | 29.1 | 56.6 | 61.9 | $0.00240 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s2 | structured | 12 | 83% (10/12) | 8,470 | 5,361 | 5,427 | 34.2 | 57.7 | 64.9 | $0.00343 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s3 | formal | 12 | 100% (12/12) | 8,730 | 4,126 | 4,159 | 46.1 | 112.4 | 140.3 | $0.00267 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s3 | structured | 12 | 92% (11/12) | 9,144 | 6,267 | 6,327 | 44.5 | 98.7 | 120.7 | $0.00393 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 0 | – | 75% (24/32) | – | 97% (31/32) | – | 0% (0/32) | – | 0% (0/32) | 48 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 0 | – | 72% (21/29) | – | 100% (29/29) | – | 0% (0/29) | – | 0% (0/29) | 48 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 61 | 0 | 1 | 0 | 0 | 4 |
| CONFLICT | 0 | 0 | 29 | 0 | 0 | 1 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q33 | ANSWER 42, CONFLICT 6 | 3 | 100% (48/48) | ANSWER 42, CONFLICT 6 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q34 | ANSWER 24, CONFLICT 24 | 3 | 88% (42/48) | CONFLICT 24, ANSWER 19, PARSE 5 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 15 | 100% (15/15) | 0% (0/15) | 100% (15/15) | 0 | 0 | 3 | CONFLICT 15 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 15 | 93% (14/15) | 0% (0/15) | 100% (15/15) | 0 | 0 | 6 | CONFLICT 14, PARSE 1 |

## Compile mode

The model writes one to three plans (a Prolog goal over the material's predicates, with the readings it adopts); the engine validates and runs them (engine/compile.pl) and answers ANSWER if every run agrees, AMBIGUOUS if not. In the open configuration forks the plan leaves unfixed are expanded by the engine. Errors get one repair turn. First pass = the first reply alone; final = after repair. No run = no plan survived validation and execution (counted as unparsed). Text material is not offered compile mode.

| model | layer | config | prompt | repr | n | correct (first pass) | correct (final) | repaired | repair cleared errors | no run (final) | first reply status | plans per PLAN reply | PLAN replies with >1 plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 48 | 92% (44/48) | 98% (47/48) | 8% (4/48) | 75% (3/4) | 1 | PLAN 36, CONFLICT 12 | 1.00 | 0% (0/36) |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 48 | 83% (40/48) | 90% (43/48) | 15% (7/48) | 43% (3/7) | 4 | PLAN 39, CONFLICT 9 | 1.00 | 0% (0/39) |

First-pass errors by kind (all compile records): list as one value 8, V not bound 3.

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 16 | 94% (15/16) |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 16 | 75% (12/16) |

