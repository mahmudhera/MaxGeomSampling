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
    max_hash_value = 2**64 - 1
    sketch = FracMinHashSketch(scale, max_hash_value)
    
    # Sample data: random 1M strings over alphabet
    data = generate_random_strings(100000, 10)
    
    for item in data:
        hash_value = get_mmh3_hash(item)
        sketch.add_hash(hash_value)
    
    print(f"Scale: {sketch.get_scale()}")
    print(f"Number of hashes in sketch: {len(sketch)}")
    
    # MaxGeomSampling with k=100, w=64
    max_geom_sample = MaxGeomSample(k=100, w=64, seed=42)
    max_geom_sample.update_many(data)
    print(f"MaxGeomSampling buckets: {len(max_geom_sample._buckets)}")