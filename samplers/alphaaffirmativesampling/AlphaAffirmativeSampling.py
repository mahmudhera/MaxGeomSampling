from __future__ import annotations

import math
from bisect import insort
from typing import Any, Iterable, List, Optional, Sequence, Set

from hashes.hash_utils import get_mmh3_hash


class AlphaAffirmativeSketch:
    """
    Stores *hash values* in ascending order (smallest first), and maintains two thresholds:

    ------ acceptance region1 ---- | ---- acceptance region2 ---- | ---- rejection region ----
    -------------------------- threshold2 ------------------ threshold1 ----------------------

      threshold1 = current largest stored hash
      threshold2 = current ceil(alpha · S)-th smallest stored hash, where S = current sketch size

    Update rule:
      - If sketch is empty: insert; set threshold1 = threshold2 = inserted value.
      - Else:
          * if value > threshold1: reject
          * elif value > threshold2: accept; then erase the current maximum; update threshold1 to new max
          * else (value <= threshold2): accept; update threshold2 to the ⌈alpha · S⌉-th smallest

    Notes:
      - Duplicates are ignored (membership set).
      - Sketch size can exceed the initial size due to the `value <= threshold2` acceptance region
    """

    def __init__(self, alpha: float, seed: int = 42) -> None:
        if not (0.0 < alpha <= 1.0):
            raise ValueError("alpha must be in (0, 1]")
        self.alpha: float = float(alpha)
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
        """Hash `z` to 64-bit and feed it to the alpha-affirmative sampling rule."""
        h = get_mmh3_hash(z, seed=self.seed)
        self.add_hash(h)

    def add_many_items(self, stream: Iterable[Any]) -> None:
        for z in stream:
            self.add_item(z)

    def add_hash(self, value: int) -> None:
        """Feed a precomputed hash value (int) to the alpha-affirmative sampling rule."""
        if value in self._seen:
            return

        if not self._data:
            self._insert(value)
            self._recompute_thresholds()
            return

        if self.threshold1 is None or self.threshold2 is None:
            self._recompute_thresholds()

        if self.threshold1 is None or self.threshold2 is None:
            return

        if value > self.threshold1:  # reject
            return
        elif value > self.threshold2:
            # accept, then erase current maximum (rbegin)
            self._insert(value)
            self._erase_max()
            self.threshold1 = self._data[-1] if self._data else None
        else:
            # accept, then update threshold2 = ⌈alpha · S⌉-th smallest
            self._insert(value)
            self.threshold1 = self._data[-1] if self._data else None
            if self._data:
                r = self._alpha_rank(len(self._data))
                self.threshold2 = self._data[r - 1]
            else:
                self.threshold2 = None

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

    def jaccard(self, other: "AlphaAffirmativeSketch") -> float:
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

    def _alpha_rank(self, m: int) -> int:
        """Return r = ⌈alpha · m⌉ clamped to [1, m]."""
        if m <= 0:
            return 0
        r = int(math.ceil(self.alpha * m - 1e-12))
        if r < 1:
            return 1
        if r > m:
            return m
        return r

    def _insert(self, value: int) -> None:
        """Insert into sorted list + membership set."""
        insort(self._data, value)
        self._seen.add(value)

    def _erase_max(self) -> None:
        """Erase the current maximum value (equivalent to `data_.erase(data_.rbegin()->first)`)."""
        if not self._data:
            return
        vmax = self._data.pop()
        self._seen.discard(vmax)

    def _recompute_thresholds(self) -> None:
        """Recompute thresholds from current data (defensive helper)."""
        if not self._data:
            self.threshold1 = None
            self.threshold2 = None
            return
        self.threshold1 = self._data[-1]
        r = self._alpha_rank(len(self._data))
        self.threshold2 = self._data[r - 1]

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
            f"AlphaAffirmativeSketch(alpha={self.alpha}, size={len(self._data)}, "
            f"threshold1={self.threshold1}, threshold2={self.threshold2})"
        )