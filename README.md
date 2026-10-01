# CerebraQ
## An Explainable Hybrid Quantum–Classical Framework for Brain MRI Analysis

CerebraQ is a college research project for multimodal brain MRI analysis. The planned pipeline combines MRI preprocessing, tumor-region analysis, classical feature extraction, quantum feature processing, hybrid classification, explainability, uncertainty estimation, patient-level analysis, and reporting.

### Dataset
The MRI dataset is intentionally excluded. Place the extracted BraTS-compatible dataset under:
`data/raw/BraTS2023_TrainingData/ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData/`

Expected patient files:
- `*-t1n.nii.gz`
- `*-t1c.nii.gz`
- `*-t2w.nii.gz`
- `*-t2f.nii.gz`
- `*-seg.nii.gz`

Do not assume HGG/LGG labels are present in this dataset. A verified grade-label source is required before supervised HGG/LGG training.
