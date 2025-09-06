import random

from samplers import FracMinHashSketch, MaxGeomSample
from helpers.string_utils import generate_random_strings

if __name__ == "__main__":
    random.seed(42)
    num_runs_each_setting = 20
    scale = 0.01
    w = 64
    k = 100

    # generate data sizes
    data_sizes = [i for i in range(10000, 1000001, 10000)]

    # vary size of data from 10K to 100K in steps of 10K
    data_size_to_avg_fmh_sketch_size = {}
    data_size_to_avg_maxgeom_sample_size = {}
    data_size_to_stddev_fmh_sketch_size = {}
    data_size_to_stddev_maxgeom_sample_size = {}
    
    for data_size in data_sizes:
        print(f"\nData size: {data_size}")
        data = generate_random_strings(data_size, 10)
        
        # FMH sketch with scale 0.01
        fmh_sketch_sizes = []
        for seed in range(num_runs_each_setting):
            fmh_sketch = FracMinHashSketch(scale, seed=seed)
            fmh_sketch.add_many_items(data)
            fmh_sketch_sizes.append(len(fmh_sketch))
        avg_fmh_sketch_size = sum(fmh_sketch_sizes) / num_runs_each_setting
        stddev_fmh_sketch_size = (sum((x - avg_fmh_sketch_size) ** 2 for x in fmh_sketch_sizes) / num_runs_each_setting) ** 0.5
        data_size_to_avg_fmh_sketch_size[data_size] = avg_fmh_sketch_size
        data_size_to_stddev_fmh_sketch_size[data_size] = stddev_fmh_sketch_size
        
        # MaxGeomSampling with k=100, w=64
        maxgeom_sample_sizes = []
        for seed in range(num_runs_each_setting):
            max_geom_sample = MaxGeomSample(k=k, w=w, seed=seed)
            max_geom_sample.add_many_items(data)
            maxgeom_sample_sizes.append(len(max_geom_sample))
        avg_maxgeom_sample_size = sum(maxgeom_sample_sizes) / num_runs_each_setting
        stddev_maxgeom_sample_size = (sum((x - avg_maxgeom_sample_size) ** 2 for x in maxgeom_sample_sizes) / num_runs_each_setting) ** 0.5
        data_size_to_avg_maxgeom_sample_size[data_size] = avg_maxgeom_sample_size
        data_size_to_stddev_maxgeom_sample_size[data_size] = stddev_maxgeom_sample_size
        
    print("\nData Size\tAvg FMH Sketch Size\tStddev FMH Sketch Size\tAvg MaxGeom Sample Size\tStddev MaxGeom Sample Size")
    for data_size in data_sizes:
        print(f"{data_size}\t{data_size_to_avg_fmh_sketch_size[data_size]:.2f}\t{data_size_to_stddev_fmh_sketch_size[data_size]:.2f}\t{data_size_to_avg_maxgeom_sample_size[data_size]:.2f}\t{data_size_to_stddev_maxgeom_sample_size[data_size]:.2f}")
        