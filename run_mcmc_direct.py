import sys
import os

# Добавляем текущую директорию в путь, чтобы импортировать наш likelihood
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cobaya.run import run
from likelihood_icc import icc_likelihood  # Прямой импорт класса

info = {
    "params": {
        "delta_star": {"prior": {"min": 0.05, "max": 0.15}, "ref": {"dist": "norm", "loc": 0.105, "scale": 0.005}},
        "alpha": {"prior": {"min": 2.5, "max": 3.5}, "ref": 3.00},
        "H0": {"prior": {"min": 50, "max": 90}, "ref": 67.4},
        "omega_b": {"prior": {"min": 0.01, "max": 0.05}, "ref": 0.0224},
        "omega_cdm": {"prior": {"min": 0.05, "max": 0.99}, "ref": 0.12}
    },
    "likelihood": {
        "icc_likelihood": icc_likelihood,  # ✅ Передаём класс напрямую, без path!
        "h0_prior": {"value": {"H0": 73.0}, "sigma": 1.0}
    },
    "sampler": {
        "mcmc": {
            "burn_in": 50,
            "Rminus1_stop": 0.1,
            "covmat": "auto"
        }
    },
    "output": "chains/icc_test/",
    "stop_at": 300
}

print("🚀 Запуск MCMC (прямая передача класса)...")
run(info, force=True)
print("✅ Готово. Цепи сохранены в chains/icc_test/")
