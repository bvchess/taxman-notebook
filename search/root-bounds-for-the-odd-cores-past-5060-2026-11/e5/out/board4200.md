## n = 4200: PB 5552033, opt 5550660, gap 1373

H has 1594 sources and 222 numbers up to n/2; S* differs from H in 15 numbers (H only) and 15 (S* only), all up to n/2.  Layer 4's residual has 116 members; 58 of them survive peeling the fiber members alone, 38 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 3 distinct in 155 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 127, 137, 199 | 127: 12,18,20,27,30; 137: 18,27,30; 199: 12,18,20 |
| c2 | 11 | 127, 131, 137, 199 | 127: 12,20,30; 131: 18,27; 137: 18,27,30; 199: 12,18,20 |
| c3 | 23 | 47, 53, 59 | 47: 28,30,42,45,50,52,63,75,78; 53: 28,42,45,50,52,63,70,75,78; 59: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T23 | 47, 53, 59 | 1 | 23 (5) | 1316 | yes | loss 1316: drop 28x47 | none |
| I2 | T11 | 127, 131, 137, 199 | 2 | 13 (1) | 1728 | yes | loss 942: drop 15x131, drop 10x199, add 9x131, add 14x131 | none |

#### I1 (T23) on 47, 53, 59

Pattern: 47: 28,30,42,45,50,52,63,75,78; 53: 28,42,45,50,52,63,70,75,78; 59: 30,42,45,63,70.  Hangers: 27x53.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 47 | 28* [L4] | - | 28 |
| 53 | - | - | 0 |
| 59 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 28x47 + 0x53 + 0x59 = 1316.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 9}.  Clean.
Subsets of the territory differences: 1 clean of 1.  Smallest clean ones have 1 numbers: drop 28x47 (loss 1316).

#### I2 (T11) on 127, 131, 137, 199

Pattern: 127: 12,18,20,27,30; 131: 18,27; 137: 18,27,30; 199: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 127 | - | - | 0 |
| 131 | 6 [L3], 15 [L3] | 9 [L3], 14 [L3] | -2 |
| 137 | - | - | 0 |
| 199 | 10 [L3] | - | 10 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x127 + -2x131 + 0x137 + 10x199 = 1728.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 4}.  Clean.
Subsets of the territory differences: 10 clean of 31.  Smallest clean ones have 1 numbers: drop 10x199 (loss 1990).

#### All templates together: loss 3044; template cores broken = True, new residual none; clean.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1316 | 0, 0 | 1316 | L4 |
| template 2 | 3, 4741 | 2, 3013 | 1728 | L3 |
| other residual fiber | 1, 1488 | 1, 1984 | -496 | L6,L7 |
| smooth | 10, 15432 | 10, 13653 | 1779 | L4,L5,L6,L7,L8 |
| unrelated fiber | 0, 0 | 2, 2954 | -2954 | L3,L4 |
| total | 15, 22977 | 15, 21604 | 1373 | gap 1373 |

Layer-4 differences: 9, of which 1 inside a template's fibers (8 outside: 1071 (smooth), 1274 (smooth), 12x107 (unrelated fiber), 1365 (smooth), 1375 (smooth), 1425 (smooth), 1449 (smooth), 1617 (smooth)).

