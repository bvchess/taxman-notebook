## n = 2600: PB 2131409, opt 2130970, gap 439

H has 986 sources and 141 numbers up to n/2; S* differs from H in 13 numbers (H only) and 13 (S* only), all up to n/2.  Layer 4's residual has 97 members; 14 of them survive peeling the fiber members alone, 56 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 73, 79, 127 | 73: 12,18,20,27,30; 79: 18,27,30; 127: 12,18,20 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T11 | 73, 79, 127 | 1 | 11 (1) | 24 | no | loss 876: drop 12x73 | none |

#### I1 (T11) on 73, 79, 127

Pattern: 73: 12,18,20,27,30; 79: 18,27,30; 127: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 73 | 12* [L4] | 16 [L5] | -4 |
| 79 | 16 [L5] | 12 [L4] | 4 |
| 127 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x73 + 4x79 + 0x127 = 24.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x79', '20x79']}, residual members gone {4: 5}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 15.  Smallest clean ones have 1 numbers: drop 12x73 (loss 876).

#### All templates together: loss 24; template cores broken = True, new residual {4: ['12x79', '20x79']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 2140 | 2, 2116 | 24 | L4,L5 |
| other residual fiber | 4, 3811 | 4, 3894 | -83 | L3,L4,L5 |
| smooth | 5, 4624 | 3, 2671 | 1953 | L4,L5,L6 |
| unrelated fiber | 2, 2132 | 4, 3587 | -1455 | L3,L4,L5 |
| total | 13, 12707 | 13, 12268 | 439 | gap 439 |

Layer-4 differences: 16, of which 2 inside a template's fibers (14 outside: 765 (smooth), 12x67 (unrelated fiber), 20x41 (unrelated fiber), 27x31 (other residual fiber), 18x47 (other residual fiber), 855 (smooth), 858 (smooth), 20x43 (unrelated fiber), 28x31 (other residual fiber), 875 (smooth), 30x31 (other residual fiber), 27x37 (other residual fiber), 20x53 (unrelated fiber), 30x37 (other residual fiber)).

