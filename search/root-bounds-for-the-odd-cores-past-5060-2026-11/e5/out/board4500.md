## n = 4500: PB 6369675, opt 6368078, gap 1597

H has 1707 sources and 237 numbers up to n/2; S* differs from H in 17 numbers (H only) and 17 (S* only), all up to n/2.  Layer 4's residual has 123 members; 55 of them survive peeling the fiber members alone, 57 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 7 distinct in 160 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 137, 139, 223 | 137: 12,18,20,27,30; 139: 18,27,30; 223: 12,18,20 |
| c2 | 12 | 131, 137, 373 | 131: 8,18,20,27,30; 137: 12,18,20,27,30; 373: 8,12 |
| c3 | 13 | 131, 137, 139, 373 | 131: 8,18,20,27,30; 137: 12,20,30; 139: 18,27,30; 373: 8,12 |
| c4 | 13 | 131, 139, 223, 373 | 131: 8,18,20,27,30; 139: 18,27,30; 223: 12,18,20; 373: 8,12 |
| c5 | 14 | 131, 137, 223, 557 | 131: 8,18,20,27,30; 137: 12,18,20,27,30; 223: 12,18,20; 557: 8 |
| c6 | 14 | 37, 41 | 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105 |
| c7 | 15 | 131, 137, 139, 223, 557 | 131: 8,18,20,27,30; 137: 12,20,30; 139: 18,27,30; 223: 12,18,20; 557: 8 |

Mixed cores (with a smooth member): 12 distinct sampled, sizes 33-64.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 37, 41 | 1 | 14 (4) | 111 | yes | loss 111: drop 45x37, add 42x37 | none |
| I2 | T11 | 131, 137, 139, 223, 373, 557 | 6 | 19 (2) | 332 | no | loss 2692: drop 8x131, drop 12x137 | drop 1430 (smooth), drop 1470 (smooth), drop 1575 (smooth), drop 45x37 (template 1) |

#### I1 (T14) on 37, 41

Pattern: 37: 45,50,63,70,75,98,105; 41: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | 45* [L4] | 42 [L4] | 3 |
| 41 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x37 + 0x41 = 111.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 7}.  Clean.
Subsets of the territory differences: 2 clean of 3.  Smallest clean ones have 1 numbers: drop 45x37 (loss 1665).

#### I2 (T11) on 131, 137, 139, 223, 373, 557

Pattern: 131: 8,18,20,27,30; 137: 12,18,20,27,30; 139: 18,27,30; 223: 12,18,20; 373: 8,12; 557: 8.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 131 | 8* [L4] | 16 [L5] | -8 |
| 137 | 12* [L4], 15 [L3] | 8 [L4], 14 [L3] | 5 |
| 139 | 15 [L3], 16 [L5] | 12 [L4], 14 [L3] | 5 |
| 223 | - | - | 0 |
| 373 | - | - | 0 |
| 557 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -8x131 + 5x137 + 5x139 + 0x223 + 0x373 + 0x557 = 332.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['8x137', '12x139', '20x139', '28x137', '28x139'], 6: ['32x131']}, residual members gone {4: 11, 6: 1}.  Not clean: it needs drop 1430 (smooth), drop 1470 (smooth), drop 1575 (smooth), drop 45x37 (template 1) as well.
Subsets of the territory differences: 32 clean of 1023.  Smallest clean ones have 2 numbers: drop 8x131, drop 12x137 (loss 2692); drop 8x131, drop 15x137 (loss 3103); drop 8x131, drop 15x139 (loss 3133).

#### All templates together: loss 443; template cores broken = True, new residual {4: ['8x137', '12x139', '20x139', '28x137', '28x139'], 6: ['32x131']}; not clean, it needs drop 1430 (smooth), drop 1470 (smooth), drop 1575 (smooth) as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1665 | 1, 1554 | 111 | L4 |
| template 2 | 5, 9056 | 5, 8724 | 332 | L3,L4,L5 |
| other residual fiber | 1, 1484 | 0, 0 | 1484 | L4 |
| smooth | 10, 15676 | 9, 13230 | 2446 | L4,L5,L6,L7 |
| unrelated fiber | 0, 0 | 2, 2776 | -2776 | L4 |
| total | 17, 27881 | 17, 26284 | 1597 | gap 1597 |

Layer-4 differences: 14, of which 6 inside a template's fibers (8 outside: 1287 (smooth), 28x47 (unrelated fiber), 1375 (smooth), 1430 (smooth), 20x73 (unrelated fiber), 28x53 (other residual fiber), 1518 (smooth), 1625 (smooth)).

