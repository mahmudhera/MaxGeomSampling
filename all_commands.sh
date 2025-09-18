conda create -n maxgeom -y
conda activate maxgeom
pip install -r requirements.txt

export PYTHONPATH=$(pwd):$PYTHONPATH

# basic implementation test
python scripts/expt_basic_implementation.py

# growth against data size (against FMH)
python scripts/expt_growth_of_samples_against_fmh.py > results/results_growth_of_samples

# growth against k
python scripts/expt_growth_of_mgs_varying_k.py > results/results_growth_of_mgs_varying_k

# plot basic MGS results
python scripts/plot_sample_sizes.py

# growth of alpha-MGS samples against data size
python scripts/expt_growth_of_amgs_varying_alpha.py > results/results_growth_of_amgs_varying_alpha

# plot alpha-MGS results
python scripts/plot_alpha_MGS_sample_sizes.py

# experiment for accuracy of jaccard estimation without refining
python scripts/expt_accuracy_no_refining.py

# plot accuracy results
python scripts/plot_accuracy_jaccard_no_refining.py

# experiment for accuracy of jaccard estimation with refining
python scripts/expt_accuracy_with_refining.py

# plot accuracy results with refining
python scripts/plot_accuracy_jaccard_with_refining.py