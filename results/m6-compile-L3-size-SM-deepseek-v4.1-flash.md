# Compile mode: deepseek/deepseek-v4.1-flash at layer(s) 3

152 scored records, 0 API errors left out. Cost $0.1201; prompt tokens 2,438,613, completion tokens 151,230 (reasoning 142,425); mean 9.8 s per call.
Providers: InferenceNet 147, DeepInfra 3, Baidu 2.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 152.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 76 | 99% (75/76) | 99% (71/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 76 | 99% (75/76) | 99% (71/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 1 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 0 | 40 | 98% (39/40) | 98% (39/40) | – | – | – | – | – | – | 0% (0/40) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 1 | 56 | 98% (55/56) | 98% (55/56) | – | – | – | – | – | – | 0% (0/56) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | 2 | 48 | 100% (48/48) | 100% (48/48) | – | – | – | – | – | – | 0% (0/48) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | None | 8 | 100% (8/8) | – | – | – | – | – | 100% (8/8) | 100% (8/8) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | 76 | 99% (75/76) | 99% (71/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | 76 | 99% (75/76) | 99% (71/72) | – | – | – | – | 100% (4/4) | 100% (4/4) | 0% (0/72) | 1 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | formal | 38 | 97% (37/38) | 23,389 | 979 | 1,043 | 8.9 | 22.8 | 29.3 | $0.00096 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | M-s1 | structured | 38 | 100% (38/38) | 22,024 | 937 | 997 | 10.3 | 26.1 | 51.4 | $0.00091 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | formal | 38 | 100% (38/38) | 10,115 | 773 | 829 | 9.3 | 21.1 | 55.8 | $0.00059 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | S-s1 | structured | 38 | 97% (37/38) | 8,646 | 1,059 | 1,111 | 10.5 | 29.9 | 41.9 | $0.00070 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 0 | – | 54% (38/71) | – | 79% (56/71) | – | 0% (0/71) | – | 0% (0/71) | 76 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 0 | – | 55% (39/71) | – | 79% (56/71) | – | 1% (1/71) | – | 0% (0/71) | 76 |

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
| ANSWER | 142 | 0 | 0 | 0 | 0 | 2 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 8 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q01 | ANSWER 8 | 0 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q02 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q03 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q04 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q05 | ANSWER 8 | 0 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q11 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q12 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q13 | ANSWER 8 | 1 | 88% (7/8) | ANSWER 7, PARSE 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q14 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q15 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | Q16 | ANSWER 8 | 1 | 100% (8/8) | ANSWER 8 |
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
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 76 | 80% (61/76) | 99% (75/76) | 20% (15/76) | 93% (14/15) | 1 | PLAN 72, OUT_OF_SCOPE 4 | 1.00 | 0% (0/72) |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 76 | 89% (68/76) | 99% (75/76) | 11% (8/76) | 88% (7/8) | 1 | PLAN 72, OUT_OF_SCOPE 4 | 1.00 | 0% (0/72) |

First-pass errors by kind (all compile records): V not bound 10, list as one value 9, not a predicate of the material 4.

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | formal | 0 | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | compile | structured | 0 | – |

