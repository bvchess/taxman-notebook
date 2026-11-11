## n = 4400: PB 6088036, opt 6085856, gap 2180

H has 1667 sources and 234 numbers up to n/2; S* differs from H in 16 numbers (H only) and 16 (S* only), all up to n/2.  Layer 4's residual has 141 members; 50 of them survive peeling the fiber members alone, 56 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 7 distinct in 193 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 131, 137, 211 | 131: 12,18,20,27,30; 137: 18,27,30; 211: 12,18,20 |
| c2 | 12 | 127, 131, 359 | 127: 8,18,20,27,30; 131: 12,18,20,27,30; 359: 8,12 |
| c3 | 13 | 127, 131, 137, 359 | 127: 8,18,20,27,30; 131: 12,20,30; 137: 18,27,30; 359: 8,12 |
| c4 | 13 | 127, 137, 211, 359 | 127: 8,18,20,27,30; 137: 18,27,30; 211: 12,18,20; 359: 8,12 |
| c5 | 14 | 127, 131, 211, 547 | 127: 8,18,20,27,30; 131: 12,18,20,27,30; 211: 12,18,20; 547: 8 |
| c6 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c7 | 15 | 127, 131, 137, 211, 547 | 127: 8,18,20,27,30; 131: 12,20,30; 137: 18,27,30; 211: 12,18,20; 547: 8 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41 | 1 | 14 (4) | 111 | no | loss 1665: drop 45x37 | none |
| I2 | T11 | 127, 131, 137, 211, 359, 547 | 6 | 19 (2) | 659 | no | loss 2207: drop 12x131, drop 15x127, add 10x127 | none |

#### I1 (T14) on 37, 41

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | 42 [L4] | 3 |
| 41 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x37 + 0x41 = 111.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x37']}, residual members gone {4: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 1 clean of 3.  Smallest clean ones have 1 numbers: drop 45x37 (loss 1665).

#### I2 (T11) on 127, 131, 137, 211, 359, 547

Pattern: 127: 8,18,20,27,30; 131: 12,18,20,27,30; 137: 18,27,30; 211: 12,18,20; 359: 8,12; 547: 8.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 127 | 15 [L3] | 10 [L3] | 5 |
| 131 | 12* [L4] | 16 [L5] | -4 |
| 137 | 16 [L5] | 12 [L4] | 4 |
| 211 | - | - | 0 |
| 359 | - | - | 0 |
| 547 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 5x127 + -4x131 + 4x137 + 0x211 + 0x359 + 0x547 = 659.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x137', '20x137'], 6: ['32x131']}, residual members gone {4: 8, 6: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 4 clean of 63.  Smallest clean ones have 2 numbers: drop 12x131, drop 15x127 (loss 3477).

#### All templates together: loss 770; template cores broken = True, new residual {4: ['42x37', '12x137', '20x137'], 6: ['32x131']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1665 | 1, 1554 | 111 | L4 |
| template 2 | 3, 5669 | 3, 5010 | 659 | L3,L4,L5 |
| other residual fiber | 1, 1410 | 2, 2780 | -1370 | L4,L5 |
| smooth | 10, 15673 | 8, 11503 | 4170 | L4,L5,L6,L7 |
| unrelated fiber | 1, 1422 | 2, 2812 | -1390 | L4,L6 |
| total | 16, 25839 | 16, 23659 | 2180 | gap 2180 |

Layer-4 differences: 13, of which 4 inside a template's fibers (9 outside: 28x47 (other residual fiber), 1326 (smooth), 1375 (smooth), 30x47 (other residual fiber), 20x71 (unrelated fiber), 18x79 (unrelated fiber), 1482 (smooth), 1518 (smooth), 1715 (smooth)).

