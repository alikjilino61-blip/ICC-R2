#!/usr/bin/env python3
"""
ICC-R2 | Bridge: Lattice Delta -> Cosmology H0
Connects Track 1 (Delta_star) with Track 4 (CLASS prediction).
"""
import subprocess, os, sys, glob, json

c_kms = 299792.458

# === Конфигурация ===
ALPHA = 3.00          # Геометрический фактор (из ICC VII)
DELTA_DEFAULT = 0.105 # Значение из Q2 2026 (Track 1 result)
CLASS_BIN = "./class" # Путь к бинарнику CLASS
WORK_DIR = "results/bridge"

def run_bridge(delta_star, alpha=ALPHA, negative_density=False):
    """
    Выполняет полный цикл: Delta -> mu -> CLASS -> H0
    """
    print(f"🚀 ICC-R2 Bridge: Запуск для Δ* = {delta_star}")
    
    # 1. Вычисление mu_icc
    # Формула связи: mu_icc = alpha * Delta (или с другим коэффициентом)
    # Примечание: если H должно подавляться, возможно mu_icc должен быть отрицательным?
    mu_icc = alpha * delta_star
    if negative_density:
        mu_icc = -mu_icc
        
    print(f"   📐 Расчет: mu_icc = alpha * Δ* = {alpha} * {delta_star} = {mu_icc:.4f}")
    print(f"   ⚠️  Интерпретация: mu_icc = Omega_icc = {mu_icc*100:.2f}% от критической плотности")

    # 2. Подготовка директории
    os.makedirs(WORK_DIR, exist_ok=True)

    # 3. Создание .ini файла для LCDM (базовый)
    ini_lcdm = f"{WORK_DIR}/lcdm_base.ini"
    with open(ini_lcdm, "w") as f:
        f.write(f"""root = {WORK_DIR}/lcdm_
overwrite_root = y
write_background = y
background_verbose = 0
has_icc = n
output = mPk
z_max_pk = 2
""")
    
    # 4. Создание .ini файла для ICC
    ini_icc = f"{WORK_DIR}/icc_delta.ini"
    with open(ini_icc, "w") as f:
        f.write(f"""root = {WORK_DIR}/icc_
overwrite_root = y
write_background = y
background_verbose = 0
has_icc = y
mu_icc = {mu_icc}
output = mPk
z_max_pk = 2
""")

    # 5. Запуск CLASS
    print(f"   ⏳ Запуск CLASS (LCDM)...")
    res_lcdm = subprocess.run([CLASS_BIN, ini_lcdm], capture_output=True, text=True)
    if res_lcdm.returncode != 0:
        print(f"   ❌ Ошибка CLASS (LCDM): {res_lcdm.stderr[:200]}")
        return

    print(f"   ⏳ Запуск CLASS (ICC)...")
    res_icc = subprocess.run([CLASS_BIN, ini_icc], capture_output=True, text=True)
    if res_icc.returncode != 0:
        print(f"   ❌ Ошибка CLASS (ICC): {res_icc.stderr[:200]}")
        return

    # 6. Чтение результатов
    def read_H0(prefix):
        files = sorted(glob.glob(f"{WORK_DIR}/{prefix}*background.dat"))
        if not files: return None
        with open(files[-1]) as f:
            for line in f:
                if line.startswith('#'): continue
                p = line.split()
                if len(p) >= 4 and float(p[0]) < 0.01:
                    return float(p[3])
        return None

    h0_lcdm = read_H0("lcdm_")
    h0_icc = read_H0("icc_")

    if not h0_lcdm or not h0_icc:
        print("   ❌ Не удалось найти H0 в output файлах")
        return

    diff_pct = (h0_icc - h0_lcdm) / h0_lcdm * 100
    h0_icc_kms = h0_icc * c_kms
    h0_lcdm_kms = h0_lcdm * c_kms

    # 7. Вывод отчета
    print("\n" + "="*50)
    print("🎯 ICC-R2 BRIDGE RESULT")
    print("="*50)
    print(f"📊 Input (Track 1):  Δ* = {delta_star}")
    print(f"🔗 Coupling:        mu_icc = {mu_icc:.4f} (Omega_icc = {mu_icc*100:.2f}%)")
    print(f"🌌 Output (Track 4):")
    print(f"   H0 (LCDM) = {h0_lcdm_kms:.3f} km/s/Mpc")
    print(f"   H0 (ICC)  = {h0_icc_kms:.3f} km/s/Mpc")
    print(f"   📈 Effect   = {diff_pct:+.4f}%")
    print("="*50)
    
    # 8. Сохранение результата в JSON
    report = {
        "delta_star": delta_star,
        "alpha": alpha,
        "mu_icc": mu_icc,
        "H0_lcdm": h0_lcdm_kms,
        "H0_icc": h0_icc_kms,
        "diff_pct": diff_pct
    }
    with open(f"{WORK_DIR}/bridge_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"💾 Отчет сохранен: {WORK_DIR}/bridge_report.json")
    print("="*50)

if __name__ == "__main__":
    # Парсинг аргументов
    import argparse
    parser = argparse.ArgumentParser(description="ICC-R2 Bridge Script")
    parser.add_argument("--delta", type=float, default=DELTA_DEFAULT, help="Value of Delta_star (default: 0.105)")
    parser.add_argument("--alpha", type=float, default=ALPHA, help="Coupling factor (default: 3.0)")
    parser.add_argument("--negative", action="store_true", help="Use negative density (for H suppression)")
    args = parser.parse_args()

    # Проверка наличия CLASS
    if not os.path.exists(CLASS_BIN):
        print(f"❌ CLASS executable not found at '{CLASS_BIN}'. Run from class_public dir.")
        sys.exit(1)

    run_bridge(args.delta, args.alpha, args.negative)
