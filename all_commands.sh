conda create -n maxgeom -y
conda activate maxgeom
pip install --file requirements.txt

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

# vary jaccard from 0 to 1, see how accuracy changes
python scripts/expt_vary_jaccard.py

# plot accuracy results by varying jaccard
python scripts/plot_accuracy_by_varying_jaccard.py

# fixed similarity, vary set sizes experiments using MGS
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.1 --metric jaccard --k 100 --seeds 500 --growth x2 --out results/expt_fixed_jaccard_vary_set_size_jaccard_k100_t0.1.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.2 --metric jaccard --k 100 --seeds 500 --growth x2 --out results/expt_fixed_jaccard_vary_set_size_jaccard_k100_t0.2.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.3 --metric jaccard --k 100 --seeds 500 --growth x2 --out results/expt_fixed_jaccard_vary_set_size_jaccard_k100_t0.3.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.4 --metric jaccard --k 100 --seeds 500 --growth x2 --out results/expt_fixed_jaccard_vary_set_size_jaccard_k100_t0.4.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.5 --metric jaccard --k 100 --seeds 500 --growth x2 --out results/expt_fixed_jaccard_vary_set_size_jaccard_k100_t0.5.tsv

python scripts/expt_fixed_similarity_vary_set_size.py --t 0.1 --metric cosine --k 100 --seeds 1000 --growth x2 --out results/expt_fixed_cosine_vary_set_size_cosine_k100_t0.1.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.2 --metric cosine --k 100 --seeds 1000 --growth x2 --out results/expt_fixed_cosine_vary_set_size_cosine_k100_t0.2.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.3 --metric cosine --k 100 --seeds 1000 --growth x2 --out results/expt_fixed_cosine_vary_set_size_cosine_k100_t0.3.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.4 --metric cosine --k 100 --seeds 1000 --growth x2 --out results/expt_fixed_cosine_vary_set_size_cosine_k100_t0.4.tsv
python scripts/expt_fixed_similarity_vary_set_size.py --t 0.5 --metric cosine --k 100 --seeds 1000 --growth x2 --out results/expt_fixed_cosine_vary_set_size_cosine_k100_t0.5.tsv

# fixed similarity, vary set sizes experiments using FMH
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.1 --metric jaccard --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_jaccard_vary_set_size_jaccard_FMH_s0.001_t0.1.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.2 --metric jaccard --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_jaccard_vary_set_size_jaccard_FMH_s0.001_t0.2.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.3 --metric jaccard --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_jaccard_vary_set_size_jaccard_FMH_s0.001_t0.3.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.4 --metric jaccard --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_jaccard_vary_set_size_jaccard_FMH_s0.001_t0.4.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.5 --metric jaccard --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_jaccard_vary_set_size_jaccard_FMH_s0.001_t0.5.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.1 --metric cosine --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_cosine_vary_set_size_cosine_FMH_s0.001_t0.1.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.2 --metric cosine --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_cosine_vary_set_size_cosine_FMH_s0.001_t0.2.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.3 --metric cosine --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_cosine_vary_set_size_cosine_FMH_s0.001_t0.3.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.4 --metric cosine --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_cosine_vary_set_size_cosine_FMH_s0.001_t0.4.tsv
python scripts/expt_fixed_similarity_vary_set_size_FMH.py --t 0.5 --metric cosine --s 0.001 --seeds 200 --growth x2 --seed 42 --out results/expt_fixed_cosine_vary_set_size_cosine_FMH_s0.001_t0.5.tsv