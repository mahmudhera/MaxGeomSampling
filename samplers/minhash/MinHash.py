from hashes.hash_utils import get_mmh3_hash
from typing import Iterable, Optional
import random

try:
    import numpy as np
    _HAS_NUMPY = True
except Exception:
    _HAS_NUMPY = False


class MinHashSketch:
    """
    Fast MinHash:
      - Single mmh3 call per item (seed=0) to get base hash.
      - Derive k hashes via affine transforms mod a large prime p.
      - Vectorized across k with NumPy when available.
      - Incremental updates on add_item/add_many_items.
    """

    # Large 61-bit prime for modular arithmetic
    _P = (1 << 61) - 1  # 2^61 - 1

    def __init__(self, k: int, seed: int = 42, use_numpy: Optional[bool] = None):
        self.k = int(k)
        self.seed = int(seed)
        self.all_items = set()
        self._initialized = False
        self._minhashes = None  # internal storage (np.ndarray or list)
        # Choose whether to use NumPy
        self._use_numpy = _HAS_NUMPY if use_numpy is None else (use_numpy and _HAS_NUMPY)
        # Pre-generate affine parameters a, b for k hash functions
        rng = random.Random(self.seed)
        # Make sure a != 0 mod p
        self._a = [rng.randrange(1, self._P) for _ in range(self.k)]
        self._b = [rng.randrange(0, self._P) for _ in range(self.k)]
        if self._use_numpy:
            self._a = np.array(self._a, dtype=np.uint64)
            self._b = np.array(self._b, dtype=np.uint64)
            self._p = np.uint64(self._P)
            self._max = np.uint64(self._P - 1)
        else:
            self._p = self._P
            self._max = self._P - 1

    # ---- Public API ----
    def add_item(self, item: str):
        # Add to set and incrementally update minhash state
        if item in self.all_items:
            return
        self.all_items.add(item)
        self._ensure_state()
        self._update_with_item(item)

    def add_many_items(self, items: Iterable[str]):
        # If many items, batch the updates for speed
        batch = []
        for it in items:
            if it not in self.all_items:
                self.all_items.add(it)
                batch.append(it)
        if not batch:
            return
        self._ensure_state()
        if self._use_numpy:
            self._update_batch_numpy(batch)
        else:
            for it in batch:
                self._update_with_item_pure(it)

    def create_minhash_sample(self):
        # Rebuild from scratch (rarely needed now that updates are incremental)
        self._reset_state()
        if not self.all_items:
            return
        if self._use_numpy:
            self._build_numpy()
        else:
            self._build_pure()

    def __len__(self):
        return self.k

    def jaccard_index(self, other: 'MinHashSketch') -> float:
        if self.k != other.k:
            raise ValueError("Both MinHashSketch instances must have the same k value for Jaccard index computation.")
        self._ensure_state()
        other._ensure_state()

        if self._use_numpy and isinstance(self._minhashes, np.ndarray) and isinstance(other._minhashes, np.ndarray):
            matches = int((self._minhashes == other._minhashes).sum())
        else:
            matches = sum(int(a == b) for a, b in zip(self._iter_hashes(), other._iter_hashes()))
        return matches / self.k

    def sample_size(self) -> int:
        return self.k

    # ---- Internals ----
    def _ensure_state(self):
        if not self._initialized:
            # Initialize minhashes to "infinity"
            if self._use_numpy:
                self._minhashes = np.full(self.k, self._max, dtype=np.uint64)
            else:
                self._minhashes = [self._max] * self.k
            self._initialized = True

    def _reset_state(self):
        self._initialized = False
        self._minhashes = None

    def _base_hash(self, item: str) -> int:
        # Single mmh3 call per item; seed fixed to 0
        # Ensure non-negative and fit into 64-bit domain
        h = int(get_mmh3_hash(item, seed=0))
        # mmh3 can be signed 32-bit depending on wrapper; normalize to uint64 range
        if h < 0:
            h += (1 << 32)
        return h

    # ----- NumPy path -----
    def _build_numpy(self):
        # Vectorized across k; loop over items
        self._ensure_state()
        for it in self.all_items:
            self._update_with_item_numpy(it)

    def _update_with_item_numpy(self, item: str):
        h = np.uint64(self._base_hash(item))
        # Compute k transformed hashes and take elementwise min
        # (a*h + b) % p
        vals = (self._a * h + self._b) % self._p
        np.minimum(self._minhashes, vals, out=self._minhashes)

    def _update_batch_numpy(self, batch_items):
        # Slightly faster than per-item loop for bigger batches
        # Build array of base hashes, shape (m,)
        hs = np.fromiter((self._base_hash(it) for it in batch_items), dtype=np.uint64)
        # For each h, update minhashes; keep memory bounded (still very fast)
        for h in hs:
            vals = (self._a * h + self._b) % self._p
            np.minimum(self._minhashes, vals, out=self._minhashes)

    # ----- Pure-Python path -----
    def _build_pure(self):
        self._ensure_state()
        for it in self.all_items:
            self._update_with_item_pure(it)

    def _update_with_item(self, item: str):
        if self._use_numpy:
            self._update_with_item_numpy(item)
        else:
            self._update_with_item_pure(item)

    def _update_with_item_pure(self, item: str):
        h = self._base_hash(item) % self._p
        a = self._a
        b = self._b
        p = self._p
        mh = self._minhashes
        # Manual loop across k
        for i in range(self.k):
            val = (int(a[i]) * h + int(b[i])) % p
            if val < mh[i]:
                mh[i] = val

    def _iter_hashes(self):
        # Helper to iterate regardless of backend
        if self._use_numpy and isinstance(self._minhashes, np.ndarray):
            return self._minhashes.tolist()
        return self._minhashes
