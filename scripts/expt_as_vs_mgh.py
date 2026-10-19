"""
In this script, we will compare AS and MGH.
"""
from samplers import MaxGeomSample, AffirmativeSketch
from samplers import AlphaAffirmativeSketch, AlphaMaxGeomSample
from helpers.string_utils import generate_random_strings
from tqdm import tqdm
import math
import random
import argparse
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor



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


def _run_pair_experiment(args):
    """Run all permutation and seed trials for one pair in a worker process."""
    pair_id, A, B, num_runs, sketch_kind = args
    w = 64
    rng = random.Random(42 + pair_id)
    permutation_rows = []
    seed_rows = []

    if sketch_kind == "plain":
        as_class = AffirmativeSketch
        mgh_class = MaxGeomSample
        as_kwargs = {"k": 100}
        mgh_kwargs = {"k": 70, "w": w}
    else:
        parameter = 0.5
        as_class = AlphaAffirmativeSketch
        mgh_class = AlphaMaxGeomSample
        as_kwargs = {"alpha": parameter}
        mgh_kwargs = {"alpha": 0.4, "w": w}

    for permute_id in range(num_runs):
        A_perm = list(A)
        B_perm = list(B)
        rng.shuffle(A_perm)
        rng.shuffle(B_perm)

        as_sketch_A = as_class(seed=42, **as_kwargs)
        as_sketch_B = as_class(seed=42, **as_kwargs)
        mgh_sketch_A = mgh_class(seed=42, **mgh_kwargs)
        mgh_sketch_B = mgh_class(seed=42, **mgh_kwargs)
        as_sketch_A.add_many_items(A_perm)
        mgh_sketch_A.add_many_items(A_perm)
        as_sketch_B.add_many_items(B_perm)
        mgh_sketch_B.add_many_items(B_perm)

        permutation_rows.append(
            (pair_id, permute_id, 42, len(A), len(B), as_sketch_A.size(),
             as_sketch_B.size(), mgh_sketch_A.size(), mgh_sketch_B.size(),
             as_sketch_A.jaccard(as_sketch_B), mgh_sketch_A.jaccard(mgh_sketch_B))
        )

    for seed_id in range(num_runs):
        as_sketch_A = as_class(seed=seed_id, **as_kwargs)
        as_sketch_B = as_class(seed=seed_id, **as_kwargs)
        mgh_sketch_A = mgh_class(seed=seed_id, **mgh_kwargs)
        mgh_sketch_B = mgh_class(seed=seed_id, **mgh_kwargs)
        as_sketch_A.add_many_items(A)
        mgh_sketch_A.add_many_items(A)
        as_sketch_B.add_many_items(B)
        mgh_sketch_B.add_many_items(B)

        seed_rows.append(
            (pair_id, seed_id, len(A), len(B), as_sketch_A.size(),
             as_sketch_B.size(), mgh_sketch_A.size(), mgh_sketch_B.size(),
             as_sketch_A.jaccard(as_sketch_B), mgh_sketch_A.jaccard(mgh_sketch_B))
        )

    return permutation_rows, seed_rows


def _run_experiment(sketch_kind, permutation_path, seed_path):
    w = 64
    num_runs = 100
    num_pairs = 20
    set_size = 100000
    t = 0.5
    universal_pool = generate_random_strings(3000000, 10)
    rng = random.Random(42)
    jobs = []
    for pair_id in range(num_pairs):
        A, B = synthesize_sets_jaccard(t, set_size, universal_pool, rng)
        jobs.append((pair_id, list(A), list(B), num_runs, sketch_kind))

    parameter_name = "parameter_k" if sketch_kind == "plain" else "parameter_alpha"
    parameter = 70 if sketch_kind == "plain" else 0.4
    permutation_header = f"{parameter_name},pair_id,permute_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n"
    seed_header = f"{parameter_name},pair_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n"

    with open(permutation_path, "w") as f_permute, open(seed_path, "w") as f_seed:
        f_permute.write(permutation_header)
        f_seed.write(seed_header)
        with ProcessPoolExecutor(max_workers=min(num_pairs, os.cpu_count() or 1)) as executor:
            for permutation_rows, seed_rows in tqdm(
                executor.map(_run_pair_experiment, jobs),
                total=num_pairs,
                desc="Pairs",
                leave=False,
            ):
                for row in permutation_rows:
                    f_permute.write(f"{parameter},{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{row[8]},{t},{row[9]},{row[10]}\n")
                for row in seed_rows:
                    f_seed.write(f"{parameter},{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]},{row[7]},{t},{row[8]},{row[9]}\n")



def expt_permutation_test_as_vs_mgh():
    """
    Create two sets A and B
    Permute them x times
    Compute AS and MGH sketches for each permutation
    Compute Jaccard for each permutation
    Record the estimated Jaccard values
    Later, we can plot the distribution of estimated Jaccard values
    """
    _run_experiment("plain", "results/as_vs_mgh_plain_varying_perm.txt", "results/as_vs_mgh_plain_varying_seed.txt")

    print ("Results saved to\nas_vs_mgh_plain_varying_perm.txt,\nas_vs_mgh_plain_varying_seed.txt")




def expt_permutation_test_alpha_as_vs_alpha_mgh():
    """
    Create two sets A and B
    Permute them x times
    Compute AS and MGH sketches for each permutation
    Compute Jaccard for each permutation
    Record the estimated Jaccard values
    Later, we can plot the distribution of estimated Jaccard values
    """
    _run_experiment("alpha", "results/alpha_as_vs_alpha_mgh_varying_perm.txt", "results/alpha_as_vs_alpha_mgh_varying_seed.txt")

    print ("Results saved to\nalpha_as_vs_alpha_mgh_varying_perm.txt,\nalpha_as_vs_alpha_mgh_varying_seed.txt")


def main():
    expt_permutation_test_as_vs_mgh()
    expt_permutation_test_alpha_as_vs_alpha_mgh()


if __name__ == "__main__":
    main()