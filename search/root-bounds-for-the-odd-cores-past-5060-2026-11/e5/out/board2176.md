## n = 2176: PB 1494928, opt 1494161, gap 767

H has 823 sources and 125 numbers up to n/2; S* differs from H in 11 numbers (H only) and 11 (S* only), all up to n/2.  Layer 4's residual has 109 members; 16 of them survive peeling the fiber members alone, 66 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 61, 67, 107 | 61: 12,18,20,27,30; 67: 18,27,30; 107: 12,18,20 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T11 | 61, 67, 107 | 1 | 11 (1) | 24 | no | loss 732: drop 12x61 | none |

#### I1 (T11) on 61, 67, 107

Pattern: 61: 12,18,20,27,30; 67: 18,27,30; 107: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 61 | 12* [L4] | 16 [L5] | -4 |
| 67 | 16 [L5] | 12 [L4] | 4 |
| 107 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x61 + 4x67 + 0x107 = 24.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x67', '20x67'], 6: ['32x61']}, residual members gone {4: 5, 6: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 2 clean of 15.  Smallest clean ones have 1 numbers: drop 12x61 (loss 732).

#### All templates together: loss 24; template cores broken = True, new residual {4: ['12x67', '20x67'], 6: ['32x61']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 1804 | 2, 1780 | 24 | L4,L5 |
| smooth | 9, 6923 | 6, 4182 | 2741 | L3,L4,L5,L6 |
| unrelated fiber | 0, 0 | 3, 1998 | -1998 | L4,L5 |
| total | 11, 8727 | 11, 7960 | 767 | gap 767 |

Layer-4 differences: 10, of which 2 inside a template's fibers (8 outside: 12x53 (unrelated fiber), 644 (smooth), 650 (smooth), 18x37 (unrelated fiber), 676 (smooth), 686 (smooth), 690 (smooth), 836 (smooth)).

