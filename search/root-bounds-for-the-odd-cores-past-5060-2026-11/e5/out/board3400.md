## n = 3400: PB 3637883, opt 3636563, gap 1320

H has 1286 sources and 187 numbers up to n/2; S* differs from H in 20 numbers (H only) and 20 (S* only), all up to n/2.  Layer 4's residual has 150 members; 50 of them survive peeling the fiber members alone, 70 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 2 distinct in 152 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 101, 109, 167 | 101: 12,18,20,27,30; 109: 18,27,30; 167: 12,18,20 |
| c2 | 14 | 29, 31 | 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 29, 31 | 1 | 14 (4) | 242 | no | loss 1305: drop 45x29 | none |
| I2 | T11 | 101, 109, 167 | 1 | 11 (1) | 218 | yes | loss 218: drop 10x109, drop 15x109, add 9x109, add 14x109 | none |

#### I1 (T14) on 29, 31

Pattern: 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | 45* [L4] | 42 [L4] | 3 |
| 31 | 45* [L4] | 40 [L5] | 5 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x29 + 5x31 = 242.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x29'], 5: ['40x31'], 6: ['48x31', '72x31', '80x31', '108x31']}, residual members gone {4: 2, 5: 6}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 15.  Smallest clean ones have 1 numbers: drop 45x29 (loss 1305); drop 45x31 (loss 1395).

#### I2 (T11) on 101, 109, 167

Pattern: 101: 12,18,20,27,30; 109: 18,27,30; 167: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 101 | - | - | 0 |
| 109 | 10 [L3], 15 [L3] | 9 [L3], 14 [L3] | 2 |
| 167 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x101 + 2x109 + 0x167 = 218.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 2}.  Clean.
Subsets of the territory differences: 7 clean of 15.  Smallest clean ones have 1 numbers: drop 10x109 (loss 1090); drop 15x109 (loss 1635).

#### All templates together: loss 460; template cores broken = True, new residual {4: ['42x29'], 5: ['40x31'], 6: ['48x31', '72x31', '80x31', '108x31']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 2700 | 2, 2458 | 242 | L4,L5 |
| template 2 | 2, 2725 | 2, 2507 | 218 | L3 |
| other residual fiber | 2, 2776 | 3, 3864 | -1088 | L3,L4 |
| smooth | 13, 15452 | 11, 12456 | 2996 | L4,L5,L6,L7,L8,L9 |
| unrelated fiber | 1, 1239 | 2, 2287 | -1048 | L3,L4 |
| total | 20, 24892 | 20, 23572 | 1320 | gap 1320 |

Layer-4 differences: 14, of which 3 inside a template's fibers (11 outside: 875 (smooth), 1035 (smooth), 1078 (smooth), 27x41 (unrelated fiber), 20x59 (unrelated fiber), 1197 (smooth), 1225 (smooth), 27x47 (other residual fiber), 18x73 (other residual fiber), 28x47 (other residual fiber), 20x73 (other residual fiber)).

