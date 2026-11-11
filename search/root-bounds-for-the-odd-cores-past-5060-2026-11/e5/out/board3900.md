## n = 3900: PB 4791874, opt 4790282, gap 1592

H has 1481 sources and 208 numbers up to n/2; S* differs from H in 13 numbers (H only) and 13 (S* only), all up to n/2.  Layer 4's residual has 113 members; 45 of them survive peeling the fiber members alone, 50 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 1 distinct in 151 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 14 | 31, 37 | 31: 45,50,63,70,75,98,105; 37: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 31, 37 | 1 | 14 (4) | 93 | no | loss 1395: drop 45x31 | none |

#### I1 (T14) on 31, 37

Pattern: 31: 45,50,63,70,75,98,105; 37: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 31 | 45* [L4] | 42 [L4] | 3 |
| 37 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x31 + 0x37 = 93.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x31']}, residual members gone {4: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 1 clean of 3.  Smallest clean ones have 1 numbers: drop 45x31 (loss 1395).

#### All templates together: loss 93; template cores broken = True, new residual {4: ['42x31']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1395 | 1, 1302 | 93 | L4 |
| other residual fiber | 1, 1269 | 0, 0 | 1269 | L4 |
| smooth | 11, 15297 | 10, 12611 | 2686 | L4,L5,L6,L7,L8 |
| unrelated fiber | 0, 0 | 2, 2456 | -2456 | L4 |
| total | 13, 17961 | 13, 16369 | 1592 | gap 1592 |

Layer-4 differences: 13, of which 2 inside a template's fibers (11 outside: 1150 (smooth), 1190 (smooth), 1196 (smooth), 20x61 (unrelated fiber), 1225 (smooth), 12x103 (unrelated fiber), 27x47 (other residual fiber), 1274 (smooth), 1287 (smooth), 1330 (smooth), 1365 (smooth)).

