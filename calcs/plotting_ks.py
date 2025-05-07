import numpy as np
import matplotlib.pyplot as plt

from .calc_ks import k1,k2,calc_kii

def plotting_ks(ratio_lim,depth_vector,A):
    ratio_values=np.linspace(ratio_lim[0],ratio_lim[1],100)

    k1_results={depth:[] for depth in depth_vector}
    k2_results={depth:[] for depth in depth_vector}

    for ratio in ratio_values:
        for depth in depth_vector:
            k1_results[depth].append(k1(ratio,depth,A))
            k2_results[depth].append(k2(ratio,depth,A))

    colors = ['blue', 'red', 'orange', 'green', 'purple', 'brown', 'pink', 'gray']

    # plotting k1
    plt.figure(figsize=(12,6))
    for i,depth in enumerate(depth_vector):
        linewidth=2.5 if depth in [0, (1/10*np.sqrt(A)), (1/6*np.sqrt(A))] else 1
        plt.plot(ratio_values,k1_results[depth], label=f'depth={depth:.2f}',color=colors[i % len(colors)],linewidth=linewidth)
    
    plt.xlabel('Ratio')
    plt.ylabel('k1')
    plt.title('k1 vs Ratio for Different Depths')
    plt.legend()
    plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)
    plt.xlim(0,8)
    plt.ylim(0.85,1.4)
    plt.show()


# plotting k2
    plt.figure(figsize=(12,6))
    for i,depth in enumerate(depth_vector):
        linewidth=2.5 if depth in [0, (1/10*np.sqrt(A)), (1/6*np.sqrt(A))] else 1
        plt.plot(ratio_values,k2_results[depth], label=f'depth={depth:.2f}',color=colors[i % len(colors)],linewidth=linewidth)
    plt.xlabel('Ratio')
    plt.ylabel('k2')
    plt.title('k2 vs Ratio for Different Depths')
    plt.legend()
    plt.grid(True, which='both', axis='both',linestyle='--', linewidth=0.5)
    plt.xlim(0,8)
    plt.ylim(3,7)
    plt.show()

def plotting_kii():
    nrods_values = np.arange(1, 201)
    kii_values = [kii(nrods) for nrods in nrods_values]

    plt.figure(figsize=(10, 6))
    plt.plot(nrods_values, kii_values, label='kii vs nrods', color='blue', linewidth=2)
    plt.xlabel('Number of Rods (nrods)')
    plt.ylabel('kii')
    plt.title('kii vs Number of Rods')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xlim(0, 200)
    plt.ylim(0, max(kii_values) * 1.1)
    plt.legend()
    plt.show()
