## n = 4800: PB 7249863, opt 7247978, gap 1885

H has 1822 sources and 255 numbers up to n/2; S* differs from H in 20 numbers (H only) and 20 (S* only), all up to n/2.  Layer 4's residual has 132 members; 73 of them survive peeling the fiber members alone, 45 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 5 distinct in 158 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 139, 151, 239 | 139: 12,18,20,27,30; 151: 18,27,30; 239: 12,18,20 |
| c2 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c3 | 14 | 37, 43 | 37: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c4 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c5 | 23 | 59, 61, 67 | 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 67: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41, 43 | 3 | 21 (7) | 234 | yes | loss 234: drop 45x37, drop 45x41, add 42x37, add 42x41 | none |
| I2 | T23 | 59, 61, 67 | 1 | 23 (4) | 59 | yes | loss 59: drop 28x59, add 27x59 | none |
| I3 | T11 | 139, 151, 239 | 1 | 11 (1) | 954 | no | loss 1510: drop 10x151 | none |

#### I1 (T14) on 37, 41, 43

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | 42 [L4] | 3 |
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x37 + 3x41 + 0x43 = 234.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 15, 5: 6}.  Clean.
Subsets of the territory differences: 4 clean of 15.  Smallest clean ones have 2 numbers: drop 45x37, drop 45x41 (loss 3510).

#### I2 (T23) on 59, 61, 67

Pattern: 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 67: 30,42,45,63,70.  Hangers: 27x61.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 59 | 28* [L4] | 27 [L4] | 1 |
| 61 | - | - | 0 |
| 67 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 1x59 + 0x61 + 0x67 = 59.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 9, 5: 5}.  Clean.
Subsets of the territory differences: 2 clean of 3.  Smallest clean ones have 1 numbers: drop 28x59 (loss 1652).

#### I3 (T11) on 139, 151, 239

Pattern: 139: 12,18,20,27,30; 151: 18,27,30; 239: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 139 | 12* [L4] | 16 [L5] | -4 |
| 151 | 10 [L3] | - | 10 |
| 239 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x139 + 10x151 + 0x239 = 954.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {6: ['32x139']}, residual members gone {4: 8}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 7.  Smallest clean ones have 1 numbers: drop 10x151 (loss 1510); drop 12x139 (loss 1668).

#### All templates together: loss 1247; template cores broken = True, new residual {6: ['32x139']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3510 | 2, 3276 | 234 | L4 |
| template 2 | 1, 1652 | 1, 1593 | 59 | L4 |
| template 3 | 2, 3178 | 1, 2224 | 954 | L3,L4,L5 |
| other residual fiber | 1, 1550 | 1, 1488 | 62 | L4,L6 |
| smooth | 13, 21451 | 10, 15467 | 5984 | L4,L5,L6,L7 |
| unrelated fiber | 1, 2384 | 5, 7792 | -5408 | L3,L4,L5 |
| total | 20, 33725 | 20, 31840 | 1885 | gap 1885 |

Layer-4 differences: 16, of which 7 inside a template's fibers (9 outside: 50x29 (unrelated fiber), 28x53 (unrelated fiber), 50x31 (other residual fiber), 20x79 (unrelated fiber), 1666 (smooth), 1683 (smooth), 1694 (smooth), 1715 (smooth), 12x149 (unrelated fiber)).

