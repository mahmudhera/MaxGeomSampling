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
    k_values_tested = [70, 80, 90, 100]
    colors = ['#a6cee3','#b2df8a', '#1f78b4', '#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#ab93b7']
    markers = ['D', '<', 'o', '>', '^', 'v', '*', 'P', 'X']
    colors = colors[0:4]
    markers = markers[0:4]

    plt.figure(figsize=(4, 3))
    color_idx = 0
    for k in k_values_tested:
        subset = df[df['k'] == k]
        plt.scatter(subset['True_Jaccard'], subset['Estimated_Jaccard'], label=f'MaxGeomHash ($b$={k})', color=colors[color_idx], alpha=0.3, s=10, marker=markers[color_idx])
        color_idx += 1
    
    # plot a diagonal line y=x
    max_val = df['True_Jaccard'].max()
    print(max_val)
    plt.plot([0, max_val], [0, max_val], 'k--', label='True Jaccard', linewidth=0.75)
    plt.xlabel('True Jaccard')
    plt.ylabel('Estimated Jaccard')
    plt.legend(fontsize=8)

    # change the alpha values in the legend to 1.0
    leg = plt.gca().get_legend()
    for handle in leg.legend_handles:
        handle.set_alpha(1.0)

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # export with high resolution
    plt.savefig(output_file, dpi=500)
    plt.close()
    
    print("Plot saved to: ", output_file )

    # now calculate the R^2 value for each method and parameter
    for k in k_values_tested:
        subset = df[df['k'] == k]
        r2 = np.corrcoef(subset['True_Jaccard'], subset['Estimated_Jaccard'])[0, 1] ** 2
        print(f'R^2 for MaxGeomHash (b={k}): {r2:.4f}')
    