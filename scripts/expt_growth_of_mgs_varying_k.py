"""
In this script, we conduct experiments to analyze the growth of MaxGeomSampling samples
by varying the parameter k.
"""

import random
from samplers import MaxGeomSample
from tqdm import tqdm
import string

def generate_random_strings(num_strings: int, length: int) -> list:
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]

if __name__ == "__main__":
    num_runs_each_setting = 100
    w = 64
    #k_values = [25, 50, 100, 200, 400, 800]
    k_values = [100]

    # generate data sizes
    data_sizes = [10000, 20000, 30000, 40000]

    # vary size of data from 10K to 1M in steps of 10K
    data_size_to_avg_maxgeom_sample_size_per_k = {k: {} for k in k_values}
    data_size_to_stddev_maxgeom_sample_size_per_k = {k: {} for k in k_values}
    
    for data_size in tqdm(data_sizes):
        data = generate_random_strings(data_size, 10)
        
        for k in k_values:
            maxgeom_sample_sizes = []
            for seed in range(num_runs_each_setting):
                max_geom_sample = MaxGeomSample(k=k, w=w, seed=seed)
                max_geom_sample.add_many_items(data)
                maxgeom_sample_sizes.append(len(max_geom_sample))
            avg_maxgeom_sample_size = sum(maxgeom_sample_sizes) / num_runs_each_setting
            stddev_maxgeom_sample_size = (sum((x - avg_maxgeom_sample_size) ** 2 for x in maxgeom_sample_sizes) / num_runs_each_setting) ** 0.5
            data_size_to_avg_maxgeom_sample_size_per_k[k][data_size] = avg_maxgeom_sample_size
            data_size_to_stddev_maxgeom_sample_size_per_k[k][data_size] = stddev_maxgeom_sample_size
        
    # Print results
    header = "set_size"
    for k in k_values:
        header += f"\tmgs_sample_size_avg_k_{k}\tmgs_sample_size_stddev_k_{k}"
    print(header)
    
    for data_size in data_sizes:
        row = f"{data_size}"
        for k in k_values:
            avg_size = data_size_to_avg_maxgeom_sample_size_per_k[k][data_size]
            stddev_size = data_size_to_stddev_maxgeom_sample_size_per_k[k][data_size]
            row += f"\t{avg_size:.2f}\t{stddev_size:.2f}"
        print(row)
