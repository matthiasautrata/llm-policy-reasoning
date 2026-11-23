# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

456 scored records, 0 API errors left out. Cost $0.4801; prompt tokens 11,543,065, completion tokens 547,309 (reasoning 519,604); mean 9.2 s per call.
Providers: InferenceNet 441, Baidu 10, CoreWeave 5.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 456.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 152 | 99% (150/152) | 99% (142/144) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/144) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 152 | 98% (149/152) | 98% (141/144) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/144) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 152 | 98% (149/152) | 98% (141/144) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/144) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 0 | 120 | 98% (118/120) | 98% (118/120) | – | – | – | – | – | – | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 1 | 168 | 96% (162/168) | 96% (162/168) | – | – | – | – | – | – | 0% (0/168) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 2 | 144 | 100% (144/144) | 100% (144/144) | – | – | – | – | – | – | 0% (0/144) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | None | 24 | 100% (24/24) | – | – | – | – | – | 100% (24/24) | 100% (24/24) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | L-s1 | 228 | 98% (224/228) | 98% (212/216) | – | – | – | – | 100% (12/12) | 100% (12/12) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | 114 | 96% (110/114) | 96% (104/108) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/108) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | 114 | 100% (114/114) | 100% (108/108) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/108) | 0 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | L-s1 | formal | 76 | 100% (76/76) | 38,110 | 1,250 | 1,299 | 9.2 | 19.1 | 44.5 | $0.00122 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | L-s1 | structured | 76 | 97% (74/76) | 42,117 | 1,830 | 1,892 | 13.8 | 38.4 | 130.0 | $0.00163 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | L-s1 | text | 76 | 97% (74/76) | 35,641 | 1,300 | 1,383 | 11.7 | 34.7 | 74.2 | $0.00149 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | formal | 38 | 95% (36/38) | 18,175 | 881 | 939 | 6.9 | 17.9 | 24.8 | $0.00080 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | structured | 38 | 97% (37/38) | 19,166 | 1,001 | 1,063 | 7.3 | 15.1 | 49.7 | $0.00080 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | text | 38 | 97% (37/38) | 15,156 | 857 | 922 | 6.7 | 17.7 | 40.8 | $0.00072 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | formal | 38 | 100% (38/38) | 8,006 | 619 | 669 | 5.9 | 11.3 | 37.2 | $0.00049 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | structured | 38 | 100% (38/38) | 7,063 | 671 | 723 | 6.6 | 13.7 | 34.1 | $0.00050 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | text | 38 | 100% (38/38) | 4,465 | 885 | 939 | 7.9 | 22.4 | 77.2 | $0.00063 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 0 | – | 54% (76/142) | – | 59% (84/142) | – | 0% (0/142) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 0 | – | 52% (74/141) | – | 61% (86/141) | – | 0% (0/141) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 0 | – | 46% (65/141) | – | 54% (76/141) | – | 0% (0/141) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q11 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q17 | 24 | 100% (24/24) | – | ANSWER 24 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 432 | 0 | 0 | 0 | 0 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 24 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q01 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q02 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q03 | ANSWER 24 | 0 | 92% (22/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q04 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q05 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q11 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q12 | ANSWER 24 | 1 | 96% (23/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q13 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q14 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q15 | ANSWER 24 | 1 | 83% (20/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q16 | ANSWER 24 | 1 | 96% (23/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q17 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q21 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q22 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q23 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q24 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q25 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q26 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q91 | OUT_OF_SCOPE 24 | None | 100% (24/24) | OUT_OF_SCOPE 24 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 38 | 100% (38/38) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 38 | 100% (38/38) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 38 | 100% (38/38) |

