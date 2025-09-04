from samplers import FracMinHashSketch
import mmh3
import random
import string

def get_mmh3_hash(value: str) -> int:
    return mmh3.hash64(value, signed=False)[0]

def generate_random_strings(num_strings: int, length: int) -> list:
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]

if __name__ == "__main__":
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