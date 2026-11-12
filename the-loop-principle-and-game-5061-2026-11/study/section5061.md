## 10. Game 5061: the centerpiece

*What is known: 5061 = 3·7·241, a restriction; 5060 is proven (opt 8,053,621, gap 2,557); best-known(5061) =
8,057,936, so δ = 746 against δ_PB = 254, rise 492, gap 3,049 if the score is right; the root bounds give
opt(5061) ≤ 8,059,751; thirteen plays from the proven 5060 found nothing.  The scripts of this section are
`study/family21.py`, `study/family21_regimes.py`, `study/g5061.py` and `study/onecell.py`, with their outputs.*

### 10.1 The mechanism, from the proven set of 5060 and the best-known set of 5061 (measured)

**Column 0 at 5060** (the rows 1..20 of 241): the moves 6P = 1446 (paying 2P) and 9P = 2169 (paying 3P); 10P = 2410
is out; 12P pays 4P, 14P pays 7P, 15P pays 5P, 16P pays 8P, 20P pays 10P, and **18P = 4338 pays with the hub 18**:
regime (ii) of Section 13.1.  The hub 20 is held by (20, −1) = 5020, the hubs 12, 14, 15, 21 by far cells (5052 =
12·421, 1918 = 14·137, 2085 = 15·139, 1869 = 21·89).

**What 5061 does, in the best-known game.**  5061 pays with 7P; 14P falls back on 2P; 6P has no payment left (3P is
9P's, the hub 6 is far) and leaves; 18P takes 6P and releases the hub 18; the hub 18 lands on 18·157 = 2826, a
source of layer 4 in the column of 157 (rows up to 32), which had paid with 9·157 = 1413 and now pays with the hub,
freeing 1413; and then the three columns of 151, 157 and 163 reshuffle their hubs 18, 27, 29, 30 and 32: in the
column of 157, 6·157 = 942 and 16·157 = 2512 become moves (32·157 = 5024 takes the hub 32 instead of 16·157) and
10·157 = 1570 and 12·157 = 1884 cease; in the column of 151, 12·151 = 1812 becomes a move and 16·151 = 2416 ceases
(32·151 = 4832 gives up the hub 32 and takes 16·151; 30·151 takes the hub 30); in the column of 163, 9·163 = 1467 and
14·163 = 2282 become moves and 15·163 = 2445 ceases (27·163 takes the hub 27).  The far region nets +700 (column 151
−604, column 157 0, column 163 +1304), so δ = 1446 − 700 = 746.  Every number of the change is in
`study/g5061_out.txt`.

**Against 5019 = 21·239, proven, δ = 492.**  Same regime, same first steps (5019 pays 7P₁, 14P₁ → 2P₁, 6P₁ out,
18P₁ → 6P₁), and the hub 18 lands on the same cell 18·157, which there frees 6·157 = 942 as a move and nothing else
changes: δ = 1434 − 942 = 492, rise 0.  The coincidence the coordinator notes is this: 746 − 254 = 492 = 6·239 −
6·157 is the value of 5019's step, not a number of 5061's; 5061's rise and 5019's shortfall are equal because both
are "6P minus 6·157" with P = 239 in one and the two models' difference in the other.  Nothing structural follows
from it that the next paragraphs do not say better.

**Why 5061 cannot do what 5019 did** (probes, `study/g5061_out.txt`): the game S\*(5060) − 1446 + 5061 + 942, worth
242 more than the best-known score, is unplayable on board 5061 with a core of 152 members; so are
best-known(5061) + 242 (131 members) and best-known(5061) − 942 + 1434 (152).  Between 5019 and 5060 the column of
157 gained the row 32 (5024 = 32·157 arrived at 5024, and with it the hub 32 came to the column at 5060, where 32·157
pays with 16·157), and the columns of 151 and 163 changed their hub holders; in that state the hub 18 alone frees
nothing playable, and the recovery has to be bought with the five-hub shuffle above.  The heuristic found that
shuffle, which is a point in its favor; whether a better one exists is the question.

### 10.2 The 492: what it is not, and what it must be

A natural reading, that the parity bound's extra is one cell of a hub row added to the best-known configuration
(492 = 12·41, and at the family's other exceptions 236 = 4·59 at 3297, 496 = 16·31 at 5943, 568 = 8·71 at 6153,
764 = 4·191 at 6573 and 6657, the last in the very column the best-known game reshuffles), is **false** at every one
of them: the recorded set plus that cell is already dependent at a parity (`study/onecell_out.txt`, a GF(2) check
with the parity vectors of W1), so no heaviest set holds it.  The parity bound's extra 492 is a different
configuration, which the recorded sets cannot show.  What the first-round experiments say it must be: at every
departure of the two models seen so far (688, 1328, 1460, 2512 in E5), the parity-only part of the defect is a hub
paid twice, a cell of a hub row held by a GF(2) combination that no scheme realizes, reached by a circuit through
rows that only an unclean column holds; the columns of 151, 157 and 163 at 5061 hold rows up to 33 and, by E7, such
windows have thousands of odd cores.  So the 492 is, with near certainty, a hub of that region (18, 27, 29, 30, 32,
16 or 12) used twice in the parity bound's set.  **E10** (paritydump at 5060 and 5061, with 5018, 5019, 3296, 3297,
3506, 3507 for comparison, and the probe that applies the parity bound's change to the recorded sets) names it:
which cells, which hub, which circuit, and whether applying it to the best-known set of 5061 closes an odd core
(the genuine reading's obstruction) or a core with a factor that another re-payment frees (a route a game can take).

### 10.3 Is the best-known score optimal?  The evidence, both ways

* *For a short score.*  Past 5060 the five regime-(ii) games of the family are the five exceptions, all with a rise
  of 1.75 to 2.4 P; in the proven range, 2 of 16 regime-(ii) games have a positive rise (1.3 to 1.5 P), 12 have rise
  0 and 2 a negative one.  Under the proven rate, five of five is about a one-in-thirty-thousand event; a heuristic
  that finds the first-order recovery (one cell per freed hub) but not every second-order one (a hub reshuffle across
  three columns) explains it with no coincidence.  The recovery the best-known game found, +700 over five hubs and
  three columns, shows what a search in that region is like.
* *For a genuine rise.*  The proven exceptions 3297 and 3507 have the same mechanism (hub 18 to column −1, hub 20 to
  a far column, a far reshuffle; the parity bound recovers 776 and 824 against the game's 540 and 609), so the gap
  does rise this way; the region is exactly where E7 finds odd cores and E5 finds the two models parting; and
  thirteen plays from the proven 5060 at levels 4 and 5 found nothing, nor did the probes.

Judgment: **undecided, with the family's statistics leaning to "short" and the mechanism leaning to "genuine"**; I
put it near even, not at the first round's "more likely short".  The two readings are told apart cheaply:

* **E10** (above), the parity bound's own change at 5061 and its probe.  If the change applied to the best-known set
  is playable, 5061 is short by its value and the game is in hand; if it closes an odd core, the core's shape against
  3297's says whether 5061 is 3297's case.
* **E11, the region solve.**  E8's `window` tool, generalized from "columns 0..D" to a list of primes: game 5061 with
  every promotion outside the columns of 151, 157, 163, 241 and 251 fixed as in the proven set of 5060 (the region
  where the best-known change lives), then with the columns E10 names added.  Seconds.  If it beats 8,057,936, 5061
  is short and the game proves it; if it returns 8,057,936, no game with 5060's set outside the region does better,
  which with E10's core is the genuine reading's evidence, short of a proof.

### 10.4 A local proof of δ(5061) ≥ 746: what it is, and what it rests on

In the style of L2 and L4: from any optimal set S of 5061 (given U at 5061, so that S holds U\*(5061): 5019, 14P,
15P, 18P, 20P, 12P, 16P, the far hub holders 5020, 5052, 2826, 4832, 5024, …), T = S − 5061 plus numbers worth at
least 746 is playable in game 5060.  The argument has three parts, of which two are the known technique and one is
new.

1. **Column 0 (finite, L4's kind).**  5061 pays with 7P, 3P or 21.  If 21: the hub 21's holder in S (a cell 21t) lost
   it; in game 5060 put 21t back on the hub or, if 21t ∈ S paying otherwise, put back what it released; the cases
   give at least 746 or a contradiction with S's optimality.  If 3P: 9P ∉ S or pays with the hub 9; put 9P back
   (2169).  If 7P: 14P pays 2P or 14; with 2P, 6P ∉ S or pays with 6 (far: then put 6P's displaced holder back);
   with 6P ∉ S the put-back is 6P = 1446 *provided 18P can release 6P*, that is 18P pays with 9P (then 9P ∉ S, put
   9P back instead) or with the hub 18.  So the one case that does not close at once is: 5061 → 7P, 14P → 2P,
   18P → 6P, 9P ∈ S, and the hub 18 paid by some 18t ∈ S, t ≠ 241.  This is the best-known game's case, and the
   only one the enumeration of Section 5.3 would leave open.
2. **The hub-18 chain (new; the part that serves every c ≥ 18 game).**  In that case the put-back is: 18t gives up
   the hub 18, which 18P takes, and 6P joins paying 2P (+1446); 18t falls back on 6t or 9t, which leaves S if it was
   a move (−6t or −9t), and the column of t re-pays what the departure frees.  So

       δ(5061) ≥ 1446 − R_t,   R_t = the most that column t and the columns coupled to it through hubs can lose
       when 18t loses the hub 18, over every configuration of an optimal S,

   and δ ≥ 746 needs R_t ≤ 700 for every t that an optimal S can use.  Three facts bound where t can be.  (a) In a
   clean column (rows ≤ 20 or 21, the four layer-3 sources saturating 2t, 3t, 5t, 7t) the hub 18 frees nothing
   playable, so an optimal S does not spend it there: t is a prime whose column has fewer saturating sources or more
   candidates, which is a prime far below P (rows above 21) or one of the few above P whose 10t is a source; the
   recorded games use t = 157, 191, 193 and the column −1.  (b) 6t ≤ 700 settles every t ≤ 116 at once.  (c) For the
   remaining t (about thirty primes in 127..281) R_t is the value of hub 18 to column t and its hub neighbors: a
   finite optimization over the column's cells (rows up to 5061/t, candidates up to 2530/t) and the hubs it can
   reach, the same object as E8's window but for an unclean region.  At t = 157 the best-known game says R_t ≥ 700
   (its shuffle reversed), and the parity bound says R_t^PB = 1192: the proof must show that the 492 between them is
   a hub paid twice, for every configuration of the region, not only the recorded one.
3. **The seal (the lemma the first round named, now for an unclean region).**  Part 2's optimization is a proof only
   if the region's cascade cannot leave it: every hub the region touches (18, 27, 29, 30, 32, 16, 12 at t = 157) is
   held by a far cell that is heavier than anything the region offers for it, so no chain crosses out.  That is the
   far-hub lemma of Section 4.4 for the specific hubs of the region, a per-hub check: "the holder of hub h in every
   optimal set is the heaviest h-cell that needs it, and the region's cells are lighter".

So the local proof is: part 1 by hand or by the enumerator (E12), part 2 by a sealed-region search per t (E11's tool,
run for each candidate t with the region free and the rest fixed, *plus* the hub-neighbor columns), part 3 by a
lemma that is new and worth having on its own.  **It is computer-assisted and finite, but it is not a window proof**:
the region is unclean, and that is exactly why the two models part there.  If part 2 returns R_t ≤ 700 for every t
with the seal, the theorem is δ(5061) ≥ 746 given U at 5061, and the best-known game settles 5061.  If part 2
returns R_t > 700 at some t with a playable configuration, that configuration is a better game and 5061 was short.
Either way the run decides the game.

**Does it cover the other 21P exceptions?**  Yes in form: 5943, 6153 (hub 18 to 18·191, 18·193) and 6573, 6657 (hub
18 to column −1, as at 3297 and 3507) have the same parts 1 and 2 with their own t and region; each needs its own
region solve, from a best-known predecessor rather than a proven one, so the result there is "optimal if n − 1 is"
plus the seal.  And 3297 and 3507, proven, are the test of the method: part 2 must return R_t = 540 and 609 there
(the chain's values), which checks the tool before 5061.

**What it says about c ≥ 18 in general.**  Every family from 18 on has a hub (18, 20, or both) that n's arrival
pushes out of column 0 or column 1, and the family law then has two regimes read in game n − 1: the hub is in the
window (a regime-(ii) step, δ = (the half-like cell) − R) or it is not (regime (i), a single-column cascade with a
fixed δ, provable by the enumerator).  R is the value of the pushed-out hub to the rest of the board, a far,
unclean-region quantity; the parity bound's R is at least as large wherever the region has an odd core the bound can
use, and the gap rises by the difference.  So for c ≥ 18: (i) the regime-(i) law is the provable, settling rule
(21P: 34 of the 39 games past 5060; the hub-18 holder of game n − 1 is its test); (ii) regime-(ii) games are settled
only by a region solve with a seal, game by game, which is cheap but needs the seal lemma to be a proof; (iii) the
parity form is not to be trusted there without the seal, since it is exactly where the bound finds hubs to pay twice.
The seal lemma is the one thing that would serve all of them; its statement is a property of hubs and the heaviest
cells, and E14 extended to the far hubs (which cells hold hubs 12..32 in every heaviest set of 5060 and 5061, and
whether the region's cells have circuits through them) is its test.

### 10.5 What to run for 5061, in order

1. **E10**: `paritydump 5060 5061 5018 5019 3296 3297 3506 3507` with E5's analysis and probe.  Names the 492.
2. **E11**: the region solve of 5061 with 5060's proven set outside; first the columns of 151, 157, 163, 241, 251,
   then those E10 names.  Decides "short" if it beats the best-known score; otherwise bounds the region.
3. **E11 at 3297 and 3507** (proven): the region solve must return opt(n); its R_t are the method's calibration.
4. **The seal check** (E14 extended): for the hubs 12, 16, 18, 27, 29, 30, 32, their holders in every heaviest set of
   5060 and 5061 (forced or not) and whether any circuit of a region cell passes through them.
5. Only then, if the owner wants a theorem: part 2 as a run over every candidate t with the seal, which is the local
   proof; its cost is the region solves, seconds each, not the 2,300 CPU-hours of a plain search.

