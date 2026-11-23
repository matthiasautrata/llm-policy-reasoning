# Read mode: deepseek/deepseek-v4.1-flash at layer(s) 0, 1, 2, 3

4728 scored records, 0 API errors left out. Cost $1.5200; prompt tokens 28,663,090, completion tokens 3,978,773 (reasoning 3,735,017); mean 6.7 s per call.
Providers: DeepInfra 2933, Baidu 1791, InferenceNet 4.
Status spelled with an accepted alias (UNDETERMINED): 50.
Finish reasons: stop 4724, length 4.

Overreach: the key is UNDERDETERMINED (the layer lacks a definition or rule the question needs) and the model gave a value. Abstained (lenient): an UNDERDETERMINED or OUT_OF_SCOPE key met with either abstention. Overreach = later key: of the overreaching ANSWERs, the share whose value equals the decided key once the question's layer is present.

## By representation

| model | layer | config | prompt | representation | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 576 | 71% (407/576) | 99% (119/120) | – | – | 28% (122/432) | 66% (78/118) | 73% (334/456) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 576 | 70% (402/576) | 99% (119/120) | – | – | 30% (128/432) | 73% (93/127) | 72% (328/456) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 576 | 66% (383/576) | 99% (119/120) | – | – | 35% (151/432) | 73% (109/149) | 67% (305/456) | 100% (24/24) | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 408 | 89% (362/408) | 99% (286/288) | – | – | 29% (28/96) | 96% (27/28) | 77% (92/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 408 | 91% (370/408) | 99% (285/288) | – | – | 34% (33/96) | 94% (31/33) | 72% (87/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 408 | 87% (354/408) | 100% (287/288) | – | – | 42% (40/96) | 95% (38/40) | 67% (80/120) | 100% (24/24) | 0% (0/288) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 296 | 92% (271/296) | 99% (222/225) | – | – | 2% (1/48) | 0% (0/1) | 98% (55/56) | 100% (8/8) | 0% (0/225) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 296 | 91% (269/296) | 99% (223/225) | – | – | 17% (8/48) | 88% (7/8) | 86% (48/56) | 100% (8/8) | 0% (0/225) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 296 | 85% (251/296) | 99% (223/225) | – | – | 58% (28/48) | 64% (18/28) | 50% (28/56) | 100% (8/8) | 0% (1/225) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 296 | 95% (280/296) | 100% (272/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 296 | 95% (282/296) | 100% (272/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 296 | 95% (281/296) | 99% (270/273) | – | – | – | – | 100% (8/8) | 100% (8/8) | 0% (0/273) | 1 |

## By key's min_layer

| model | layer | config | prompt | min_layer | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 0 | 360 | 99% (357/360) | 99% (357/360) | – | – | – | – | – | – | 0% (0/360) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 1 | 432 | 39% (170/432) | – | – | – | 60% (260/432) | 65% (170/260) | 40% (172/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 2 | 432 | 53% (227/432) | – | – | – | 19% (82/432) | 92% (72/78) | 81% (350/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | 3 | 432 | 85% (366/432) | – | – | – | 14% (59/432) | 68% (38/56) | 86% (373/432) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | None | 72 | 100% (72/72) | – | – | – | – | – | 100% (72/72) | 100% (72/72) | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 0 | 360 | 99% (357/360) | 99% (357/360) | – | – | – | – | – | – | 0% (0/360) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 1 | 504 | 99% (501/504) | 99% (501/504) | – | – | – | – | – | – | 0% (0/504) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 2 | 144 | 50% (72/144) | – | – | – | 50% (72/144) | 100% (72/72) | 50% (72/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | 3 | 144 | 58% (84/144) | – | – | – | 20% (29/144) | 83% (24/29) | 80% (115/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | None | 72 | 100% (72/72) | – | – | – | – | – | 100% (72/72) | 100% (72/72) | – | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 0 | 120 | 98% (117/120) | 98% (117/120) | – | – | – | – | – | – | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 1 | 168 | 98% (164/168) | 98% (164/168) | – | – | – | – | – | – | 1% (1/168) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 2 | 432 | 90% (387/432) | 100% (387/387) | – | – | – | – | – | – | 0% (0/387) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | 3 | 144 | 69% (99/144) | – | – | – | 26% (37/144) | 68% (25/37) | 74% (107/144) | – | – | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | None | 24 | 100% (24/24) | – | – | – | – | – | 100% (24/24) | 100% (24/24) | – | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 0 | 120 | 98% (117/120) | 98% (117/120) | – | – | – | – | – | – | 0% (0/120) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 1 | 168 | 100% (168/168) | 100% (168/168) | – | – | – | – | – | – | 0% (0/168) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 2 | 144 | 100% (144/144) | 100% (144/144) | – | – | – | – | – | – | 0% (0/144) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | 3 | 432 | 90% (390/432) | 99% (385/387) | – | – | – | – | – | – | 0% (0/387) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | None | 24 | 100% (24/24) | – | – | – | – | – | 100% (24/24) | 100% (24/24) | – | 0 |

## By world

| model | layer | config | prompt | world | n | correct | correct on ANSWER keys | AMBIGUOUS seen | AMBIGUOUS readings right | overreach | overreach = later key | abstained (lenient) | OUT_OF_SCOPE exact | false abstention | unparsed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | 432 | 69% (298/432) | 97% (87/90) | – | – | 30% (96/324) | 68% (63/92) | 72% (246/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | 432 | 69% (298/432) | 100% (90/90) | – | – | 33% (108/324) | 76% (81/107) | 68% (234/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | 432 | 69% (296/432) | 100% (90/90) | – | – | 30% (98/324) | 68% (66/97) | 71% (244/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | 432 | 69% (300/432) | 100% (90/90) | – | – | 31% (99/324) | 71% (70/98) | 71% (243/342) | 100% (18/18) | 0% (0/90) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | M-s1 | 306 | 88% (268/306) | 97% (210/216) | – | – | 35% (25/72) | 96% (24/25) | 72% (65/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s1 | 306 | 88% (268/306) | 100% (216/216) | – | – | 36% (26/72) | 100% (26/26) | 71% (64/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s2 | 306 | 91% (278/306) | 100% (216/216) | – | – | 33% (24/72) | 83% (20/24) | 73% (66/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s3 | 306 | 89% (272/306) | 100% (216/216) | – | – | 36% (26/72) | 100% (26/26) | 71% (64/90) | 100% (18/18) | 0% (0/216) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | M-s1 | 222 | 85% (188/222) | 98% (158/162) | – | – | 25% (9/36) | 44% (4/9) | 79% (33/42) | 100% (6/6) | 0% (0/162) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s1 | 222 | 86% (190/222) | 99% (161/162) | – | – | 31% (11/36) | 82% (9/11) | 74% (31/42) | 100% (6/6) | 1% (1/162) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s2 | 222 | 93% (207/222) | 100% (171/171) | – | – | 14% (5/36) | 40% (2/5) | 88% (37/42) | 100% (6/6) | 0% (0/171) | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s3 | 222 | 93% (206/222) | 99% (178/180) | – | – | 33% (12/36) | 83% (10/12) | 71% (30/42) | 100% (6/6) | 0% (0/180) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | 222 | 95% (210/222) | 99% (204/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 4 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | 222 | 95% (212/222) | 100% (206/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | 222 | 97% (215/222) | 100% (207/207) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/207) | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s3 | 222 | 93% (206/222) | 99% (197/198) | – | – | – | – | 100% (6/6) | 100% (6/6) | 0% (0/198) | 0 |

## Cost by world and representation

Per call (compile: summed over the reply and any repair turn). p90 / max s: wall time per call. length: replies cut off at the output-token cap.

| model | layer | config | prompt | world | representation | n | correct | prompt tok | reasoning tok | completion tok | mean s | p90 s | max s | cost | length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | formal | 144 | 73% (105/144) | 8,513 | 1,087 | 1,162 | 8.5 | 20.5 | 46.7 | $0.00026 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | structured | 144 | 72% (103/144) | 9,369 | 1,121 | 1,199 | 8.4 | 22.0 | 49.9 | $0.00028 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | M-s1 | text | 144 | 62% (90/144) | 7,914 | 818 | 875 | 7.7 | 15.5 | 49.3 | $0.00021 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | formal | 144 | 69% (100/144) | 2,315 | 806 | 878 | 6.7 | 14.6 | 34.2 | $0.00019 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | structured | 144 | 69% (99/144) | 2,337 | 723 | 789 | 6.0 | 13.5 | 24.4 | $0.00016 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s1 | text | 144 | 69% (99/144) | 1,854 | 659 | 723 | 5.5 | 11.4 | 31.7 | $0.00015 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | formal | 144 | 69% (100/144) | 2,316 | 869 | 945 | 9.9 | 17.8 | 129.2 | $0.00021 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | structured | 144 | 69% (100/144) | 2,338 | 899 | 977 | 11.6 | 18.3 | 291.0 | $0.00020 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s2 | text | 144 | 67% (96/144) | 1,855 | 745 | 807 | 6.3 | 14.7 | 32.9 | $0.00017 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | formal | 144 | 71% (102/144) | 2,325 | 695 | 770 | 6.1 | 11.9 | 37.1 | $0.00017 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | structured | 144 | 69% (100/144) | 2,349 | 748 | 819 | 7.6 | 15.5 | 41.6 | $0.00017 | 0 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | S-s3 | text | 144 | 68% (98/144) | 1,862 | 754 | 816 | 7.6 | 14.9 | 85.9 | $0.00017 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | M-s1 | formal | 102 | 87% (89/102) | 10,687 | 571 | 614 | 4.7 | 9.1 | 34.2 | $0.00033 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | M-s1 | structured | 102 | 87% (89/102) | 10,967 | 675 | 714 | 5.5 | 12.4 | 41.4 | $0.00037 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | M-s1 | text | 102 | 88% (90/102) | 8,728 | 573 | 615 | 4.9 | 9.3 | 40.6 | $0.00032 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s1 | formal | 102 | 88% (90/102) | 4,488 | 415 | 454 | 3.7 | 5.6 | 24.3 | $0.00023 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s1 | structured | 102 | 90% (92/102) | 3,934 | 456 | 496 | 4.1 | 9.9 | 25.5 | $0.00024 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s1 | text | 102 | 84% (86/102) | 2,667 | 404 | 441 | 3.6 | 6.0 | 32.1 | $0.00022 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s2 | formal | 102 | 91% (93/102) | 4,489 | 403 | 443 | 3.7 | 6.7 | 20.7 | $0.00022 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s2 | structured | 102 | 93% (95/102) | 3,935 | 518 | 561 | 4.4 | 10.3 | 25.4 | $0.00027 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s2 | text | 102 | 88% (90/102) | 2,668 | 417 | 459 | 3.8 | 6.8 | 31.4 | $0.00022 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s3 | formal | 102 | 88% (90/102) | 4,498 | 363 | 404 | 3.6 | 6.5 | 17.8 | $0.00020 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s3 | structured | 102 | 92% (94/102) | 3,946 | 462 | 503 | 4.1 | 9.0 | 36.6 | $0.00025 | 0 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | S-s3 | text | 102 | 86% (88/102) | 2,675 | 329 | 364 | 3.3 | 6.0 | 14.7 | $0.00018 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | M-s1 | formal | 74 | 85% (63/74) | 16,887 | 893 | 936 | 6.9 | 12.4 | 73.9 | $0.00052 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | M-s1 | structured | 74 | 88% (65/74) | 18,198 | 1,097 | 1,146 | 8.2 | 22.9 | 77.6 | $0.00062 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | M-s1 | text | 74 | 81% (60/74) | 14,833 | 1,366 | 1,409 | 9.9 | 37.1 | 70.6 | $0.00070 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s1 | formal | 74 | 89% (66/74) | 6,719 | 751 | 796 | 6.2 | 14.1 | 40.9 | $0.00038 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s1 | structured | 74 | 89% (66/74) | 6,096 | 750 | 790 | 6.1 | 16.6 | 34.5 | $0.00037 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s1 | text | 74 | 78% (58/74) | 4,143 | 1,257 | 1,302 | 9.5 | 33.2 | 82.3 | $0.00058 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s2 | formal | 74 | 96% (71/74) | 6,720 | 737 | 779 | 6.2 | 13.2 | 45.6 | $0.00035 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s2 | structured | 74 | 95% (70/74) | 6,097 | 798 | 841 | 6.5 | 21.1 | 39.2 | $0.00040 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s2 | text | 74 | 89% (66/74) | 4,144 | 1,170 | 1,209 | 9.1 | 23.9 | 89.6 | $0.00054 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s3 | formal | 74 | 96% (71/74) | 6,729 | 581 | 623 | 5.3 | 13.4 | 35.5 | $0.00031 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s3 | structured | 74 | 92% (68/74) | 6,108 | 767 | 806 | 6.5 | 15.0 | 59.3 | $0.00039 | 0 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | S-s3 | text | 74 | 91% (67/74) | 4,151 | 830 | 871 | 7.0 | 24.5 | 61.3 | $0.00040 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | formal | 74 | 95% (70/74) | 18,098 | 1,172 | 1,219 | 9.1 | 18.5 | 73.7 | $0.00063 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | structured | 74 | 95% (70/74) | 19,098 | 1,577 | 1,616 | 11.4 | 15.6 | 108.0 | $0.00078 | 3 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | M-s1 | text | 74 | 95% (70/74) | 15,140 | 1,417 | 1,456 | 10.1 | 17.7 | 100.0 | $0.00069 | 1 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | formal | 74 | 96% (71/74) | 7,930 | 832 | 876 | 6.1 | 9.8 | 44.7 | $0.00043 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | structured | 74 | 96% (71/74) | 6,996 | 1,029 | 1,072 | 7.3 | 10.5 | 70.0 | $0.00051 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s1 | text | 74 | 95% (70/74) | 4,450 | 1,110 | 1,153 | 7.9 | 12.6 | 87.6 | $0.00053 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | formal | 74 | 96% (71/74) | 7,931 | 802 | 835 | 6.5 | 10.3 | 66.0 | $0.00041 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | structured | 74 | 97% (72/74) | 6,997 | 935 | 972 | 7.0 | 9.6 | 60.2 | $0.00046 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s2 | text | 74 | 97% (72/74) | 4,451 | 850 | 894 | 6.4 | 12.1 | 56.1 | $0.00042 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s3 | formal | 74 | 92% (68/74) | 7,940 | 754 | 789 | 6.4 | 10.8 | 56.1 | $0.00039 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s3 | structured | 74 | 93% (69/74) | 7,008 | 936 | 973 | 7.7 | 9.7 | 83.8 | $0.00046 | 0 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | S-s3 | text | 74 | 93% (69/74) | 4,458 | 1,054 | 1,102 | 8.2 | 21.4 | 89.9 | $0.00050 | 0 |

## Noticed but answered

Of the overreaching ANSWERs (UNDERDETERMINED key, model ANSWER), the share whose reply or reasoning trace flags ambiguity or a missing definition, by a rough keyword heuristic (see score.py; strict and wide lists; reply = the visible reply alone). Control: the same rate on ANSWER keys answered correctly, where nothing is missing. Assumptions stated (assume prompt): the share with a non-empty assumptions list, on overreaches and on the control; absent = the list was left out.

| model | layer | config | prompt | repr | overreaching ANSWERs | noticed (strict) | control (strict) | noticed (wide) | control (wide) | in reply | control (reply) | assumptions stated | control (assumptions) | assumptions absent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 122 | 92% (112/122) | 13% (15/119) | 98% (119/122) | 18% (21/119) | 1% (1/122) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 128 | 91% (116/128) | 17% (20/119) | 95% (121/128) | 25% (30/119) | 1% (1/128) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 151 | 84% (127/151) | 5% (6/119) | 95% (143/151) | 8% (10/119) | 0% (0/151) | 0% (0/119) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 28 | 93% (26/28) | 15% (42/286) | 96% (27/28) | 19% (54/286) | 4% (1/28) | 0% (0/286) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 33 | 94% (31/33) | 13% (38/285) | 100% (33/33) | 19% (54/285) | 0% (0/33) | 0% (0/285) | – | – | – |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 40 | 88% (35/40) | 11% (31/287) | 92% (37/40) | 16% (46/287) | 0% (0/40) | 0% (0/287) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 1 | 100% (1/1) | 23% (52/222) | 100% (1/1) | 27% (61/222) | 0% (0/1) | 0% (0/222) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 8 | 100% (8/8) | 21% (47/223) | 100% (8/8) | 25% (56/223) | 0% (0/8) | 0% (0/223) | – | – | – |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 28 | 100% (28/28) | 22% (50/223) | 100% (28/28) | 26% (57/223) | 4% (1/28) | 0% (0/223) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 0 | – | 26% (71/272) | – | 31% (83/272) | – | 0% (0/272) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 0 | – | 31% (84/272) | – | 36% (98/272) | – | 0% (0/272) | – | – | – |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 0 | – | 23% (62/270) | – | 29% (77/270) | – | 0% (0/270) | – | – | – |

## Step at layer 1: questions with min_layer 1, by layer shown

Correct at each layer (below min_layer the key is UNDERDETERMINED, so correct means abstaining; lenient: OUT_OF_SCOPE counts as abstaining), and the status mix.

| model | repr | layer | config | n | correct (lenient) | model statuses |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | L0 | decided | 144 | 49% (70/144) | ANSWER 74, UNDERDETERMINED 70 |
| deepseek/deepseek-v4.1-flash | formal | L1 | decided | 168 | 99% (167/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | formal | L2 | decided | 56 | 96% (54/56) | ANSWER 56 |
| deepseek/deepseek-v4.1-flash | formal | L3 | decided | 56 | 100% (56/56) | ANSWER 56 |
| deepseek/deepseek-v4.1-flash | structured | L0 | decided | 144 | 40% (58/144) | ANSWER 86, UNDERDETERMINED 57, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | structured | L1 | decided | 168 | 99% (166/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | structured | L2 | decided | 56 | 98% (55/56) | ANSWER 56 |
| deepseek/deepseek-v4.1-flash | structured | L3 | decided | 56 | 100% (56/56) | ANSWER 56 |
| deepseek/deepseek-v4.1-flash | text | L0 | decided | 144 | 31% (44/144) | ANSWER 100, UNDERDETERMINED 43, OUT_OF_SCOPE 1 |
| deepseek/deepseek-v4.1-flash | text | L1 | decided | 168 | 100% (168/168) | ANSWER 168 |
| deepseek/deepseek-v4.1-flash | text | L2 | decided | 56 | 98% (55/56) | ANSWER 55, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | text | L3 | decided | 56 | 100% (56/56) | ANSWER 56 |
(base prompt only.)

## Step at layer 2: questions with min_layer 2, by layer shown

Correct at each layer (below min_layer the key is UNDERDETERMINED, so correct means abstaining; lenient: OUT_OF_SCOPE counts as abstaining), and the status mix.

| model | repr | layer | config | n | correct (lenient) | model statuses |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | L0 | decided | 144 | 82% (118/144) | UNDERDETERMINED 77, OUT_OF_SCOPE 41, ANSWER 26 |
| deepseek/deepseek-v4.1-flash | formal | L1 | decided | 48 | 50% (24/48) | UNDERDETERMINED 24, ANSWER 24 |
| deepseek/deepseek-v4.1-flash | formal | L2 | decided | 144 | 90% (129/144) | ANSWER 129, AMBIGUOUS 14, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | formal | L3 | decided | 48 | 100% (48/48) | ANSWER 48 |
| deepseek/deepseek-v4.1-flash | structured | L0 | decided | 144 | 82% (118/144) | UNDERDETERMINED 74, OUT_OF_SCOPE 44, ANSWER 26 |
| deepseek/deepseek-v4.1-flash | structured | L1 | decided | 48 | 50% (24/48) | UNDERDETERMINED 24, ANSWER 24 |
| deepseek/deepseek-v4.1-flash | structured | L2 | decided | 144 | 90% (129/144) | ANSWER 129, AMBIGUOUS 11, UNDERDETERMINED 4 |
| deepseek/deepseek-v4.1-flash | structured | L3 | decided | 48 | 100% (48/48) | ANSWER 48 |
| deepseek/deepseek-v4.1-flash | text | L0 | decided | 144 | 79% (114/144) | UNDERDETERMINED 76, OUT_OF_SCOPE 38, ANSWER 30 |
| deepseek/deepseek-v4.1-flash | text | L1 | decided | 48 | 50% (24/48) | UNDERDETERMINED 24, ANSWER 24 |
| deepseek/deepseek-v4.1-flash | text | L2 | decided | 144 | 90% (129/144) | ANSWER 129, AMBIGUOUS 10, UNDERDETERMINED 5 |
| deepseek/deepseek-v4.1-flash | text | L3 | decided | 48 | 100% (48/48) | ANSWER 48 |
(base prompt only.)

## Step at layer 3: questions with min_layer 3, by layer shown

Correct at each layer (below min_layer the key is UNDERDETERMINED, so correct means abstaining; lenient: OUT_OF_SCOPE counts as abstaining), and the status mix.

| model | repr | layer | config | n | correct (lenient) | model statuses |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | formal | L0 | decided | 144 | 85% (122/144) | UNDERDETERMINED 117, ANSWER 22, OUT_OF_SCOPE 5 |
| deepseek/deepseek-v4.1-flash | formal | L1 | decided | 48 | 92% (44/48) | UNDERDETERMINED 28, OUT_OF_SCOPE 16, ANSWER 4 |
| deepseek/deepseek-v4.1-flash | formal | L2 | decided | 48 | 98% (47/48) | UNDERDETERMINED 41, OUT_OF_SCOPE 6, ANSWER 1 |
| deepseek/deepseek-v4.1-flash | formal | L3 | decided | 144 | 90% (129/144) | ANSWER 144 |
| deepseek/deepseek-v4.1-flash | structured | L0 | decided | 144 | 89% (128/144) | UNDERDETERMINED 128, ANSWER 16 |
| deepseek/deepseek-v4.1-flash | structured | L1 | decided | 48 | 81% (39/48) | UNDERDETERMINED 37, ANSWER 9, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | structured | L2 | decided | 48 | 83% (40/48) | UNDERDETERMINED 38, ANSWER 8, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | structured | L3 | decided | 144 | 90% (130/144) | ANSWER 139, PARSE 3, CONFLICT 2 |
| deepseek/deepseek-v4.1-flash | text | L0 | decided | 144 | 85% (123/144) | UNDERDETERMINED 121, ANSWER 21, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | text | L1 | decided | 48 | 67% (32/48) | UNDERDETERMINED 19, ANSWER 16, OUT_OF_SCOPE 13 |
| deepseek/deepseek-v4.1-flash | text | L2 | decided | 48 | 42% (20/48) | ANSWER 28, UNDERDETERMINED 20 |
| deepseek/deepseek-v4.1-flash | text | L3 | decided | 144 | 91% (131/144) | ANSWER 140, CONFLICT 3, PARSE 1 |
(base prompt only.)

## Paraphrases: same instances, one wording changed

A paraphrase template asks the instances of its source template with different wording. Overreach = later key: the share of overreaching ANSWERs equal to the decided key at min_layer (for Q11/Q17 at L0: the roll-up reading).

| model | layer | config | prompt | template | n | correct | overreach = later key | model statuses |
|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q11 | 72 | 0% (0/72) | 1% (1/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q11 | 72 | 100% (72/72) | – | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | Q17 | 72 | 100% (72/72) | – | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q11 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | Q17 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q11 | 24 | 100% (24/24) | – | ANSWER 24 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | Q17 | 24 | 100% (24/24) | – | ANSWER 24 |

## Status confusion (rows: key, columns: model)

**deepseek/deepseek-v4.1-flash**

| key \ model | ANSWER | AMBIGUOUS | CONFLICT | UNDERDETERMINED | OUT_OF_SCOPE | PARSE |
|---|---|---|---|---|---|---|
| ANSWER | 2717 | 0 | 0 | 1 | 0 | 0 |
| CONFLICT | 36 | 35 | 5 | 10 | 0 | 4 |
| UNDERDETERMINED | 539 | 0 | 0 | 1018 | 171 | 0 |
| OUT_OF_SCOPE | 0 | 0 | 0 | 0 | 192 | 0 |

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
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q21 | UNDERDETERMINED 72 | 2 | 100% (72/72) | UNDERDETERMINED 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q22 | UNDERDETERMINED 72 | 2 | 0% (0/72) | ANSWER 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q23 | UNDERDETERMINED 72 | 2 | 78% (56/72) | UNDERDETERMINED 56, OUT_OF_SCOPE 10, ANSWER 6 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q24 | UNDERDETERMINED 72 | 2 | 43% (31/72) | OUT_OF_SCOPE 41, UNDERDETERMINED 31 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q25 | UNDERDETERMINED 72 | 2 | 94% (68/72) | UNDERDETERMINED 68, ANSWER 4 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q26 | UNDERDETERMINED 72 | 2 | 0% (0/72) | OUT_OF_SCOPE 72 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q31 | UNDERDETERMINED 72 | 3 | 60% (43/72) | UNDERDETERMINED 43, ANSWER 29 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q32 | UNDERDETERMINED 72 | 3 | 88% (63/72) | UNDERDETERMINED 63, ANSWER 9 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q33 | UNDERDETERMINED 72 | 3 | 88% (63/72) | UNDERDETERMINED 63, ANSWER 9 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q34 | UNDERDETERMINED 72 | 3 | 83% (60/72) | UNDERDETERMINED 60, ANSWER 10, OUT_OF_SCOPE 2 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q35 | UNDERDETERMINED 72 | 3 | 93% (67/72) | UNDERDETERMINED 67, OUT_OF_SCOPE 5 |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | Q36 | UNDERDETERMINED 72 | 3 | 97% (70/72) | UNDERDETERMINED 70, ANSWER 2 |
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

Keys where the material holds both sides of a disagreement and nothing at the layer says which prevails. Strict: CONFLICT. AMBIGUOUS = both sides: the reading values are exactly the key's sides (the disagreement reported as two readings). No side picked (lenient): any status but ANSWER. An ANSWER picks a side: resolved = the value the next layer's resolution rule gives (L3 decided key), other = any other value. Engine-detected (compile mode): CONFLICT or a CONFLICT reading that the engine found by running the plan in the exclusion-enforced program, not declared by the model.

| model | layer | config | prompt | repr | n | CONFLICT | AMBIGUOUS = both sides | no side picked | ANSWER = resolved | ANSWER = other | engine-detected | statuses |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 15 | 0% (0/15) | 93% (14/15) | 100% (15/15) | 0 | 0 | 0 | AMBIGUOUS 14, UNDERDETERMINED 1 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 15 | 0% (0/15) | 73% (11/15) | 100% (15/15) | 0 | 0 | 0 | AMBIGUOUS 11, UNDERDETERMINED 4 |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 15 | 0% (0/15) | 67% (10/15) | 100% (15/15) | 0 | 0 | 0 | AMBIGUOUS 10, UNDERDETERMINED 5 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 15 | 0% (0/15) | 0% (0/15) | 0% (0/15) | 0 | 15 | 0 | ANSWER 15 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 15 | 13% (2/15) | 0% (0/15) | 33% (5/15) | 0 | 10 | 0 | ANSWER 10, PARSE 3, CONFLICT 2 |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 15 | 20% (3/15) | 0% (0/15) | 27% (4/15) | 0 | 11 | 0 | ANSWER 11, CONFLICT 3, PARSE 1 |

## Stability across repetitions

| model | layer | config | prompt | repr | question cells with ≥2 reps | same status every rep |
|---|---|---|---|---|---|---|
| deepseek/deepseek-v4.1-flash | L0 | decided | base | formal | 192 | 78% (149/192) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | structured | 192 | 86% (165/192) |
| deepseek/deepseek-v4.1-flash | L0 | decided | base | text | 192 | 79% (152/192) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | formal | 136 | 96% (131/136) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | structured | 136 | 95% (129/136) |
| deepseek/deepseek-v4.1-flash | L1 | decided | base | text | 136 | 92% (125/136) |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | formal | 64 | 91% (58/64) |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | structured | 64 | 88% (56/64) |
| deepseek/deepseek-v4.1-flash | L2 | decided | base | text | 64 | 86% (55/64) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | formal | 48 | 100% (48/48) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | structured | 48 | 96% (46/48) |
| deepseek/deepseek-v4.1-flash | L3 | decided | base | text | 48 | 92% (44/48) |

