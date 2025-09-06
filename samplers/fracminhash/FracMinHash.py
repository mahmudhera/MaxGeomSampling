from hashes.hash_utils import get_mmh3_hash
from typing import Iterable

class FracMinHashSketch:
    
    def __init__(self, scale: float, seed: int = 42):
        self.scale = scale
        self.max_hash_value = 2**64 - 1
        self.threshold = int(scale * self.max_hash_value)
        self.hashes = set()
        self.seed = seed
        
    def add_item(self, item: str):
        hash_value = get_mmh3_hash(item, seed=self.seed)
        if hash_value <= self.threshold:
            self.hashes.add(hash_value)
            
    def add_many_items(self, items: Iterable[str]):
        for item in items:
            self.add_item(item)
            
    def get_hashes(self):
        return self.hashes
    
    def get_scale(self):
        return self.scale

    def get_max_hash_value(self):
        return self.max_hash_value

    def get_threshold(self):
        return self.threshold
    
    def __len__(self):
        return len(self.hashes)
