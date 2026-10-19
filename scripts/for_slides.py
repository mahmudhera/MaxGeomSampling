import random
from samplers import AffirmativeSketch
from samplers import FracMinHashSketch

from tqdm import tqdm
import string

from matplotlib import pyplot as plt


alphabet = string.ascii_letters + string.digits


def generate_random_strings(num_strings: int, length: int) -> list:
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]


if __name__ == "__main__":
    num_runs = 2000
    w = 64
    k = 200
    original_set_size_low = 10
    original_set_size_high = 1000_000
    seed=42
    scale = 0.01
    mh_sample_size = 1000

    as_sample_sizes = []
    fmh_sample_sizes = []
    mh_sample_sizes = []
    original_set_sizes = []

    for _ in tqdm(range(num_runs)):
        original_set_size = random.randint(original_set_size_low, original_set_size_high)
        data = generate_random_strings(original_set_size, 10)
        affirmative_sketch = AffirmativeSketch(k=k, seed=seed)
        affirmative_sketch.add_many_items(data)
        
        
        fmh_sketch = FracMinHashSketch(scale)
        fmh_sketch.add_many_items(data)
        
        original_set_sizes.append(original_set_size)
        as_sample_sizes.append(len(affirmative_sketch))
        fmh_sample_sizes.append(len(fmh_sketch))
        mh_sample_sizes.append(mh_sample_size)

    size = 8

    plt.figure(figsize=(10, 6))
    plt.scatter(original_set_sizes, as_sample_sizes, label=f'Affirmative Sampling (k = {k})', alpha=0.9, s=size, color='green')
    plt.scatter(original_set_sizes, fmh_sample_sizes, label=f'FracMinHash (scale = {scale})', alpha=0.9, s=size)
    plt.scatter(original_set_sizes, mh_sample_sizes, label=f'MinHash (k = {mh_sample_size})', alpha=0.9, s=size)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Original Set Size (log scale)')
    plt.ylabel('Sample Size (log scale)')
    plt.title('Sample Size vs Original Set Size')
    plt.legend()
    plt.grid(True, which="both", ls="--", linewidth=0.5)
    plt.show()