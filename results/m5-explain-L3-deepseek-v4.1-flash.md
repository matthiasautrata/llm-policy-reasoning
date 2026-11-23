# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 3

306 scored records, 0 API errors left out. Cost $0.1312; prompt tokens 2,884,794, completion tokens 237,346 (reasoning 212,485); mean 6.6 s per call.
Providers: DeepInfra 297, Baidu 9.
Status spelled with an accepted alias (UNDETERMINED): 0.
Finish reasons: stop 306.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | formal | 102 | 100% (102/102) | 100% (102/102) | – | – | – | – | – | – | 0% (0/102) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | structured | 102 | 100% (102/102) | 100% (102/102) | – | – | – | – | – | – | 0% (0/102) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | text | 102 | 100% (102/102) | 100% (102/102) | – | – | – | – | – | – | 0% (0/102) | 0 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | 1 | 36 | 100% (36/36) | 100% (36/36) | – | – | – | – | – | – | 0% (0/36) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | 2 | 108 | 100% (108/108) | 100% (108/108) | – | – | – | – | – | – | 0% (0/108) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | 3 | 162 | 100% (162/162) | 100% (162/162) | – | – | – | – | – | – | 0% (0/162) | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | M-s1 | 81 | 100% (81/81) | 100% (81/81) | – | – | – | – | – | – | 0% (0/81) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | S-s1 | 81 | 100% (81/81) | 100% (81/81) | – | – | – | – | – | – | 0% (0/81) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | S-s2 | 81 | 100% (81/81) | 100% (81/81) | – | – | – | – | – | – | 0% (0/81) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | S-s3 | 63 | 100% (63/63) | 100% (63/63) | – | – | – | – | – | – | 0% (0/63) | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | formal | 0 | – | 31% (32/102) | – | 33% (34/102) | – | 0% (0/102) | – | 0% (0/102) | 102 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | structured | 0 | – | 23% (23/102) | – | 31% (32/102) | – | 0% (0/102) | – | 0% (0/102) | 102 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | text | 0 | – | 16% (16/102) | – | 24% (24/102) | – | 0% (0/102) | – | 0% (0/102) | 102 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 306 | 0 | 0 | 0 | 0 | 0 |

## By template

| model | layer | config | prompt | template | keys | min_layer | correct | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q14 | ANSWER 36 | 1 | 100% (36/36) | ANSWER 36 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q21 | ANSWER 36 | 2 | 100% (36/36) | ANSWER 36 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q24 | ANSWER 36 | 2 | 100% (36/36) | ANSWER 36 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q26 | ANSWER 36 | 2 | 100% (36/36) | ANSWER 36 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q31 | ANSWER 45 | 3 | 100% (45/45) | ANSWER 45 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q32 | ANSWER 36 | 3 | 100% (36/36) | ANSWER 36 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q33 | ANSWER 27 | 3 | 100% (27/27) | ANSWER 27 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q35 | ANSWER 27 | 3 | 100% (27/27) | ANSWER 27 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | Q36 | ANSWER 27 | 3 | 100% (27/27) | ANSWER 27 |

## Explanations (explain prompt, graded against the why/2 tree)

Only replies whose key and answer are both ANSWER true (why/2 justifies true answers only). Core: the rules of the tree's rule nodes; an explanation must name them. Support: the rules behind the tree's closed-world negations, aggregates and if-then-else conditions; an explanation may name them. Ids are compared without a reading suffix (R104b = R104). Recall = share of core named; precision = share of named rules that are in core or support; exact = recall 1 and nothing outside core and support.

| model | layer | config | prompt | repr | n | ANSWER true | core recall | full recall | precision | nothing outside | exact | empty list | mean ids named |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | formal | 102 | 102 | 0.97 | 94% (96/102) | 0.97 | 95% (97/102) | 92% (94/102) | 0 | 4.24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | structured | 102 | 102 | 0.97 | 93% (95/102) | 0.96 | 90% (92/102) | 89% (91/102) | 0 | 4.39 |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | text | 102 | 102 | 0.97 | 95% (97/102) | 0.94 | 80% (82/102) | 79% (81/102) | 0 | 4.46 |

Core recall per rule class (correct replies, all representations): a needed rule of the class, named or not. H4 predicts conservative rules (rearranging what is asserted) are left unnamed more often.

| layer | class | conservative | needed | named |
|---|---|---|---|---|
| 1 | definitional | True | 252 | 94% (237/252) |
| 2 | fitness | True | 36 | 100% (36/36) |
| 2 | temporal | True | 414 | 91% (377/414) |
| 3 | defeasible | False | 72 | 88% (63/72) |
| 3 | definitional | True | 27 | 67% (18/27) |
| 3 | entitlement | False | 72 | 88% (63/72) |
| 3 | incompatibility | False | 27 | 100% (27/27) |
| 3 | material_inference | False | 117 | 75% (88/117) |

Most often missed core rules: R103 15, R305 10, R308 10, R201 10, R301 9, R203 9, R310 9, R204 9, R202 9, R304 9.
Most often named outside core and support: R303 11, R311 9, R312 9, R204 7, R201 6, R313 4, R205 4, R104 4, R110 4, R106 4.

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | formal | 34 | 100% (34/34) |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | structured | 34 | 100% (34/34) |
| deepseek/deepseek-v4.1-flash | L3 | decided | explain | text | 34 | 100% (34/34) |

