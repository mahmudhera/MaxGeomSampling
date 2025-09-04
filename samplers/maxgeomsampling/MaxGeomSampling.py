
def test_import():
    print ("Importing Successful")
    
    
class MaxGeomSample:
    def __init__(self, k: int):
        self.hashes = []
        self.k = k

    def add_hash(self, hash_value):
        self.hashes.append(hash_value)
