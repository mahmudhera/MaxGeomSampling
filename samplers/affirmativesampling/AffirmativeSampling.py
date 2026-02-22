from __future__ import annotations

from dataclasses import dataclass
from bisect import bisect_left, insort
from typing import Any, Iterable, List, Optional, Sequence, Set

from hashes.hash_utils import get_mmh3_hash


class AffirmativeSketch:
    """
    Stores *hash values* in ascending order (smallest first), and maintains two thresholds:

    ------ acceptance region1 ---- | ---- acceptance region2 ---- | ---- rejection region ----
    -------------------------- threshold2 ------------------ threshold1 ----------------------

      threshold1 = current largest stored hash
      threshold2 = current k-th smallest stored hash

    Update rule:
      - If sketch has < k items: always insert; set threshold1 = threshold2 = current max.
      - Else (size >= k):
          * if value > threshold1: reject
          * elif value > threshold2: accept; then erase the current maximum; update threshold1 to new max
          * else (value <= threshold2): accept; update threshold2 to the k-th smallest

    Notes:
      - Duplicates are ignored (membership set).
      - Sketch size can exceed k due to the `value <= threshold2` acceptance region
    """

    def __init__(self, k: int, seed: int = 42) -> None:
        if k <= 0:
            raise ValueError("k must be positive")
        self.k: int = k
        self.seed: int = seed

        # Sorted list of stored hash values (ascending) + membership set
        self._data: List[int] = []
        self._seen: Set[int] = set()

        self.threshold1: Optional[int] = None
        self.threshold2: Optional[int] = None

    # ---------------- Public API ----------------

    def size(self) -> int:
        """Return the number of stored unique hashes (size of sketch)."""
        return len(self._data)

    def get(self) -> List[int]:
        """Return the sketch values as a sorted (ascending) list."""
        return list(self._data)

    def add_item(self, z: Any) -> None:
        """Hash `z` to 64-bit and feed it to the affirmative sampling rule."""
        h = get_mmh3_hash(z, seed=self.seed)
        self.add_hash(h)

    def add_many_items(self, stream: Iterable[Any]) -> None:
        for z in stream:
            self.add_item(z)

    def add_hash(self, value: int) -> None:
        """Feed a precomputed hash value (int) to the affirmative sampling rule."""
        # if value in sketch, do nothing
        if value in self._seen:
            return

        # For the first k elements: always add; threshold1_ = threshold2_ = max
        if len(self._data) < self.k:
            self._insert(value)
            mx = self._data[-1]
            self.threshold1 = mx
            self.threshold2 = mx
            return

        # From here: len >= k, thresholds should be defined
        if self.threshold1 is None or self.threshold2 is None:
            # Defensive: recompute if somehow missing
            self._recompute_thresholds()


        if value > self.threshold1:  # reject
            return
        elif value > self.threshold2:
            # accept, then erase current maximum (rbegin)
            self._insert(value)
            self._erase_max()
            self.threshold1 = self._data[-1] if self._data else None
        else:
            # accept, then update threshold2 = k-th smallest
            self._insert(value)
            if len(self._data) >= self.k:
                self.threshold2 = self._data[self.k - 1]
            else:
                self.threshold2 = self._data[-1] if self._data else None


    def set(self, vec: Sequence[int]) -> None:
        """clears and re-adds values using `add()` logic."""
        self.clear()
        for v in vec:
            self.add_hash(int(v))

    def clear(self) -> None:
        self._data.clear()
        self._seen.clear()
        self.threshold1 = None
        self.threshold2 = None

    def jaccard(self, other: "AffirmativeSketch") -> float:
        """
        Compute Jaccard similarity between two sketches:
        1) Find the *largest* common hash (scanning from the end of sorted vectors).
        2) Restrict both sketches to values <= that hash.
        3) Return |intersection| / |union| over the restricted values.

        Returns 0 if there is no common hash.
        """
        a = self.get()
        b = other.get()

        if not a or not b:
            return 0.0

        i, j = len(a) - 1, len(b) - 1
        found = False
        largest_common = None

        # Two-pointer from the end 
        while i > 0 and j > 0:
            if a[i] == b[j]:
                found = True
                largest_common = a[i]
                break
            elif a[i] > b[j]:
                i -= 1
            else:
                j -= 1

        if not found or largest_common is None:
            return 0.0

        # Union of values <= largest_common
        union_set: Set[int] = set()
        for v in a:
            if v > largest_common:
                break
            union_set.add(v)
        for v in b:
            if v > largest_common:
                break
            union_set.add(v)

        # Intersection of values <= largest_common
        b_leq = set()
        for v in b:
            if v > largest_common:
                break
            b_leq.add(v)

        inter_set: Set[int] = set()
        for v in a:
            if v > largest_common:
                break
            if v in b_leq:
                inter_set.add(v)

        if not union_set:
            return 0.0
        return len(inter_set) / len(union_set)

    # ---------------- Internals ----------------

    def _insert(self, value: int) -> None:
        """Insert into sorted list + membership set."""
        insort(self._data, value)
        self._seen.add(value)

    def _erase_max(self) -> None:
        """Erase the current maximum value (equivalent to `data_.erase(data_.rbegin()->first)`)."""
        if not self._data:
            return
        vmax = self._data.pop()  # largest due to ascending sort
        self._seen.discard(vmax)

    def _recompute_thresholds(self) -> None:
        """Recompute thresholds from current data (defensive helper)."""
        if not self._data:
            self.threshold1 = None
            self.threshold2 = None
            return
        self.threshold1 = self._data[-1]
        if len(self._data) >= self.k:
            self.threshold2 = self._data[self.k - 1]
        else:
            self.threshold2 = self._data[-1]

    # ---------------- Convenience ----------------

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0

    def sample_size(self) -> int:
        """Total number of stored unique hashes (size of sketch)."""
        return len(self._data)

    def __repr__(self) -> str:
        return (
            f"AffirmativeSketch(k={self.k}, size={len(self._data)}, "
            f"threshold1={self.threshold1}, threshold2={self.threshold2})"
        )
