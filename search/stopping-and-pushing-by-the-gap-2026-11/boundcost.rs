//! Scratch timing for study B13 (not committed): the board, its preparation, and the root's GF(2) bound.
//!
//! cargo run --release --example boundcost -- N...

use std::time::Instant;
use taxman::bits::Bits;
use taxman::board::Board;
use taxman::gf2::{Gf2Bound, Gf2Graph};
use taxman::search::SearchTactics;

fn time_of<const W: usize>(n: u32) -> String {
    let t0 = Instant::now();
    let board = Board::<W>::for_n(n);
    let t1 = Instant::now();
    let p = board.prepare(SearchTactics::default()).expect("prepare");
    let digest = p.problem().digest();
    let t2 = Instant::now();
    let graph = Gf2Graph::new(&p.model, &p.root, &p.candidates);
    let mut bound = Gf2Bound::<W>::new(&graph);
    bound.reset(&Bits::EMPTY, &p.candidates);
    let value = bound.evaluate(p.max_total, None).value;
    let t3 = Instant::now();
    format!(
        "n={n} bound={} board {:.3} s, prepare and problem {:.3} s, gf2 bound {:.3} s (digest {digest:x})",
        board.in_the_bag + value,
        (t1 - t0).as_secs_f64(),
        (t2 - t1).as_secs_f64(),
        (t3 - t2).as_secs_f64()
    )
}

fn main() {
    for n in std::env::args().skip(1).map(|a| a.parse::<u32>().unwrap()) {
        println!("{}", taxman::with_width!(n, W => time_of::<W>(n)));
    }
}
