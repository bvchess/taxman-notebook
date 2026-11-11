## n = 4600: PB 6651728, opt 6650209, gap 1519

H has 1746 sources and 239 numbers up to n/2; S* differs from H in 17 numbers (H only) and 17 (S* only), all up to n/2.  Layer 4's residual has 135 members; 59 of them survive peeling the fiber members alone, 58 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 4 distinct in 159 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 137, 149, 229 | 137: 12,18,20,27,30; 149: 18,27,30; 229: 12,18,20 |
| c2 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c3 | 14 | 37, 43 | 37: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c4 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41, 43 | 3 | 21 (6) | 1782 | no | loss 1788: drop 45x37, drop 45x41, add 42x41 | none |
| I2 | T11 | 137, 149, 229 | 1 | 11 (1) | 298 | yes | loss 298: drop 10x149, drop 15x149, add 9x149, add 14x149 | none |

#### I1 (T14) on 37, 41, 43

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | 42 [L4] | 3 |
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | 36 [L5] | - | 36 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x37 + 3x41 + 36x43 = 1782.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x37']}, residual members gone {4: 8, 5: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 4 clean of 31.  Smallest clean ones have 2 numbers: drop 45x37, drop 45x41 (loss 3510).

#### I2 (T11) on 137, 149, 229

Pattern: 137: 12,18,20,27,30; 149: 18,27,30; 229: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 137 | - | - | 0 |
| 149 | 10 [L3], 15 [L3] | 9 [L3], 14 [L3] | 2 |
| 229 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x137 + 2x149 + 0x229 = 298.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 2}.  Clean.
Subsets of the territory differences: 7 clean of 15.  Smallest clean ones have 1 numbers: drop 10x149 (loss 1490); drop 15x149 (loss 2235).

#### All templates together: loss 2080; template cores broken = True, new residual {4: ['42x37']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 3, 5058 | 2, 3276 | 1782 | L4,L5 |
| template 2 | 2, 3725 | 2, 3427 | 298 | L3 |
| other residual fiber | 1, 2020 | 1, 1818 | 202 | L4 |
| smooth | 9, 14726 | 7, 10953 | 3773 | L4,L5,L6,L7 |
| unrelated fiber | 2, 3153 | 5, 7689 | -4536 | L3,L4,L5 |
| total | 17, 28682 | 17, 27163 | 1519 | gap 1519 |

Layer-4 differences: 16, of which 4 inside a template's fibers (12 outside: 28x47 (unrelated fiber), 1375 (smooth), 1430 (smooth), 28x53 (unrelated fiber), 18x83 (unrelated fiber), 20x79 (unrelated fiber), 1625 (smooth), 1666 (smooth), 1694 (smooth), 1715 (smooth), 18x101 (other residual fiber), 20x101 (other residual fiber)).

