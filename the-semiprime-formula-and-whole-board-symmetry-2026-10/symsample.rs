//! Research measurement, not for the build: what share of a search from the roles of F4 the whole-board
//! prime-exchange inequalities would cut, sampled at the open units of a pause (`symsample N SECONDS`).
//!
//! The search runs SECONDS and pauses.  Each open unit (a subtree the search has still to explore) is then tested by
//! the inequalities c_p(S) ≤ c_q(S) of the pairs p < q with p² > n and ⌊n/p⌋ = ⌊n/q⌋: the hopeless test (the forced
//! picks' c_p already exceeds what c_q can reach), and the parity bound with a Lagrangian on the inequalities.  Each
//! unit is then searched to the end on its own, to count the nodes a cut there would save.  The share is a lower
//! bound on what the rule saves: it sees only the units open at one moment, not the nodes inside the others.

use std::time::{Duration, Instant};
use taxman_prover::game::{Board, Prover, Role, Verdict};
use taxman_prover::jsonl::{committed_chain, recorded_games_to};
use taxman_prover::parity::{Meet, Outcome, Parity};
use taxman_prover::primes::{is_prime, smallest_prime_factors};
use taxman_prover::upper::{low_roles, omega, recorded_ustar};

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let n: u32 = args[0].parse().unwrap();
    let seconds: f64 = args[1].parse().unwrap();
    // "floor": pairs with the same ⌊n/p⌋, cofactor sums over all picks; "f4": pairs whose exchange maps the numbers
    // up to n/2 and the numbers of layers 3 and up onto themselves, cofactor sums over the picks of layers 3 and up.
    let f4 = args.get(2).map(|s| s == "f4").unwrap_or(false);
    let known = recorded_games_to(&[committed_chain()], u64::from(n));
    let spf = smallest_prime_factors(n as usize + 1);
    let (score, moves) = &known[&u64::from(n)];
    let target = *score as i64;
    let board = Board::new(n, &spf);
    let ustar = recorded_ustar(u64::from(n), moves, &spf);
    let unit = low_roles(n, &spf, &ustar);

    // The classes: primes above √n with the same ⌊n/p⌋.
    let primes: Vec<u32> = (2..=n / 2)
        .filter(|&p| u64::from(p) * u64::from(p) > u64::from(n) && is_prime(u64::from(p), &spf))
        .collect();
    let mut all_pairs: Vec<(u32, u32)> = Vec::new();
    let mut adjacent: Vec<(u32, u32)> = Vec::new();
    for (i, &p) in primes.iter().enumerate() {
        for &q in &primes[i + 1..] {
            let ok = if f4 {
                n / (2 * p) == n / (2 * q) && (n / q + 1..=n / p).all(|t| omega(t, &spf) == 1)
            } else {
                n / p == n / q
            };
            if ok {
                all_pairs.push((p, q));
                if adjacent.iter().all(|&(a, _)| a != p) {
                    adjacent.push((p, q));
                }
            }
        }
    }
    let counted = |x: u32| -> bool { !f4 || omega(x, &spf) >= 3 };
    let cof = |roles: &[Role], want: Role, r: u32| -> i64 {
        (r..=n).step_by(r as usize).filter(|&x| roles[x as usize] == want && counted(x)).map(|x| i64::from(x / r)).sum()
    };
    let hopeless = |roles: &[Role]| -> bool {
        all_pairs.iter().any(|&(p, q)| cof(roles, Role::Pick, p) > cof(roles, Role::Pick, q) + cof(roles, Role::Free, q))
    };
    let solve = |roles: &[Role], mu: &[i64]| -> Option<(i64, Vec<u32>)> {
        let mut w: Vec<i64> = (0..=i64::from(n)).collect();
        for (i, &(p, q)) in adjacent.iter().enumerate() {
            for x in (p..=n).step_by(p as usize).filter(|&x| counted(x)) {
                w[x as usize] -= mu[i] * i64::from(x / p);
            }
            for x in (q..=n).step_by(q as usize).filter(|&x| counted(x)) {
                w[x as usize] += mu[i] * i64::from(x / q);
            }
        }
        assert!(w[2..].iter().all(|&v| v > 0), "n={n}: a weight fell to 0");
        match Meet::new(Parity::pair(&board, &w)).solve(roles) {
            Outcome::Bound(b) => Some((b.value, b.set)),
            Outcome::Infeasible => None,
            Outcome::Uncertified => panic!("n={n}: a bound is not certified"),
        }
    };
    // The parity bound with a Lagrangian on the adjacent pairs' inequalities, fitted by subgradient steps: the best
    // value found, or None when the forced picks are dependent.
    let lagrange = |roles: &[Role]| -> Option<i64> {
        let mut mu = vec![0i64; adjacent.len()];
        let mut best = i64::MAX;
        let mut theta = 1.0f64;
        let mut since = 0;
        for _ in 0..25 {
            let (value, set) = solve(roles, &mu)?;
            if value < best {
                best = value;
                since = 0;
            } else {
                since += 1;
                if since >= 3 {
                    theta /= 2.0;
                    since = 0;
                }
            }
            if best <= target {
                break;
            }
            let inset = |r: u32| -> i64 {
                set.iter().filter(|&&x| x % r == 0 && counted(x)).map(|&x| i64::from(x / r)).sum()
            };
            let g: Vec<i64> = adjacent.iter().map(|&(p, q)| inset(q) - inset(p)).collect();
            let norm: i64 = g.iter().zip(&mu).map(|(&gi, &m)| if gi < 0 || m > 0 { gi * gi } else { 0 }).sum();
            if norm == 0 || theta < 0.01 {
                break;
            }
            let step = theta * ((value - target).max(1) as f64) / norm as f64;
            for (i, &(p, _)) in adjacent.iter().enumerate() {
                let next = (mu[i] as f64 - step * g[i] as f64).round().max(0.0) as i64;
                mu[i] = next.min(i64::from(p) / 2);
            }
        }
        Some(best)
    };

    let t0 = Instant::now();
    let mut prover = Prover::new(&board, *score, u64::MAX)
        .pause_at(Instant::now() + Duration::from_secs_f64(seconds))
        .with_parity();
    let first = prover.run_units(vec![unit]);
    let first_nodes = prover.nodes;
    assert!(matches!(first, Verdict::Paused), "n={n}: the search ended before the pause: {first:?}");
    let units = prover.take_units(Instant::now() + Duration::from_secs(1_000_000));
    let (mut total, mut by_base, mut by_hopeless, mut by_lagrange) = (0u64, 0u64, 0u64, 0u64);
    let (mut c_base, mut c_hopeless, mut c_lagrange) = (0usize, 0usize, 0usize);
    for roles in &units {
        let base = solve(roles, &vec![0; adjacent.len()]).map(|b| b.0);
        let hop = hopeless(roles);
        let lag = if hop { None } else { lagrange(roles) };
        let mut sub = Prover::new(&board, *score, u64::MAX).with_parity();
        let verdict = sub.run_units(vec![roles.clone()]);
        assert!(matches!(verdict, Verdict::Proven), "n={n}: a unit did not prove: {verdict:?}");
        total += sub.nodes;
        if base.is_none_or(|b| b <= target) {
            by_base += sub.nodes;
            c_base += 1;
        } else if hop {
            by_hopeless += sub.nodes;
            c_hopeless += 1;
        } else if lag.is_none_or(|l| l <= target) {
            by_lagrange += sub.nodes;
            c_lagrange += 1;
        }
    }
    println!(
        "{{\"n\":{n},\"f4\":{f4},\"score\":{target},\"pairs\":{},\"first_nodes\":{first_nodes},\"units\":{},\"unit_nodes\":{total},\
         \"cut_by_base\":[{c_base},{by_base}],\"hopeless\":[{c_hopeless},{by_hopeless}],\
         \"lagrange\":[{c_lagrange},{by_lagrange}],\"saved_share\":{:.4},\"secs\":{:.1}}}",
        all_pairs.len(),
        units.len(),
        (by_hopeless + by_lagrange) as f64 / (first_nodes + total) as f64,
        t0.elapsed().as_secs_f64()
    );
}
