from __future__ import annotations
from dataclasses import dataclass
from hashes.hash_utils import get_mmh3_hash
import heapq
from typing import Any, Dict, Iterable, List, Tuple

@dataclass
class _Entry:
    hprime: int
    freq: int

class MaxGeomSample:
    """
    MaxGeomSampling(Z : hash stream; S : sample)

    Parameters
    ----------
    k : int
        Max items to keep per bucket i (top-k by h').
    w : int, default 32
        Number of top bits used to locate the left-most '1'.
        Must satisfy 1 <= w <= 64.
    seed : int, default 0
        Salt for the internal 64-bit hash (deterministic across runs).

    Notes
    -----
    - For each incoming element z:
        h  := 64-bit hash(z)
        i  := zpl(h) + 1            # 1 <= i <= w  (position of left-most 1 in top w bits)
        h' := tail(h, i)            # suffix bits after that 1
        Update per-bucket structure S[i] accordingly (top-k by h').
    - If z already exists in S[i], only its frequency is incremented.
    - If S[i] is full and z not present, z is inserted only if its h' exceeds
      the current minimum h' in that bucket; then the smallest is evicted.
    """

    def __init__(self, k: int, w: int = 64, seed: int = 42) -> None:
        if not (1 <= w <= 64):
            raise ValueError("w must be in [1, 64]")
        if k <= 0:
            raise ValueError("k must be positive")

        self.k = k
        self.w = w
        self.seed = seed

        # S: bucket_index -> { item -> _Entry(hprime, freq) }
        self._buckets: Dict[int, Dict[Any, _Entry]] = {}
        
        # Min-heaps per bucket for quick eviction: bucket_index -> [(hprime, item), ...]
        self._heaps: Dict[int, List[Tuple[int, Any]]] = {}

    # ---------- Public API ----------

    def add_item(self, z: Any) -> None:
        """Process a single element."""
        h = get_mmh3_hash(z, seed=self.seed)
        i = self._zpl_plus_one(h)           # 1..w
        hprime = self._tail_after_leftmost_one(h, i)

        if i not in self._buckets:
            self._buckets[i] = {}
            self._heaps[i] = []

        bucket = self._buckets[i]
        heap = self._heaps[i]

        if z in bucket:
            bucket[z].freq += 1
            return

        # Not present: consider adding if capacity or h' among top-k
        if len(bucket) < self.k:
            bucket[z] = _Entry(hprime=hprime, freq=1)
            heapq.heappush(heap, (hprime, z))
        else:
            # Check smallest h' in current top-k
            min_hprime, _ = heap[0]
            if hprime > min_hprime:
                # Insert candidate
                bucket[z] = _Entry(hprime=hprime, freq=1)
                heapq.heappush(heap, (hprime, z))
                # Evict smallest to keep |S[i]| == k
                self._evict_smallest(i)
            # else: drop z (not among k largest)
        # done

    def add_many_items(self, stream: Iterable[Any]) -> None:
        """Process an iterable of elements."""
        for z in stream:
            self.add_item(z)

    def sample(self) -> Dict[int, List[Tuple[Any, int, int]]]:
        """
        Get the current sample.

        Returns
        -------
        dict: i -> list of (item, hprime, freq), sorted by h' descending.
        """
        out: Dict[int, List[Tuple[Any, int, int]]] = {}
        for i, bucket in self._buckets.items():
            rows = [(z, ent.hprime, ent.freq) for z, ent in bucket.items()]
            rows.sort(key=lambda r: r[1], reverse=True)
            out[i] = rows
        return out

    def bucket(self, i: int) -> List[Tuple[Any, int, int]]:
        """Return the contents of bucket i as (item, hprime, freq), sorted by h' descending."""
        return self.sample().get(i, [])

    # ---------- Internals ----------

    def _evict_smallest(self, i: int) -> None:
        """Evict elements with smallest h' until bucket size is k."""
        bucket = self._buckets[i]
        heap = self._heaps[i]

        # Pop until the top of heap is consistent with bucket and size <= k
        while len(bucket) > self.k:
            hmin, zmin = heapq.heappop(heap)
            # If this pair is stale (e.g., z was evicted earlier), skip it.
            ent = bucket.get(zmin)
            if ent is not None and ent.hprime == hmin:
                del bucket[zmin]
                break

    def _zpl_plus_one(self, h: int) -> int:
        """
        zpl(h) + 1, i.e., position (1..w) of the left-most 1 in the top-w bits.
        If all top-w bits are zero, returns w.
        """
        w = self.w
        topw = (h >> (64 - w)) & ((1 << w) - 1)  # exactly w bits
        if topw == 0:
            return w
        # number of leading zeros in these w bits:
        leading_zeros = w - topw.bit_length()
        return leading_zeros + 1  # i in 1..w

    def _tail_after_leftmost_one(self, h: int, i: int) -> int:
        """
        Return h' := tail(h, i), i.e., all bits AFTER the left-most 1 within the top-w bits.
        This concatenates:
          - the remaining (w - i) bits of the top-w after that '1'
          - all the lower (64 - w) bits
        """
        w = self.w
        lower_bits = 64 - w
        topw = (h >> (64 - w)) & ((1 << w) - 1)
        # mask for remaining bits after position i (1-based):
        rem_len = max(0, w - i)
        rem_top = topw & ((1 << rem_len) - 1)
        low = h & ((1 << lower_bits) - 1)
        return (rem_top << lower_bits) | low

    # ---------- Convenience ----------

    def size(self) -> int:
        """Return the total number of unique items in the sample across all buckets."""
        return sum(len(bucket) for bucket in self._buckets.values())

    def __len__(self) -> int:
        """Total number of stored items across all buckets."""
        return sum(len(bucket) for bucket in self._buckets.values())

    def __repr__(self) -> str:
        repr_str = f"MaxGeomSample(k={self.k}, w={self.w}, buckets={len(self._buckets)})"
        return repr_str
    
    # check if empty
    def is_empty(self) -> bool:
        return len(self) == 0
    
    # check if two samples are equal
    def __eq__(self, other: MaxGeomSample) -> bool:
        if not isinstance(other, MaxGeomSample):
            return False
        return self.k == other.k and self.w == other.w and self.sample() == other.sample()
    
    def jaccard(self, other: MaxGeomSample) -> float:
        return self.jaccard_index(other)

    def jaccard_index(self, other: MaxGeomSample) -> float:
        """Compute Jaccard index between two samples."""
        if not isinstance(other, MaxGeomSample):
            raise ValueError("Can only compute Jaccard index with another MaxGeomSample")
        
        union_size = 0
        intersection_size = 0

        # get all i values that are in both buckets
        self_valid_i = set(self._buckets.keys())
        other_valid_i = set(other._buckets.keys())
        common_i = self_valid_i.intersection(other_valid_i)

        # go over all buckets
        for i in common_i:
            # get the buckets
            self_hprimes = {ent.hprime for ent in self._buckets[i].values()}
            other_hprimes = {ent.hprime for ent in other._buckets[i].values()}
            union_hprimes = self_hprimes.union(other_hprimes)
            union_hprimes = heapq.nlargest(self.k, union_hprimes)
            intersection_hprimes = self_hprimes.intersection(other_hprimes)
            intersection_hprimes = intersection_hprimes.intersection(set(union_hprimes))

            # compute union and intersection sizes
            union_size += len(union_hprimes)
            intersection_size += len(intersection_hprimes)

        if union_size == 0:
            return 1.0  # both are empty

        return intersection_size / union_size


    def union(self, other: MaxGeomSample) -> MaxGeomSample:
        """Merge another MaxGeomSample into this one and return a new MaxGeomSample."""
        if not isinstance(other, MaxGeomSample):
            raise ValueError("Can only merge with another MaxGeomSample")
        if self.k != other.k or self.w != other.w:
            raise ValueError("Can only merge samples with the same k and w")

        merged = MaxGeomSample(k=self.k, w=self.w, seed=self.seed)

        # Add items from self
        for i, bucket in self._buckets.items():
            for z, ent in bucket.items():
                for _ in range(ent.freq):
                    merged.add_item(z)

        # Add items from other
        for i, bucket in other._buckets.items():
            for z, ent in bucket.items():
                for _ in range(ent.freq):
                    merged.add_item(z)

        return merged

    
    def cosine_similarity(self, other: MaxGeomSample) -> float:
        """Compute Cosine similarity between two samples."""
        if not isinstance(other, MaxGeomSample):
            raise ValueError("Can only compute Cosine similarity with another MaxGeomSample")
        
        dot_product = 0
        self_norm_sq = 0
        other_norm_sq = 0

        # get all i values that are in both buckets
        self_valid_i = set(self._buckets.keys())
        other_valid_i = set(other._buckets.keys())
        common_i = self_valid_i.intersection(other_valid_i)

        # go over all buckets
        for i in common_i:
            # get the buckets
            self_hprimes = {ent.hprime: ent.freq for ent in self._buckets[i].values()}
            other_hprimes = {ent.hprime: ent.freq for ent in other._buckets[i].values()}
            union_hprimes = set(self_hprimes.keys()).union(set(other_hprimes.keys()))
            union_hprimes = heapq.nlargest(self.k, union_hprimes)

            # compute dot product and norms
            for hprime in union_hprimes:
                freq1 = self_hprimes.get(hprime, 0)
                freq2 = other_hprimes.get(hprime, 0)
                dot_product += freq1 * freq2
                self_norm_sq += freq1 * freq1
                other_norm_sq += freq2 * freq2

        if self_norm_sq == 0 or other_norm_sq == 0:
            return 0.0  # one is empty

        return dot_product / ((self_norm_sq ** 0.5) * (other_norm_sq ** 0.5))
    

    def sample_size(self) -> int:
        """Return the total number of unique items in the sample across all buckets."""
        return sum(len(bucket) for bucket in self._buckets.values())