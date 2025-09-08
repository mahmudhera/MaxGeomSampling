import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def plot_growth_against_fmh(data_filename, output_filename):
    df = pd.read_csv(data_filename, sep='\t', index_col=False)
    plt.figure(figsize=(10, 6))
    
    # column naes: set_size  fmh_sketch_size_avg fmh_sketch_size_stddev  maxgeom_sample_size_avg maxgeom_sample_size_stddev
    # need to plot fmh_sketch_size_avg and maxgeom_sample_size_avg against set_size
    
    colors = sns.color_palette("husl", 2)
    
    # plot with error bars as shaded region using stddev
    plt.plot(df['set_size'], df['fmh_sketch_size_avg'], label='FMH Sketch Size', color=colors[0], marker='o', markersize=3)
    plt.fill_between(df['set_size'], 
                     df['fmh_sketch_size_avg'] - df['fmh_sketch_size_stddev'], 
                     df['fmh_sketch_size_avg'] + df['fmh_sketch_size_stddev'], 
                     color=colors[0], alpha=0.2)

    plt.plot(df['set_size'], df['maxgeom_sample_size_avg'], label='MaxGeom Sample Size', color=colors[1], marker='o', markersize=3)
    plt.fill_between(df['set_size'], 
                     df['maxgeom_sample_size_avg'] - df['maxgeom_sample_size_stddev'], 
                     df['maxgeom_sample_size_avg'] + df['maxgeom_sample_size_stddev'], 
                     color=colors[1], alpha=0.2)

    plt.xlabel('Original set size')
    plt.ylabel('Sample size (averaged over 20 runs)')
    plt.title('Growth of Sample Sizes Against Original Set Size')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_filename)
    plt.close()
    
    
    
def plot_growth_against_multiple_k(data_filename, output_filename):
    df = pd.read_csv(data_filename, sep='\t', index_col=False)
    plt.figure(figsize=(10, 6))
    
    # column names: set_size	mgs_sample_size_avg_k_25	mgs_sample_size_stddev_k_25	mgs_sample_size_avg_k_50	mgs_sample_size_stddev_k_50	mgs_sample_size_avg_k_100	mgs_sample_size_stddev_k_100	mgs_sample_size_avg_k_200	mgs_sample_size_stddev_k_200	mgs_sample_size_avg_k_400	mgs_sample_size_stddev_k_400	mgs_sample_size_avg_k_800	mgs_sample_size_stddev_k_800
    # need to plot sample sizes for different k values against set_size with error bars as shaded region using stddev

    #k_values = [25, 50, 100, 200, 400, 800]
    k_values = [400, 800]
    colors = sns.color_palette("husl", len(k_values))
    for k, color in zip(k_values, colors):
        avg_col = f'mgs_sample_size_avg_k_{k}'
        stddev_col = f'mgs_sample_size_stddev_k_{k}'
        plt.plot(df['set_size'], df[avg_col], label=f'k={k}', color=color, marker='o', markersize=3)
        plt.fill_between(df['set_size'], 
                         df[avg_col] - df[stddev_col], 
                         df[avg_col] + df[stddev_col], 
                         color=color, alpha=0.6)
        
    # also plot theoretical line: y = k * long(n/k) for each k
    for k, color in zip(k_values, colors):
        theoretical_sizes = k * np.log2(df['set_size'] / k)
        plt.plot(df['set_size'], theoretical_sizes, linestyle='--', color=color, alpha=0.8, label=f'$k \log_2(n/k)$ for k={k}')

    plt.xlabel('Original set size')
    plt.ylabel('MaxGeom Sample size (averaged over 20 runs)')
    plt.title('Growth of MaxGeom Sample Sizes Against Original Set Size for Different k Values')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_filename)
    plt.close()


if __name__ == "__main__":
    data_file = os.path.join('results', 'results_growth_of_samples')
    output_file = os.path.join('plots', 'growth_against_fmh.pdf')
    plot_growth_against_fmh(data_file, output_file)
    
    data_file_k = os.path.join('results', 'results_growth_of_mgs_varying_k')
    output_file_k = os.path.join('plots', 'growth_against_multiple_k.pdf')
    plot_growth_against_multiple_k(data_file_k, output_file_k)
