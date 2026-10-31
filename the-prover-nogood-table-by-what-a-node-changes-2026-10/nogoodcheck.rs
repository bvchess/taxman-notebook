//! Scratch (not for commit): the search of `exact` from the roles of F4, with no pause, and its fingerprint (nodes,
//! the prover's counters, the parity bound's, the size and a hash of the nogood table), to check that a change keeps
//! every count.  `nogoodcheck BUDGET N...` (BUDGET 0: no budget).  Compiles against the table as a Vec<Vec<u32>> and
//! as `Nogoods`.

use std::time::Instant;
use taxman_prover::game::{Board, Prover};
use taxman_prover::jsonl::{committed_chain, recorded_games_to};
use taxman_prover::primes::smallest_prime_factors;
use taxman_prover::upper::{low_roles, recorded_ustar};

fn main() {
    let args: Vec<u64> = std::env::args().skip(1).map(|a| a.parse().unwrap()).collect();
    let budget = if args[0] == 0 { u64::MAX } else { args[0] };
    let games = &args[1..];
    let top = games.iter().copied().max().unwrap();
    let known = recorded_games_to(&[committed_chain()], top);
    let spf = smallest_prime_factors(top as usize);
    for &n in games {
        let (score, moves) = &known[&n];
        let board = Board::new(n as u32, &spf);
        let ustar = recorded_ustar(n, moves, &spf);
        let unit = low_roles(n as u32, &spf, &ustar);
        let started = Instant::now();
        let mut prover = Prover::new(&board, *score, budget).with_parity();
        let verdict = prover.run_units(vec![unit]);
        let secs = started.elapsed().as_secs_f64();
        let mut hash = 0xcbf29ce484222325u64;
        for k in prover.nogoods.iter() {
            for &c in k.iter() {
                hash = (hash ^ u64::from(c)).wrapping_mul(0x100000001b3);
            }
            hash = (hash ^ 0xffff).wrapping_mul(0x100000001b3);
        }
        println!(
            "n={n} verdict={verdict:?} nodes={} secs={secs:.2} ms/node={:.3} stats={:?} nogoods={} hash={hash:016x}",
            prover.nodes,
            1e3 * secs / prover.nodes as f64,
            prover.stats,
            prover.nogoods.len()
        );
        println!("  parity {:?}", prover.parity_stats());
    }
}
