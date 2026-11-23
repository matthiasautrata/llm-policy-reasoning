# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 0

224 scored records, 0 API errors left out. Cost $0.4838; prompt tokens 2,471,254, completion tokens 780,868 (reasoning 756,331); mean 27.6 s per call.
Providers: InferenceNet 218, Baidu 6.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 224.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | formal | 74 | 55% (41/74) | 100% (30/30) | – | – | 75% (33/44) | 67% (22/33) | 25% (11/44) | – | 0% (0/30) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | structured | 150 | 57% (86/150) | 100% (30/30) | – | – | 39% (45/114) | 78% (35/45) | 61% (73/120) | 100% (6/6) | 0% (0/30) | 2 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | 0 | 60 | 100% (60/60) | 100% (60/60) | – | – | – | – | – | – | 0% (0/60) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | 1 | 73 | 12% (9/73) | – | – | – | 78% (57/73) | 68% (39/57) | 19% (14/73) | – | – | 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | 2 | 49 | 53% (26/49) | – | – | – | 27% (13/49) | 92% (12/13) | 73% (36/49) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | 3 | 36 | 72% (26/36) | – | – | – | 22% (8/36) | 75% (6/8) | 78% (28/36) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | None | 6 | 100% (6/6) | – | – | – | – | – | 100% (6/6) | 100% (6/6) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | M-s1 | 224 | 57% (127/224) | 100% (60/60) | – | – | 49% (78/158) | 73% (57/78) | 51% (84/164) | 100% (6/6) | 0% (0/60) | 2 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | M-s1 | formal | 74 | 55% (41/74) | 10,494 | 3,016 | 3,109 | 22.4 | 57.2 | 132.4 | $0.00198 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | M-s1 | structured | 150 | 57% (86/150) | 11,298 | 3,555 | 3,672 | 30.1 | 78.6 | 283.9 | $0.00225 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | formal | 33 | 97% (32/33) | 30% (9/30) | 100% (33/33) | 63% (19/30) | 9% (3/33) | 0% (0/30) | 0% (0/33) | 0% (0/30) | 74 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | structured | 45 | 100% (45/45) | 37% (11/30) | 100% (45/45) | 43% (13/30) | 2% (1/45) | 0% (0/30) | 0% (0/45) | 0% (0/30) | 150 |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q11 | 12 | 0% (0/12) | 0% (0/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q17 | 6 | 0% (0/6) | 100% (6/6) | ANSWER 6 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 60 | 0 | 0 | 0 | 0 | 0 |
| UNDERDETERMINED | 78 | 0 | 0 | 61 | 17 | 2 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 6 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q01 | ANSWER 12 | 0 | 100% (12/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q02 | ANSWER 12 | 0 | 100% (12/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q03 | ANSWER 12 | 0 | 100% (12/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q04 | ANSWER 12 | 0 | 100% (12/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q05 | ANSWER 12 | 0 | 100% (12/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q11 | UNDERDETERMINED 12 | 1 | 0% (0/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q12 | UNDERDETERMINED 12 | 1 | 58% (7/12) | UNDERDETERMINED 7, ANSWER 5 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q13 | UNDERDETERMINED 12 | 1 | 0% (0/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q14 | UNDERDETERMINED 12 | 1 | 17% (2/12) | ANSWER 10, UNDERDETERMINED 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q15 | UNDERDETERMINED 10 | 1 | 0% (0/10) | OUT_OF_SCOPE 5, ANSWER 4, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q16 | UNDERDETERMINED 9 | 1 | 0% (0/9) | ANSWER 8, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q17 | UNDERDETERMINED 6 | 1 | 0% (0/6) | ANSWER 6 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q21 | UNDERDETERMINED 12 | 2 | 100% (12/12) | UNDERDETERMINED 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q22 | UNDERDETERMINED 12 | 2 | 0% (0/12) | ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q23 | UNDERDETERMINED 7 | 2 | 71% (5/7) | UNDERDETERMINED 5, OUT_OF_SCOPE 1, ANSWER 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q24 | UNDERDETERMINED 6 | 2 | 50% (3/6) | UNDERDETERMINED 3, OUT_OF_SCOPE 3 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q25 | UNDERDETERMINED 6 | 2 | 100% (6/6) | UNDERDETERMINED 6 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q26 | UNDERDETERMINED 6 | 2 | 0% (0/6) | OUT_OF_SCOPE 6 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q31 | UNDERDETERMINED 6 | 3 | 50% (3/6) | UNDERDETERMINED 3, ANSWER 3 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q32 | UNDERDETERMINED 6 | 3 | 33% (2/6) | ANSWER 4, UNDERDETERMINED 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q33 | UNDERDETERMINED 6 | 3 | 83% (5/6) | UNDERDETERMINED 5, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q34 | UNDERDETERMINED 6 | 3 | 100% (6/6) | UNDERDETERMINED 6 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q35 | UNDERDETERMINED 6 | 3 | 83% (5/6) | UNDERDETERMINED 5, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q36 | UNDERDETERMINED 6 | 3 | 83% (5/6) | UNDERDETERMINED 5, ANSWER 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | Q91 | OUT_OF_SCOPE 6 | None | 100% (6/6) | OUT_OF_SCOPE 6 |

## Compile mode

The model writes one to three plans (a Prolog goal over the material's predicates, with the readings it adopts); the engine validates and runs them (engine/compile.pl) and answers ANSWER if every run agrees, AMBIGUOUS if not. In the open configuration forks the plan leaves unfixed are expanded by the engine. Errors get one repair turn. First pass = the first reply alone; final = after repair. No run = no plan survived validation and execution (counted as unparsed). Text material is not offered compile mode.

| model | layer | config | prompt | repr | n | correct (first pass) | correct (final) | repaired | repair cleared errors | no run (final) | first reply status | plans per PLAN reply | PLAN replies with >1 plan |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | formal | 74 | 50% (37/74) | 55% (41/74) | 16% (12/74) | 100% (12/12) | 0 | PLAN 63, UNDERDETERMINED 11 | 1.10 | 10% (6/63) |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | structured | 150 | 54% (81/150) | 57% (86/150) | 14% (21/150) | 90% (19/21) | 2 | PLAN 81, UNDERDETERMINED 48, OUT_OF_SCOPE 18, PARSE 3 | 1.15 | 14% (11/81) |

First-pass errors by kind (all compile records): readings 35, list as one value 10, no JSON / no plan 3, V not bound 1, not a predicate of the material 1, several values 1.

UNDERDETERMINED keys in compile mode (overreach). First reply: blocked = a plan called a predicate the layer does not define (an existence error, reported as "not a predicate of the material"); inlined = a plan ran and gave a value, the model computing the missing concept from what the layer has; abstained = UNDERDETERMINED or OUT_OF_SCOPE. Final: after the repair turn. Flagged = the inlined plan uses aggregation or arithmetic (engine/compile.pl constructs). = later key: the inlined value equals the key at the layer that defines the concept. Control: ANSWER keys of the same cells, share whose final plan is flagged (the flag is a report, not a rejection).

| model | layer | config | prompt | repr | n | first: blocked | first: inlined | first: abstained | final: inlined | final: abstained | final: no run | inlined, flagged | inlined = later key | control: ANSWER keys flagged |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | formal | 44 | 0% (0/44) | 57% (25/44) | 25% (11/44) | 75% (33/44) | 25% (11/44) | 0% (0/44) | 39% (13/33) | 67% (22/33) | 20% (6/30) |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | structured | 114 | 1% (1/114) | 32% (36/114) | 53% (60/114) | 39% (45/114) | 59% (67/114) | 2% (2/114) | 47% (21/45) | 78% (35/45) | 20% (6/30) |

Final outcome per template (UNDERDETERMINED keys): Q11 inlined 12; Q12 abstained 7, inlined 5; Q13 inlined 12; Q14 inlined 10, abstained 2; Q15 abstained 5, inlined 4, other 1; Q16 inlined 8, other 1; Q17 inlined 6; Q21 abstained 12; Q22 inlined 12; Q23 abstained 6, inlined 1; Q24 abstained 6; Q25 abstained 6; Q26 abstained 6; Q31 abstained 3, inlined 3; Q32 inlined 4, abstained 2; Q33 abstained 6; Q34 abstained 6; Q35 abstained 6; Q36 abstained 5, inlined 1.

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | formal | 24 | 96% (23/24) |
| deepseek/deepseek-v4.1-flash | L0 | decided | compile | structured | 50 | 72% (36/50) |

