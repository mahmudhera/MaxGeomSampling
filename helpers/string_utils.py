import random
import string

random.seed(42)

def generate_random_strings(num_strings: int, length: int) -> list:
    alphabet = string.ascii_letters + string.digits
    return [''.join(random.choices(alphabet, k=length)) for _ in range(num_strings)]