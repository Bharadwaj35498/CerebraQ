from pathlib import Path
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "data" / "raw" / "BraTS2023_TrainingData" / "ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData"
PATIENT_ID = "BraTS-GLI-00000-000"
PATIENT_DIR = DATASET_DIR / PATIENT_ID
OUTPUT_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_volume(modality):
    path = PATIENT_DIR / f"{PATIENT_ID}-{modality}.nii.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    return nib.load(str(path)).get_fdata()

def main():
    print(f"Loading patient: {PATIENT_ID}")
    t1n, t1c = load_volume("t1n"), load_volume("t1c")
    t2w, t2f = load_volume("t2w"), load_volume("t2f")
    seg = load_volume("seg")
    tumor_per_slice = np.sum(seg > 0, axis=(0, 1))
    slice_index = int(np.argmax(tumor_per_slice))
    print("Volume shape:", t1n.shape)
    print("Selected slice:", slice_index)
    print("Tumor pixels on selected slice:", int(tumor_per_slice[slice_index]))
    print("Total tumor voxels:", int(np.sum(seg > 0)))

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    for ax, (vol, title) in zip(axes.flat[:4], [(t1n,"T1 Native"),(t1c,"T1 Contrast Enhanced"),(t2w,"T2 Weighted"),(t2f,"FLAIR")]):
        ax.imshow(np.rot90(vol[:, :, slice_index]), cmap="gray")
        ax.set_title(title); ax.axis("off")
    seg_slice = np.rot90(seg[:, :, slice_index])
    axes[1,1].imshow(seg_slice, cmap="viridis"); axes[1,1].set_title("Tumor Segmentation"); axes[1,1].axis("off")
    axes[1,2].imshow(np.rot90(t1c[:, :, slice_index]), cmap="gray")
    axes[1,2].imshow(np.ma.masked_where(seg_slice == 0, seg_slice), cmap="autumn", alpha=0.45)
    axes[1,2].set_title("T1c + Tumor Overlay"); axes[1,2].axis("off")
    plt.suptitle(f"CerebraQ MRI Inspection — {PATIENT_ID}", fontsize=16)
    plt.tight_layout()
    output = OUTPUT_DIR / f"{PATIENT_ID}_mri_inspection.png"
    plt.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved visualization:", output)

if __name__ == "__main__":
    main()
