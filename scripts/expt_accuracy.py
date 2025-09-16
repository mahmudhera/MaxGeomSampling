from samplers import FracMinHashSketch, MaxGeomSample, AlphaMaxGeomSample
from helpers.string_utils import generate_random_strings
import random

if __name__ == '__main__':
    # constants
    num_trails = 10000
    num_samples_each_trial = 20
    alpha_values_tested = [0.2, 0.3, 0.4, 0.5]
    k_values_tested = [50, 100, 200, 400]
    output_file = 'results/results_accuracy_of_jaccard_no_filtering'
    
    # set random seed for reproducibility
    random.seed(42)
    
    # generate a universal set of 20K random strings
    universal_set = generate_random_strings(20000, 10)
    
    # create one set with 10K random strings from universal set
    set1 = set(random.sample(universal_set, 10000))
    
    # for each trial, create another set whose length is random between 1K ans 20K, then compute true jaccard, and estimate jaccard using different MGS and alpha-MGS samples
    # for the results, we have a dictionary with keys as 'MGS' or 'alpha-MGS', and values as (parameter, length of set2, true jaccard, estimated jaccard)
    results = {'MGS': [], 'alpha-MGS': []}
    for _ in range(num_trails):
        # create another set with random length between 1K and 20K
        len_set2 = random.randint(1000, 20000)
        set2 = set(random.sample(universal_set, len_set2))
        
        # compute true jaccard index
        true_jaccard = len(set1.intersection(set2)) / len(set1.union(set2))
        
        # estimate jaccard using MGS with different k values, repeat num_samples_each_trial times, each with a different random seed
        
        # test MGS with different k values
        for k in k_values_tested:
            for seed in range(num_samples_each_trial):
                mgs1 = MaxGeomSample(k=k, w=64, seed=seed)
                mgs1.add_many_items(set1)
                mgs2 = MaxGeomSample(k=k, w=64, seed=seed)
                mgs2.add_many_items(set2)
                estimated_jaccard = mgs1.jaccard_index(mgs2)
                results['MGS'].append((k, len_set2, true_jaccard, estimated_jaccard))
        
        # test alpha-MGS with different alpha values
        for alpha in alpha_values_tested:
            for seed in range(num_samples_each_trial):
                alpha_mgs1 = AlphaMaxGeomSample(alpha=alpha, w=64, seed=seed)
                alpha_mgs1.add_many_items(set1)
                alpha_mgs2 = AlphaMaxGeomSample(alpha=alpha, w=64, seed=seed)
                alpha_mgs2.add_many_items(set2)
                estimated_jaccard = alpha_mgs1.jaccard_index(alpha_mgs2)
                results['alpha-MGS'].append((alpha, len_set2, true_jaccard, estimated_jaccard))  
            
    # print results to a file
    with open('expt_accuracy_results.txt', 'w') as f:
        f.write('Method\tParameter\tLen_Set2\tTrue_Jaccard\tEstimated_Jaccard\n')
        for method, records in results.items():
            for record in records:
                param, len_set2, true_jaccard, est_jaccard = record
                f.write(f'{method}\t{param}\t{len_set2}\t{true_jaccard:.4f}\t{est_jaccard:.4f}\n') 
    