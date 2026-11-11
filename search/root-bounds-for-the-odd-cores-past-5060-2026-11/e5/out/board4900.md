## n = 4900: PB 7559194, opt 7557145, gap 2049

H has 1857 sources and 265 numbers up to n/2; S* differs from H in 20 numbers (H only) and 20 (S* only), all up to n/2.  Layer 4's residual has 137 members; 79 of them survive peeling the fiber members alone, 44 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 5 distinct in 175 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 149, 157, 241 | 149: 12,18,20,27,30; 157: 18,27,30; 241: 12,18,20 |
| c2 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c3 | 14 | 37, 43 | 37: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c4 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c5 | 23 | 59, 61, 67 | 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 67: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41, 43 | 3 | 21 (7) | 1788 | yes | loss 1788: drop 45x37, drop 45x41, add 42x41 | none |
| I2 | T23 | 59, 61, 67 | 1 | 23 (4) | -1514 | no | loss 201: drop 30x67, add 27x67 | none |
| I3 | T11 | 149, 157, 241 | 1 | 11 (1) | 974 | no | loss 1570: drop 10x157 | none |

#### I1 (T14) on 37, 41, 43

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | - | 45 |
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 45x37 + 3x41 + 0x43 = 1788.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 15, 5: 3}.  Clean.
Subsets of the territory differences: 2 clean of 7.  Smallest clean ones have 2 numbers: drop 45x37, drop 45x41 (loss 3510).

#### I2 (T23) on 59, 61, 67

Pattern: 59: 28,30,42,45,50,52,63,75,78; 61: 28,42,45,50,52,63,70,75,78; 67: 30,42,45,63,70.  Hangers: 27x61.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 59 | - | 27 [L4] | -27 |
| 61 | 28* [L4] | 30 [L4] | -2 |
| 67 | 30* [L4] | 27 [L4] | 3 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -27x59 + -2x61 + 3x67 = -1514.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x59', '30x61'], 5: ['81x59']}, residual members gone {4: 8}.  Not clean: it needs ? as well.
Subsets of the territory differences: 5 clean of 31.  Smallest clean ones have 1 numbers: drop 28x61 (loss 1708); drop 30x67 (loss 2010).

#### I3 (T11) on 149, 157, 241

Pattern: 149: 12,18,20,27,30; 157: 18,27,30; 241: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 149 | 12* [L4] | 16 [L5] | -4 |
| 157 | 10 [L3] | - | 10 |
| 241 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x149 + 10x157 + 0x241 = 974.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {6: ['32x149']}, residual members gone {4: 8}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 7.  Smallest clean ones have 1 numbers: drop 10x157 (loss 1570); drop 12x149 (loss 1788).

#### All templates together: loss 1248; template cores broken = True, new residual {4: ['27x59', '30x61'], 5: ['81x59'], 6: ['32x149']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3510 | 1, 1722 | 1788 | L4 |
| template 2 | 2, 3718 | 3, 5232 | -1514 | L4 |
| template 3 | 2, 3358 | 1, 2384 | 974 | L3,L4,L5 |
| other residual fiber | 2, 3152 | 1, 1488 | 1664 | L4,L6 |
| smooth | 11, 18825 | 9, 14268 | 4557 | L4,L5,L6,L7 |
| unrelated fiber | 1, 2416 | 5, 7836 | -5420 | L3,L4,L5 |
| total | 20, 34979 | 20, 32930 | 2049 | gap 2049 |

Layer-4 differences: 22, of which 9 inside a template's fibers (13 outside: 1375 (smooth), 50x29 (unrelated fiber), 28x53 (unrelated fiber), 50x31 (other residual fiber), 20x79 (unrelated fiber), 18x89 (other residual fiber), 1617 (smooth), 1625 (smooth), 1666 (smooth), 1694 (smooth), 1715 (smooth), 12x151 (unrelated fiber), 1925 (smooth)).

