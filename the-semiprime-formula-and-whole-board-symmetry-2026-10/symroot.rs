//! Research measurement, not for the build: how far the whole-board prime-exchange inequalities lower the parity bound
//! at the root of the search from the roles of F4 (`symroot N...`).
//!
//! For primes p < q with p² > n and ⌊n/p⌋ = ⌊n/q⌋, exchanging p and q maps the board onto itself, so every optimal
//! set S has c_p(S) ≤ c_q(S), c_r(S) being the sum of x/r over the members x of S divisible by r.  A Lagrangian with
//! multipliers μ ≥ 0 on these inequalities adds μ·(c_q − c_p) to the weight of a set, which keeps the parity bound an
//! upper bound on every set that obeys them.  The program fits the multipliers by subgradient steps and prints the
//! root's parity bound without and with them.

use std::time::Instant;
use taxman_prover::game::Board;
use taxman_prover::jsonl::{committed_chain, recorded_games_to};
use taxman_prover::parity::{Meet, Outcome, Parity};
use taxman_prover::primes::{is_prime, smallest_prime_factors};
use taxman_prover::upper::{low_roles, recorded_ustar};

fn main() {
    let ns: Vec<u32> = std::env::args().skip(1).map(|a| a.parse().unwrap()).collect();
    let to = *ns.iter().max().unwrap();
    let known = recorded_games_to(&[committed_chain()], u64::from(to));
    let spf = smallest_prime_factors(to as usize + 1);
    for &n in &ns {
        let t0 = Instant::now();
        let (score, moves) = &known[&u64::from(n)];
        let target = *score as i64;
        let board = Board::new(n, &spf);
        let ustar = recorded_ustar(u64::from(n), moves, &spf);
        let roles = low_roles(n, &spf, &ustar);
        // The classes: primes in (√n, n/4] with the same ⌊n/p⌋; adjacent members make the pairs.
        let mut primes: Vec<u32> = (2..=n / 4).filter(|&p| (p as u64) * (p as u64) > u64::from(n)).collect();
        primes.retain(|&p| is_prime(u64::from(p), &spf));
        let mut pairs: Vec<(u32, u32)> = Vec::new();
        for w in primes.windows(2) {
            if n / w[0] == n / w[1] {
                pairs.push((w[0], w[1]));
            }
        }
        let cof = |set: &[u32], r: u32| -> i64 { set.iter().filter(|&&x| x % r == 0).map(|&x| i64::from(x / r)).sum() };
        let solve = |mu: &[i64]| -> (i64, Vec<u32>) {
            let mut w: Vec<i64> = (0..=i64::from(n)).collect();
            for (i, &(p, q)) in pairs.iter().enumerate() {
                for x in (p..=n).step_by(p as usize) {
                    w[x as usize] -= mu[i] * i64::from(x / p);
                }
                for x in (q..=n).step_by(q as usize) {
                    w[x as usize] += mu[i] * i64::from(x / q);
                }
            }
            assert!(w[2..].iter().all(|&v| v > 0), "n={n}: a weight fell to 0");
            let mut meet = Meet::new(Parity::pair(&board, &w));
            match meet.solve(&roles) {
                Outcome::Bound(b) => (b.value, b.set),
                _ => panic!("n={n}: the root is not certified"),
            }
        };
        let mut mu = vec![0i64; pairs.len()];
        let (base, set0) = solve(&mu);
        let broken0 = pairs.iter().filter(|&&(p, q)| cof(&set0, p) > cof(&set0, q)).count();
        let mut best = base;
        let mut theta = 1.0f64;
        let mut since = 0;
        let mut iters = 0;
        for _ in 0..40 {
            let (value, set) = solve(&mu);
            iters += 1;
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
            let g: Vec<i64> = pairs.iter().map(|&(p, q)| cof(&set, q) - cof(&set, p)).collect();
            let norm: i64 = g.iter().zip(&mu).map(|(&gi, &m)| if gi < 0 || m > 0 { gi * gi } else { 0 }).sum();
            if norm == 0 || theta < 0.01 {
                break;
            }
            let step = theta * ((value - target).max(1) as f64) / norm as f64;
            for (i, &(p, _)) in pairs.iter().enumerate() {
                let next = (mu[i] as f64 - step * g[i] as f64).round().max(0.0) as i64;
                mu[i] = next.min(i64::from(p) / 2);
            }
        }
        println!(
            "{{\"n\":{n},\"score\":{target},\"pairs\":{},\"broken_at_root\":{broken0},\"gap\":{},\"gap_sym\":{},\
             \"drop\":{},\"iters\":{iters},\"secs\":{:.1}}}",
            pairs.len(),
            base - target,
            best - target,
            base - best,
            t0.elapsed().as_secs_f64()
        );
    }
}
