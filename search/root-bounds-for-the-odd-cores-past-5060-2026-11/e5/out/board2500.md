## n = 2500: PB 1972506, opt 1971458, gap 1048

H has 946 sources and 140 numbers up to n/2; S* differs from H in 11 numbers (H only) and 11 (S* only), all up to n/2.  Layer 4's residual has 105 members; 51 of them survive peeling the fiber members alone, 52 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 2 distinct in 152 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 71, 79, 113 | 71: 12,18,20,27,30; 79: 18,27,30; 113: 12,18,20 |
| c2 | 18 | 29, 31 | 29: 28,30,42,45,50,52,63,75,78; 31: 28,30,42,45,50,52,63,75,78 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T23 | 29, 31 | 1 | 18 (5) | -752 | no | loss 868: drop 28x31 | none |
| I2 | T11 | 71, 79, 113 | 1 | 11 (1) | 150 | no | loss 1065: drop 15x71 | none |

#### I1 (T23) on 29, 31

Pattern: 29: 28,30,42,45,50,52,63,75,78; 31: 28,30,42,45,50,52,63,75,78.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | - | 27 [L4] | -27 |
| 31 | 28* [L4] | 27 [L4] | 1 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -27x29 + 1x31 = -752.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x29', '27x31'], 5: ['81x29']}, residual members gone {4: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 1 clean of 7.  Smallest clean ones have 1 numbers: drop 28x31 (loss 868).

#### I2 (T11) on 71, 79, 113

Pattern: 71: 12,18,20,27,30; 79: 18,27,30; 113: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 71 | 15 [L3] | 14 [L3] | 1 |
| 79 | 15 [L3] | 14 [L3] | 1 |
| 113 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 1x71 + 1x79 + 0x113 = 150.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {3: ['21x43', '931', '14x67', '21x47', '14x71', '1058', '1083', '35x31', '1127', '39x29', '1173', '25x47', '38x31', '1183', '39x31', '33x37', '26x47', '1235', '1265', '21x61', '35x37', '1309', '1311', '22x61', '21x67', '33x43', '49x29', '46x31', '39x37', '1445', '34x43', '1463', '22x67', '51x29', '21x71', '1495', '35x43', '49x31', '25x61', '1547', '22x71', '1573', '26x61', '1587', '55x29', '34x47', '1615', '38x43', '35x47', '25x67', '55x31', '1729', '57x31', '1771', '25x71', '1805', '49x37', '39x47', '1859', '65x29', '1955', '33x61', '65x31', '2023', '55x37', '2057', '2093', '49x43', '35x61', '69x31', '2185', '51x43', '2197', '33x67', '77x29', '2261', '2299', '49x47', '33x71', '35x67', '55x43', '39x61', '77x31', '51x47', '65x37', '2431', '57x43', '85x29', '35x71'], 4: ['20x79', '28x71', '28x79']}, residual members gone {4: 5}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 15.  Smallest clean ones have 1 numbers: drop 15x71 (loss 1065); drop 15x79 (loss 1185).

#### All templates together: loss -602; template cores broken = True, new residual {3: ['21x43', '931', '14x67', '21x47', '14x71', '1058', '1083', '35x31', '1127', '39x29', '1173', '25x47', '38x31', '1183', '39x31', '33x37', '26x47', '1235', '1265', '21x61', '35x37', '1309', '1311', '22x61', '21x67', '33x43', '49x29', '46x31', '39x37', '1445', '34x43', '1463', '22x67', '51x29', '21x71', '1495', '35x43', '49x31', '25x61', '1547', '22x71', '1573', '26x61', '1587', '55x29', '34x47', '1615', '38x43', '35x47', '25x67', '55x31', '1729', '57x31', '1771', '25x71', '1805', '49x37', '39x47', '1859', '65x29', '1955', '33x61', '65x31', '2023', '55x37', '2057', '2093', '49x43', '35x61', '69x31', '2185', '51x43', '2197', '33x67', '77x29', '2261', '2299', '49x47', '33x71', '35x67', '55x43', '39x61', '77x31', '51x47', '65x37', '2431', '57x43', '85x29', '35x71'], 4: ['27x29', '27x31', '20x79', '28x71', '28x79'], 5: ['81x29']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 868 | 2, 1620 | -752 | L4 |
| template 2 | 2, 2250 | 2, 2100 | 150 | L3 |
| smooth | 7, 6626 | 4, 3403 | 3223 | L3,L4,L5 |
| unrelated fiber | 1, 938 | 3, 2511 | -1573 | L3,L4 |
| total | 11, 10682 | 11, 9634 | 1048 | gap 1048 |

Layer-4 differences: 9, of which 3 inside a template's fibers (6 outside: 12x61 (unrelated fiber), 770 (smooth), 18x43 (unrelated fiber), 850 (smooth), 855 (smooth), 975 (smooth)).

