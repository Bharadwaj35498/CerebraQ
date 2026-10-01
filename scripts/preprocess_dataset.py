from pathlib import Path
import sys

import nibabel as nib
import numpy as np
from scipy.ndimage import zoom


# ============================================================
# CerebraQ - Batch MRI Preprocessing
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

TARGET_SIZE = (64, 64)
PADDING = 10

MODALITIES = {
    "t1n": "t1n",
    "t1c": "t1c",
    "t2w": "t2w",
    "t2f": "t2f",
}


# ============================================================
# Utility functions
# ============================================================

def load_nifti(path):
    """Load a NIfTI volume as float32."""
    return nib.load(str(path)).get_fdata().astype(np.float32)


def normalize_volume(volume):
    """
    Z-score normalize non-zero voxels.
    Background remains zero.
    """
    mask = volume != 0

    normalized = np.zeros_like(volume, dtype=np.float32)

    if not np.any(mask):
        return normalized

    values = volume[mask]

    mean = values.mean()
    std = values.std()

    if std > 0:
        normalized[mask] = (values - mean) / std
    else:
        normalized[mask] = values - mean

    return normalized


def resize_2d(image):
    """Resize a 2D MRI image to 64x64."""
    zoom_factors = (
        TARGET_SIZE[0] / image.shape[0],
        TARGET_SIZE[1] / image.shape[1],
    )

    return zoom(
        image,
        zoom_factors,
        order=1
    ).astype(np.float32)


def resize_mask(mask):
    """Resize a binary mask using nearest-neighbour interpolation."""
    zoom_factors = (
        TARGET_SIZE[0] / mask.shape[0],
        TARGET_SIZE[1] / mask.shape[1],
    )

    return zoom(
        mask,
        zoom_factors,
        order=0
    ).astype(np.uint8)


def find_best_tumor_slice(segmentation):
    """Find the axial slice with the largest tumour area."""
    tumor_mask = segmentation > 0

    pixels_per_slice = tumor_mask.sum(axis=(0, 1))

    best_slice = int(np.argmax(pixels_per_slice))

    return best_slice, int(pixels_per_slice[best_slice])


def get_tumor_bbox(mask):
    """Get tumour bounding box with padding."""
    rows, cols = np.where(mask)

    if len(rows) == 0:
        return None

    y_min = max(0, int(rows.min()) - PADDING)
    y_max = min(mask.shape[0], int(rows.max()) + PADDING + 1)

    x_min = max(0, int(cols.min()) - PADDING)
    x_max = min(mask.shape[1], int(cols.max()) + PADDING + 1)

    return y_min, y_max, x_min, x_max


# ============================================================
# Process one patient
# ============================================================

def process_patient(patient_dir):

    patient_id = patient_dir.name

    output_dir = OUTPUT_DIR / patient_id
    output_file = output_dir / "processed_roi.npz"

    # Skip already processed patients
    if output_file.exists():
        return "skipped", patient_id, "Already processed"

    # --------------------------------------------------------
    # Load modalities
    # --------------------------------------------------------

    volumes = {}

    for modality, suffix in MODALITIES.items():

        path = patient_dir / f"{patient_id}-{suffix}.nii.gz"

        if not path.exists():
            raise FileNotFoundError(
                f"Missing {modality}: {path.name}"
            )

        volumes[modality] = load_nifti(path)

    # --------------------------------------------------------
    # Load segmentation
    # --------------------------------------------------------

    seg_path = patient_dir / f"{patient_id}-seg.nii.gz"

    if not seg_path.exists():
        raise FileNotFoundError(
            f"Missing segmentation: {seg_path.name}"
        )

    segmentation = load_nifti(seg_path)

    # --------------------------------------------------------
    # Tumour mask
    # --------------------------------------------------------

    tumor_mask = segmentation > 0

    total_tumor_voxels = int(tumor_mask.sum())

    if total_tumor_voxels == 0:
        return "skipped", patient_id, "No tumour voxels"

    # --------------------------------------------------------
    # Select slice with largest tumour area
    # --------------------------------------------------------

    slice_index, tumor_pixels = find_best_tumor_slice(
        segmentation
    )

    # --------------------------------------------------------
    # Extract selected slice
    # --------------------------------------------------------

    modality_slices = {
        modality: volume[:, :, slice_index]
        for modality, volume in volumes.items()
    }

    segmentation_slice = segmentation[:, :, slice_index]

    tumor_slice = segmentation_slice > 0

    # --------------------------------------------------------
    # Find tumour bounding box
    # --------------------------------------------------------

    bbox = get_tumor_bbox(tumor_slice)

    if bbox is None:
        return "skipped", patient_id, "No tumour on selected slice"

    y_min, y_max, x_min, x_max = bbox

    # --------------------------------------------------------
    # Normalize and crop
    # --------------------------------------------------------

    processed_channels = []

    for modality in ["t1n", "t1c", "t2w", "t2f"]:

        normalized = normalize_volume(
            modality_slices[modality]
        )

        roi = normalized[
            y_min:y_max,
            x_min:x_max
        ]

        roi = resize_2d(roi)

        processed_channels.append(roi)

    # --------------------------------------------------------
    # Create 4-channel tensor
    # --------------------------------------------------------

    image_tensor = np.stack(
        processed_channels,
        axis=0
    ).astype(np.float32)

    # --------------------------------------------------------
    # Process tumour mask
    # --------------------------------------------------------

    roi_mask = tumor_slice[
        y_min:y_max,
        x_min:x_max
    ]

    roi_mask = resize_mask(roi_mask)

    roi_mask = (roi_mask > 0).astype(np.uint8)

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    np.savez_compressed(
        output_file,
        image=image_tensor,
        mask=roi_mask,
        slice_index=slice_index,
        tumor_pixels=tumor_pixels,
        total_tumor_voxels=total_tumor_voxels,
        bbox=np.array(
            [y_min, y_max, x_min, x_max],
            dtype=np.int32
        ),
    )

    return "processed", patient_id, ""


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("CerebraQ - Batch MRI Preprocessing")
    print("=" * 70)

    if not DATASET_DIR.exists():
        print("\nERROR: Dataset directory not found:")
        print(DATASET_DIR)
        sys.exit(1)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    patient_dirs = sorted(
        [
            path
            for path in DATASET_DIR.iterdir()
            if path.is_dir()
        ]
    )

    total = len(patient_dirs)

    print(f"\nDataset: {DATASET_DIR}")
    print(f"Patients found: {total}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Target ROI: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
    print(f"Channels: T1n, T1c, T2w, T2f")

    if total == 0:
        print("\nNo patient folders found.")
        sys.exit(1)

    processed = 0
    skipped = 0
    failed = 0

    failed_patients = []

    print("\nStarting preprocessing...\n")

    for index, patient_dir in enumerate(
        patient_dirs,
        start=1
    ):

        patient_id = patient_dir.name

        try:

            status, patient_id, message = process_patient(
                patient_dir
            )

            if status == "processed":
                processed += 1
                status_text = "PROCESSED"

            else:
                skipped += 1
                status_text = "SKIPPED"

            print(
                f"[{index:04d}/{total:04d}] "
                f"{patient_id:<25} "
                f"{status_text}"
                + (f" - {message}" if message else "")
            )

        except Exception as error:

            failed += 1

            failed_patients.append(
                (patient_id, str(error))
            )

            print(
                f"[{index:04d}/{total:04d}] "
                f"{patient_id:<25} "
                f"FAILED - {error}"
            )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("PREPROCESSING SUMMARY")
    print("=" * 70)

    print(f"Total patients : {total}")
    print(f"Processed      : {processed}")
    print(f"Skipped        : {skipped}")
    print(f"Failed         : {failed}")

    if failed_patients:

        print("\nFailed patients:")

        for patient_id, error in failed_patients:
            print(f"  {patient_id}: {error}")

    print("\nOutput directory:")
    print(OUTPUT_DIR)

    print("\n" + "=" * 70)
    print("Batch preprocessing finished.")
    print("=" * 70)


if __name__ == "__main__":
    main()