## n = 4000: PB 5036080, opt 5034874, gap 1206

H has 1519 sources and 210 numbers up to n/2; S* differs from H in 10 numbers (H only) and 10 (S* only), all up to n/2.  Layer 4's residual has 93 members; 46 of them survive peeling the fiber members alone, 31 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 14 | 31, 37 | 31: 45,50,63,70,75,98,105; 37: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 31, 37 | 1 | 14 (5) | 1395 | yes | loss 1395: drop 45x31 | none |

#### I1 (T14) on 31, 37

Pattern: 31: 45,50,63,70,75,98,105; 37: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 31 | 45* [L4] | - | 45 |
| 37 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 45x31 + 0x37 = 1395.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 1, 5: 9}.  Clean.
Subsets of the territory differences: 1 clean of 1.  Smallest clean ones have 1 numbers: drop 45x31 (loss 1395).

#### All templates together: loss 1395; template cores broken = True, new residual none; clean.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1395 | 0, 0 | 1395 | L4 |
| other residual fiber | 1, 1316 | 0, 0 | 1316 | L4 |
| smooth | 8, 11866 | 8, 10782 | 1084 | L4,L5,L6,L7 |
| unrelated fiber | 0, 0 | 2, 2589 | -2589 | L4 |
| total | 10, 14577 | 10, 13371 | 1206 | gap 1206 |

Layer-4 differences: 8, of which 1 inside a template's fibers (7 outside: 1122 (smooth), 1225 (smooth), 1274 (smooth), 12x107 (unrelated fiber), 45x29 (unrelated fiber), 28x47 (other residual fiber), 1365 (smooth)).

