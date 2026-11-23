# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

888 scored records, 0 API errors left out. Cost $0.4610; prompt tokens 8,176,817, completion tokens 958,840 (reasoning 922,630); mean 7.9 s per call.
Providers: DeepInfra 863, Baidu 25.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 884, length 4.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 296 | 95% (280/296) | 100% (272/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 296 | 95% (282/296) | 100% (272/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 296 | 95% (281/296) | 99% (270/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 1 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 0 | 120 | 98% (117/120) | 98% (117/120) | – | – | – | – | – | – | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 1 | 168 | 100% (168/168) | 100% (168/168) | – | – | – | – | – | – | 0% (0/168) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 2 | 144 | 100% (144/144) | 100% (144/144) | – | – | – | – | – | – | 0% (0/144) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 3 | 432 | 90% (390/432) | 99% (385/387) | – | – | – | – | – | – | 0% (0/387) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | None | 24 | 100% (24/24) | – | – | – | – | – | 100% (24/24) | 100% (24/24) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | 222 | 95% (210/222) | 99% (204/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | 222 | 95% (212/222) | 100% (206/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | 222 | 97% (215/222) | 100% (207/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s3 | 222 | 93% (206/222) | 99% (197/198) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/198) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 0 | – | 26% (71/272) | – | 31% (83/272) | – | 0% (0/272) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 0 | – | 31% (84/272) | – | 36% (98/272) | – | 0% (0/272) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 0 | – | 23% (62/270) | – | 29% (77/270) | – | 0% (0/270) | – | – | – |

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
| ANSWER | 819 | 0 | 0 | 0 | 0 | 0 |
| CONFLICT | 36 | 0 | 5 | 0 | 0 | 4 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 24 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q01 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q02 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q03 | ANSWER 24 | 0 | 88% (21/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q04 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q05 | ANSWER 24 | 0 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q11 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q12 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q13 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q14 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q15 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q16 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q17 | ANSWER 24 | 1 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q21 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q22 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q23 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q24 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q25 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q26 | ANSWER 24 | 2 | 100% (24/24) | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q31 | ANSWER 72 | 3 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q32 | ANSWER 72 | 3 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q33 | ANSWER 63, CONFLICT 9 | 3 | 89% (64/72) | ANSWER 71, CONFLICT 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q34 | ANSWER 36, CONFLICT 36 | 3 | 56% (40/72) | ANSWER 64, CONFLICT 4, PARSE 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q35 | ANSWER 72 | 3 | 100% (72/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q36 | ANSWER 72 | 3 | 97% (70/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q91 | OUT_OF_SCOPE 24 | None | 100% (24/24) | OUT_OF_SCOPE 24 |

## CONFLICT keys

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | model statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 15 | 0% (0/15) | 0% (0/15) | 0% (0/15) | 0 | 15 | ANSWER 15 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 15 | 13% (2/15) | 0% (0/15) | 33% (5/15) | 0 | 10 | ANSWER 10, PARSE 3, CONFLICT 2 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 15 | 20% (3/15) | 0% (0/15) | 27% (4/15) | 0 | 11 | ANSWER 11, CONFLICT 3, PARSE 1 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 48 | 100% (48/48) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 48 | 96% (46/48) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 48 | 92% (44/48) |

