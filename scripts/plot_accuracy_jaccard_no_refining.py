import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

if __name__ == "__main__":
    results_file = os.path.join("results", "results_accuracy_of_jaccard_no_filtering")
    output_file = os.path.join("plots", "accuracy_jaccard_no_refining_MGS.png")
    df = pd.read_csv(results_file, sep='\t', index_col=False)
    # columns: Method, Parameter, Len_Set2. True_Jaccard, Estimated_Jaccard
    
    # plot true jaccard vs estimated jaccard for each method and parameter
    # method names: MGS, alpha-MGS. each method has four parameters
    methods = ['MGS']
    parameters_MGS = [50, 100, 200, 400]
    colors = sns.color_palette("husl", len(methods) * len(parameters_MGS))
    
    plt.figure(figsize=(8, 6))
    color_idx = 0
    for method in methods:
        for param in parameters_MGS:
            subset = df[(df['Method'] == method) & (df['Parameter'] == param)]
            plt.scatter(subset['True_Jaccard'], subset['Estimated_Jaccard'], label=f'MaxGeomSampling (k={param})', color=colors[color_idx], alpha=0.3, s=10)
            color_idx += 1
    # plot a diagonal line y=x
    max_val = df['True_Jaccard'].max()
    print(max_val)
    plt.plot([0, max_val], [0, max_val], 'k--', label='True Jaccard', alpha=0.4)
    plt.xlabel('True Jaccard')
    plt.ylabel('Estimated Jaccard')
    plt.title('Estimated vs. True Jaccard for MaxGeomSampling (No Refining)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    # export with high resolution
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    
    # clear the plot
    plt.clf()
    
    # new plot
    output_file = os.path.join("plots", "accuracy_jaccard_no_refining_alpha-MGS.png")
    methods = ['alpha-MGS']
    parameters_alpha_MGS = [0.2, 0.3, 0.4, 0.5]
    colors = sns.color_palette("husl", len(methods) * len(parameters_alpha_MGS))

    plt.figure(figsize=(8, 6))
    color_idx = 0
    for method in methods:
        for param in parameters_alpha_MGS:
            subset = df[(df['Method'] == method) & (df['Parameter'] == param)]
            plt.scatter(subset['True_Jaccard'], subset['Estimated_Jaccard'], label=f'MaxGeomSampling (alpha={param})', color=colors[color_idx], alpha=0.3, s=10)
            color_idx += 1
    # plot a diagonal line y=x
    max_val = df['True_Jaccard'].max()
    print(max_val)
    plt.plot([0, max_val], [0, max_val], 'k--', label='True Jaccard', alpha=0.4)
    plt.xlabel('True Jaccard')
    plt.ylabel('Estimated Jaccard')
    plt.title('Estimated vs. True Jaccard for alpha-MaxGeomSampling (No Refining)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    # export with high resolution
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    