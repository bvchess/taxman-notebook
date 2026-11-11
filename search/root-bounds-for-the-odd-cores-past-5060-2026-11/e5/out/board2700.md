## n = 2700: PB 2295987, opt 2295256, gap 731

H has 1026 sources and 142 numbers up to n/2; S* differs from H in 11 numbers (H only) and 11 (S* only), all up to n/2.  Layer 4's residual has 84 members; 14 of them survive peeling the fiber members alone, 40 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 79, 83, 131 | 79: 12,18,20,27,30; 83: 18,27,30; 131: 12,18,20 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T11 | 79, 83, 131 | 1 | 11 (1) | 16 | no | loss 948: drop 12x79 | none |

#### I1 (T11) on 79, 83, 131

Pattern: 79: 12,18,20,27,30; 83: 18,27,30; 131: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 79 | 12* [L4] | 16 [L5] | -4 |
| 83 | 16 [L5] | 12 [L4] | 4 |
| 131 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x79 + 4x83 + 0x131 = 16.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x83', '20x83'], 6: ['32x79']}, residual members gone {4: 5, 6: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 2 clean of 15.  Smallest clean ones have 1 numbers: drop 12x79 (loss 948).

#### All templates together: loss 16; template cores broken = True, new residual {4: ['12x83', '20x83'], 6: ['32x79']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 2276 | 2, 2260 | 16 | L4,L5 |
| other residual fiber | 1, 868 | 1, 837 | 31 | L4 |
| smooth | 8, 7584 | 5, 4382 | 3202 | L4,L5,L6,L7 |
| unrelated fiber | 0, 0 | 3, 2518 | -2518 | L4 |
| total | 11, 10728 | 11, 9997 | 731 | gap 731 |

Layer-4 differences: 12, of which 2 inside a template's fibers (10 outside: 28x29 (unrelated fiber), 27x31 (other residual fiber), 18x47 (unrelated fiber), 20x43 (unrelated fiber), 28x31 (other residual fiber), 875 (smooth), 884 (smooth), 950 (smooth), 988 (smooth), 1029 (smooth)).

