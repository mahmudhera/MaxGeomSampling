

class FracMinHashSketch:
    
    def __init__(self, scale: float, max_hash_value: int):
        self.scale = scale
        self.max_hash_value = max_hash_value
        self.threshold = int(scale * max_hash_value)
        self.hashes = set()
        
    def add_hash(self, hash_value: int):
        if hash_value <= self.threshold:
            self.hashes.add(hash_value)
            
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
