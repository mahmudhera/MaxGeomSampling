from samplers import AlphaMaxGeomSample
import random
from helpers.string_utils import generate_random_strings
import sys
from tqdm import tqdm


if __name__ == "__main__":

    # take alpha and target_jaccard as command line args
    if len(sys.argv) < 4:
        print("Usage: python expt_alpha_MGS_simple_test.py <alpha> <target_similarity> <num_trials>")
        exit(1)

    try:
        alpha = float(sys.argv[1])
        target_similarity = float(sys.argv[2])
        num_trials = int(sys.argv[3])
    except ValueError:
        print("Both alpha and target_similarity must be numbers.")
        exit(1)

    # check ranges of inputs
    if not (0 < alpha < 1):
        print("Alpha must be in (0, 1).")
        exit(1)
    if not (0 < target_similarity < 1):
        print("Target similarity must be in (0, 1).")
        exit(1)

    print(f"Using alpha={alpha}, target_similarity={target_similarity}")

    # first, analyze for jaccard similarity
    target_jaccard = target_similarity

    # fix set sizes
    set1_size_only = set2_size_only = 50000
    set_common_size = int((2 * target_jaccard) / (1 - target_jaccard) * set1_size_only)

    # Sample data: random 1M strings over alphabet
    data1 = generate_random_strings(set1_size_only, 10)
    data2 = generate_random_strings(set2_size_only, 10)
    data3 = generate_random_strings(set_common_size, 10)

    setA = data1 + data3
    setB = data2 + data3

    # their jaccard should be 0.5
    true_jaccard = len(set(setA).intersection(set(setB))) / len(set(setA).union(set(setB)))
    print(f"True Jaccard: {true_jaccard}")

    # now create AlphaMaxGeomSample instances and compute jaccard using these samples. 
    # do this num_trials times and average the results
    recorded_jaccard_values = []
    for _ in tqdm(range(num_trials)):
        seed = random.randint(0, 2**32 - 1)
        alpha_mgs_sample1 = AlphaMaxGeomSample(alpha, seed=seed)
        alpha_mgs_sample1.update(setA)
        alpha_mgs_sample2 = AlphaMaxGeomSample(alpha, seed=seed)
        alpha_mgs_sample2.update(setB)

        est_jaccard = alpha_mgs_sample1.jaccard_index(alpha_mgs_sample2)
        recorded_jaccard_values.append(est_jaccard)

    avg_jaccard = sum(recorded_jaccard_values) / len(recorded_jaccard_values)
    print(f"Average Jaccard from AlphaMaxGeomSample with alpha={alpha}: {avg_jaccard}")


    # now make a similar test for cosine similarity
    target_cosine = target_similarity

    # create set sizes
    set1_size_only = set2_size_only = 50000
    set_common_size = int(set1_size_only * target_cosine / (1.0 - target_cosine))

    # Sample data: random 1M strings over alphabet
    data1 = generate_random_strings(set1_size_only, 10)
    data2 = generate_random_strings(set2_size_only, 10)
    data3 = generate_random_strings(set_common_size, 10)

    setA = data1 + data3
    setB = data2 + data3

    # their cosine should be target_cosine
    true_cosine = len(set(setA).intersection(set(setB))) / ((len(set(setA)) * len(set(setB)))**0.5)
    print(f"True Cosine: {true_cosine}")

    # now create AlphaMaxGeomSample instances and compute cosine using these samples.
    recorded_cosine_values = []
    for _ in tqdm(range(num_trials)):
        seed = random.randint(0, 2**32 - 1)
        alpha_mgs_sample1 = AlphaMaxGeomSample(alpha, seed=seed)
        alpha_mgs_sample1.update(setA)
        alpha_mgs_sample2 = AlphaMaxGeomSample(alpha, seed=seed)
        alpha_mgs_sample2.update(setB)

        est_cosine = alpha_mgs_sample1.cosine_similarity(alpha_mgs_sample2)
        recorded_cosine_values.append(est_cosine)
    avg_cosine = sum(recorded_cosine_values) / len(recorded_cosine_values)
    print(f"Average Cosine from AlphaMaxGeomSample with alpha={alpha}: {avg_cosine}")