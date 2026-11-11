## n = 4300: PB 5814506, opt 5812870, gap 1636

H has 1630 sources and 228 numbers up to n/2; S* differs from H in 16 numbers (H only) and 16 (S* only), all up to n/2.  Layer 4's residual has 16 members; 16 of them survive peeling the fiber members alone, 0 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 2 distinct in 153 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 127, 137, 211 | 127: 12,18,20,27,30; 137: 18,27,30; 211: 12,18,20 |
| c2 | 11 | 127, 131, 137, 211 | 127: 12,20,30; 131: 18,27; 137: 18,27,30; 211: 12,18,20 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T11 | 127, 131, 137, 211 | 2 | 13 (1) | 274 | yes | loss 274: drop 10x137, drop 15x137, add 9x137, add 14x137 | none |

#### I1 (T11) on 127, 131, 137, 211

Pattern: 127: 12,18,20,27,30; 131: 18,27; 137: 18,27,30; 211: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 127 | - | - | 0 |
| 131 | - | - | 0 |
| 137 | 10 [L3], 15 [L3] | 9 [L3], 14 [L3] | 2 |
| 211 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x127 + 0x131 + 2x137 + 0x211 = 274.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 16}.  Clean.
Subsets of the territory differences: 7 clean of 15.  Smallest clean ones have 1 numbers: drop 10x137 (loss 1370); drop 15x137 (loss 2055).

#### All templates together: loss 274; template cores broken = True, new residual none; clean.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3425 | 2, 3151 | 274 | L3 |
| smooth | 12, 19224 | 10, 15102 | 4122 | L4,L5,L7,L8,L9,L10 |
| unrelated fiber | 2, 2832 | 4, 5592 | -2760 | L4,L5,L6 |
| total | 16, 25481 | 16, 23845 | 1636 | gap 1636 |

Layer-4 differences: 8, of which 0 inside a template's fibers (8 outside: 28x47 (unrelated fiber), 1375 (smooth), 30x47 (unrelated fiber), 20x71 (unrelated fiber), 18x79 (unrelated fiber), 1449 (smooth), 1617 (smooth), 1715 (smooth)).

