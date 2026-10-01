from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "BraTS2023_TrainingData" / "ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData"

if not DATASET_DIR.exists():
    print("Dataset directory not found:", DATASET_DIR)
else:
    patients = sorted(p for p in DATASET_DIR.iterdir() if p.is_dir())
    print("Dataset:", DATASET_DIR)
    print("Patients found:", len(patients))
    if patients:
        print("First patient:", patients[0].name)
