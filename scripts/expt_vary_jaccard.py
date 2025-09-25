from samplers import FracMinHashSketch, MaxGeomSample, AlphaMaxGeomSample
from helpers.string_utils import generate_random_strings
import random
from tqdm import tqdm


'''
The scenarion in this script is as follows.
A and B are of length 50K each.
Their overlap changes, and thus the Jaccard index changes.
We want to see how the accuracy of estimating Jaccard index changes with the true Jaccard index.
We repeat this for different k values of MGS (MaxGeomSampling).
'''


if __name__ == '__main__':
    # constants
    num_trials = 5000
    k_values_tested = [50, 100, 200, 400]
    output_file = 'results/results_accuracy_by_varying_jaccard'
    random_seed = 42
    random.seed(random_seed)
    size_universe = 300000
    size_each_small_universe = size_universe/3

    len_A = 50000
    len_B = 50000

    all_recorded_results = []

    for _ in tqdm(range(num_trials)):
        # generate three sets of 100K elements
        universe_only_A = generate_random_strings(100000, 10)
        universe_only_B = generate_random_strings(100000, 10)
        universe_common = generate_random_strings(100000, 10)

        desired_jaccard = random.uniform(0.0, 1.0)
        size_common = int((desired_jaccard * (len_A + len_B)) / (1 + desired_jaccard))
        size_only_A = len_A - size_common
        size_only_B = len_B - size_common

        set_A = set(universe_only_A[:size_only_A] + universe_common[:size_common])
        set_B = set(universe_only_B[:size_only_B] + universe_common[:size_common])
        true_jaccard = len(set_A.intersection(set_B)) / len(set_A.union(set_B))
        
        for k in k_values_tested:
            sample_A = MaxGeomSample(k=k, seed=random_seed)
            sample_A.add_many_items(set_A)
            sample_B = MaxGeomSample(k=k, seed=random_seed)
            sample_B.add_many_items(set_B)
            estimated_jaccard = sample_A.jaccard_index(sample_B)
            all_recorded_results.append((k, true_jaccard, estimated_jaccard))

    # print results to a file
    with open(output_file, 'w') as f:
        f.write('k\tTrue_Jaccard\tEstimated_Jaccard\n')
        for record in all_recorded_results:
            f.write(f'{record[0]}\t{record[1]}\t{record[2]}\n')

    print("Results written to: ", output_file )