## n = 3700: PB 4312738, opt 4311272, gap 1466

H has 1405 sources and 200 numbers up to n/2; S* differs from H in 18 numbers (H only) and 18 (S* only), all up to n/2.  Layer 4's residual has 99 members; 55 of them survive peeling the fiber members alone, 34 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 3 distinct in 159 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 12 | 107, 109, 307 | 107: 8,18,20,27,30; 109: 12,18,20,27,30; 307: 8,12 |
| c2 | 14 | 107, 109, 181, 461 | 107: 8,18,20,27,30; 109: 12,18,20,27,30; 181: 12,18,20; 461: 8 |
| c3 | 14 | 29, 31 | 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 29, 31 | 1 | 14 (5) | 87 | yes | loss 87: drop 45x29, add 42x29 | none |
| I2 | T11 | 107, 109, 181, 307, 461 | 2 | 16 (2) | 107 | no | loss 535: drop 15x107, add 10x107 | none |

#### I1 (T14) on 29, 31

Pattern: 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | 45* [L4] | 42 [L4] | 3 |
| 31 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x29 + 0x31 = 87.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 8, 5: 6}.  Clean.
Subsets of the territory differences: 2 clean of 3.  Smallest clean ones have 1 numbers: drop 45x29 (loss 1305).

#### I2 (T11) on 107, 109, 181, 307, 461

Pattern: 107: 8,18,20,27,30; 109: 12,18,20,27,30; 181: 12,18,20; 307: 8,12; 461: 8.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 107 | 8* [L4], 15 [L3] | 10 [L3], 12 [L4] | 1 |
| 109 | - | - | 0 |
| 181 | - | - | 0 |
| 307 | - | - | 0 |
| 461 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 1x107 + 0x109 + 0x181 + 0x307 + 0x461 = 107.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x107']}, residual members gone {4: 2}.  Not clean: it needs ? as well.
Subsets of the territory differences: 6 clean of 15.  Smallest clean ones have 1 numbers: drop 8x107 (loss 856); drop 15x107 (loss 1605).

#### All templates together: loss 194; template cores broken = True, new residual {4: ['12x107']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1305 | 1, 1218 | 87 | L4 |
| template 2 | 2, 2461 | 2, 2354 | 107 | L3,L4 |
| smooth | 11, 14145 | 11, 12994 | 1151 | L4,L5,L6,L7,L8 |
| unrelated fiber | 4, 5442 | 4, 5321 | 121 | L4,L5 |
| total | 18, 23353 | 18, 21887 | 1466 | gap 1466 |

Layer-4 differences: 15, of which 4 inside a template's fibers (11 outside: 1078 (smooth), 1089 (smooth), 1155 (smooth), 27x43 (unrelated fiber), 20x59 (unrelated fiber), 1190 (smooth), 28x43 (unrelated fiber), 1274 (smooth), 1275 (smooth), 1287 (smooth), 30x43 (unrelated fiber)).

