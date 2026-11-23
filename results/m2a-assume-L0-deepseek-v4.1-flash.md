# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 0

1188 scored records, 99 API errors left out. Cost $0.7405; prompt tokens 2,619,648, completion tokens 1,726,459 (reasoning 1,633,052); mean 11.0 s per call.
Providers: Baidu 562, DeepInfra 332, InferenceNet 294.
Status spelled with an accepted alias (UNDETERMINED): 7.
Finish reasons: stop 1188.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | formal | 198 | 58% (115/198) | 100% (54/54) | – | – | 58% (83/144) | 74% (60/81) | 42% (61/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | structured | 198 | 56% (111/198) | 100% (54/54) | – | – | 60% (87/144) | 78% (67/86) | 40% (57/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | text | 198 | 49% (98/198) | 100% (54/54) | – | – | 69% (100/144) | 80% (79/99) | 31% (44/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 198 | 56% (110/198) | 100% (54/54) | – | – | 61% (88/144) | 75% (66/88) | 39% (56/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 198 | 47% (93/198) | 100% (54/54) | – | – | 72% (104/144) | 77% (80/104) | 28% (40/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 198 | 46% (91/198) | 100% (54/54) | – | – | 74% (106/144) | 78% (83/106) | 26% (38/144) | – | 0% (0/54) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | 0 | 162 | 100% (162/162) | 100% (162/162) | – | – | – | – | – | – | 0% (0/162) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | 1 | 324 | 41% (133/324) | – | – | – | 59% (191/324) | 70% (131/187) | 41% (133/324) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | 2 | 54 | 0% (0/54) | – | – | – | 100% (54/54) | 100% (54/54) | 0% (0/54) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | 3 | 54 | 54% (29/54) | – | – | – | 46% (25/54) | 84% (21/25) | 54% (29/54) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 0 | 162 | 100% (162/162) | 100% (162/162) | – | – | – | – | – | – | 0% (0/162) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 1 | 324 | 32% (104/324) | – | – | – | 67% (218/324) | 70% (152/218) | 33% (106/324) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 2 | 54 | 0% (0/54) | – | – | – | 100% (54/54) | 100% (54/54) | 0% (0/54) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 3 | 54 | 52% (28/54) | – | – | – | 48% (26/54) | 88% (23/26) | 52% (28/54) | – | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | S-s1 | 198 | 55% (109/198) | 100% (54/54) | – | – | 62% (89/144) | 77% (68/88) | 38% (55/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | S-s2 | 198 | 57% (112/198) | 100% (54/54) | – | – | 60% (86/144) | 76% (65/85) | 40% (58/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | S-s3 | 198 | 52% (103/198) | 100% (54/54) | – | – | 66% (95/144) | 78% (73/93) | 34% (49/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | 198 | 45% (89/198) | 100% (54/54) | – | – | 76% (109/144) | 78% (85/109) | 24% (35/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | 198 | 54% (106/198) | 100% (54/54) | – | – | 63% (91/144) | 76% (69/91) | 37% (53/144) | – | 0% (0/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | 198 | 50% (99/198) | 100% (54/54) | – | – | 68% (98/144) | 77% (75/98) | 32% (46/144) | – | 0% (0/54) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | formal | 81 | 95% (77/81) | 4% (2/54) | 100% (81/81) | 94% (51/54) | 1% (1/81) | 0% (0/54) | 95% (77/81) | 15% (8/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | structured | 86 | 92% (79/86) | 33% (18/54) | 100% (86/86) | 87% (47/54) | 2% (2/86) | 0% (0/54) | 93% (80/86) | 39% (21/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | text | 99 | 93% (92/99) | 13% (7/54) | 100% (99/99) | 91% (49/54) | 2% (2/99) | 0% (0/54) | 96% (95/99) | 17% (9/54) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 88 | 93% (82/88) | 9% (5/54) | 99% (87/88) | 19% (10/54) | 0% (0/88) | 0% (0/54) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 104 | 93% (97/104) | 13% (7/54) | 96% (100/104) | 26% (14/54) | 1% (1/104) | 0% (0/54) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 106 | 86% (91/106) | 7% (4/54) | 95% (101/106) | 9% (5/54) | 0% (0/106) | 0% (0/54) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q11 | 54 | 4% (2/54) | 0% (0/50) | ANSWER 50, UNDERDETERMINED 2, AMBIGUOUS 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q17 | 54 | 70% (38/54) | 100% (16/16) | UNDERDETERMINED 38, ANSWER 16 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | 54 | 0% (0/54) | 0% (0/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | 54 | 54% (29/54) | 100% (25/25) | UNDERDETERMINED 29, ANSWER 25 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 324 | 0 | 0 | 0 | 0 | 0 |
| UNDERDETERMINED | 564 | 4 | 0 | 294 | 2 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q01 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q03 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q05 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q11 | UNDERDETERMINED 54 | 1 | 4% (2/54) | ANSWER 50, UNDERDETERMINED 2, AMBIGUOUS 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q13 | UNDERDETERMINED 54 | 1 | 2% (1/54) | ANSWER 53, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q14 | UNDERDETERMINED 54 | 1 | 67% (36/54) | UNDERDETERMINED 36, ANSWER 18 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q15 | UNDERDETERMINED 54 | 1 | 83% (45/54) | UNDERDETERMINED 45, ANSWER 7, AMBIGUOUS 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q16 | UNDERDETERMINED 54 | 1 | 20% (11/54) | ANSWER 43, UNDERDETERMINED 11 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q17 | UNDERDETERMINED 54 | 1 | 70% (38/54) | UNDERDETERMINED 38, ANSWER 16 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q22 | UNDERDETERMINED 54 | 2 | 0% (0/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | Q31 | UNDERDETERMINED 54 | 3 | 54% (29/54) | UNDERDETERMINED 29, ANSWER 25 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q01 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q03 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q05 | ANSWER 54 | 0 | 100% (54/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | UNDERDETERMINED 54 | 1 | 0% (0/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q13 | UNDERDETERMINED 54 | 1 | 0% (0/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q14 | UNDERDETERMINED 54 | 1 | 65% (35/54) | UNDERDETERMINED 35, ANSWER 19 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q15 | UNDERDETERMINED 54 | 1 | 65% (35/54) | UNDERDETERMINED 35, ANSWER 17, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q16 | UNDERDETERMINED 54 | 1 | 9% (5/54) | ANSWER 49, UNDERDETERMINED 5 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | UNDERDETERMINED 54 | 1 | 54% (29/54) | UNDERDETERMINED 29, ANSWER 25 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q22 | UNDERDETERMINED 54 | 2 | 0% (0/54) | ANSWER 54 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q31 | UNDERDETERMINED 54 | 3 | 52% (28/54) | UNDERDETERMINED 28, ANSWER 26 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | formal | 66 | 74% (49/66) |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | structured | 66 | 79% (52/66) |
| deepseek/deepseek-v4.1-flash | L0 | decided | assume | text | 66 | 71% (47/66) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 66 | 71% (47/66) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 66 | 82% (54/66) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 66 | 76% (50/66) |

