## n = 5000: PB 7870389, opt 7868316, gap 2073

H has 1900 sources and 264 numbers up to n/2; S* differs from H in 17 numbers (H only) and 17 (S* only), all up to n/2.  Layer 4's residual has 73 members; 73 of them survive peeling the fiber members alone, 0 are smooth (largest prime up to 23).

### Template cores (minimal cores of fiber members only; 5 distinct in 162 orders)

| core | size | primes | base pattern (largest prime: cofactors) |
|---|---|---|---|
| c1 | 11 | 149, 157, 241 | 149: 12,18,20,27,30; 157: 18,27,30; 241: 12,18,20 |
| c2 | 14 | 41, 43 | 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105 |
| c3 | 14 | 41, 47 | 41: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105 |
| c4 | 14 | 43, 47 | 43: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105 |
| c5 | 23 | 59, 61, 71 | 59: 28,42,45,50,52,63,70,75,78; 61: 28,30,42,45,50,52,63,75,78; 71: 30,42,45,63,70 |

Mixed cores (with a smooth member): 0 distinct sampled.

### Instances

| instance | template | primes | cores | members (non-source) | territory loss | S* swap alone clean | cheapest clean subset of it | outside numbers it needs |
|---|---|---|---|---|---|---|---|---|
| I1 | T14 | 41, 43, 47 | 3 | 21 (6) | 252 | yes | loss 252: drop 45x41, drop 45x43, add 42x41, add 42x43 | none |
| I2 | T23 | 59, 61, 71 | 1 | 23 (5) | -1566 | no | loss 61: drop 28x61, add 27x61 | drop 1375 (smooth), drop 1650 (smooth), drop 1715 (smooth), drop 1755 (smooth), drop 45x41 (template 1), drop 1925 (smooth), drop 45x43 (template 1), drop 2142 (smooth) |
| I3 | T11 | 149, 157, 241 | 1 | 11 (1) | 314 | yes | loss 314: drop 10x157, drop 15x157, add 9x157, add 14x157 | none |

#### I1 (T14) on 41, 43, 47

Pattern: 41: 45,50,63,70,75,98,105; 43: 45,50,63,70,75,98,105; 47: 45,50,63,70,75,98,105.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 41 | 45* [L4] | 42 [L4] | 3 |
| 43 | 45* [L4] | 42 [L4] | 3 |
| 47 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 3x41 + 3x43 + 0x47 = 252.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 21}.  Clean.
Subsets of the territory differences: 4 clean of 15.  Smallest clean ones have 2 numbers: drop 45x41, drop 45x43 (loss 3780).

#### I2 (T23) on 59, 61, 71

Pattern: 59: 28,42,45,50,52,63,70,75,78; 61: 28,30,42,45,50,52,63,75,78; 71: 30,42,45,63,70.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 59 | 35 [L3] | 30 [L4] | 5 |
| 61 | 28* [L4] | 27 [L4], 35 [L3] | -34 |
| 71 | 30* [L4] | 27 [L4] | 3 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 5x59 + -34x61 + 3x71 = -1566.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual {4: ['27x61', '70x61'], 5: ['40x59', '36x71', '56x59', '60x59', '54x71', '84x59']}, residual members gone {4: 17, 5: 7}.  Not clean: it needs drop 1375 (smooth), drop 1650 (smooth), drop 1715 (smooth), drop 1755 (smooth), drop 45x41 (template 1), drop 1925 (smooth), drop 45x43 (template 1), drop 2142 (smooth) as well.
Subsets of the territory differences: 13 clean of 127.  Smallest clean ones have 1 numbers: drop 28x61 (loss 1708); drop 35x59 (loss 2065); drop 30x71 (loss 2130).

#### I3 (T11) on 149, 157, 241

Pattern: 149: 12,18,20,27,30; 157: 18,27,30; 241: 12,18,20.  Hangers: none.

| prime | drops (in H, not S*): cofactor [layer] | adds (in S*, not H): cofactor [layer] | c = Σdrop − Σadd |
|---|---|---|---|
| 149 | - | - | 0 |
| 157 | 10 [L3], 15 [L3] | 9 [L3], 14 [L3] | 2 |
| 241 | - | - | 0 |

(* = a member of one of the instance's template cores.)  Loss = Σ c·P = 0x149 + 2x157 + 0x241 = 314.  Hubs changed: none.
S* swap on the territory alone: template cores broken = True, new residual none, residual members gone {4: 2}.  Clean.
Subsets of the territory differences: 7 clean of 15.  Smallest clean ones have 1 numbers: drop 10x157 (loss 1570); drop 15x157 (loss 2355).

#### All templates together: loss -1000; template cores broken = True, new residual {5: ['40x59', '36x71', '56x59', '60x59', '54x71', '84x59']}; not clean, it needs drop 1375 (smooth), drop 1650 (smooth), drop 1715 (smooth), drop 1755 (smooth), drop 1925 (smooth), drop 2142 (smooth) as well.

### Differences by class (numbers up to n/2)

| class | H only (count, weight) | S* only (count, weight) | loss | layers of the differences |
|---|---|---|---|---|
| template 1 | 2, 3780 | 2, 3528 | 252 | L4 |
| template 2 | 3, 5903 | 4, 7469 | -1566 | L3,L4 |
| template 3 | 2, 3925 | 2, 3611 | 314 | L3 |
| smooth | 10, 17200 | 8, 12603 | 4597 | L4,L5,L6,L7 |
| unrelated fiber | 0, 0 | 1, 1524 | -1524 | L4 |
| total | 17, 30808 | 17, 28735 | 2073 | gap 2073 |

Layer-4 differences: 16, of which 9 inside a template's fibers (7 outside: 1375 (smooth), 1521 (smooth), 12x127 (unrelated fiber), 1617 (smooth), 1666 (smooth), 1715 (smooth), 1925 (smooth)).

