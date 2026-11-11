## n = 4700: PB 6949623, opt 6948490, gap 1133

H has 1784 sources and 248 numbers up to n/2; S* differs from H in 13 numbers (H only) and 13 (S* only), all up to n/2.  Layer 4's residual has 54 members; 54 of them survive peeling the fiber members alone, 0 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 4 distinct in 162 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 137, 149, 233 | 137: 12,18,20,27,30; 149: 18,27,30; 233: 12,18,20 |
| c2 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c3 | 14 | 37, 43 | 37: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c4 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41, 43 | 3 | 21 (7) | 234 | yes | loss 234: drop 45x37, drop 45x41, add 42x37, add 42x41 | none |
| I2 | T11 | 137, 149, 233 | 1 | 11 (1) | 298 | yes | loss 298: drop 10x149, drop 15x149, add 9x149, add 14x149 | none |

#### I1 (T14) on 37, 41, 43

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | 42 [L4] | 3 |
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x37 + 3x41 + 0x43 = 234.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 39, 5: 6}.  Clean.
Subsets of the territory differences: 4 clean of 15.  Smallest clean ones have 2 numbers: drop 45x37, drop 45x41 (loss 3510).

#### I2 (T11) on 137, 149, 233

Pattern: 137: 12,18,20,27,30; 149: 18,27,30; 233: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 137 | - | - | 0 |
| 149 | 10 [L3], 15 [L3] | 9 [L3], 14 [L3] | 2 |
| 233 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x137 + 2x149 + 0x233 = 298.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 2}.  Clean.
Subsets of the territory differences: 7 clean of 15.  Smallest clean ones have 1 numbers: drop 10x149 (loss 1490); drop 15x149 (loss 2235).

#### All templates together: loss 532; template cores broken = True, new residual none; clean.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3510 | 2, 3276 | 234 | L4 |
| template 2 | 2, 3725 | 2, 3427 | 298 | L3 |
| smooth | 8, 13028 | 6, 9412 | 3616 | L4,L5,L6,L7 |
| unrelated fiber | 1, 1652 | 3, 4667 | -3015 | L4 |
| total | 13, 21915 | 13, 20782 | 1133 | gap 1133 |

Layer-4 differences: 13, of which 4 inside a template's fibers (9 outside: 1287 (smooth), 1375 (smooth), 28x53 (unrelated fiber), 30x53 (unrelated fiber), 27x59 (unrelated fiber), 1625 (smooth), 28x59 (unrelated fiber), 1666 (smooth), 1715 (smooth)).

