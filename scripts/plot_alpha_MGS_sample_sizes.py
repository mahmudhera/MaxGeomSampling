import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import math


def f(alpha):
    #beta = alpha / (1.0 - alpha)
    ret_val = (1.0/alpha)*(1.0/math.log(2.0)) + 1.0 - math.log(2.0)
    #ret_val = 2 + 1.0 / (2**beta - 1)
    return ret_val


def plot_growth_against_multiple_alpha(data_filename, output_filename):
    df = pd.read_csv(data_filename, sep='\t', index_col=False)
    plt.figure(figsize=(8, 4))
    
    # column names: set_size	amgs_sample_size_avg_alpha_0.25	amgs_sample_size_stddev_alpha_0.25	amgs_sample_size_avg_alpha_0.5	amgs_sample_size_stddev_alpha_0.5	amgs_sample_size_avg_alpha_0.75	amgs_sample_size_stddev_alpha_0.75
    # need to plot sample sizes for different k values against set_size with error bars as shaded region using stddev

    alpha_values = [0.25, 0.3]
    colors = sns.color_palette("husl", len(alpha_values))
    for alpha, color in zip(alpha_values, colors):
        avg_col = f'amgs_sample_size_avg_alpha_{alpha}'
        stddev_col = f'amgs_sample_size_stddev_alpha_{alpha}'
        plt.plot(df['set_size'], df[avg_col], label=f'α={alpha}', color=color, marker='o', markersize=3)
        plt.fill_between(df['set_size'], 
                         df[avg_col] - df[stddev_col], 
                         df[avg_col] + df[stddev_col], 
                         color=color, alpha=0.6)

    # also plot theoretical line: y = n^alpha for each alpha
    for alpha, color in zip(alpha_values, colors):
        theoretical_sizes = f(alpha) * df['set_size'] ** alpha
        plt.plot(df['set_size'], theoretical_sizes, linestyle='--', color=color, alpha=0.8, label='$f(a)*n^a$, a={}'.format(alpha))
        
        
    # also plot a line y = n/1000
    #plt.plot(df['set_size'], df['set_size']/1000, linestyle=':', color='black', alpha=0.8, label='$n/1000$')

    plt.xlabel('Original set size')
    plt.ylabel('$α$-MaxGeomSampling Sample sizes')
    #plt.title('Growth of $α$-MGS Samples Against Set Size for Different $α$ Values')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_filename)
    plt.close()
    
    
if __name__ == "__main__":
    input_file = os.path.join('results', 'results_growth_of_amgs_varying_alpha')
    output_file = os.path.join('plots', 'growth_of_alpha_mgs_samples.pdf')
    plot_growth_against_multiple_alpha(input_file, output_file)