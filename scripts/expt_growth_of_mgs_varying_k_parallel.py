"""
In this script, we conduct experiments to analyze the growth of MaxGeomSampling samples
by varying the parameter k.
"""

import random
from samplers import MaxGeomSample
from tqdm import tqdm
import string

from concurrent.futures import ProcessPoolExecutor

def generate_random_strings(num_strings: int, length: int) -> list:
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]


# Note: k here is not kmer size, rather the b parameter of the MGH algorithm
def run_experiment_for_one_k_and_size(k, data_size, num_runs_each_setting, w):
    data = generate_random_strings(data_size, 10)
    maxgeom_sample_sizes = []
    for seed in range(num_runs_each_setting):
        max_geom_sample = MaxGeomSample(k=k, w=w, seed=seed)
        max_geom_sample.add_many_items(data)
        maxgeom_sample_sizes.append(len(max_geom_sample))
    avg_maxgeom_sample_size = sum(maxgeom_sample_sizes) / num_runs_each_setting
    stddev_maxgeom_sample_size = (sum((x - avg_maxgeom_sample_size) ** 2 for x in maxgeom_sample_sizes) / num_runs_each_setting) ** 0.5

    return (k, data_size, avg_maxgeom_sample_size, stddev_maxgeom_sample_size)


if __name__ == "__main__":
    random.seed(42)
    num_runs_each_setting = 100
    w = 64
    num_processes = 32
    #k_values = [25, 50, 100, 200, 400, 800]
    k_values = [70, 80, 90, 100]

    # generate data sizes
    data_sizes = [i for i in range(10000, 1000001, 500)]
    # reverse data sizes to start with larger sizes first
    data_sizes.reverse()

    data_size_to_avg_maxgeom_sample_size_per_k = {k: {} for k in k_values}
    data_size_to_stddev_maxgeom_sample_size_per_k = {k: {} for k in k_values}
    
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = []
        for data_size in data_sizes:
            for k in k_values:
                futures.append(executor.submit(run_experiment_for_one_k_and_size, k, data_size, num_runs_each_setting, w))

        for future in tqdm(futures):
            k, data_size, avg_maxgeom_sample_size, stddev_maxgeom_sample_size = future.result()
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
