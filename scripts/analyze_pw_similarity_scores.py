#!/usr/bin/env python3
"""
Build a Neighbor-Joining tree from pairwise Jaccard similarities.

Input TSV columns: sketch1, sketch2, jaccard_score
Assumes values are similarities in [0,1]. Distance = 1 - similarity.

Outputs:
  - Newick tree file
  - PNG (or any matplotlib-supported) plot of the tree

Usage:
  python nj_from_jaccard.py \
      --in pairs.tsv \
      --out-newick tree.nwk \
      --out-plot tree.png
"""

import argparse
import csv
import sys
from collections import defaultdict
from typing import Dict, Tuple, List

import matplotlib
matplotlib.use("Agg")  # for non-interactive environments
import matplotlib.pyplot as plt

from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor


def parse_args():
    p = argparse.ArgumentParser(
        description="Neighbor-Joining tree from Jaccard similarities (TSV)."
    )
    p.add_argument("--in", dest="in_path", required=True,
                   help="Input TSV with columns: sketch1, sketch2, jaccard_score")
    p.add_argument("--out-newick", required=True,
                   help="Output Newick file path")
    p.add_argument("--out-plot", required=True,
                   help="Output tree plot file path (e.g., PNG)")
    p.add_argument("--treat-as", choices=["similarity", "distance"],
                   default="similarity",
                   help="Interpret third column as similarity (default) or distance")
    p.add_argument("--similarity-to-distance",
                   choices=["one-minus", "neg-log", "mutrate"],
                   default="one-minus",
                   help="How to convert similarity to distance if --treat-as similarity. "
                        "'one-minus' uses d=1-s, 'neg-log' uses d=-ln(s+eps). mutrate converts jaccard to mutation rate estimate")
    p.add_argument("--eps", type=float, default=1e-12,
                   help="Small epsilon to avoid log(0) if using --similarity-to-distance=neg-log")
    p.add_argument("--average-duplicates", action="store_true",
                   help="If both (A,B) and (B,A) appear or duplicates exist, average them "
                        "(default is to require consistency).")
    p.add_argument("--kmer-size", type=int, default=31,
                   help="K-mer size for mutation rate distance conversion (default: 31)")
    return p.parse_args()


def sim_to_dist(sim: float, mode: str, eps: float, kmer_size: int) -> float:
    if mode == "one-minus":
        return 1.0 - sim
    elif mode == "neg-log":
        import math
        return -math.log(sim + eps)
    elif mode == "mutrate":
        if sim >= 1.0:
            return 0.0
        elif sim <= 0.0:
            return 1.0
        else:
            # this only works if sim is Jaccard similarity from k-mer sets
            return 1.0 - ( (2.0 * sim) / (1.0 + sim) ) ** (1.0 / kmer_size)
    else:
        raise ValueError(f"Unknown conversion mode: {mode}")


def read_pairs(in_path: str,
               as_what: str,
               conv_mode: str,
               eps: float,
               average_duplicates: bool,
               kmer_size: int) -> Tuple[List[str], Dict[Tuple[str, str], float]]:
    """
    Returns:
      - sorted list of taxa
      - dict of pairwise distances keyed by (a,b) with a<b
    """
    taxa = set()
    pair_values = defaultdict(list)  # to handle duplicates if needed

    with open(in_path, "r", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required_cols = {"sketch1", "sketch2", "jaccard_score"}
        if set(reader.fieldnames or []) != required_cols and not required_cols.issubset(set(reader.fieldnames or [])):
            sys.exit(f"ERROR: Expected columns {required_cols}, got {reader.fieldnames}")

        for row in reader:
            a = str(row["sketch1"]).strip()
            b = str(row["sketch2"]).strip()
            try:
                val = float(row["jaccard_score"])
            except Exception:
                sys.exit(f"ERROR: Non-numeric score in row: {row}")

            if a == b:
                # Ignore/skip self-lines if present; diagonal will be set to 0 distance later
                continue

            taxa.update([a, b])

            if as_what == "similarity":
                d = sim_to_dist(val, conv_mode, eps, kmer_size)
            else:
                d = val

            # normalize key (unordered pair)
            key = (a, b) if a < b else (b, a)
            pair_values[key].append(d)

    # Resolve duplicates and create single distance per unordered pair
    distances: Dict[Tuple[str, str], float] = {}
    for key, vals in pair_values.items():
        if len(vals) == 1:
            distances[key] = vals[0]
        else:
            if average_duplicates:
                distances[key] = sum(vals) / len(vals)
            else:
                # require all duplicates to be (almost) identical
                mx, mn = max(vals), min(vals)
                if abs(mx - mn) > 1e-9:
                    sys.exit(
                        f"ERROR: Conflicting distances for pair {key}: {vals}. "
                        "Use --average-duplicates to average them."
                    )
                distances[key] = vals[0]

    taxa_list = sorted(taxa)

    taxa_list = [ x.split('/')[-1].split('.')[0] for x in taxa_list ]
    distances = { (a.split('/')[-1].split('.')[0], b.split('/')[-1].split('.')[0]): d for (a, b), d in distances.items() }

    return taxa_list, distances


def build_distance_matrix(taxa: List[str], distances: Dict[Tuple[str, str], float]) -> DistanceMatrix:
    """
    Biopython's DistanceMatrix expects a lower-triangular matrix (including 0 diag),
    provided as a list of rows with increasing length.
    """
    n = len(taxa)
    # Validate completeness
    missing = []
    for i in range(n):
        for j in range(i):
            a, b = taxa[i], taxa[j]
            key = (a, b) if a < b else (b, a)
            if key not in distances:
                missing.append((a, b))
    if missing:
        msg = "\n".join([f"  {a} - {b}" for a, b in missing])
        sys.exit(f"ERROR: Missing distances for the following pairs:\n{msg}")

    matrix: List[List[float]] = []
    for i in range(n):
        row = []
        for j in range(i + 1):  # include diagonal
            if i == j:
                row.append(0.0)
            else:
                a, b = taxa[i], taxa[j]
                key = (a, b) if a < b else (b, a)
                row.append(distances[key])
        matrix.append(row)

    return DistanceMatrix(names=taxa, matrix=matrix)


def main():
    args = parse_args()

    taxa, dist_pairs = read_pairs(
        in_path=args.in_path,
        as_what=args.treat_as,
        conv_mode=args.similarity_to_distance,
        eps=args.eps,
        average_duplicates=args.average_duplicates,
        kmer_size=args.kmer_size,
    )

    if len(taxa) < 3:
        sys.exit("ERROR: Need at least 3 taxa to build a NJ tree.")

    dm = build_distance_matrix(taxa, dist_pairs)

    constructor = DistanceTreeConstructor()
    tree = constructor.upgma(dm)  # UPGMA or NJ can be used; NJ is default but UPGMA is faster

    # before writing, flatten all distances to 1.0
    #for clade in tree.find_clades():
    #    if clade.branch_length is not None:
    #        clade.branch_length = 1.0

    readable_names = {
        'Bos_taurus'                : 'Cow',
        'Canis_lupus_familiaris'    : 'Dog',
        'Equus_caballus'            : 'Horse',
        'Felis_catus'               : 'Cat',
        'Homo_sapiens'              : 'Human',
        'Monodelphis_domestica'     : 'Opossum',
        'Mus_musculus'              : 'Mouse',
        'Pan_troglodytes'           : 'Chimpanzee                 ',
        'Rattus_norvegicus'         : 'Rat',
        'Sus_scrofa'                : 'Pig',
    }
    #change names in tree
    for clade in tree.find_clades():
        if clade.name in readable_names:
            clade.name = readable_names[clade.name]

    # remove inner node names
    for clade in tree.find_clades():
        if clade.name is not None and clade.is_terminal() is False:
            clade.name = None

    # Write Newick
    Phylo.write(tree, args.out_newick, "newick")

    # Also print Newick to stdout for convenience
    try:
        from io import StringIO
        buf = StringIO()
        Phylo.write(tree, buf, "newick")
        #print(buf.getvalue().strip())
    except Exception:
        pass

    for clade in tree.find_clades():
        clade.color = 'black'
        clade.width = 0.4

    # set font size to 10
    matplotlib.rcParams.update({'font.size': 8})
    # Plot and save
    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_subplot(1, 1, 1)
    # draw tree, make edges thin
    Phylo.draw(tree, do_show=False, axes=ax)
    # remove y ticks and labels
    ax.yaxis.set_ticks([])
    ax.yaxis.set_ticklabels([])
    # set x label to "Branch length (mutation rate)"
    ax.set_xlabel("Branch length (mutation rate)")
    if 'bottomk' in args.in_path:
        # set xlim to 0.12
        ax.set_xlim(right=0.14)
    else:
        ax.set_xlim(right=0.16)
    plt.tight_layout()
    plt.savefig(args.out_plot, bbox_inches="tight")

    print(f"Wrote Newick to: {args.out_newick}")
    print(f"Wrote plot to:   {args.out_plot}")


if __name__ == "__main__":
    main()
