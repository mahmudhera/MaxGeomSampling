# MaxGeomHash

This repository contains the code to recreate all results presented in the manuscript, submitted to RECOMB-2026 for review. Installation for Python environment is through conda and pip. The C++ implementation needs to be downloaded and built separately, and the path to the bin folder needs to be added in the PATH variable. To install the C++ implementation, use the instructions available here: https://github.com/mahmudhera/kmer-sketch.

## Installation
After downloading the repository, `cd` to the repository path and run the following.
```
conda create -n maxgeom -y
conda activate maxgeom
pip install --file requirements.txt
export PYTHONPATH=$(pwd):$PYTHONPATH
export PATH=path-to-kmer-sketch-bin:$PATH
```

## Running experiments
```
bash all_commands.sh
```