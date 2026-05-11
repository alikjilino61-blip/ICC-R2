# ICC-R2: Implementation Protocol and Roadmap (v1.1)

> **Author**: Alik Gimranov  
> **ORCID**: [0009-0001-5952-9887](https://orcid.org/0009-0001-5952-9887)  
> **DOI**: `10.5281/zenodo.20041595` (v1.0) → *new DOI for v1.1 after upload*  
> **License**: [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/)

## Abstract
This document defines the implementation protocol for Information-Copying Cosmology (ICC-R2), including quarterly milestones, reproducibility standards, and Q2 2026 results. **Update v1.1**: Confirmed successful integration of ICC background component into CLASS v3.3.4, with calibrated linear response `H0(μ) = H0^ΛCDM × (1 + 0.5 μ)` and reproducible scanning scripts.

## New in v1.1
- ✅ CLASS v3.3.4 integration with ICC background component
- ✅ Calibration: `H0(μ) = 67.81 × (1 + 0.5 μ) km/s/Mpc` verified for μ ∈ [0, 0.05]
- ✅ Bridge script: `Δ* → μ = α·Δ* → H0` (α = 3.0)
- ✅ Auto-scanning: `scan_delta_star.py` for Δ* ∈ [0.08, 0.12]
- ✅ Draft Methods section for preprint

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run Track 4: mu_icc scan
cd code/
python scan_mu_icc.py  # Results in ../results/scan_mu/

# Run Bridge: Delta* -> H0
python bridge_delta_to_class.py --delta 0.105 --negative

# Run Auto-scan: Delta* range
python scan_delta_star.py  # Plots in ../results/auto_scan/
