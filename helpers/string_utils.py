import random
import string


def generate_random_strings(num_strings: int, length: int, seed: int = 42) -> list:
    random.seed(seed)
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]