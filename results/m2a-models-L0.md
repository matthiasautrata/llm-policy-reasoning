# Read mode: deepseek/deepseek-v4.1-flash, qwen/qwen3.8-flash, z-ai/glm-5.3 at layer(s) 0

792 scored records, 0 API errors left out. Cost $1.0167; prompt tokens 4,757,042, completion tokens 1,387,256 (reasoning 1,322,665); mean 25.9 s per call.
Providers: Novita 264, Alibaba 264, Baidu 239, InferenceNet 25.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 787, length 5.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 88 | 51% (45/88) | 100% (24/24) | – | – | 67% (43/64) | 70% (30/43) | 33% (21/64) | – | 0% (0/24) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 88 | 49% (43/88) | 100% (24/24) | – | – | 70% (45/64) | 78% (35/45) | 30% (19/64) | – | 0% (0/24) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 88 | 40% (35/88) | 96% (23/24) | – | – | 81% (52/64) | 79% (41/52) | 19% (12/64) | – | 0% (0/24) | 0 |
| qwen/qwen3.8-flash | L0 | decided | base | formal | 88 | 56% (49/88) | 96% (23/24) | – | – | 58% (37/64) | 80% (28/35) | 41% (26/64) | – | 0% (0/24) | 2 |
| qwen/qwen3.8-flash | L0 | decided | base | structured | 88 | 45% (40/88) | 96% (23/24) | – | – | 72% (46/64) | 82% (37/45) | 27% (17/64) | – | 0% (0/24) | 1 |
| qwen/qwen3.8-flash | L0 | decided | base | text | 88 | 45% (40/88) | 100% (24/24) | – | – | 70% (45/64) | 80% (33/41) | 25% (16/64) | – | 0% (0/24) | 3 |
| z-ai/glm-5.3 | L0 | decided | base | formal | 88 | 40% (35/88) | 96% (23/24) | – | – | 81% (52/64) | 80% (36/45) | 19% (12/64) | – | 0% (0/24) | 0 |
| z-ai/glm-5.3 | L0 | decided | base | structured | 88 | 36% (32/88) | 100% (24/24) | – | – | 88% (56/64) | 80% (41/51) | 12% (8/64) | – | 0% (0/24) | 0 |
| z-ai/glm-5.3 | L0 | decided | base | text | 88 | 30% (26/88) | 92% (22/24) | – | – | 94% (60/64) | 86% (44/51) | 6% (4/64) | – | 0% (0/24) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 0 | 72 | 99% (71/72) | 99% (71/72) | – | – | – | – | – | – | 0% (0/72) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 1 | 144 | 26% (38/144) | – | – | – | 74% (106/144) | 68% (72/106) | 26% (38/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 2 | 24 | 0% (0/24) | – | – | – | 100% (24/24) | 100% (24/24) | 0% (0/24) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 3 | 24 | 58% (14/24) | – | – | – | 42% (10/24) | 100% (10/10) | 58% (14/24) | – | – | 0 |
| qwen/qwen3.8-flash | L0 | decided | base | 0 | 72 | 97% (70/72) | 97% (70/72) | – | – | – | – | – | – | 0% (0/72) | 1 |
| qwen/qwen3.8-flash | L0 | decided | base | 1 | 144 | 27% (39/144) | – | – | – | 69% (100/144) | 75% (70/93) | 27% (39/144) | – | – | 5 |
| qwen/qwen3.8-flash | L0 | decided | base | 2 | 24 | 0% (0/24) | – | – | – | 100% (24/24) | 100% (24/24) | 0% (0/24) | – | – | 0 |
| qwen/qwen3.8-flash | L0 | decided | base | 3 | 24 | 83% (20/24) | – | – | – | 17% (4/24) | 100% (4/4) | 83% (20/24) | – | – | 0 |
| z-ai/glm-5.3 | L0 | decided | base | 0 | 72 | 96% (69/72) | 96% (69/72) | – | – | – | – | – | – | 0% (0/72) | 0 |
| z-ai/glm-5.3 | L0 | decided | base | 1 | 144 | 4% (6/144) | – | – | – | 96% (138/144) | 78% (91/117) | 4% (6/144) | – | – | 0 |
| z-ai/glm-5.3 | L0 | decided | base | 2 | 24 | 0% (0/24) | – | – | – | 100% (24/24) | 100% (24/24) | 0% (0/24) | – | – | 0 |
| z-ai/glm-5.3 | L0 | decided | base | 3 | 24 | 75% (18/24) | – | – | – | 25% (6/24) | 100% (6/6) | 75% (18/24) | – | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | 132 | 48% (63/132) | 97% (35/36) | – | – | 71% (68/96) | 75% (51/68) | 29% (28/96) | – | 0% (0/36) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | 132 | 45% (60/132) | 100% (36/36) | – | – | 75% (72/96) | 76% (55/72) | 25% (24/96) | – | 0% (0/36) | 0 |
| qwen/qwen3.8-flash | L0 | decided | base | M-s1 | 132 | 50% (66/132) | 97% (35/36) | – | – | 65% (62/96) | 80% (48/60) | 32% (31/96) | – | 0% (0/36) | 4 |
| qwen/qwen3.8-flash | L0 | decided | base | S-s1 | 132 | 48% (63/132) | 97% (35/36) | – | – | 69% (66/96) | 82% (50/61) | 29% (28/96) | – | 0% (0/36) | 2 |
| z-ai/glm-5.3 | L0 | decided | base | M-s1 | 132 | 33% (43/132) | 92% (33/36) | – | – | 90% (86/96) | 81% (62/77) | 10% (10/96) | – | 0% (0/36) | 0 |
| z-ai/glm-5.3 | L0 | decided | base | S-s1 | 132 | 38% (50/132) | 100% (36/36) | – | – | 85% (82/96) | 84% (59/70) | 15% (14/96) | – | 0% (0/36) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 43 | 95% (41/43) | 4% (1/24) | 98% (42/43) | 4% (1/24) | 2% (1/43) | 0% (0/24) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 45 | 93% (42/45) | 29% (7/24) | 98% (44/45) | 42% (10/24) | 2% (1/45) | 0% (0/24) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 52 | 87% (45/52) | 0% (0/23) | 94% (49/52) | 9% (2/23) | 0% (0/52) | 0% (0/23) | – | – | – |
| qwen/qwen3.8-flash | L0 | decided | base | formal | 35 | 97% (34/35) | 43% (10/23) | 100% (35/35) | 65% (15/23) | 0% (0/35) | 0% (0/23) | – | – | – |
| qwen/qwen3.8-flash | L0 | decided | base | structured | 45 | 100% (45/45) | 57% (13/23) | 100% (45/45) | 70% (16/23) | 0% (0/45) | 0% (0/23) | – | – | – |
| qwen/qwen3.8-flash | L0 | decided | base | text | 41 | 100% (41/41) | 54% (13/24) | 100% (41/41) | 67% (16/24) | 0% (0/41) | 0% (0/24) | – | – | – |
| z-ai/glm-5.3 | L0 | decided | base | formal | 45 | 47% (21/45) | 0% (0/23) | 49% (22/45) | 4% (1/23) | 4% (2/45) | 0% (0/23) | – | – | – |
| z-ai/glm-5.3 | L0 | decided | base | structured | 51 | 35% (18/51) | 4% (1/24) | 43% (22/51) | 4% (1/24) | 6% (3/51) | 0% (0/24) | – | – | – |
| z-ai/glm-5.3 | L0 | decided | base | text | 51 | 43% (22/51) | 0% (0/22) | 45% (23/51) | 5% (1/22) | 6% (3/51) | 0% (0/22) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | 24 | 0% (0/24) | 4% (1/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | 24 | 42% (10/24) | 100% (14/14) | ANSWER 14, UNDERDETERMINED 10 |
| qwen/qwen3.8-flash | L0 | decided | base | Q11 | 24 | 0% (0/24) | 5% (1/22) | ANSWER 22, AMBIGUOUS 2 |
| qwen/qwen3.8-flash | L0 | decided | base | Q17 | 24 | 25% (6/24) | 100% (18/18) | ANSWER 18, UNDERDETERMINED 6 |
| z-ai/glm-5.3 | L0 | decided | base | Q11 | 24 | 0% (0/24) | 0% (0/23) | ANSWER 23, AMBIGUOUS 1 |
| z-ai/glm-5.3 | L0 | decided | base | Q17 | 24 | 4% (1/24) | 100% (23/23) | ANSWER 23, UNDERDETERMINED 1 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 72 | 0 | 0 | 0 | 0 | 0 |
| UNDERDETERMINED | 140 | 0 | 0 | 52 | 0 | 0 |

**qwen/qwen3.8-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 71 | 0 | 0 | 0 | 0 | 1 |
| UNDERDETERMINED | 121 | 7 | 0 | 59 | 0 | 5 |

**z-ai/glm-5.3**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 72 | 0 | 0 | 0 | 0 | 0 |
| UNDERDETERMINED | 147 | 21 | 0 | 24 | 0 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q01 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q03 | ANSWER 24 | 0 | 96% (23/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q05 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q13 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q14 | UNDERDETERMINED 24 | 1 | 50% (12/24) | ANSWER 12, UNDERDETERMINED 12 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q15 | UNDERDETERMINED 24 | 1 | 54% (13/24) | UNDERDETERMINED 13, ANSWER 11 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q16 | UNDERDETERMINED 24 | 1 | 12% (3/24) | ANSWER 21, UNDERDETERMINED 3 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | UNDERDETERMINED 24 | 1 | 42% (10/24) | ANSWER 14, UNDERDETERMINED 10 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q22 | UNDERDETERMINED 24 | 2 | 0% (0/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q31 | UNDERDETERMINED 24 | 3 | 58% (14/24) | UNDERDETERMINED 14, ANSWER 10 |
| qwen/qwen3.8-flash | L0 | decided | base | Q01 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| qwen/qwen3.8-flash | L0 | decided | base | Q03 | ANSWER 24 | 0 | 96% (23/24) | ANSWER 24 |
| qwen/qwen3.8-flash | L0 | decided | base | Q05 | ANSWER 24 | 0 | 96% (23/24) | ANSWER 23, PARSE 1 |
| qwen/qwen3.8-flash | L0 | decided | base | Q11 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 22, AMBIGUOUS 2 |
| qwen/qwen3.8-flash | L0 | decided | base | Q13 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 24 |
| qwen/qwen3.8-flash | L0 | decided | base | Q14 | UNDERDETERMINED 24 | 1 | 46% (11/24) | ANSWER 12, UNDERDETERMINED 11, PARSE 1 |
| qwen/qwen3.8-flash | L0 | decided | base | Q15 | UNDERDETERMINED 24 | 1 | 79% (19/24) | UNDERDETERMINED 19, ANSWER 2, PARSE 2, AMBIGUOUS 1 |
| qwen/qwen3.8-flash | L0 | decided | base | Q16 | UNDERDETERMINED 24 | 1 | 12% (3/24) | ANSWER 15, AMBIGUOUS 4, UNDERDETERMINED 3, PARSE 2 |
| qwen/qwen3.8-flash | L0 | decided | base | Q17 | UNDERDETERMINED 24 | 1 | 25% (6/24) | ANSWER 18, UNDERDETERMINED 6 |
| qwen/qwen3.8-flash | L0 | decided | base | Q22 | UNDERDETERMINED 24 | 2 | 0% (0/24) | ANSWER 24 |
| qwen/qwen3.8-flash | L0 | decided | base | Q31 | UNDERDETERMINED 24 | 3 | 83% (20/24) | UNDERDETERMINED 20, ANSWER 4 |
| z-ai/glm-5.3 | L0 | decided | base | Q01 | ANSWER 24 | 0 | 96% (23/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q03 | ANSWER 24 | 0 | 92% (22/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q05 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q11 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 23, AMBIGUOUS 1 |
| z-ai/glm-5.3 | L0 | decided | base | Q13 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q14 | UNDERDETERMINED 24 | 1 | 12% (3/24) | ANSWER 21, UNDERDETERMINED 3 |
| z-ai/glm-5.3 | L0 | decided | base | Q15 | UNDERDETERMINED 24 | 1 | 8% (2/24) | AMBIGUOUS 20, UNDERDETERMINED 2, ANSWER 2 |
| z-ai/glm-5.3 | L0 | decided | base | Q16 | UNDERDETERMINED 24 | 1 | 0% (0/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q17 | UNDERDETERMINED 24 | 1 | 4% (1/24) | ANSWER 23, UNDERDETERMINED 1 |
| z-ai/glm-5.3 | L0 | decided | base | Q22 | UNDERDETERMINED 24 | 2 | 0% (0/24) | ANSWER 24 |
| z-ai/glm-5.3 | L0 | decided | base | Q31 | UNDERDETERMINED 24 | 3 | 75% (18/24) | UNDERDETERMINED 18, ANSWER 6 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 44 | 75% (33/44) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 44 | 84% (37/44) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 44 | 82% (36/44) |
| qwen/qwen3.8-flash | L0 | decided | base | formal | 44 | 80% (35/44) |
| qwen/qwen3.8-flash | L0 | decided | base | structured | 44 | 75% (33/44) |
| qwen/qwen3.8-flash | L0 | decided | base | text | 44 | 80% (35/44) |
| z-ai/glm-5.3 | L0 | decided | base | formal | 44 | 86% (38/44) |
| z-ai/glm-5.3 | L0 | decided | base | structured | 44 | 95% (42/44) |
| z-ai/glm-5.3 | L0 | decided | base | text | 44 | 93% (41/44) |

