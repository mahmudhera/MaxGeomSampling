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



def expt_permutation_test_as_vs_mgh():
    """
    Create two sets A and B
    Permute them x times
    Compute AS and MGH sketches for each permutation
    Compute Jaccard for each permutation
    Record the estimated Jaccard values
    Later, we can plot the distribution of estimated Jaccard values
    """
    # experiment parameters
    w = 64
    k = 70
    num_runs = 100
    num_pairs = 20
    set_size = 100000
    t = 0.5
    seed = 42

    # create a universal pool of strings
    universal_pool = generate_random_strings(3000000, 10)

    # create a random number generator
    rng = random.Random(seed)

    f_permute = open("as_vs_mgh_plain_varying_perm.txt", "w")
    f_seed = open("as_vs_mgh_plain_varying_seed.txt", "w")
    f_permute.write("parameter_k,pair_id,permute_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n")
    f_seed.write("parameter_k,pair_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n")

    for pair_id in tqdm(range(num_pairs), desc="Pairs", leave=False):
        # create two sets A and B with Jaccard similarity t
        A, B = synthesize_sets_jaccard(t, set_size, universal_pool, rng)
        A, B = list(A), list(B)

        for permute_id in tqdm(range(num_runs), desc="Runs", leave=False):
            # permute A and B
            random.shuffle(A)
            random.shuffle(B)
            A_perm = list(A)
            B_perm = list(B)

            # compute AS and MGH sketches
            as_sketch_A = AffirmativeSketch(k=k, seed=seed)
            as_sketch_B = AffirmativeSketch(k=k, seed=seed)
            mgh_sketch_A = MaxGeomSample(k=k, w=w, seed=seed)
            mgh_sketch_B = MaxGeomSample(k=k, w=w, seed=seed)

            as_sketch_A.add_many_items(A_perm)
            mgh_sketch_A.add_many_items(A_perm)
            as_sketch_B.add_many_items(B_perm)
            mgh_sketch_B.add_many_items(B_perm)

            # compute Jaccard similarity
            jaccard_estimate_as = as_sketch_A.jaccard(as_sketch_B)
            jaccard_estimate_mgh = mgh_sketch_A.jaccard(mgh_sketch_B)

            f_permute.write(f"{k},{pair_id},{permute_id},{seed},{len(A)},{len(B)},{as_sketch_A.size()},{as_sketch_B.size()},{mgh_sketch_A.size()},{mgh_sketch_B.size()},{t},{jaccard_estimate_as},{jaccard_estimate_mgh}\n")

        A_perm = list(A)
        B_perm = list(B)

        for seed_id in tqdm(range(num_runs), desc="Seeds", leave=False):
            # create new sketches with different seeds
            as_sketch_A = AffirmativeSketch(k=k, seed=seed_id)
            as_sketch_B = AffirmativeSketch(k=k, seed=seed_id)
            mgh_sketch_A = MaxGeomSample(k=k, w=w, seed=seed_id)
            mgh_sketch_B = MaxGeomSample(k=k, w=w, seed=seed_id)

            as_sketch_A.add_many_items(A_perm)
            mgh_sketch_A.add_many_items(A_perm)
            as_sketch_B.add_many_items(B_perm)
            mgh_sketch_B.add_many_items(B_perm)

            # compute Jaccard similarity
            jaccard_estimate_as = as_sketch_A.jaccard(as_sketch_B)
            jaccard_estimate_mgh = mgh_sketch_A.jaccard(mgh_sketch_B)

            f_seed.write(f"{k},{pair_id},{seed_id},{len(A)},{len(B)},{as_sketch_A.size()},{as_sketch_B.size()},{mgh_sketch_A.size()},{mgh_sketch_B.size()},{t},{jaccard_estimate_as},{jaccard_estimate_mgh}\n")

    f_permute.close()
    f_seed.close()

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
    # experiment parameters
    w = 64
    alpha = 0.4
    num_runs = 100
    num_pairs = 20
    set_size = 100000
    t = 0.5
    seed = 42

    # create a universal pool of strings
    universal_pool = generate_random_strings(3000000, 10)

    # create a random number generator
    rng = random.Random(seed)

    f_permute = open("alpha_as_vs_alpha_mgh_varying_perm.txt", "w")
    f_seed = open("alpha_as_vs_alpha_mgh_varying_seed.txt", "w")
    f_permute.write("parameter_alpha,pair_id,permute_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n")
    f_seed.write("parameter_alpha,pair_id,seed,A_size,B_size,as_sketch_size_A,as_sketch_size_B,mgh_sketch_size_A,mgh_sketch_size_B,true_jaccard,jaccard_as,jaccard_mgh\n")

    for pair_id in tqdm(range(num_pairs), desc="Pairs", leave=False):
        # create two sets A and B with Jaccard similarity t
        A, B = synthesize_sets_jaccard(t, set_size, universal_pool, rng)
        A, B = list(A), list(B)

        for permute_id in tqdm(range(num_runs), desc="Runs", leave=False):
            # permute A and B
            random.shuffle(A)
            random.shuffle(B)
            A_perm = list(A)
            B_perm = list(B)

            # compute AS and MGH sketches
            as_sketch_A = AlphaAffirmativeSketch(alpha=alpha, seed=seed)
            as_sketch_B = AlphaAffirmativeSketch(alpha=alpha, seed=seed)
            mgh_sketch_A = AlphaMaxGeomSample(alpha=alpha, w=w, seed=seed)
            mgh_sketch_B = AlphaMaxGeomSample(alpha=alpha, w=w, seed=seed)

            as_sketch_A.add_many_items(A_perm)
            mgh_sketch_A.add_many_items(A_perm)
            as_sketch_B.add_many_items(B_perm)
            mgh_sketch_B.add_many_items(B_perm)

            # compute Jaccard similarity
            jaccard_estimate_as = as_sketch_A.jaccard(as_sketch_B)
            jaccard_estimate_mgh = mgh_sketch_A.jaccard(mgh_sketch_B)

            f_permute.write(f"{alpha},{pair_id},{permute_id},{seed},{len(A)},{len(B)},{as_sketch_A.size()},{as_sketch_B.size()},{mgh_sketch_A.size()},{mgh_sketch_B.size()},{t},{jaccard_estimate_as},{jaccard_estimate_mgh}\n")

        A_perm = list(A)
        B_perm = list(B)

        for seed_id in tqdm(range(num_runs), desc="Seeds", leave=False):
            # create new sketches with different seeds
            as_sketch_A = AlphaAffirmativeSketch(alpha=alpha, seed=seed_id)
            as_sketch_B = AlphaAffirmativeSketch(alpha=alpha, seed=seed_id)
            mgh_sketch_A = AlphaMaxGeomSample(alpha=alpha, w=w, seed=seed_id)
            mgh_sketch_B = AlphaMaxGeomSample(alpha=alpha, w=w, seed=seed_id)

            as_sketch_A.add_many_items(A_perm)
            mgh_sketch_A.add_many_items(A_perm)
            as_sketch_B.add_many_items(B_perm)
            mgh_sketch_B.add_many_items(B_perm)

            # compute Jaccard similarity
            jaccard_estimate_as = as_sketch_A.jaccard(as_sketch_B)
            jaccard_estimate_mgh = mgh_sketch_A.jaccard(mgh_sketch_B)

            f_seed.write(f"{alpha},{pair_id},{seed_id},{len(A)},{len(B)},{as_sketch_A.size()},{as_sketch_B.size()},{mgh_sketch_A.size()},{mgh_sketch_B.size()},{t},{jaccard_estimate_as},{jaccard_estimate_mgh}\n")

    f_permute.close()
    f_seed.close()

    print ("Results saved to\nalpha_as_vs_alpha_mgh_varying_perm.txt,\nalpha_as_vs_alpha_mgh_varying_seed.txt")


def main():
    expt_permutation_test_as_vs_mgh()
    expt_permutation_test_alpha_as_vs_alpha_mgh()


if __name__ == "__main__":
    main()