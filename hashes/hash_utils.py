import mmh3

def get_mmh3_hash(value: str, seed: int = 42) -> int:
    return mmh3.hash64(value, signed=False, seed=seed)[0]