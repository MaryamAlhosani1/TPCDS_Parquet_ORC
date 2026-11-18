# TPC-DS: Parquet vs ORC — Compression and Timing Experiments

Reproduction of selected compression experiments from Liu et al. (2025), *Data formats in analytical DBMSs: performance trade-offs and future directions*, *The VLDB Journal*, 34, article 30, DOI: https://doi.org/10.1007/s00778-025-00911-1. 

## Reproduce on Google Colab (CPU)

Requirements: Linux/Colab, Python 3, Java 17+, Git, bzip2, tar, internet access, enough free disk space, and a CPU runtime. Spark 4.0.5 is pinned in `requirements.txt`. To reproduce the paper figures’ Tinos typography on Ubuntu/Colab, install the system font package `fonts-croscore` before regenerating charts (for example, `!apt-get -qq install -y fonts-croscore` in a Colab cell). This package installs the font locally and is not included in the repository.

```bash
python -m pip install -r requirements.txt```

The runner processes SF1, SF2 and SF5 compression measurements first, then write/count timings for the same scales in **one Spark session**. It subsequently runs the SF1 data-type and sensitivity experiments and generates the CSV statistics and eight figures. Downloaded benchmark data are removed after a completed run unless `--keep-data` is used; input datasets remain available through the timing phase. The latest accepted results are already bundled: do not re-run the full pipeline just to generate the report charts.

To rebuild CSV summaries and **all eight** figures from the bundled data without downloading or starting Spark:

```bash
python run_all.py --analysis-only
```

## Project map

- `run_all.py` — full experiment or analysis-only entry point
- `src/sequence.py` — shared-session compression → timing sequence
- `src/experiment.py` — Snappy Parquet/ORC compression ratios
- `src/performance.py` — per-table write-action and read/count-action timings
- `src/data_types.py`, `src/sensitivity.py` — additional SF1 experiments
- `src/statistical_analysis.py` — aggregation, descriptive analysis and Figures 1–6
- `src/performance_analysis.py` — timing aggregation and Figures 7–8
- `src/visualization.py`, `src/common.py`, `src/prepare_data.py` — helper functions
- `results/compression_sf*/`, `results/performance_sf*/`, `results/types_sf1/`, `results/sensitivity_sf1/`, `results/statistics/` — accepted CSVs and environment metadata
- `figures/` — the eight report illustrations in PNG/SVG, when available