use rand::Rng;
use std::f64;
use std::time::Instant;

fn compute_ratio(n: usize, k: usize) -> f64 {
    let mut rng = rand::thread_rng();

    let mut points: Vec<Vec<f64>> = Vec::with_capacity(k);
    for _ in 0..k {
        let point: Vec<f64> = (0..n).map(|_| rng.gen()).collect();
        points.push(point);
    }

    let mut dmax = 0.0;
    let mut dmin = f64::MAX;

    for i in 0..k {
        for j in (i + 1)..k {
            let dist = euclidean_distance(&points[i], &points[j]);
            if dist > dmax {
                dmax = dist;
            }
            if dist < dmin {
                dmin = dist;
            }
        }
    }

    dmax / dmin
}

fn euclidean_distance(a: &[f64], b: &[f64]) -> f64 {
    a.iter()
        .zip(b.iter())
        .map(|(x, y)| (x - y).powi(2))
        .sum::<f64>()
        .sqrt()
}

fn main() {
    let k = 50;
    let ns = vec![1, 10, 100, 1000, 10000];

    for &n in &ns {
        println!("Computing for n = {}", n);
        let start = Instant::now();
        let ratio = compute_ratio(n, k);
        let duration = start.elapsed();
        println!("For n = {}, dmax/dmin = {:.6}", n, ratio);
        println!("Time taken: {:?}", duration);
        println!("-----------------------------------");
    }
}

