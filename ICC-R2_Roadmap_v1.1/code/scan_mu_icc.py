#!/usr/bin/env python3
"""
ICC-R2 | Track 4: mu_icc scan via CLASS
Scans Omega_icc = mu_icc in [0.0, 0.05] and plots H_ICC(z)/H_LCDM(z)
"""
import subprocess, json, os, numpy as np, matplotlib.pyplot as plt, glob

ALPHA = 3.00  # H0(mu) ≈ H0_LC * (1 + 0.5*mu)
MU_RANGE = np.arange(0.0, 0.051, 0.005)
Z_RANGE = np.linspace(0.0, 3.0, 50)
CLASS_BIN = "./class"
RESULTS_DIR = "results/scan_mu"

os.makedirs(RESULTS_DIR, exist_ok=True)

def find_bg(prefix):
    """Find latest background.dat file with given prefix"""
    files = sorted(glob.glob(f"{prefix}*background.dat"))
    return files[-1] if files else None

def read_H0(fname):
    """Read H0 from background.dat (z≈0, column 4 = H [1/Mpc])"""
    with open(fname) as f:
        for line in f:
            if line.startswith('#'): continue
            p = line.split()
            if len(p) >= 4:
                z = float(p[0])
                if z < -0.315:  # today
                    return float(p[3])
    return None

def run_class(mu_icc, label):
    """Run CLASS with given mu_icc"""
    ini = f"{RESULTS_DIR}/test_{label}.ini"
    with open(ini, "w") as f:
        f.write(f"""root = {RESULTS_DIR}/{label}_
overwrite_root = y
write_background = y
background_verbose = 0
has_icc = {'y' if mu_icc > 0 else 'n'}
mu_icc = {mu_icc}
output = mPk
z_max_pk = 3
""")
    res = subprocess.run([CLASS_BIN, ini], capture_output=True, text=True)
    return res.returncode == 0

def main():
    print("🔍 ICC-R2: Scanning mu_icc (Omega_icc)...")
    results = {"alpha": ALPHA, "scans": [], "H0_values": []}
    
    # Reference LCDM run
    print("  → Running ΛCDM reference (mu=0)...")
    if not run_class(0.0, "lcdm_ref"):
        print("❌ LCDM run failed")
        return
    f_lcdm = find_bg(f"{RESULTS_DIR}/lcdm_ref_")
    if not f_lcdm:
        print("❌ LCDM background.dat not found")
        return
    h0_lcdm = read_H0(f_lcdm)
    print(f"  ✓ H0_LCDM = {h0_lcdm*299792.458:.3f} km/s/Mpc")
    
    # Scan over mu_icc
    for mu in MU_RANGE:
        label = f"mu_{mu:.3f}".replace('.','p')
        print(f"  → mu_icc={mu:.3f} (Δ≈{mu/ALPHA:.3f})...")
        if not run_class(mu, label):
            print(f"    ❌ CLASS failed")
            continue
        f_bg = find_bg(f"{RESULTS_DIR}/{label}_")
        if not f_bg: continue
        h0 = read_H0(f_bg)
        if h0 is None: continue
        diff_pct = (h0 - h0_lcdm) / h0_lcdm * 100
        results["H0_values"].append({"mu": float(mu), "H0_1Mpc": float(h0), "diff_%": float(diff_pct)})
        print(f"    ✓ H0 = {h0*299792.458:.3f} km/s/Mpc | ΔH0/H0 = {diff_pct:+.4f}%")
    
    # Save JSON
    with open(f"{RESULTS_DIR}/scan_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Saved: {RESULTS_DIR}/scan_results.json")
    
    # Plot H0 vs mu
    plt.figure(figsize=(6, 4))
    mus = [r["mu"] for r in results["H0_values"]]
    diffs = [r["diff_%"] for r in results["H0_values"]]
    plt.plot(mus, diffs, 'o-', label="CLASS results")
    plt.plot(mus, [0.5*m*100 for m in mus], '--', label="Theory: 0.5×mu", alpha=0.7)
    plt.xlabel(r"$\mu_{\rm icc} = \Omega_{\rm icc}$"); plt.ylabel(r"$\Delta H_0 / H_0$ [%]")
    plt.title("ICC-R2: H0 dependence on Omega_icc"); plt.grid(alpha=0.3); plt.legend()
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/H0_vs_mu.pdf", dpi=150)
    print(f"✅ Plot: {RESULTS_DIR}/H0_vs_mu.pdf")

if __name__ == "__main__":
    main()
