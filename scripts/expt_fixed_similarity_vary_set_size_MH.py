from samplers import MinHashSketch 
from helpers.string_utils import generate_random_strings
from tqdm import tqdm
import math
import random
import argparse
import os


def synthesize_sets_jaccard(t, n, universal_pool, rng):
    """
    Build sets A,B with approximately Jaccard = t.
    |A|=|B|=n, intersection x = (2*n*t)/(1+t)
    """
    x = int(round((2 * n * t) / (1 + t)))
    x = max(0, min(x, n))
    a = b = n

    # Randomly select shared and unique elements from universal pool
    shared = set(rng.sample(universal_pool, x))
    remaining = list(set(universal_pool) - shared)
    rng.shuffle(remaining)

    a_only = set(remaining[: a - x])
    b_only = set(remaining[a - x : a - x + (b - x)])

    A = shared | a_only
    B = shared | b_only

    return A, B

def estimate_with_minhash(A, B, k, seeds, metric="jaccard"):
    ests = []
    a, b = len(A), len(B)
    sample_sizes_A = []
    sample_sizes_B = []

    for s in tqdm(seeds):
        m1 = MinHashSketch(k=k, seed=s)
        m2 = MinHashSketch(k=k, seed=s)
        m1.add_many_items(A)
        m2.add_many_items(B)

        if metric == "jaccard":
            ests.append(m1.jaccard_index(m2))
        else:
            raise ValueError("metric must be 'jaccard' for MinHash estimation")

        sample_sizes_A.append(m1.sample_size())
        sample_sizes_B.append(m2.sample_size())

    return ests, sample_sizes_A, sample_sizes_B


def mse(vs, target):
    return sum((v - target) ** 2 for v in vs) / len(vs) if vs else float('nan')


def run_experiment(
    t,
    metric,
    k,
    seeds_per_size,
    base_n,
    steps,
    growth,
    output_file,
    global_seed=42
):
    rng = random.Random(global_seed)
    metric = metric.lower()
    scale = 2 if growth == "x2" else 10 if growth == "x10" else None
    if scale is None:
        raise ValueError("growth must be 'x2' or 'x10'")

    seeds = list(range(seeds_per_size))

    # Generate a universal pool of unique strings
    max_size_needed = base_n * (scale ** (steps - 1)) * 2
    pool_size = int(max_size_needed)  # large enough buffer
    universal_pool = generate_random_strings(pool_size, 10)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    with open(output_file, "w") as f:
        f.write("metric\tMinHash_k\tstep\t|A|\t|B|\tmean_sample_size_A\tmean_sample_size_B\ttrue_sim\tmean_est\tmse\n")

    for step in range(steps):
        print(f"Step {step + 1}/{steps} (set size growth {growth}): ")

        n = base_n * (scale ** step)
        A, B = synthesize_sets_jaccard(t, n, universal_pool, rng)
        
        # Compute true similarity
        if metric == "jaccard":
            true_sim = len(A & B) / len(A | B)
        else:
            true_sim = len(A & B) / math.sqrt(len(A) * len(B))

        ests, sample_sizes_A, sample_sizes_B = estimate_with_minhash(A, B, k, seeds, metric)

        mean_est = sum(ests) / len(ests)
        mean_sample_size_A = sum(sample_sizes_A) / len(sample_sizes_A)
        mean_sample_size_B = sum(sample_sizes_B) / len(sample_sizes_B)
        err = mse(ests, true_sim)

        with open(output_file, "a") as f:
            f.write(f"{metric}\t{k}\t{step}\t{len(A)}\t{len(B)}\t{mean_sample_size_A:.6f}\t{mean_sample_size_B:.6f}\t{true_sim:.6f}\t{mean_est:.6f}\t{err:.6e}\n")

    print(f"\nResults written to:\n{output_file}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MGS similarity experiment (exact-target sets)")
    parser.add_argument("--t", type=str, required=True,
                        help="Target similarity t, a floating point number between 0 and 1.")
    parser.add_argument("--metric", type=str, choices=["jaccard"], required=True,
                        help="Similarity metric to target and evaluate.")
    parser.add_argument("--k", type=int, default=500, help="MinHash parameter k (number of hash functions).")
    parser.add_argument("--seeds", type=int, default=50, help="Number of salt seeds per size.")
    parser.add_argument("--base_n", type=int, default=1_000, help="Base |A|=|B| scale before growth multipliers.")
    parser.add_argument("--steps", type=int, default=10, help="Number of size growth steps.")
    parser.add_argument("--growth", type=str, choices=["x2", "x10"], default="x2",
                        help="How to grow |A| and |B| each step.")
    parser.add_argument("--out", type=str, default="results/mgs_similarity_experiment",
                        help="Per-seed results csv path.")
    parser.add_argument("--seed", type=int, default=42, help="Global RNG seed for reproducibility.")
    args = parser.parse_args()

    print("Running with the following parameters:")
    for key, value in vars(args).items():
        print(f"  {key}: {value}")

    run_experiment(
        t=float(args.t),
        metric=args.metric,
        k=args.k,
        seeds_per_size=args.seeds,
        base_n=args.base_n,
        steps=args.steps,
        growth=args.growth,
        output_file=args.out,
        global_seed=args.seed
    )
