"""Run the reproducible Ledgerly pipeline from raw synthesis through decisions."""
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parent
STEPS=[[sys.executable,"02-data/generate_data.py"],[sys.executable,"02-data/load_to_db.py"],[sys.executable,"03-etl-and-analysis/python/etl_pipeline.py"],[sys.executable,"04-modeling/train_models.py"],[sys.executable,"05-cost-based-decisioning/threshold_optimizer.py"],[sys.executable,"06-experiment/power_analysis.py"],[sys.executable,"06-experiment/simulate_experiment.py"],[sys.executable,"create_notebooks.py"],[sys.executable,"write_reports.py"]]
for command in STEPS:
    print(f"\n>>> {' '.join(command)}",flush=True); subprocess.run(command,cwd=ROOT,check=True)
print("\nPipeline complete. So what? Every published metric is regenerated from source data and artifacts.")
