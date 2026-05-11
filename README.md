# ICC-R2: Implementation Protocol and Roadmap (v1.1)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20041595.svg)](https://doi.org/10.5281/zenodo.20041595)

## 📖 Overview
This repository provides the complete implementation of the **Information-Copying Cosmology (ICC-R2)** model integrated into the **CLASS** (Cosmic Linear Anisotropy Solving System) Boltzmann code (v3.3.4).

The ICC-R2 framework posits that spacetime geometry emerges from stochastic copying dynamics on a simplicial complex, leading to a defect parameter $\Delta^*$ that modifies the standard cosmological background. This code bridges the microscopic lattice parameter $\Delta^*$ to the macroscopic Hubble parameter $H_0$.

## 🚀 Quick Start

### 1. Prerequisites
*   **Python 3.9+** with `numpy`, `scipy`, `matplotlib`.
*   **GCC/Clang compiler** for building CLASS.
*   **CLASS v3.3.4** (source code included or required).

### 2. Build ICC-Enabled CLASS
The `class_modifications/` directory contains the patched source files. To build the modified version of CLASS:

```bash
# 1. Replace original CLASS files with modified versions
cp class_modifications/source/background.c CLASS/source/
cp class_modifications/source/input.c CLASS/source/
cp class_modifications/include/background.h CLASS/include/
cp class_modifications/include/common.h CLASS/include/

# 2. Compile CLASS
cd CLASS
make clean && make -j$(nproc)
