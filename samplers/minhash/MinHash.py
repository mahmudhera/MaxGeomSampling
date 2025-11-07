from hashes.hash_utils import get_mmh3_hash
from typing import Iterable
import random

class MinHashSketch:
    
    def __init__(self, k: int, seed: int = 42):
        self.k = k
        self.seed = seed
        self.all_items = set()
        
    def add_item(self, item: str):
        self.all_items.add(item)
            
    def add_many_items(self, items: Iterable[str]):
        for item in items:
            self.add_item(item)


    def create_minhash_sample(self):
        # create k seeds randomly based on self.seed
        seeds = [ random.Random(self.seed + i).randint(0, 2**32 - 1) for i in range(self.k) ]
        minhashes = []
        for seed in seeds:
            min_hash_this_seed = None 
            for item in self.all_items:
                hash_value = get_mmh3_hash(item, seed=seed)
                if min_hash_this_seed is None or hash_value < min_hash_this_seed:
                    min_hash_this_seed = hash_value
            if min_hash_this_seed is not None:
                minhashes.append(min_hash_this_seed)
        self.minhashes = minhashes

    
    def __len__(self):
        return self.k
    

    def jaccard_index(self, other: 'MinHashSketch') -> float:
        if self.k != other.k:
            raise ValueError("Both MinHashSketch instances must have the same k value for Jaccard index computation.")
        if not hasattr(self, "minhashes"):
            self.create_minhash_sample()
        if not hasattr(other, "minhashes"):
            other.create_minhash_sample()
        num_matches = 0
        for minhash1, minhash2 in zip(self.minhashes, other.minhashes):
            if minhash1 == minhash2:
                num_matches += 1
        return num_matches / self.k


    def sample_size(self) -> int:
        return self.k