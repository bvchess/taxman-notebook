## n = 3300: PB 3429272, opt 3427829, gap 1443

H has 1248 sources and 182 numbers up to n/2; S* differs from H in 22 numbers (H only) and 22 (S* only), all up to n/2.  Layer 4's residual has 148 members; 70 of them survive peeling the fiber members alone, 69 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 8 distinct in 169 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 101, 107, 163 | 101: 12,18,20,27,30; 107: 18,27,30; 163: 12,18,20 |
| c2 | 12 | 97, 101, 271 | 97: 8,18,20,27,30; 101: 12,18,20,27,30; 271: 8,12 |
| c3 | 13 | 97, 101, 107, 271 | 97: 8,18,20,27,30; 101: 12,20,30; 107: 18,27,30; 271: 8,12 |
| c4 | 13 | 97, 107, 163, 271 | 97: 8,18,20,27,30; 107: 18,27,30; 163: 12,18,20; 271: 8,12 |
| c5 | 14 | 97, 101, 163, 409 | 97: 8,18,20,27,30; 101: 12,18,20,27,30; 163: 12,18,20; 409: 8 |
| c6 | 14 | 29, 31 | 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105 |
| c7 | 15 | 97, 101, 107, 163, 409 | 97: 8,18,20,27,30; 101: 12,20,30; 107: 18,27,30; 163: 12,18,20; 409: 8 |
| c8 | 23 | 37, 41, 47 | 37: 28,30,42,45,50,52,63,75,78; 41: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 29, 31 | 1 | 14 (4) | 175 | no | loss 87: drop 45x29, add 42x29 | none |
| I2 | T23 | 37, 41, 47 | 1 | 23 (5) | -940 | no | loss 1148: drop 28x41 | none |
| I3 | T11 | 97, 101, 107, 163, 271, 409 | 6 | 19 (2) | 799 | no | loss 1846: drop 8x97, drop 10x107 | none |

#### I1 (T14) on 29, 31

Pattern: 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | 45* [L4] | 42 [L4], 44 [L4] | -41 |
| 31 | 44 [L4] | - | 44 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -41x29 + 44x31 = 175.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {5: ['88x29', '104x29']}, residual members gone {4: 38, 5: 1}.  Not clean: it needs ? as well.
Subsets of the territory differences: 4 clean of 15.  Smallest clean ones have 1 numbers: drop 45x29 (loss 1305).

#### I2 (T23) on 37, 41, 47

Pattern: 37: 28,30,42,45,50,52,63,75,78; 41: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70.  Hangers: 27x41.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 37 | - | 27 [L4] | -27 |
| 41 | 28* [L4] | 30 [L4] | -2 |
| 47 | 30* [L4] | 27 [L4] | 3 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -27x37 + -2x41 + 3x47 = -940.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x37', '30x41', '27x47'], 5: ['81x37']}, residual members gone {4: 6}.  Not clean: it needs ? as well.
Subsets of the territory differences: 3 clean of 31.  Smallest clean ones have 1 numbers: drop 28x41 (loss 1148); drop 30x47 (loss 1410).

#### I3 (T11) on 97, 101, 107, 163, 271, 409

Pattern: 97: 8,18,20,27,30; 101: 12,18,20,27,30; 107: 18,27,30; 163: 12,18,20; 271: 8,12; 409: 8.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 97 | 8* [L4] | 16 [L5] | -8 |
| 101 | 12* [L4], 15 [L3] | 8 [L4], 14 [L3] | 5 |
| 107 | 10 [L3] | - | 10 |
| 163 | - | - | 0 |
| 271 | - | - | 0 |
| 409 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -8x97 + 5x101 + 10x107 + 0x163 + 0x271 + 0x409 = 799.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['8x101', '28x101'], 6: ['32x97']}, residual members gone {4: 13}.  Not clean: it needs ? as well.
Subsets of the territory differences: 16 clean of 127.  Smallest clean ones have 2 numbers: drop 8x97, drop 10x107 (loss 1846); drop 8x97, drop 12x101 (loss 1988); drop 8x97, drop 15x101 (loss 2291).

#### All templates together: loss 34; template cores broken = True, new residual {4: ['8x101', '27x37', '30x41', '28x101'], 5: ['88x29', '81x37', '104x29'], 6: ['32x97']}; not clean, it needs ? as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 2669 | 2, 2494 | 175 | L4 |
| template 2 | 2, 2558 | 3, 3498 | -940 | L4 |
| template 3 | 4, 4573 | 3, 3774 | 799 | L3,L4,L5 |
| smooth | 12, 13705 | 11, 11781 | 1924 | L4,L5,L6,L7 |
| unrelated fiber | 2, 3193 | 3, 3708 | -515 | L3,L4,L5 |
| total | 22, 26698 | 22, 25255 | 1443 | gap 1443 |

Layer-4 differences: 20, of which 12 inside a template's fibers (8 outside: 850 (smooth), 1014 (smooth), 1035 (smooth), 1071 (smooth), 1078 (smooth), 1155 (smooth), 12x103 (unrelated fiber), 1274 (smooth)).

