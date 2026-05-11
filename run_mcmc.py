from cobaya.run import run
import yaml

with open("icc_mcmc.yaml") as f:
    info = yaml.safe_load(f)

print("🚀 Запуск MCMC...")
run(info, force=True)
print("✅ Готово. Цепи в chains/icc_test/")
