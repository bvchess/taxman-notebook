## n = 3500: PB 3857567, opt 3856650, gap 917

H has 1324 sources and 193 numbers up to n/2; S* differs from H in 14 numbers (H only) and 14 (S* only), all up to n/2.  Layer 4's residual has 106 members; 66 of them survive peeling the fiber members alone, 35 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 3 distinct in 153 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 107, 109, 173 | 107: 12,18,20,27,30; 109: 18,27,30; 173: 12,18,20 |
| c2 | 14 | 29, 31 | 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105 |
| c3 | 23 | 41, 43, 47 | 41: 28,30,42,45,50,52,63,75,78; 43: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70 |

Mixed cores (with a smooth member): 38 distinct sampled, sizes 36-63.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 29, 31 | 1 | 14 (4) | 87 | no | loss 1305: drop 45x29 | drop 1274 (smooth) |
| I2 | T23 | 41, 43, 47 | 1 | 23 (5) | 55 | no | loss 141: drop 30x47, add 27x47 | drop 975 (smooth), drop 1274 (smooth), drop 45x29 (template 1) |
| I3 | T11 | 107, 109, 173 | 1 | 11 (1) | 8 | no | loss 1284: drop 12x107 | drop 28x43 (template 2), drop 1260 (smooth), drop 1274 (smooth), drop 30x47 (template 2), drop 1470 (smooth) |

#### I1 (T14) on 29, 31

Pattern: 29: 45,50,63,70,75,98,105; 31: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 29 | 45* [L4] | 42 [L4] | 3 |
| 31 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x29 + 0x31 = 87.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['42x29']}, residual members gone {4: 1}.  Not clean: it needs drop 1274 (smooth) as well.
Subsets of the territory differences: 1 clean of 3.  Smallest clean ones have 1 numbers: drop 45x29 (loss 1305).

#### I2 (T23) on 41, 43, 47

Pattern: 41: 28,30,42,45,50,52,63,75,78; 43: 28,42,45,50,52,63,70,75,78; 47: 30,42,45,63,70.  Hangers: 27x43.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 41 | - | - | 0 |
| 43 | 28* [L4] | 30 [L4] | -2 |
| 47 | 30* [L4] | 27 [L4] | 3 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x41 + -2x43 + 3x47 = 55.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['30x43']}, residual members gone {4: 8}.  Not clean: it needs drop 975 (smooth), drop 1274 (smooth), drop 45x29 (template 1) as well.
Subsets of the territory differences: 5 clean of 15.  Smallest clean ones have 1 numbers: drop 28x43 (loss 1204); drop 30x47 (loss 1410).

#### I3 (T11) on 107, 109, 173

Pattern: 107: 12,18,20,27,30; 109: 18,27,30; 173: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 107 | 12* [L4] | 16 [L5] | -4 |
| 109 | 16 [L5] | 12 [L4] | 4 |
| 173 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = -4x107 + 4x109 + 0x173 = 8.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['12x109', '20x109'], 6: ['32x107']}, residual members gone {4: 5, 6: 1}.  Not clean: it needs drop 28x43 (template 2), drop 1260 (smooth), drop 1274 (smooth), drop 30x47 (template 2), drop 1470 (smooth) as well.
Subsets of the territory differences: 2 clean of 15.  Smallest clean ones have 1 numbers: drop 12x107 (loss 1284).

#### All templates together: loss 150; template cores broken = True, new residual {4: ['42x29', '30x43', '12x109', '20x109'], 6: ['32x107']}; not clean, it needs drop 975 (smooth), drop 1260 (smooth), drop 1274 (smooth), drop 1470 (smooth) as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 1, 1305 | 1, 1218 | 87 | L4 |
| template 2 | 2, 2614 | 2, 2559 | 55 | L4 |
| template 3 | 2, 3028 | 2, 3020 | 8 | L4,L5 |
| smooth | 9, 11245 | 8, 9442 | 1803 | L4,L5,L6,L7,L8,L9 |
| unrelated fiber | 0, 0 | 1, 1036 | -1036 | L4 |
| total | 14, 18192 | 14, 17275 | 917 | gap 917 |

Layer-4 differences: 11, of which 8 inside a template's fibers (3 outside: 975 (smooth), 28x37 (unrelated fiber), 1274 (smooth)).

