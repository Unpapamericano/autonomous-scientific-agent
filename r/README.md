# Scientific dashboard (R + C++ + Polars)

This folder contains a polished R/Shiny dashboard for scientific benchmark results produced by the project’s C++ tools and Python/Polars analysis stack.

## Files

- `generate_demo_data.py` — creates sample `math_results.csv` and `quantum_results.csv` with Polars.
- `shiny_dashboard.R` — professional dashboard with uploads, KPI cards, and interactive plots.

## Quick start

1. Install R and package dependencies:
   ```bash
   Rscript -e "install.packages(c('shiny','bslib','ggplot2','dplyr','plotly','reticulate','DT'), repos='https://cloud.r-project.org')"
   ```

2. Install Polars for the Python backend used by the dashboard:
   ```bash
   python -m pip install polars
   ```

3. Generate demo data:
   ```bash
   python r/generate_demo_data.py
   ```

4. Launch the dashboard:
   ```bash
   Rscript r/shiny_dashboard.R
   ```

5. Optional: replace the demo CSVs with outputs from the C++ benchmark utilities under `cpp/math_test` and `cpp/quantum`.

## Notes

- The dashboard loads sample data from `data/` by default.
- If Reticulate + Polars are available, CSVs are read with Polars for better scientific data handling.
- The app supports uploading custom CSVs and visualizing pass/fail outcomes, topic errors, and quantum quality tradeoffs.
