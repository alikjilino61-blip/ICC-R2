from cobaya.likelihood import Likelihood
import os, subprocess, numpy as np, re

# ⚠️ ИМЯ КЛАССА ДОЛЖНО СОВПАДАТЬ С КЛЮЧОМ В YAML
class icc_likelihood(Likelihood):
    def initialize(self):
        self.class_path = "/home/alik/QW/icc-r2-q2/class_public"
        self.ini_path = os.path.join(self.class_path, "test_icc.ini")
        self.class_exe = os.path.join(self.class_path, "class")
        self.alpha = self.ini.float('alpha', 3.00)
        self.sign = self.ini.float('sign', -1.0)
        self._cache = {}

    def get_param_names(self):
        return ['delta_star', 'alpha']

    def logp(self, **params):
        delta_star = params.get('delta_star', 0.105)
        alpha = params.get('alpha', self.alpha)
        mu_icc = self.sign * alpha * delta_star

        cache_key = (round(delta_star, 4), round(alpha, 4))
        if cache_key in self._cache:
            h0_pred = self._cache[cache_key]
        else:
            self._update_ini(mu_icc)
            h0_pred = self._run_class()
            self._cache[cache_key] = h0_pred

        if h0_pred is None:
            return -1e10

        h0_obs, h0_err = 73.0, 1.0
        chi2 = ((h0_pred - h0_obs) / h0_err) ** 2
        return -0.5 * chi2

    def _update_ini(self, mu_icc):
        with open(self.ini_path, 'r') as f: content = f.read()
        content = re.sub(r'(mu_icc\s*=\s*)[-+]?\d*\.?\d+', rf'\g<1>{mu_icc:.6f}', content)
        with open(self.ini_path, 'w') as f: f.write(content)

    def _run_class(self):
        try:
            res = subprocess.run([self.class_exe, self.ini_path],
                                 capture_output=True, text=True, cwd=self.class_path, timeout=30)
            if res.returncode != 0: return None
            bg_file = os.path.join(self.class_path, "results", "icc__background.dat")
            if not os.path.exists(bg_file): return None
            with open(bg_file, 'r') as f:
                for line in f:
                    if line.startswith('#'): continue
                    parts = line.split()
                    if len(parts) >= 4 and float(parts[0]) < 0.01:
                        return float(parts[3]) * 299792.458
            return None
        except Exception: return None
