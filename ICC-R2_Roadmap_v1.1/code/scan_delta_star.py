#!/usr/bin/env python3
"""
ICC-R2 | Auto-scan: Delta_star -> H0
Scans Δ* ∈ [0.08, 0.12] and plots H0(Δ*) with theoretical prediction.
"""
import subprocess, json, os, sys, glob, numpy as np, matplotlib.pyplot as plt

# === Конфигурация ===
ALPHA = 3.00          # Геометрический фактор (из ICC VII)
DELTA_RANGE = np.linspace(0.08, 0.12, 9)  # Δ* из Трека 1: [0.08, 0.12]
CLASS_BIN = "./class"
WORK_DIR = "results/auto_scan"
USE_NEGATIVE = True   # Если ожидается подавление H(z), используйте отрицательный знак

os.makedirs(WORK_DIR, exist_ok=True)

def run_class_for_delta(delta, alpha=ALPHA, negative=False):
    """Запуск CLASS для заданного Δ*"""
    mu_icc = alpha * delta
    if negative:
        mu_icc = -mu_icc
    
    # Создаём .ini для LCDM
    ini_lcdm = f"{WORK_DIR}/lcdm_ref.ini"
    with open(ini_lcdm, "w") as f:
        f.write(f"""root = {WORK_DIR}/lcdm_ref_
overwrite_root = y
write_background = y
background_verbose = 0
has_icc = n
output = mPk
z_max_pk = 2
""")
    
    # Создаём .ini для ICC
    ini_icc = f"{WORK_DIR}/icc_delta_{delta:.3f}.ini"
    with open(ini_icc, "w") as f:
        f.write(f"""root = {WORK_DIR}/icc_{delta:.3f}_
overwrite_root = y
write_background = y
background_verbose = 0
has_icc = y
mu_icc = {mu_icc}
output = mPk
z_max_pk = 2
""")
    
    # Запускаем CLASS
    res_lcdm = subprocess.run([CLASS_BIN, ini_lcdm], capture_output=True, text=True)
    res_icc = subprocess.run([CLASS_BIN, ini_icc], capture_output=True, text=True)
    
    if res_lcdm.returncode != 0 or res_icc.returncode != 0:
        print(f"❌ CLASS failed for Δ*={delta}")
        return None, None
    
    # Читаем H0 из background.dat
    def read_H0(prefix):
        files = sorted(glob.glob(f"{WORK_DIR}/{prefix}*background.dat"))
        if not files:
            return None
        with open(files[-1]) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                p = line.split()
                if len(p) >= 4 and float(p[0]) < 0.01:
                    return float(p[3])
        return None
    
    h0_lcdm = read_H0("lcdm_ref_")
    h0_icc = read_H0(f"icc_{delta:.3f}_")
    
    if h0_lcdm is None or h0_icc is None:
        return None, None
    
    return h0_lcdm * 299792.458, h0_icc * 299792.458  # в км/с/Мпк

def main():
    print("🔍 ICC-R2: Auto-scan Δ* → H0")
    print(f"   Диапазон: Δ* ∈ [{DELTA_RANGE[0]:.3f}, {DELTA_RANGE[-1]:.3f}]")
    print(f"   Связь: mu_icc = {'-' if USE_NEGATIVE else ''}{ALPHA} × Δ*")
    print("="*60)
    
    results = []
    h0_lcdm_ref = None
    
    for delta in DELTA_RANGE:
        print(f"   → Δ* = {delta:.3f} ...", end=" ")
        h0_lcdm, h0_icc = run_class_for_delta(delta, ALPHA, USE_NEGATIVE)
        
        if h0_lcdm is None:
            print("❌ ошибка")
            continue
        
        if h0_lcdm_ref is None:
            h0_lcdm_ref = h0_lcdm
        
        diff_pct = (h0_icc - h0_lcdm) / h0_lcdm * 100
        theory_pct = (0.5 * (-ALPHA * delta if USE_NEGATIVE else ALPHA * delta)) * 100
        
        print(f"H0 = {h0_icc:.3f} км/с/Мпк | Δ = {diff_pct:+.3f}% (теория: {theory_pct:+.3f}%)")
        
        results.append({
            "delta": float(delta),
            "mu_icc": float((-ALPHA if USE_NEGATIVE else ALPHA) * delta),
            "H0_LCDM": float(h0_lcdm),
            "H0_ICC": float(h0_icc),
            "diff_observed": float(diff_pct),
            "diff_theory": float(theory_pct)
        })
    
    # Сохраняем результаты
    with open(f"{WORK_DIR}/auto_scan_results.json", "w") as f:
        json.dump({"alpha": ALPHA, "negative": USE_NEGATIVE, "scans": results}, f, indent=2)
    print(f"\n✅ Сохранено: {WORK_DIR}/auto_scan_results.json")
    
    # Строим график
    if not results:
        print("❌ Нет данных для графика")
        return
    
    deltas = [r["delta"] for r in results]
    h0_vals = [r["H0_ICC"] for r in results]
    diff_obs = [r["diff_observed"] for r in results]
    diff_th = [r["diff_theory"] for r in results]
    
    # График 1: H0 vs Δ*
    plt.figure(figsize=(8, 5))
    plt.plot(deltas, h0_vals, 'o-', label="CLASS results", linewidth=2)
    plt.xlabel(r"$\Delta^*$ (defect rate from lattice)", fontsize=12)
    plt.ylabel(r"$H_0$ [km/s/Mpc]", fontsize=12)
    plt.title(f"ICC-R2: H0 dependence on Δ* (α={ALPHA}, sign={'−' if USE_NEGATIVE else '+'})", fontsize=13)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{WORK_DIR}/H0_vs_delta.pdf", dpi=150)
    print(f"✅ График 1: {WORK_DIR}/H0_vs_delta.pdf")
    
    # График 2: Отклонение от ΛCDM
    plt.figure(figsize=(8, 5))
    plt.plot(deltas, diff_obs, 'o-', label="Observed ΔH0/H0", linewidth=2)
    plt.plot(deltas, diff_th, '--', label=f"Theory: 0.5×μ (μ={'−' if USE_NEGATIVE else ''}αΔ*)", alpha=0.7)
    plt.axhline(0, color="gray", ls=":", alpha=0.5)
    plt.xlabel(r"$\Delta^*$", fontsize=12)
    plt.ylabel(r"$\Delta H_0 / H_0$ [%]", fontsize=12)
    plt.title("ICC-R2: Deviation from ΛCDM", fontsize=13)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{WORK_DIR}/deviation_vs_delta.pdf", dpi=150)
    print(f"✅ График 2: {WORK_DIR}/deviation_vs_delta.pdf")
    
    # Печать сводки
    print("\n" + "="*60)
    print("📊 СВОДКА")
    print("="*60)
    print(f"Δ* диапазон: [{min(deltas):.3f}, {max(deltas):.3f}]")
    print(f"H0 диапазон: [{min(h0_vals):.3f}, {max(h0_vals):.3f}] км/с/Мпк")
    print(f"Отклонение: [{min(diff_obs):+.3f}%, {max(diff_obs):+.3f}%]")
    print(f"Согласие с теорией: среднее отклонение = {np.mean(np.array(diff_obs)-np.array(diff_th)):+.4f}%")
    print("="*60)

if __name__ == "__main__":
    if not os.path.exists(CLASS_BIN):
        print(f"❌ CLASS executable not found at '{CLASS_BIN}'")
        sys.exit(1)
    main()
