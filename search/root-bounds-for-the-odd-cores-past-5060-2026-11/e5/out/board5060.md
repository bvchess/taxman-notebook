## n = 5060: PB 8056178, opt 8053621, gap 2557

H has 1921 sources and 268 numbers up to n/2; S* differs from H in 17 numbers (H only) and 17 (S* only), all up to n/2.  Layer 4's residual has 129 members; 77 of them survive peeling the fiber members alone, 47 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 5 distinct in 172 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 151, 163, 251 | 151: 12,18,20,27,30; 163: 18,27,30; 251: 12,18,20 |
| c2 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c3 | 14 | 41, 47 | 41: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105 |
| c4 | 14 | 43, 47 | 43: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105 |
| c5 | 23 | 59, 61, 71 | 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 71: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 41, 43, 47 | 3 | 21 (6) | 252 | no | loss 2058: drop 45x41, drop 45x43, add 42x41 | drop 1690 (smooth) |
| I2 | T23 | 59, 61, 71 | 1 | 23 (5) | 71 | no | loss 1708: drop 28x61 | drop 1638 (smooth), drop 1690 (smooth), drop 1710 (smooth), drop 1911 (smooth), drop 1950 (smooth) |
| I3 | T11 | 151, 163, 251 | 1 | 11 (1) | 1026 | no | loss 1630: drop 10x163 | drop 1710 (smooth), drop 56x31 (unrelated fiber), drop 1950 (smooth), drop 1980 (smooth), drop 2142 (smooth), drop 16x157 (unrelated fiber) |

#### I1 (T14) on 41, 43, 47

Pattern: 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | 45* [L4] | 42 [L4] | 3 |
| 47 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x41 + 3x43 + 0x47 = 252.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x43']}, residual members gone {4: 8}.  Not clean: it needs drop 1690 (smooth) as well.
Subsets of the territory differences: 2 clean of 15.  Smallest clean ones have 2 numbers: drop 45x41, drop 45x43 (loss 3780).

#### I2 (T23) on 59, 61, 71

Pattern: 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 71: 30,42,45,63,70.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 59 | 30* [L4] | 35 [L3] | -5 |
| 61 | 28* [L4], 35 [L3] | 27 [L4], 30 [L4] | 6 |
| 71 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -5x59 + 6x61 + 0x71 = 71.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['70x59'], 5: ['81x61']}, residual members gone {4: 10, 5: 4}.  Not clean: it needs drop 1638 (smooth), drop 1690 (smooth), drop 1710 (smooth), drop 1911 (smooth), drop 1950 (smooth) as well.
Subsets of the territory differences: 9 clean of 63.  Smallest clean ones have 1 numbers: drop 28x61 (loss 1708); drop 30x59 (loss 1770); drop 35x61 (loss 2135).

#### I3 (T11) on 151, 163, 251

Pattern: 151: 12,18,20,27,30; 163: 18,27,30; 251: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 151 | 12* [L4] | 16 [L5] | -4 |
| 163 | 10 [L3] | - | 10 |
| 251 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x151 + 10x163 + 0x251 = 1026.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {6: ['32x151']}, residual members gone {4: 8}.  Not clean: it needs drop 1710 (smooth), drop 56x31 (unrelated fiber), drop 1950 (smooth), drop 1980 (smooth), drop 2142 (smooth), drop 16x157 (unrelated fiber) as well.
Subsets of the territory differences: 3 clean of 7.  Smallest clean ones have 1 numbers: drop 10x163 (loss 1630); drop 12x151 (loss 1812).

#### All templates together: loss 1349; template cores broken = True, new residual {4: ['42x43', '70x59'], 5: ['81x61'], 6: ['32x151']}; not clean, it needs drop 1638 (smooth), drop 1690 (smooth), drop 1710 (smooth), drop 56x31 (unrelated fiber), drop 1911 (smooth), drop 1950 (smooth), drop 1980 (smooth), drop 2142 (smooth), drop 16x157 (unrelated fiber) as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3780 | 2, 3528 | 252 | L4 |
| template 2 | 3, 5613 | 3, 5542 | 71 | L3,L4 |
| template 3 | 2, 3442 | 1, 2416 | 1026 | L3,L4,L5 |
| smooth | 8, 14653 | 7, 10993 | 3660 | L4,L5,L6,L7 |
| unrelated fiber | 2, 4248 | 4, 6700 | -2452 | L3,L4,L5 |
| total | 17, 31736 | 17, 29179 | 2557 | gap 2557 |

Layer-4 differences: 15, of which 9 inside a template's fibers (6 outside: 12x131 (unrelated fiber), 1625 (smooth), 1666 (smooth), 1690 (smooth), 12x157 (unrelated fiber), 1911 (smooth)).

