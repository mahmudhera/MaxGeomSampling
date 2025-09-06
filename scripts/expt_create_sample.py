from samplers import FracMinHashSketch, MaxGeomSample
from hashes.hash_utils import get_mmh3_hash
import random
import string

def generate_random_strings(num_strings: int, length: int) -> list:
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]

if __name__ == "__main__":
    # FMH sketch with scale 0.1
    scale = 0.1
    fmh_sketch = FracMinHashSketch(scale)

    # Sample data: random 1M strings over alphabet
    data = generate_random_strings(100000, 10)
    fmh_sketch.add_many_items(data)

    print(f"Scale: {fmh_sketch.get_scale()}")
    print(f"Number of hashes in sketch: {len(fmh_sketch)}")

    # MaxGeomSampling with k=100, w=64
    max_geom_sample = MaxGeomSample(k=100, w=64, seed=42)
    max_geom_sample.add_many_items(data)
    print(f"MaxGeomSampling buckets: {len(max_geom_sample._buckets)}")
    # print number of items in all buckets
    print(f"Total items in MaxGeomSampling: {len(max_geom_sample)}")
    
    # check equality
    another_sample = MaxGeomSample(k=100, w=64, seed=42)
    another_sample.add_many_items(data)
    print(f"Samples equal: {max_geom_sample == another_sample}")
    
    # create another sample after shuffling the data
    random.shuffle(data)
    shuffled_sample = MaxGeomSample(k=100, w=64, seed=42)
    shuffled_sample.add_many_items(data)
    print(f"Samples equal after shuffling: {max_geom_sample == shuffled_sample}")
    
    # randomly shuffle data 10 times and check equality
    all_equal = True
    for _ in range(10):
        random.shuffle(data)
        temp_sample = MaxGeomSample(k=100, w=64, seed=42)
        temp_sample.add_many_items(data)
        if max_geom_sample != temp_sample:
            all_equal = False
            break
    print(f"Samples equal after 10 random shuffles: {all_equal}")