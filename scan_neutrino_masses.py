#!/usr/bin/env python3
"""
ICC-R2 Track 2: Scan neutrino masses from copying dynamics
"""
import numpy as np, json, os, matplotlib.pyplot as plt

# Parameters from Track 4 calibration
ALPHA = 3.00
DELTA_DEFAULT = 0.105
DELTA_ERR = 0.005

def compute_masses(delta, alpha=ALPHA):
    """Compute neutrino masses from defect parameter"""
    epsilon = alpha * delta
    m0 = np.sqrt(7.53e-5 / (2 * epsilon))  # eV, from Δm²_21
    
    m1 = m0 * (1 - epsilon)
    m2 = m0
    m3 = m0 * (1 + epsilon)
    
    return {
        'm1': m1, 'm2': m2, 'm3': m3,
        'sum_mnu': m1 + m2 + m3,
        'dm21': 2 * m0**2 * epsilon,
        'dm31': 4 * m0**2 * epsilon,
        'ratio': 2 / epsilon
    }

def main():
    print("🔍 ICC-R2 Track 2: Neutrino mass scan")
    results = []
    
    # Scan over Δ* uncertainty
    for delta in np.linspace(0.095, 0.115, 21):
        res = compute_masses(delta)
        results.append({'delta': delta, **res})
        print(f"Δ*={delta:.3f}: Σm_ν={res['sum_mnu']*1e3:.2f} meV, ratio={res['ratio']:.2f}")
    
    # Save
    os.makedirs('results/neutrino', exist_ok=True)
    with open('results/neutrino/mass_scan.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Plot
    deltas = [r['delta'] for r in results]
    sums = [r['sum_mnu']*1e3 for r in results]  # meV
    plt.figure(figsize=(6,4))
    plt.plot(deltas, sums, 'o-')
    plt.axvspan(0.100, 0.110, alpha=0.2, label='Δ* = 0.105 ± 0.005')
    plt.xlabel(r'$\Delta^*$'); plt.ylabel(r'$\sum m_\nu$ [meV]')
    plt.title('ICC-R2: Neutrino mass sum vs. defect parameter')
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig('results/neutrino/sum_mnu_vs_delta.pdf')
    print("✅ Plot: results/neutrino/sum_mnu_vs_delta.pdf")

if __name__ == "__main__":
    main()
