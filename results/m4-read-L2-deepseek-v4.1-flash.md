# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 2

1092 scored records, 0 API errors left out. Cost $0.6167; prompt tokens 9,553,991, completion tokens 1,249,842 (reasoning 1,195,026); mean 8.2 s per call.
Providers: DeepInfra 1058, Baidu 34.
Status spelled with an accepted alias (UNDETERMINED): 1.
Finish reasons: stop 1092.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 296 | 92% (271/296) | 99% (222/225) | – | – | 2% (1/48) | 0% (0/1) | 98% (55/56) | 100% (8/8) | 0% (0/225) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 296 | 91% (269/296) | 99% (223/225) | – | – | 17% (8/48) | 88% (7/8) | 86% (48/56) | 100% (8/8) | 0% (0/225) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 296 | 85% (251/296) | 99% (223/225) | – | – | 58% (28/48) | 64% (18/28) | 50% (28/56) | 100% (8/8) | 0% (1/225) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | formal | 68 | 94% (64/68) | 100% (19/19) | 92% (45/49) | 92% (45/49) | – | – | – | – | 0% (0/19) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | structured | 68 | 97% (66/68) | 100% (19/19) | 100% (49/49) | 96% (47/49) | – | – | – | – | 0% (0/19) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | text | 68 | 97% (66/68) | 100% (19/19) | 96% (47/49) | 96% (47/49) | – | – | – | – | 0% (0/19) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 0 | 120 | 98% (117/120) | 98% (117/120) | – | – | – | – | – | – | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 1 | 168 | 98% (164/168) | 98% (164/168) | – | – | – | – | – | – | 1% (1/168) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 2 | 432 | 90% (387/432) | 100% (387/387) | – | – | – | – | – | – | 0% (0/387) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 3 | 144 | 69% (99/144) | – | – | – | 26% (37/144) | 68% (25/37) | 74% (107/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | None | 24 | 100% (24/24) | – | – | – | – | – | 100% (24/24) | 100% (24/24) | – | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | 1 | 144 | 94% (136/144) | 100% (15/15) | 95% (123/129) | 94% (121/129) | – | – | – | – | 0% (0/15) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | 2 | 60 | 100% (60/60) | 100% (42/42) | 100% (18/18) | 100% (18/18) | – | – | – | – | 0% (0/42) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | M-s1 | 222 | 85% (188/222) | 98% (158/162) | – | – | 25% (9/36) | 44% (4/9) | 79% (33/42) | 100% (6/6) | 0% (0/162) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s1 | 222 | 86% (190/222) | 99% (161/162) | – | – | 31% (11/36) | 82% (9/11) | 74% (31/42) | 100% (6/6) | 1% (1/162) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s2 | 222 | 93% (207/222) | 100% (171/171) | – | – | 14% (5/36) | 40% (2/5) | 88% (37/42) | 100% (6/6) | 0% (0/171) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s3 | 222 | 93% (206/222) | 99% (178/180) | – | – | 33% (12/36) | 83% (10/12) | 71% (30/42) | 100% (6/6) | 0% (0/180) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | M-s1 | 42 | 93% (39/42) | 100% (9/9) | 97% (32/33) | 91% (30/33) | – | – | – | – | 0% (0/9) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | M-s2 | 18 | 100% (18/18) | 100% (9/9) | 100% (9/9) | 100% (9/9) | – | – | – | – | 0% (0/9) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | M-s3 | 18 | 100% (18/18) | 100% (9/9) | 100% (9/9) | 100% (9/9) | – | – | – | – | 0% (0/9) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | S-s1 | 42 | 95% (40/42) | 100% (9/9) | 94% (31/33) | 94% (31/33) | – | – | – | – | 0% (0/9) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | S-s2 | 42 | 95% (40/42) | 100% (12/12) | 93% (28/30) | 93% (28/30) | – | – | – | – | 0% (0/12) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | S-s3 | 42 | 98% (41/42) | 100% (9/9) | 97% (32/33) | 97% (32/33) | – | – | – | – | 0% (0/9) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 1 | 100% (1/1) | 23% (52/222) | 100% (1/1) | 27% (61/222) | 0% (0/1) | 0% (0/222) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 8 | 100% (8/8) | 21% (47/223) | 100% (8/8) | 25% (56/223) | 0% (0/8) | 0% (0/223) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 28 | 100% (28/28) | 22% (50/223) | 100% (28/28) | 26% (57/223) | 4% (1/28) | 0% (0/223) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | open | base | formal | 0 | – | 89% (17/19) | – | 95% (18/19) | – | 0% (0/19) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | open | base | structured | 0 | – | 84% (16/19) | – | 84% (16/19) | – | 0% (0/19) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | open | base | text | 0 | – | 74% (14/19) | – | 79% (15/19) | – | 0% (0/19) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q11 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q17 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q11 | 24 | 100% (24/24) | – | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q17 | 24 | 75% (18/24) | – | AMBIGUOUS 18, ANSWER 6 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 731 | 0 | 0 | 1 | 0 | 0 |
| AMBIGUOUS | 6 | 141 | 0 | 0 | 0 | 0 |
| CONFLICT | 0 | 35 | 0 | 10 | 0 | 0 |
| UNDERDETERMINED | 37 | 0 | 0 | 99 | 8 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 24 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q01 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q02 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q03 | ANSWER 24 | 0 | 88% (21/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q04 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q05 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q11 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q12 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q13 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q14 | ANSWER 24 | 1 | 96% (23/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q15 | ANSWER 24 | 1 | 88% (21/24) | ANSWER 23, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q16 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q17 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q21 | ANSWER 72 | 2 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q22 | ANSWER 72 | 2 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q23 | ANSWER 72 | 2 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q24 | ANSWER 72 | 2 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q25 | CONFLICT 45, ANSWER 27 | 2 | 38% (27/72) | AMBIGUOUS 35, ANSWER 27, UNDERDETERMINED 10 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q26 | ANSWER 72 | 2 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q31 | UNDERDETERMINED 72 | 3 | 56% (40/72) | UNDERDETERMINED 40, ANSWER 32 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q33 | UNDERDETERMINED 72 | 3 | 82% (59/72) | UNDERDETERMINED 59, OUT_OF_SCOPE 8, ANSWER 5 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q91 | OUT_OF_SCOPE 24 | None | 100% (24/24) | OUT_OF_SCOPE 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q11 | AMBIGUOUS 24 | 1 | 100% (24/24) | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q12 | AMBIGUOUS 24 | 1 | 100% (24/24) | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q13 | AMBIGUOUS 24 | 1 | 96% (23/24) | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q14 | ANSWER 12, AMBIGUOUS 12 | 1 | 100% (24/24) | ANSWER 12, AMBIGUOUS 12 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q15 | AMBIGUOUS 21, ANSWER 3 | 1 | 96% (23/24) | AMBIGUOUS 21, ANSWER 3 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q17 | AMBIGUOUS 24 | 1 | 75% (18/24) | AMBIGUOUS 18, ANSWER 6 |
| deepseek/deepseek-v4.1-flash | L2 | open | base | Q22 | ANSWER 42, AMBIGUOUS 18 | 2 | 100% (60/60) | ANSWER 42, AMBIGUOUS 18 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | model statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 15 | 0% (0/15) | 93% (14/15) | 100% (15/15) | 0 | 0 | AMBIGUOUS 14, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 15 | 0% (0/15) | 73% (11/15) | 100% (15/15) | 0 | 0 | AMBIGUOUS 11, UNDERDETERMINED 4 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 15 | 0% (0/15) | 67% (10/15) | 100% (15/15) | 0 | 0 | AMBIGUOUS 10, UNDERDETERMINED 5 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 64 | 91% (58/64) |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 64 | 88% (56/64) |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 64 | 86% (55/64) |
| deepseek/deepseek-v4.1-flash | L2 | open | base | formal | 4 | 100% (4/4) |
| deepseek/deepseek-v4.1-flash | L2 | open | base | structured | 4 | 100% (4/4) |
| deepseek/deepseek-v4.1-flash | L2 | open | base | text | 4 | 100% (4/4) |

