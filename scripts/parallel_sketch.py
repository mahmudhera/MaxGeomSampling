#!/usr/bin/env python3
"""
Parallel sketching runner.

- Reads a filelist (one input file path per line).
- Runs `sketch` in parallel across a process pool.
- Algorithm is user-specified.
  * If algo == maxgeom, requires --k
  * If algo == alphamaxgeom, requires --alpha
- Uses fixed options per the spec:
    --kmer 31 --w 64 --seed 42 --canonical
- Output filename defaults to "<input_basename>.<algo>.sketch" in the same dir,
  or use --outdir to place outputs elsewhere.

Examples
--------
# MaxGeom with k=200 using 8 workers
python parallel_sketch.py filelist.txt --algo maxgeom --k 200 --threads 8

# AlphaMaxGeom with alpha=0.75 using all cores, writing to ./out
python parallel_sketch.py filelist.txt --algo alphamaxgeom --alpha 0.75 --outdir out
"""

from __future__ import annotations
import argparse
import concurrent.futures as cf
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run 'sketch' in parallel for a list of input files."
    )
    p.add_argument("filelist", type=Path,
                   help="Path to a text file containing input filenames (one per line).")
    p.add_argument("--threads", type=int, default=os.cpu_count() or 1,
                   help="Number of worker processes (default: number of CPU cores).")
    p.add_argument("--algo", required=True, choices=["maxgeom", "alphamaxgeom", "fracminhash", "minhash", "bottomk"],
                   help="Sketching algorithm to use.")
    # Algo-specific params
    p.add_argument("--k", type=int,
                   help="Required if --algo maxgeom or bottomk. Example: --k 200")
    p.add_argument("--alpha", type=float,
                   help="Required if --algo alphamaxgeom. Example: --alpha 0.75")
    p.add_argument("--scale", type=float,
                   help="Required if --algo fracminhash. Example: --scale 0.001")
    p.add_argument("--num_permutations", type=int,
                   help="Required if --algo minhash. Example: --num_permutations 1000")
    # Optional output handling
    p.add_argument("--outdir", type=Path, default=None,
                   help="Directory to place output files. Defaults to the same dir as each input.")
    p.add_argument("--suffix", type=str, default=None,
                   help="Custom output suffix (default: '.<algo>.sketch'). Do not include leading dot for extension only.")
    # Fixed params per spec, exposed for advanced users if needed
    p.add_argument("--kmer", type=int, default=31,
                   help="k-mer size (default: 31).")
    p.add_argument("--w", type=int, default=64,
                   help="Window size (default: 64, not used for FracMinHash).")
    p.add_argument("--seed", type=int, default=42,
                   help="Random seed (default: 42).")
    p.add_argument("--no-canonical", action="store_true",
                   help="Disable --canonical flag (enabled by default).")
    p.add_argument("--dry-run", action="store_true",
                   help="Print commands without running them.")
    return p.parse_args()

def read_filelist(path: Path) -> List[Path]:
    if not path.exists():
        sys.exit(f"ERROR: filelist '{path}' does not exist.")
    files: List[Path] = []
    with path.open() as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            files.append(Path(s))
    if not files:
        sys.exit("ERROR: filelist is empty after filtering comments/blank lines.")
    return files

def output_for(input_path: Path, algo: str, outdir: Optional[Path], suffix: Optional[str]) -> Path:
    base_dir = outdir if outdir is not None else input_path.parent
    base_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem  # keeps single extension; for multi-ext, user can set --suffix
    if suffix:
        # If user passed a raw suffix like ".mgs", keep as is; if "mgs", add leading dot.
        if not suffix.startswith(".") and "." not in suffix:
            suffix = f".{suffix}"
        outname = f"{stem}{suffix}"
    else:
        outname = f"{stem}.{algo}.sketch"
    return base_dir / outname

def build_cmd(
    input_file: Path,
    output_file: Path,
    algo: str,
    k: Optional[int],
    alpha: Optional[float],
    kmer: int,
    w: int,
    seed: int,
    canonical: bool,
    scale: float,
    num_permutations: int
) -> List[str]:
    """
    Construct the 'sketch' command.

    Spec baseline:
    sketch --input {input_filename} --kmer 31 --algo maxgeom --k 200 --w 64 --seed 42 --canonical --output {output_filename}
    """
    cmd = [
        "sketch",
        "--input", str(input_file),
        "--kmer", str(kmer),
        "--algo", algo,
        "--w", str(w),
        "--seed", str(seed),
        "--output", str(output_file),
    ]
    if canonical:
        cmd.append("--canonical")
    if algo == "maxgeom" or algo == "bottomk":
        if k is None:
            raise ValueError(f"Algorithm '{algo}' requires --k.")
        cmd += ["--k", str(k)]
    elif algo == "alphamaxgeom":
        if alpha is None:
            raise ValueError("Algorithm 'alphamaxgeom' requires --alpha.")
        cmd += ["--alpha", str(alpha)]
    elif algo == "fracminhash":
        if scale is None:
            raise ValueError("Algorithm 'fracminhash' requires --scale.")
        cmd += ["--scale", str(scale)]
    elif algo == "minhash":
        if num_permutations is None:
            raise ValueError("Algorithm 'minhash' requires --num_permutations.")
        cmd += ["--num-perm", str(num_permutations)]

    return cmd

def run_one(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a single command, returning (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError as e:
        return 127, "", f"Executable not found: {e}"
    except Exception as e:
        return 1, "", f"Unexpected error: {e}"


def run_single_threaded(paths: List[Path], args: argparse.Namespace) -> None:
    num_failed = 0
    for f in paths:
        if not f.exists():
            print(f"WARNING: input not found, skipping: {f}", file=sys.stderr)
            continue
        out = output_for(f, args.algo, args.outdir, args.suffix)
        try:
            cmd = build_cmd(
                input_file=f,
                output_file=out,
                algo=args.algo,
                k=args.k,
                alpha=args.alpha,
                kmer=args.kmer,
                w=args.w,
                seed=args.seed,
                canonical=not args.no_canonical,
                scale=args.scale,
                num_permutations=args.num_permutations,
            )
        except ValueError as ve:
            sys.exit(f"ERROR: {ve}")

        if args.dry_run:
            print(f"# {f} -> {out}")
            print(" ".join(map(str, cmd)))
            continue

        rc, stdout, stderr = run_one(cmd)
        if rc == 0:
            print(f"[OK]   {f} -> {out}")
            if stdout.strip():
                print(stdout.strip())
        else:
            print(f"[FAIL] {f} -> {out} (rc={rc})", file=sys.stderr)
            num_failed += 1
            if stderr.strip():
                print(stderr.strip(), file=sys.stderr)
                
    if num_failed:
        sys.exit(f"Completed with {num_failed} failure(s).")
    else:
        print("All jobs completed successfully.")


def main() -> None:
    args = parse_args()

    # Validate conditional requirements
    if args.algo == "maxgeom" and args.k is None:
        sys.exit("ERROR: --algo maxgeom requires --k (e.g., --k 200).")
    if args.algo == "alphamaxgeom" and args.alpha is None:
        sys.exit("ERROR: --algo alphamaxgeom requires --alpha (e.g., --alpha 0.75).")

    inputs = read_filelist(args.filelist)


    # if only one thread is requested, run single-threaded
    if args.threads == 1:
        run_single_threaded(inputs, args)
        return

    # Pre-build jobs (command lines)
    jobs = []
    for f in inputs:
        if not f.exists():
            print(f"WARNING: input not found, skipping: {f}", file=sys.stderr)
            continue
        out = output_for(f, args.algo, args.outdir, args.suffix)
        try:
            cmd = build_cmd(
                input_file=f,
                output_file=out,
                algo=args.algo,
                k=args.k,
                alpha=args.alpha,
                kmer=args.kmer,
                w=args.w,
                seed=args.seed,
                canonical=not args.no_canonical,
                scale=args.scale,
                num_permutations=args.num_permutations,
            )
        except ValueError as ve:
            sys.exit(f"ERROR: {ve}")
        jobs.append((f, out, cmd))

    if not jobs:
        sys.exit("ERROR: no valid inputs to process after checks.")

    # Optionally print planned commands
    if args.dry_run:
        for f, out, cmd in jobs:
            print(f"# {f} -> {out}")
            print(" ".join(map(str, cmd)))
        return

    # Run in parallel
    failures = 0
    print(f"Running {len(jobs)} sketches with {args.threads} workers (algo={args.algo})...")
    with cf.ProcessPoolExecutor(max_workers=args.threads) as ex:
        future_to_job = {ex.submit(run_one, cmd): (f, out, cmd) for (f, out, cmd) in jobs}
        for fut in cf.as_completed(future_to_job):
            f, out, cmd = future_to_job[fut]
            try:
                rc, stdout, stderr = fut.result()
            except Exception as e:
                failures += 1
                print(f"[FAIL] {f} -> {out} : crashed with exception: {e}", file=sys.stderr)
                continue

            if rc == 0:
                print(f"[OK]   {f} -> {out}")
                if stdout.strip():
                    print(stdout.strip())
            else:
                failures += 1
                print(f"[FAIL] {f} -> {out} (rc={rc})", file=sys.stderr)
                if stderr.strip():
                    print(stderr.strip(), file=sys.stderr)

    if failures:
        sys.exit(f"Completed with {failures} failure(s).")
    else:
        print("All jobs completed successfully.")

if __name__ == "__main__":
    main()
