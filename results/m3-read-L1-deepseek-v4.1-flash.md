# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 0, 1

2880 scored records, 0 API errors left out. Cost $1.0141; prompt tokens 13,545,936, completion tokens 2,656,469 (reasoning 2,492,284); mean 7.1 s per call.
Providers: DeepInfra 1636, Baidu 1170, InferenceNet 74.
Status spelled with an accepted alias (UNDETERMINED): 24.
Finish reasons: stop 2880.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 408 | 70% (285/408) | 99% (119/120) | – | – | 46% (122/264) | 72% (88/122) | 58% (166/288) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 408 | 67% (272/408) | 99% (119/120) | – | – | 51% (134/264) | 76% (102/134) | 53% (154/288) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 408 | 62% (253/408) | 99% (119/120) | – | – | 58% (153/264) | 78% (120/153) | 47% (135/288) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 408 | 89% (362/408) | 99% (286/288) | – | – | 29% (28/96) | 96% (27/28) | 77% (92/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 408 | 91% (370/408) | 99% (285/288) | – | – | 34% (33/96) | 94% (31/33) | 72% (87/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 408 | 87% (354/408) | 100% (287/288) | – | – | 42% (40/96) | 95% (38/40) | 67% (80/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 144 | 16% (23/144) | 60% (9/15) | 12% (16/129) | 11% (14/129) | – | – | – | – | 40% (6/15) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | structured | 144 | 97% (140/144) | 100% (15/15) | 98% (126/129) | 97% (125/129) | – | – | – | – | 0% (0/15) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | text | 144 | 95% (137/144) | 100% (15/15) | 96% (124/129) | 95% (122/129) | – | – | – | – | 0% (0/15) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 0 | 360 | 99% (357/360) | 99% (357/360) | – | – | – | – | – | – | 0% (0/360) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 1 | 504 | 40% (203/504) | – | – | – | 59% (299/504) | 70% (209/299) | 41% (205/504) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 2 | 144 | 50% (72/144) | – | – | – | 50% (72/144) | 100% (72/72) | 50% (72/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 3 | 144 | 74% (106/144) | – | – | – | 26% (38/144) | 76% (29/38) | 74% (106/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | None | 72 | 100% (72/72) | – | – | – | – | – | 100% (72/72) | 100% (72/72) | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 0 | 360 | 99% (357/360) | 99% (357/360) | – | – | – | – | – | – | 0% (0/360) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 1 | 504 | 99% (501/504) | 99% (501/504) | – | – | – | – | – | – | 0% (0/504) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 2 | 144 | 50% (72/144) | – | – | – | 50% (72/144) | 100% (72/72) | 50% (72/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 3 | 144 | 58% (84/144) | – | – | – | 20% (29/144) | 83% (24/29) | 80% (115/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | None | 72 | 100% (72/72) | – | – | – | – | – | 100% (72/72) | 100% (72/72) | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | 1 | 432 | 69% (300/432) | 87% (39/45) | 69% (266/387) | 67% (261/387) | – | – | – | – | 13% (6/45) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | 306 | 66% (203/306) | 97% (87/90) | – | – | 51% (100/198) | 75% (75/100) | 54% (116/216) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | 306 | 64% (195/306) | 100% (90/90) | – | – | 56% (111/198) | 78% (87/111) | 49% (105/216) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | 306 | 68% (207/306) | 100% (90/90) | – | – | 49% (98/198) | 72% (71/98) | 55% (118/216) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | 306 | 67% (205/306) | 100% (90/90) | – | – | 51% (100/198) | 77% (77/100) | 54% (116/216) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | M-s1 | 306 | 88% (268/306) | 97% (210/216) | – | – | 35% (25/72) | 96% (24/25) | 72% (65/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s1 | 306 | 88% (268/306) | 100% (216/216) | – | – | 36% (26/72) | 100% (26/26) | 71% (64/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s2 | 306 | 91% (278/306) | 100% (216/216) | – | – | 33% (24/72) | 83% (20/24) | 73% (66/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s3 | 306 | 89% (272/306) | 100% (216/216) | – | – | 36% (26/72) | 100% (26/26) | 71% (64/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | M-s1 | 108 | 69% (74/108) | 78% (7/9) | 69% (68/99) | 68% (67/99) | – | – | – | – | 22% (2/9) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s1 | 108 | 74% (80/108) | 89% (8/9) | 73% (72/99) | 73% (72/99) | – | – | – | – | 11% (1/9) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s2 | 108 | 67% (72/108) | 83% (15/18) | 66% (59/90) | 63% (57/90) | – | – | – | – | 17% (3/18) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s3 | 108 | 69% (74/108) | 100% (9/9) | 68% (67/99) | 66% (65/99) | – | – | – | – | 0% (0/9) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 122 | 93% (114/122) | 13% (15/119) | 98% (120/122) | 18% (21/119) | 1% (1/122) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 134 | 93% (124/134) | 17% (20/119) | 96% (128/134) | 25% (30/119) | 1% (1/134) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 153 | 86% (132/153) | 5% (6/119) | 95% (145/153) | 8% (10/119) | 0% (0/153) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 28 | 93% (26/28) | 15% (42/286) | 96% (27/28) | 19% (54/286) | 4% (1/28) | 0% (0/286) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 33 | 94% (31/33) | 13% (38/285) | 100% (33/33) | 19% (54/285) | 0% (0/33) | 0% (0/285) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 40 | 88% (35/40) | 11% (31/287) | 92% (37/40) | 16% (46/287) | 0% (0/40) | 0% (0/287) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 0 | – | 100% (9/9) | – | 100% (9/9) | – | 0% (0/9) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | open | base | structured | 0 | – | 100% (15/15) | – | 100% (15/15) | – | 0% (0/15) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | open | base | text | 0 | – | 87% (13/15) | – | 87% (13/15) | – | 0% (0/15) | – | – | – |

## Step at layer 1: questions with min_layer 1, by layer shown

Correct at each layer (below min_layer the key is UNDERDETERMINED, so correct means abstaining; lenient: OUT_OF_SCOPE counts as abstaining), and the status mix.

| model | repr | layer | config | n | correct (lenient) | model statuses |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | L0 | decided | 168 | 49% (83/168) | ANSWER 85, UNDERDETERMINED 83 |
| deepseek/deepseek-v4.1-flash | formal | L1 | decided | 168 | 99% (167/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | formal | L1 | open | 144 | 16% (23/144) | UNDERDETERMINED 117, AMBIGUOUS 16, ANSWER 11 |
| deepseek/deepseek-v4.1-flash | structured | L0 | decided | 168 | 41% (69/168) | ANSWER 99, UNDERDETERMINED 68, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | structured | L1 | decided | 168 | 99% (166/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | structured | L1 | open | 144 | 97% (140/144) | AMBIGUOUS 126, ANSWER 18 |
| deepseek/deepseek-v4.1-flash | text | L0 | decided | 168 | 32% (53/168) | ANSWER 115, UNDERDETERMINED 52, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | text | L1 | decided | 168 | 100% (168/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | text | L1 | open | 144 | 95% (137/144) | AMBIGUOUS 124, ANSWER 20 |
(base prompt only.)

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | 72 | 0% (0/72) | 1% (1/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | 72 | 46% (33/72) | 100% (39/39) | ANSWER 39, UNDERDETERMINED 33 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q11 | 72 | 100% (72/72) | – | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q17 | 72 | 100% (72/72) | – | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q11 | 72 | 75% (54/72) | – | AMBIGUOUS 54, UNDERDETERMINED 18 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q17 | 72 | 60% (43/72) | – | AMBIGUOUS 43, UNDERDETERMINED 20, ANSWER 9 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 1263 | 0 | 0 | 6 | 0 | 0 |
| AMBIGUOUS | 10 | 266 | 0 | 111 | 0 | 0 |
| UNDERDETERMINED | 510 | 0 | 0 | 537 | 33 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 144 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q01 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q02 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q03 | ANSWER 72 | 0 | 96% (69/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q04 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q05 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | UNDERDETERMINED 72 | 1 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q12 | UNDERDETERMINED 72 | 1 | 94% (68/72) | UNDERDETERMINED 68, ANSWER 4 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q13 | UNDERDETERMINED 72 | 1 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q14 | UNDERDETERMINED 72 | 1 | 64% (46/72) | UNDERDETERMINED 46, ANSWER 26 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q15 | UNDERDETERMINED 72 | 1 | 64% (46/72) | UNDERDETERMINED 46, ANSWER 24, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q16 | UNDERDETERMINED 72 | 1 | 14% (10/72) | ANSWER 62, UNDERDETERMINED 10 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q17 | UNDERDETERMINED 72 | 1 | 46% (33/72) | ANSWER 39, UNDERDETERMINED 33 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q21 | UNDERDETERMINED 72 | 2 | 100% (72/72) | UNDERDETERMINED 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q22 | UNDERDETERMINED 72 | 2 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q31 | UNDERDETERMINED 72 | 3 | 60% (43/72) | UNDERDETERMINED 43, ANSWER 29 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q33 | UNDERDETERMINED 72 | 3 | 88% (63/72) | UNDERDETERMINED 63, ANSWER 9 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q91 | OUT_OF_SCOPE 72 | None | 100% (72/72) | OUT_OF_SCOPE 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q01 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q02 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q03 | ANSWER 72 | 0 | 96% (69/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q04 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q05 | ANSWER 72 | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q11 | ANSWER 72 | 1 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q12 | ANSWER 72 | 1 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q13 | ANSWER 72 | 1 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q14 | ANSWER 72 | 1 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q15 | ANSWER 72 | 1 | 97% (70/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q16 | ANSWER 72 | 1 | 99% (71/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q17 | ANSWER 72 | 1 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q21 | UNDERDETERMINED 72 | 2 | 100% (72/72) | UNDERDETERMINED 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q22 | UNDERDETERMINED 72 | 2 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q31 | UNDERDETERMINED 72 | 3 | 64% (46/72) | UNDERDETERMINED 46, ANSWER 26 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q33 | UNDERDETERMINED 72 | 3 | 53% (38/72) | UNDERDETERMINED 38, OUT_OF_SCOPE 31, ANSWER 3 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q91 | OUT_OF_SCOPE 72 | None | 100% (72/72) | OUT_OF_SCOPE 72 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q11 | AMBIGUOUS 72 | 1 | 75% (54/72) | AMBIGUOUS 54, UNDERDETERMINED 18 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q12 | AMBIGUOUS 72 | 1 | 67% (48/72) | AMBIGUOUS 49, UNDERDETERMINED 23 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q13 | AMBIGUOUS 72 | 1 | 65% (47/72) | AMBIGUOUS 48, UNDERDETERMINED 23, ANSWER 1 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q14 | AMBIGUOUS 36, ANSWER 36 | 1 | 78% (56/72) | ANSWER 31, AMBIGUOUS 25, UNDERDETERMINED 16 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q15 | AMBIGUOUS 63, ANSWER 9 | 1 | 72% (52/72) | AMBIGUOUS 47, UNDERDETERMINED 17, ANSWER 8 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q17 | AMBIGUOUS 72 | 1 | 60% (43/72) | AMBIGUOUS 43, UNDERDETERMINED 20, ANSWER 9 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 136 | 78% (106/136) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 136 | 87% (118/136) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 136 | 82% (112/136) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 136 | 96% (131/136) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 136 | 95% (129/136) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 136 | 92% (125/136) |
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 48 | 62% (30/48) |
| deepseek/deepseek-v4.1-flash | L1 | open | base | structured | 48 | 96% (46/48) |
| deepseek/deepseek-v4.1-flash | L1 | open | base | text | 48 | 92% (44/48) |

