## n = 4100: PB 5290029, opt 5288819, gap 1210

H has 1559 sources and 214 numbers up to n/2; S* differs from H in 9 numbers (H only) and 9 (S* only), all up to n/2.  Layer 4's residual has 92 members; 15 of them survive peeling the fiber members alone, 38 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 113, 127, 199 | 113: 12,18,20,27,30; 127: 18,27,30; 199: 12,18,20 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T11 | 113, 127, 199 | 1 | 11 (2) | 56 | no | loss 1356: drop 12x113 | none |

#### I1 (T11) on 113, 127, 199

Pattern: 113: 12,18,20,27,30; 127: 18,27,30; 199: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 113 | 12* [L4] | 16 [L5] | -4 |
| 127 | 16 [L5] | 12 [L4] | 4 |
| 199 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x113 + 4x127 + 0x199 = 56.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x127', '20x127'], 5: ['16x113', '24x113'], 6: ['32x113']}, residual members gone {4: 5, 6: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 2 clean of 15.  Smallest clean ones have 1 numbers: drop 12x113 (loss 1356).

#### All templates together: loss 56; template cores broken = True, new residual {4: ['12x127', '20x127'], 5: ['16x113', '24x113'], 6: ['32x113']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3388 | 2, 3332 | 56 | L4,L5 |
| smooth | 7, 10843 | 5, 6633 | 4210 | L4,L5,L7 |
| unrelated fiber | 0, 0 | 2, 3056 | -3056 | L4,L5 |
| total | 9, 14231 | 9, 13021 | 1210 | gap 1210 |

Layer-4 differences: 10, of which 2 inside a template's fibers (8 outside: 1122 (smooth), 1274 (smooth), 28x47 (unrelated fiber), 1330 (smooth), 1365 (smooth), 1375 (smooth), 1444 (smooth), 1449 (smooth)).

