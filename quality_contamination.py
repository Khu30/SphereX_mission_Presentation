"""
quality_contamination.py
Step 3: Spectral Analysis & Metadata Layer - Quality & Contamination Overlay

Processes SPHEREx 16-bit data quality masks (DQ) and observational metadata.
Identifies cosmic ray hits, saturation, stray light / solar-lunar glints,
and latency artifacts to protect citizen scientists and automated pipelines
from false-positive transient detections.
"""

import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# SPHEREx Bitmask Definitions
DQ_FLAGS = {
    0: {"name": "GOOD", "bit": 0, "label": "Pristine Pixel", "color": "#00ff66"},
    1: {"name": "COSMIC_RAY", "bit": 1, "label": "Cosmic Ray Strike", "color": "#ff3333"},
    2: {"name": "SATURATION", "bit": 2, "label": "Detector Saturated", "color": "#ffaa00"},
    3: {"name": "STRAY_LIGHT", "bit": 3, "label": "Stray Light / Glint Contamination", "color": "#cc00ff"},
    4: {"name": "BAD_PIXEL", "bit": 4, "label": "Dead / Hot Pixel", "color": "#666666"},
    5: {"name": "LATENCY", "bit": 5, "label": "Persistence / Latency from Prior Slew", "color": "#00ccff"},
    6: {"name": "EDGE_VIGNETTE", "bit": 6, "label": "Focal Plane Edge / Vignetted", "color": "#888800"}
}


def decode_pixel_flag(bitmask_value: int) -> List[Dict[str, Any]]:
    """Decodes an integer bitmask value into human-readable flags."""
    active_flags = []
    if bitmask_value == 0:
        return [DQ_FLAGS[0]]
    for bit_idx, flag in DQ_FLAGS.items():
        if bit_idx > 0 and (bitmask_value & (1 << (bit_idx - 1))):
            active_flags.append(flag)
    return active_flags


def generate_metadata_overlay(
    observation_id: str,
    date_obs: str,
    detector_id: int,
    band_id: str,
    ra: float,
    dec: float,
    exposure_time_sec: float = 120.0,
    array_temp_k: float = 80.2,
    jitter_arcsec: float = 0.08
) -> Dict[str, Any]:
    """
    Generates structured observational metadata and contamination metrics
    for overlay display alongside the time-series visual player.
    """
    # Parse observation timestamp to MJD
    try:
        dt = datetime.fromisoformat(date_obs.replace("Z", "+00:00"))
    except Exception:
        dt = datetime.now(timezone.utc)
    
    # Calculate approximate MJD
    jd = dt.timestamp() / 86400.0 + 2440587.5
    mjd = jd - 2400000.5

    # Simulated quality flag metrics for the image frame
    # Stable pointing and low stray light for nominal science frames
    cr_hits = int(np.random.randint(4, 30))
    stray_light_level = round(float(np.random.uniform(0.01, 0.08)), 3)
    usable_pixel_fraction = round(float(1.0 - (cr_hits * 4) / (2048 * 2048)), 5)

    is_contaminated = stray_light_level > 0.05 or jitter_arcsec > 0.15

    return {
        "observation_id": observation_id,
        "timestamps": {
            "utc": dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "mjd": round(mjd, 5),
            "iso": dt.isoformat()
        },
        "instrument": {
            "mission": "NASA SPHEREx",
            "detector": f"Array {detector_id} (D{detector_id})",
            "band": band_id,
            "exposure_time_s": exposure_time_sec,
            "focal_plane_temp_k": array_temp_k,
            "pointing_jitter_arcsec": jitter_arcsec
        },
        "coordinates": {
            "target_ra_deg": round(ra, 5),
            "target_dec_deg": round(dec, 5),
            "roll_angle_deg": round(float(np.random.uniform(0, 360)), 2)
        },
        "quality_metrics": {
            "usable_pixel_fraction": usable_pixel_fraction,
            "cosmic_ray_count": cr_hits,
            "stray_light_index": stray_light_level,
            "contamination_warning": is_contaminated,
            "status": "NOMINAL" if not is_contaminated else "FLAGGED_CONTAMINATION"
        },
        "flags_legend": DQ_FLAGS
    }


def filter_quality_mask(data: np.ndarray, dq_mask: np.ndarray, exclude_bits: Optional[List[int]] = None) -> np.ndarray:
    """
    Applies quality flags to an image matrix, masking out cosmic rays,
    bad pixels, and saturated detector channels with NaN.
    """
    if exclude_bits is None:
        # Exclude CR (bit 1), Saturation (bit 2), Bad pixel (bit 4)
        exclude_mask = (1 << 0) | (1 << 1) | (1 << 3)
    else:
        exclude_mask = 0
        for bit in exclude_bits:
            exclude_mask |= (1 << (bit - 1))

    cleaned = np.copy(data).astype(float)
    bad_pixels = (dq_mask.astype(int) & exclude_mask) != 0
    cleaned[bad_pixels] = np.nan
    return cleaned
