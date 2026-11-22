# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 0

1728 scored records, 0 API errors left out. Cost $0.3382; prompt tokens 6,529,617, completion tokens 1,549,400 (reasoning 1,428,789); mean 7.6 s per call.
Providers: Baidu 1724, InferenceNet 4.
Status spelled with an accepted alias (UNDETERMINED): 44.
Finish reasons: stop 1728.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By model and representation

| model | representation | n | correct | correct on ANSWER keys | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | 576 | 71% (407/576) | 99% (119/120) | 28% (122/432) | 66% (78/118) | 73% (334/456) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | structured | 576 | 70% (402/576) | 99% (119/120) | 30% (128/432) | 73% (93/127) | 72% (328/456) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | text | 576 | 66% (383/576) | 99% (119/120) | 35% (151/432) | 73% (109/149) | 67% (305/456) | 100% (24/24) | 0% (0/120) | 0 |

## By model and key's min_layer

| model | key's min_layer | n | correct | correct on ANSWER keys | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | 0 | 360 | 99% (357/360) | 99% (357/360) | – | – | – | – | 0% (0/360) | 0 |
| deepseek/deepseek-v4.1-flash | 1 | 432 | 39% (170/432) | – | 60% (260/432) | 65% (170/260) | 40% (172/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | 2 | 432 | 53% (227/432) | – | 19% (82/432) | 92% (72/78) | 81% (350/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | 3 | 432 | 85% (366/432) | – | 14% (59/432) | 68% (38/56) | 86% (373/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | None | 72 | 100% (72/72) | – | – | – | 100% (72/72) | 100% (72/72) | – | 0 |

## By model and world

| model | world | n | correct | correct on ANSWER keys | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | M-s1 | 432 | 69% (298/432) | 97% (87/90) | 30% (96/324) | 68% (63/92) | 72% (246/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | S-s1 | 432 | 69% (298/432) | 100% (90/90) | 33% (108/324) | 76% (81/107) | 68% (234/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | S-s2 | 432 | 69% (296/432) | 100% (90/90) | 30% (98/324) | 68% (66/97) | 71% (244/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | S-s3 | 432 | 69% (300/432) | 100% (90/90) | 31% (99/324) | 71% (70/98) | 71% (243/342) | 100% (18/18) | 0% (0/90) | 0 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 360 | 0 | 0 | 0 | 0 | 0 |
| UNDERDETERMINED | 401 | 0 | 0 | 763 | 132 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 72 | 0 |

## By template

| model | template | key | min_layer | correct | model statuses |
|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | Q01 | ANSWER | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q02 | ANSWER | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q03 | ANSWER | 0 | 96% (69/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q04 | ANSWER | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q05 | ANSWER | 0 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q11 | UNDERDETERMINED | 1 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q12 | UNDERDETERMINED | 1 | 94% (68/72) | UNDERDETERMINED 68, ANSWER 4 |
| deepseek/deepseek-v4.1-flash | Q13 | UNDERDETERMINED | 1 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q14 | UNDERDETERMINED | 1 | 64% (46/72) | UNDERDETERMINED 46, ANSWER 26 |
| deepseek/deepseek-v4.1-flash | Q15 | UNDERDETERMINED | 1 | 64% (46/72) | UNDERDETERMINED 46, ANSWER 24, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | Q16 | UNDERDETERMINED | 1 | 14% (10/72) | ANSWER 62, UNDERDETERMINED 10 |
| deepseek/deepseek-v4.1-flash | Q21 | UNDERDETERMINED | 2 | 100% (72/72) | UNDERDETERMINED 72 |
| deepseek/deepseek-v4.1-flash | Q22 | UNDERDETERMINED | 2 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | Q23 | UNDERDETERMINED | 2 | 78% (56/72) | UNDERDETERMINED 56, OUT_OF_SCOPE 10, ANSWER 6 |
| deepseek/deepseek-v4.1-flash | Q24 | UNDERDETERMINED | 2 | 43% (31/72) | OUT_OF_SCOPE 41, UNDERDETERMINED 31 |
| deepseek/deepseek-v4.1-flash | Q25 | UNDERDETERMINED | 2 | 94% (68/72) | UNDERDETERMINED 68, ANSWER 4 |
| deepseek/deepseek-v4.1-flash | Q26 | UNDERDETERMINED | 2 | 0% (0/72) | OUT_OF_SCOPE 72 |
| deepseek/deepseek-v4.1-flash | Q31 | UNDERDETERMINED | 3 | 60% (43/72) | UNDERDETERMINED 43, ANSWER 29 |
| deepseek/deepseek-v4.1-flash | Q32 | UNDERDETERMINED | 3 | 88% (63/72) | UNDERDETERMINED 63, ANSWER 9 |
| deepseek/deepseek-v4.1-flash | Q33 | UNDERDETERMINED | 3 | 88% (63/72) | UNDERDETERMINED 63, ANSWER 9 |
| deepseek/deepseek-v4.1-flash | Q34 | UNDERDETERMINED | 3 | 83% (60/72) | UNDERDETERMINED 60, ANSWER 10, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | Q35 | UNDERDETERMINED | 3 | 93% (67/72) | UNDERDETERMINED 67, OUT_OF_SCOPE 5 |
| deepseek/deepseek-v4.1-flash | Q36 | UNDERDETERMINED | 3 | 97% (70/72) | UNDERDETERMINED 70, ANSWER 2 |
| deepseek/deepseek-v4.1-flash | Q91 | OUT_OF_SCOPE | None | 100% (72/72) | OUT_OF_SCOPE 72 |

## Stability across repetitions

| model | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | 192 | 78% (149/192) |
| deepseek/deepseek-v4.1-flash | structured | 192 | 86% (165/192) |
| deepseek/deepseek-v4.1-flash | text | 192 | 79% (152/192) |

