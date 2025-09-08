"""
In this script, we conduct experiments to analyze the growth of MaxGeomSampling samples
by varying the parameter k.
"""

import random
from samplers import AlphaMaxGeomSample
from helpers.string_utils import generate_random_strings

if __name__ == "__main__":
    random.seed(42)
    num_runs_each_setting = 20
    w = 64
    alpha_values = [0.25, 0.5, 0.75]

    # generate data sizes
    data_sizes = [i for i in range(10000, 1000001, 10000)]

    # vary size of data from 10K to 1M in steps of 10K
    data_size_to_avg_maxgeom_sample_size_per_alpha = {alpha: {} for alpha in alpha_values}
    data_size_to_stddev_maxgeom_sample_size_per_alpha = {alpha: {} for alpha in alpha_values}

    for data_size in data_sizes:
        data = generate_random_strings(data_size, 10)

        for alpha in alpha_values:
            maxgeom_sample_sizes = []
            for seed in range(num_runs_each_setting):
                max_geom_sample = AlphaMaxGeomSample(alpha=alpha, w=w, seed=seed)
                max_geom_sample.add_many_items(data)
                maxgeom_sample_sizes.append(len(max_geom_sample))
            avg_maxgeom_sample_size = sum(maxgeom_sample_sizes) / num_runs_each_setting
            stddev_maxgeom_sample_size = (sum((x - avg_maxgeom_sample_size) ** 2 for x in maxgeom_sample_sizes) / num_runs_each_setting) ** 0.5
            data_size_to_avg_maxgeom_sample_size_per_alpha[alpha][data_size] = avg_maxgeom_sample_size
            data_size_to_stddev_maxgeom_sample_size_per_alpha[alpha][data_size] = stddev_maxgeom_sample_size

    # Print results
    header = "set_size"
    for alpha in alpha_values:
        header += f"\tamgs_sample_size_avg_alpha_{alpha}\tamgs_sample_size_stddev_alpha_{alpha}"
    print(header)
    
    for data_size in data_sizes:
        row = f"{data_size}"
        for alpha in alpha_values:
            avg_size = data_size_to_avg_maxgeom_sample_size_per_alpha[alpha][data_size]
            stddev_size = data_size_to_stddev_maxgeom_sample_size_per_alpha[alpha][data_size]
            row += f"\t{avg_size:.2f}\t{stddev_size:.2f}"
        print(row)
