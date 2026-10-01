from pathlib import Path

import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import zoom


# ============================================================
# CerebraQ - MRI Preprocessing
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "BraTS2023_TrainingData"
    / "ASNR-MICCAI-BraTS2023-GLI-Challenge-TrainingData"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

PATIENT_ID = "BraTS-GLI-00000-000"

MODALITIES = {
    "t1n": f"{PATIENT_ID}-t1n.nii.gz",
    "t1c": f"{PATIENT_ID}-t1c.nii.gz",
    "t2w": f"{PATIENT_ID}-t2w.nii.gz",
    "t2f": f"{PATIENT_ID}-t2f.nii.gz",
}

SEGMENTATION_FILE = f"{PATIENT_ID}-seg.nii.gz"

TARGET_SIZE = (64, 64)
PADDING = 10


# ============================================================
# Utility functions
# ============================================================

def load_nifti(path):
    """Load a NIfTI file as float32 numpy array."""
    return nib.load(str(path)).get_fdata().astype(np.float32)


def normalize_volume(volume):
    """
    Z-score normalize non-zero voxels.

    Background remains zero.
    """
    mask = volume != 0

    normalized = np.zeros_like(volume, dtype=np.float32)

    if np.any(mask):
        values = volume[mask]
        mean = values.mean()
        std = values.std()

        if std > 0:
            normalized[mask] = (values - mean) / std
        else:
            normalized[mask] = values - mean

    return normalized


def resize_2d(image, target_size=(64, 64)):
    """Resize a 2D image using interpolation."""
    zoom_factors = (
        target_size[0] / image.shape[0],
        target_size[1] / image.shape[1],
    )

    return zoom(image, zoom_factors, order=1).astype(np.float32)


def resize_mask(mask, target_size=(64, 64)):
    """Resize segmentation mask using nearest-neighbour interpolation."""
    zoom_factors = (
        target_size[0] / mask.shape[0],
        target_size[1] / mask.shape[1],
    )

    return zoom(mask, zoom_factors, order=0).astype(np.uint8)


def find_best_tumor_slice(segmentation):
    """
    Select the axial slice containing the largest number
    of tumour pixels.
    """
    tumor_mask = segmentation > 0

    tumor_pixels_per_slice = tumor_mask.sum(axis=(0, 1))

    best_slice = int(np.argmax(tumor_pixels_per_slice))

    return best_slice, int(tumor_pixels_per_slice[best_slice])


def get_tumor_bbox(mask, padding=10):
    """
    Find the 2D bounding box around the tumour and
    add padding.
    """
    rows, cols = np.where(mask)

    if len(rows) == 0:
        raise ValueError("No tumour pixels found.")

    y_min = max(0, rows.min() - padding)
    y_max = min(mask.shape[0], rows.max() + padding + 1)

    x_min = max(0, cols.min() - padding)
    x_max = min(mask.shape[1], cols.max() + padding + 1)

    return y_min, y_max, x_min, x_max


# ============================================================
# Main preprocessing pipeline
# ============================================================

def main():

    print("=" * 60)
    print("CerebraQ MRI Preprocessing")
    print("=" * 60)

    patient_dir = DATASET_DIR / PATIENT_ID

    if not patient_dir.exists():
        raise FileNotFoundError(
            f"Patient directory not found:\n{patient_dir}"
        )

    print(f"\nPatient: {PATIENT_ID}")

    # --------------------------------------------------------
    # 1. Load MRI modalities
    # --------------------------------------------------------

    volumes = {}

    for modality, filename in MODALITIES.items():

        path = patient_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        print(f"Loading {modality}: {filename}")

        volumes[modality] = load_nifti(path)

        print(
            f"  Shape: {volumes[modality].shape}"
        )

    # --------------------------------------------------------
    # 2. Load segmentation
    # --------------------------------------------------------

    seg_path = patient_dir / SEGMENTATION_FILE

    if not seg_path.exists():
        raise FileNotFoundError(
            f"Missing segmentation: {seg_path}"
        )

    segmentation = load_nifti(seg_path)

    print(f"Segmentation shape: {segmentation.shape}")

    # --------------------------------------------------------
    # 3. Create tumour mask
    # --------------------------------------------------------

    tumor_mask = segmentation > 0

    total_tumor_voxels = int(tumor_mask.sum())

    print(
        f"Total tumour voxels: {total_tumor_voxels}"
    )

    if total_tumor_voxels == 0:
        raise ValueError("No tumour detected.")

    # --------------------------------------------------------
    # 4. Select slice with largest tumour area
    # --------------------------------------------------------

    slice_index, tumor_pixels = find_best_tumor_slice(
        segmentation
    )

    print(
        f"Selected axial slice: {slice_index}"
    )

    print(
        f"Tumour pixels on selected slice: "
        f"{tumor_pixels}"
    )

    # --------------------------------------------------------
    # 5. Extract selected slice
    # --------------------------------------------------------

    slices = {}

    for modality, volume in volumes.items():

        slices[modality] = volume[:, :, slice_index]

    seg_slice = segmentation[:, :, slice_index]

    tumor_slice = seg_slice > 0

    # --------------------------------------------------------
    # 6. Normalize MRI slices
    # --------------------------------------------------------

    normalized_slices = {}

    for modality, image in slices.items():

        normalized_slices[modality] = normalize_volume(
            image
        )

    # --------------------------------------------------------
    # 7. Find tumour bounding box
    # --------------------------------------------------------

    y_min, y_max, x_min, x_max = get_tumor_bbox(
        tumor_slice,
        padding=PADDING
    )

    print("\nTumour bounding box:")
    print(
        f"  Y: {y_min}:{y_max}"
    )
    print(
        f"  X: {x_min}:{x_max}"
    )

    # --------------------------------------------------------
    # 8. Crop tumour ROI
    # --------------------------------------------------------

    roi_images = {}

    for modality, image in normalized_slices.items():

        roi = image[
            y_min:y_max,
            x_min:x_max
        ]

        roi_images[modality] = resize_2d(
            roi,
            TARGET_SIZE
        )

    roi_mask = tumor_slice[
        y_min:y_max,
        x_min:x_max
    ]

    roi_mask = resize_mask(
        roi_mask,
        TARGET_SIZE
    )

    # --------------------------------------------------------
    # 9. Create 4-channel MRI tensor
    # --------------------------------------------------------

    # Channel order:
    # T1n, T1c, T2w, T2f

    image_tensor = np.stack(
        [
            roi_images["t1n"],
            roi_images["t1c"],
            roi_images["t2w"],
            roi_images["t2f"],
        ],
        axis=0
    ).astype(np.float32)

    roi_mask = (roi_mask > 0).astype(np.uint8)

    print("\nProcessed tensor shape:")
    print(
        f"  MRI: {image_tensor.shape}"
    )

    print(
        f"  Mask: {roi_mask.shape}"
    )

    # --------------------------------------------------------
    # 10. Save processed patient
    # --------------------------------------------------------

    patient_output = OUTPUT_DIR / PATIENT_ID

    patient_output.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = patient_output / "processed_roi.npz"

    np.savez_compressed(
        output_file,
        image=image_tensor,
        mask=roi_mask,
        slice_index=slice_index,
        tumor_pixels=tumor_pixels,
        total_tumor_voxels=total_tumor_voxels,
    )

    print(
        f"\nSaved processed data:"
    )

    print(output_file)

    # --------------------------------------------------------
    # 11. Create visualization
    # --------------------------------------------------------

    visualization_file = (
        patient_output / "preprocessing_preview.png"
    )

    fig, axes = plt.subplots(
        2,
        5,
        figsize=(16, 7)
    )

    modality_names = [
        "T1 Native",
        "T1 Contrast",
        "T2 Weighted",
        "FLAIR",
    ]

    modality_keys = [
        "t1n",
        "t1c",
        "t2w",
        "t2f",
    ]

    # Original MRI
    for i, (name, key) in enumerate(
        zip(modality_names, modality_keys)
    ):

        axes[0, i].imshow(
            slices[key].T,
            cmap="gray",
            origin="lower"
        )

        axes[0, i].set_title(
            f"Original - {name}"
        )

        axes[0, i].axis("off")

    # Original segmentation
    axes[0, 4].imshow(
        tumor_slice.T,
        cmap="gray",
        origin="lower"
    )

    axes[0, 4].set_title(
        "Tumour Mask"
    )

    axes[0, 4].axis("off")

    # Processed MRI
    for i, (name, key) in enumerate(
        zip(modality_names, modality_keys)
    ):

        axes[1, i].imshow(
            roi_images[key].T,
            cmap="gray",
            origin="lower"
        )

        axes[1, i].set_title(
            f"64×64 ROI - {name}"
        )

        axes[1, i].axis("off")

    # Processed mask
    axes[1, 4].imshow(
        roi_mask.T,
        cmap="gray",
        origin="lower"
    )

    axes[1, 4].set_title(
        "64×64 ROI Mask"
    )

    axes[1, 4].axis("off")

    fig.suptitle(
        f"CerebraQ Preprocessing — {PATIENT_ID}",
        fontsize=16
    )

    plt.tight_layout()

    plt.savefig(
        visualization_file,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved preprocessing preview:"
    )

    print(visualization_file)

    print("\n" + "=" * 60)
    print("Preprocessing completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()