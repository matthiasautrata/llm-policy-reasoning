# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 1

144 scored records, 0 API errors left out. Cost $0.1348; prompt tokens 944,358, completion tokens 312,236 (reasoning 298,121); mean 13.4 s per call.
Providers: DeepInfra 139, Baidu 5.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 144.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 144 | 87% (125/144) | 93% (14/15) | 91% (118/129) | 86% (111/129) | – | – | – | – | 0% (0/15) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | 1 | 144 | 87% (125/144) | 93% (14/15) | 91% (118/129) | 86% (111/129) | – | – | – | – | 0% (0/15) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | M-s1 | 36 | 92% (33/36) | 100% (3/3) | 94% (31/33) | 91% (30/33) | – | – | – | – | 0% (0/3) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s1 | 36 | 89% (32/36) | 100% (3/3) | 94% (31/33) | 88% (29/33) | – | – | – | – | 0% (0/3) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s2 | 36 | 94% (34/36) | 83% (5/6) | 97% (29/30) | 97% (29/30) | – | – | – | – | 0% (0/6) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | S-s3 | 36 | 72% (26/36) | 100% (3/3) | 82% (27/33) | 70% (23/33) | – | – | – | – | 0% (0/3) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 0 | – | 100% (14/14) | – | 100% (14/14) | – | 0% (0/14) | – | – | – |

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q11 | 24 | 100% (24/24) | – | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q17 | 24 | 58% (14/24) | – | AMBIGUOUS 14, ANSWER 10 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 15 | 0 | 0 | 0 | 0 | 0 |
| AMBIGUOUS | 11 | 118 | 0 | 0 | 0 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q11 | AMBIGUOUS 24 | 1 | 100% (24/24) | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q12 | AMBIGUOUS 24 | 1 | 79% (19/24) | AMBIGUOUS 23, ANSWER 1 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q13 | AMBIGUOUS 24 | 1 | 100% (24/24) | AMBIGUOUS 24 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q14 | AMBIGUOUS 12, ANSWER 12 | 1 | 100% (24/24) | AMBIGUOUS 12, ANSWER 12 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q15 | AMBIGUOUS 21, ANSWER 3 | 1 | 83% (20/24) | AMBIGUOUS 21, ANSWER 3 |
| deepseek/deepseek-v4.1-flash | L1 | open | base | Q17 | AMBIGUOUS 24 | 1 | 58% (14/24) | AMBIGUOUS 14, ANSWER 10 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L1 | open | base | formal | 48 | 85% (41/48) |

