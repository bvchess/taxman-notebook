## n = 3200: PB 3227369, opt 3226356, gap 1013

H has 1211 sources and 178 numbers up to n/2; S* differs from H in 11 numbers (H only) and 11 (S* only), all up to n/2.  Layer 4's residual has 112 members; 54 of them survive peeling the fiber members alone, 51 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 23 | 37, 41, 43 | 37: 28,30,42,45,50,52,63,75,78; 41: 28,42,45,50,52,63,70,75,78; 43: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T23 | 37, 41, 43 | 1 | 23 (5) | -948 | no | loss 37: drop 28x37, add 27x37 | none |

#### I1 (T23) on 37, 41, 43

Pattern: 37: 28,30,42,45,50,52,63,75,78; 41: 28,42,45,50,52,63,70,75,78; 43: 30,42,45,63,70.  Hangers: 27x41.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 28* [L4] | 27 [L4] | 1 |
| 41 | 28* [L4] | 30 [L4] | -2 |
| 43 | 30* [L4] | 24 [L5], 27 [L4] | -21 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 1x37 + -2x41 + -21x43 = -948.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['30x41'], 5: ['24x43', '36x43', '54x43', '56x43'], 6: ['72x43']}, residual members gone {4: 64}.  Not clean: it needs ? as well.
Subsets of the territory differences: 17 clean of 127.  Smallest clean ones have 1 numbers: drop 28x37 (loss 1036); drop 28x41 (loss 1148); drop 30x43 (loss 1290).

#### All templates together: loss -948; template cores broken = True, new residual {4: ['30x41'], 5: ['24x43', '36x43', '54x43', '56x43'], 6: ['72x43']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 3, 3474 | 4, 4422 | -948 | L4,L5 |
| other residual fiber | 2, 2465 | 1, 1218 | 1247 | L4,L5 |
| smooth | 5, 5930 | 4, 4216 | 1714 | L4,L5,L6,L7 |
| unrelated fiber | 1, 1116 | 2, 2116 | -1000 | L4,L5 |
| total | 11, 12985 | 11, 11972 | 1013 | gap 1013 |

Layer-4 differences: 10, of which 6 inside a template's fibers (4 outside: 12x73 (unrelated fiber), 1029 (smooth), 42x29 (other residual fiber), 45x29 (other residual fiber)).

