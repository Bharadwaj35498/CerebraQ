from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "BraTS2023_TrainingData" / "ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
REPORTS_DIR = PROJECT_ROOT / "reports"

for d in (PROCESSED_DIR, INTERIM_DIR, REPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)
