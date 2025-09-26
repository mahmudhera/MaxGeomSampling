import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

if __name__ == "__main__":
    results_file = os.path.join("results", "results_accuracy_by_varying_jaccard")
    output_file = os.path.join("plots", "accuracy_jaccard_by_varying_jaccard.png")
    df = pd.read_csv(results_file, sep='\t', index_col=False)
    # columns: k, True_Jaccard, Estimated_Jaccard
    
    # plot true jaccard vs estimated jaccard for each method and parameter
    # method names: MGS, alpha-MGS. each method has four parameters
    k_values_tested = [50, 100, 200, 400]
    colors = sns.color_palette("husl", len(k_values_tested))

    plt.figure(figsize=(8, 6))
    color_idx = 0
    for k in k_values_tested:
        subset = df[df['k'] == k]
        plt.scatter(subset['True_Jaccard'], subset['Estimated_Jaccard'], label=f'MaxGeomSampling (k={k})', color=colors[color_idx], alpha=0.3, s=10)
        color_idx += 1
    
    # plot a diagonal line y=x
    max_val = df['True_Jaccard'].max()
    print(max_val)
    plt.plot([0, max_val], [0, max_val], 'k--', label='True Jaccard', alpha=0.4)
    plt.xlabel('True Jaccard')
    plt.ylabel('Estimated Jaccard')
    plt.title('Estimated vs. True Jaccard for MaxGeomSampling (With Refining)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    # export with high resolution
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print("Plot saved to: ", output_file )
    