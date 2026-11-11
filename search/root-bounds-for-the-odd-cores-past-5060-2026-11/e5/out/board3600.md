## n = 3600: PB 4087976, opt 4086597, gap 1379

H has 1367 sources and 199 numbers up to n/2; S* differs from H in 18 numbers (H only) and 18 (S* only), all up to n/2.  Layer 4's residual has 123 members; 75 of them survive peeling the fiber members alone, 46 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 4 distinct in 162 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 12 | 103, 107, 293 | 103: 8,18,20,27,30; 107: 12,18,20,27,30; 293: 8,12 |
| c2 | 14 | 103, 107, 179, 449 | 103: 8,18,20,27,30; 107: 12,18,20,27,30; 179: 12,18,20; 449: 8 |
| c3 | 14 | 29, 31 | 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105 |
| c4 | 23 | 41, 43, 47 | 41: 28,30,42,45,50,52,63,75,78; 43: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 29, 31 | 1 | 14 (4) | 87 | yes | loss 87: drop 45x29, add 42x29 | none |
| I2 | T23 | 41, 43, 47 | 1 | 23 (5) | 1261 | no | loss 1204: drop 28x43 | none |
| I3 | T11 | 103, 107, 179, 293, 449 | 2 | 16 (2) | 103 | no | loss 515: drop 15x103, add 10x103 | none |

#### I1 (T14) on 29, 31

Pattern: 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | 45* [L4] | 42 [L4] | 3 |
| 31 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x29 + 0x31 = 87.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 7}.  Clean.
Subsets of the territory differences: 2 clean of 3.  Smallest clean ones have 1 numbers: drop 45x29 (loss 1305).

#### I2 (T23) on 41, 43, 47

Pattern: 41: 28,30,42,45,50,52,63,75,78; 43: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70.  Hangers: 27x43, 50x47, 75x47.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 41 | 30* [L4] | 35 [L3] | -5 |
| 43 | 28* [L4], 35 [L3] | 30 [L4] | 33 |
| 47 | 28 [L4] | 27 [L4] | 1 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -5x41 + 33x43 + 1x47 = 1261.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x47', '70x41']}, residual members gone {4: 26, 5: 4}.  Not clean: it needs ? as well.
Subsets of the territory differences: 18 clean of 127.  Smallest clean ones have 1 numbers: drop 28x43 (loss 1204); drop 30x41 (loss 1230); drop 35x43 (loss 1505).

#### I3 (T11) on 103, 107, 179, 293, 449

Pattern: 103: 8,18,20,27,30; 107: 12,18,20,27,30; 179: 12,18,20; 293: 8,12; 449: 8.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 103 | 8* [L4], 15 [L3] | 10 [L3], 12 [L4] | 1 |
| 107 | - | - | 0 |
| 179 | - | - | 0 |
| 293 | - | - | 0 |
| 449 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 1x103 + 0x107 + 0x179 + 0x293 + 0x449 = 103.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x103']}, residual members gone {4: 2}.  Not clean: it needs ? as well.
Subsets of the territory differences: 6 clean of 15.  Smallest clean ones have 1 numbers: drop 8x103 (loss 824); drop 15x103 (loss 1545).

#### All templates together: loss 1451; template cores broken = True, new residual {4: ['12x103', '27x47', '70x41']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1305 | 1, 1218 | 87 | L4 |
| template 2 | 4, 5255 | 3, 3994 | 1261 | L3,L4 |
| template 3 | 2, 2369 | 2, 2266 | 103 | L3,L4 |
| smooth | 11, 13628 | 10, 11554 | 2074 | L4,L5,L6,L7 |
| unrelated fiber | 0, 0 | 2, 2146 | -2146 | L4 |
| total | 18, 22557 | 18, 21178 | 1379 | gap 1379 |

Layer-4 differences: 16, of which 9 inside a template's fibers (7 outside: 975 (smooth), 1035 (smooth), 28x37 (unrelated fiber), 1078 (smooth), 1089 (smooth), 30x37 (unrelated fiber), 1155 (smooth)).

