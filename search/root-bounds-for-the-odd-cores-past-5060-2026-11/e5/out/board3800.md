## n = 3800: PB 4552838, opt 4551564, gap 1274

H has 1445 sources and 205 numbers up to n/2; S* differs from H in 14 numbers (H only) and 14 (S* only), all up to n/2.  Layer 4's residual has 121 members; 51 of them survive peeling the fiber members alone, 52 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 23 | 43, 47, 53 | 43: 28,30,42,45,50,52,63,75,78; 47: 28,42,45,50,52,63,70,75,78; 53: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T23 | 43, 47, 53 | 1 | 23 (5) | 1257 | no | loss 1204: drop 28x43 | none |

#### I1 (T23) on 43, 47, 53

Pattern: 43: 28,30,42,45,50,52,63,75,78; 47: 28,42,45,50,52,63,70,75,78; 53: 30,42,45,63,70.  Hangers: 27x47.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 43 | 28* [L4] | - | 28 |
| 47 | - | - | 0 |
| 53 | 28 [L4] | 27 [L4] | 1 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 28x43 + 0x47 + 1x53 = 1257.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x53'], 5: ['36x53', '54x53']}, residual members gone {4: 15, 5: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 2 clean of 7.  Smallest clean ones have 1 numbers: drop 28x43 (loss 1204).

#### All templates together: loss 1257; template cores broken = True, new residual {4: ['27x53'], 5: ['36x53', '54x53']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 2688 | 1, 1431 | 1257 | L4 |
| other residual fiber | 1, 1519 | 0, 0 | 1519 | L3 |
| smooth | 10, 13526 | 11, 13621 | -95 | L4,L5,L6 |
| unrelated fiber | 1, 1220 | 2, 2627 | -1407 | L3,L4 |
| total | 14, 18953 | 14, 17679 | 1274 | gap 1274 |

Layer-4 differences: 9, of which 3 inside a template's fibers (6 outside: 1078 (smooth), 1196 (smooth), 18x67 (unrelated fiber), 20x61 (unrelated fiber), 1274 (smooth), 1287 (smooth)).

