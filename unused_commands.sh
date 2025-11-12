# download 22k bacterial genomes dataset, can do this separately in a different location
conda create -n ncbi-cli -y
conda ativate ncbi-cli
conda install -c conda-forge ncbi-datasets-cli
datasets download genome taxon 2 --reference --assembly-source refseq --filename bacteria_refseq.zip
unzip bacteria_refseq.zip
find $(pwd) -type f -name '*.fna' > data/22k_bacteria_filelist
conda deactivate

# manual downloads
# from https://trace.ncbi.nlm.nih.gov/Traces/?view=run_browser&acc=SRR35934838&display=download


# generate sketches for 22k bacterial genomes using kmer-sketch
/usr/bin/time -v python scripts/parallel_sketch.py data/22k_bacteria_filelist --threads 8 --algo maxgeom --k 200 --outdir sketches --kmer 31
# time it took: 2 hours 53 seconds

# installing mash
conda create -n mash -y
conda activate mash
conda install -c bioconda mash -y


# installing sourmash 
conda create -n sourmash -y
conda activate sourmash
conda install -c conda-forge -c bioconda sourmash-minimal -y