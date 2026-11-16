"""
epoch_arithmetic.py
Step 2: Time-Series Visualizer & Interactive Controls - Epoch Image Arithmetic

Provides matrix addition, subtraction (difference imaging), and blink comparison
between different SPHEREx observation dates to isolate faint moving objects
(Planet X candidates, brown dwarfs, comets) and transient variable stars
against static background celestial stars.
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional


def normalize_background(image: np.ndarray, clip_percentile: float = 99.5) -> np.ndarray:
    """Normalizes an image array using robust median background subtraction."""
    valid_vals = image[np.isfinite(image)]
    if len(valid_vals) == 0:
        return image
    median_bg = np.median(valid_vals)
    scale = np.percentile(valid_vals, clip_percentile) - median_bg
    if scale <= 0:
        scale = 1.0
    return (image - median_bg) / scale


def subtract_epochs(
    epoch_early: np.ndarray,
    epoch_late: np.ndarray,
    normalize: bool = True,
    threshold_sigma: float = 3.5
) -> Dict[str, Any]:
    """
    Computes difference imaging: Delta_I = I_late - I_early.
    Static stars cancel out to near zero.
    Moving objects and variable sources produce prominent dipolar or positive residual signals.
    """
    img1 = np.asarray(epoch_early, dtype=float)
    img2 = np.asarray(epoch_late, dtype=float)

    if img1.shape != img2.shape:
        raise ValueError(f"Shape mismatch: {img1.shape} vs {img2.shape}")

    if normalize:
        img1_norm = normalize_background(img1)
        img2_norm = normalize_background(img2)
    else:
        img1_norm = img1
        img2_norm = img2

    diff_image = img2_norm - img1_norm

    # Robust statistics for thresholding
    valid_diff = diff_image[np.isfinite(diff_image)]
    if len(valid_diff) > 0:
        median = float(np.median(valid_diff))
        std = float(np.std(valid_diff))
    else:
        median, std = 0.0, 1.0

    threshold = median + threshold_sigma * std
    significant_residuals = np.abs(diff_image) > threshold

    return {
        "status": "success",
        "operation": "subtraction",
        "diff_matrix": diff_image.tolist() if diff_image.size < 10000 else None,
        "mean_residual": round(float(np.nanmean(diff_image)), 5),
        "std_residual": round(std, 5),
        "positive_transient_count": int(np.sum(diff_image > threshold)),
        "negative_transient_count": int(np.sum(diff_image < -threshold)),
        "threshold_value": round(float(threshold), 5)
    }


def add_epochs(
    epoch_early: np.ndarray,
    epoch_late: np.ndarray
) -> Dict[str, Any]:
    """
    Sums image epochs to maximize signal-to-noise for ultra-faint stationary objects.
    """
    img1 = np.asarray(epoch_early, dtype=float)
    img2 = np.asarray(epoch_late, dtype=float)
    sum_image = img1 + img2

    return {
        "status": "success",
        "operation": "addition",
        "combined_matrix": sum_image.tolist() if sum_image.size < 10000 else None,
        "max_flux": round(float(np.nanmax(sum_image)), 3),
        "mean_flux": round(float(np.nanmean(sum_image)), 3)
    }


def simulate_epoch_pair_difference(target_type: str = "moving_object", size: int = 64) -> Dict[str, Any]:
    """
    Generates synthetic realistic sequential observation frames demonstrating
    epoch arithmetic for the interactive web visualizer.
    """
    np.random.seed(42)
    # Background sky noise
    epoch1 = np.random.normal(10.0, 1.2, (size, size))
    epoch2 = np.random.normal(10.0, 1.2, (size, size))

    # Stationary background stars
    num_stars = 8
    star_positions = [(np.random.randint(5, size - 5), np.random.randint(5, size - 5)) for _ in range(num_stars)]
    for y, x in star_positions:
        flux = np.random.uniform(50.0, 200.0)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                dist_sq = dy**2 + dx**2
                profile = flux * np.exp(-dist_sq / 1.5)
                epoch1[y + dy, x + dx] += profile
                epoch2[y + dy, x + dx] += profile

    # Inject target behavior
    if target_type == "moving_object":
        # Planet X or Brown Dwarf shifts by 10 pixels between Epoch 1 and Epoch 2
        p1 = (size // 2 - 5, size // 2 - 5)
        p2 = (size // 2 + 5, size // 2 + 5)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                profile = 120.0 * np.exp(-(dy**2 + dx**2) / 1.5)
                epoch1[p1[0] + dy, p1[1] + dx] += profile
                epoch2[p2[0] + dy, p2[1] + dx] += profile
        note = "Moving celestial object shifts +10 px; stationary stars cancel out perfectly in difference imaging."
    elif target_type == "variable_star":
        # Star brightens dramatically between Epoch 1 and 2
        p = (size // 2, size // 2)
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                epoch1[p[0] + dy, p[1] + dx] += 40.0 * np.exp(-(dy**2 + dx**2) / 1.5)
                epoch2[p[0] + dy, p[1] + dx] += 250.0 * np.exp(-(dy**2 + dx**2) / 1.5)
        note = "Variable star brightens from 40 to 250 counts, showing strong positive peak in difference image."
    else:
        note = "Nominal stationary field."

    diff_result = subtract_epochs(epoch1, epoch2, normalize=False)
    
    return {
        "target_type": target_type,
        "note": note,
        "epoch1_shape": epoch1.shape,
        "epoch2_shape": epoch2.shape,
        "epoch1_slice": epoch1[:8, :8].round(2).tolist(),
        "epoch2_slice": epoch2[:8, :8].round(2).tolist(),
        "diff_metrics": {
            "transients_detected": diff_result["positive_transient_count"],
            "threshold": diff_result["threshold_value"],
            "mean_residual": diff_result["mean_residual"]
        }
    }
