"""
spectral_bands.py
Step 3: Spectral Analysis & Metadata Layer - 102-Band Near-Infrared Handling

NASA's SPHEREx mission maps the entire sky every six months across 102 near-infrared
spectral channels (spanning 0.75 um to 5.00 um) utilizing six distinct detector arrays.

Detector Arrays & Wavelength Ranges:
- Array 1 (D1): 0.75 - 1.11 um (Bands 1 - 17, R ~ 41)
- Array 2 (D2): 1.11 - 1.64 um (Bands 18 - 34, R ~ 41)
- Array 3 (D3): 1.64 - 2.42 um (Bands 35 - 51, R ~ 41)
- Array 4 (D4): 2.42 - 3.82 um (Bands 52 - 68, R ~ 35)
- Array 5 (D5): 3.82 - 4.42 um (Bands 69 - 85, R ~ 130)
- Array 6 (D6): 4.42 - 5.00 um (Bands 86 - 102, R ~ 130)

Key Molecular Features:
- Water (H2O) Ice & Vapor: 1.4 um, 1.9 um, 3.05 um
- Carbon Dioxide (CO2) Ice & Gas: 4.27 um
- Carbon Monoxide (CO): 4.67 um
- Methane (CH4): 1.66 um, 2.3 um, 3.3 um
- Hydrogen Paschen/Brackett & PAH: 1.28 um, 3.3 um
"""

import numpy as np
from typing import Dict, List, Any, Optional

# Define the 6 SPHEREx detector arrays configuration
DETECTOR_ARRAYS = {
    1: {"name": "Array 1 (D1)", "bands": (1, 17), "wave_min": 0.75, "wave_max": 1.11, "res": 41},
    2: {"name": "Array 2 (D2)", "bands": (18, 34), "wave_min": 1.11, "wave_max": 1.64, "res": 41},
    3: {"name": "Array 3 (D3)", "bands": (35, 51), "wave_min": 1.64, "wave_max": 2.42, "res": 41},
    4: {"name": "Array 4 (D4)", "bands": (52, 68), "wave_min": 2.42, "wave_max": 3.82, "res": 35},
    5: {"name": "Array 5 (D5)", "bands": (69, 85), "wave_min": 3.82, "wave_max": 4.42, "res": 130},
    6: {"name": "Array 6 (D6)", "bands": (86, 102), "wave_min": 4.42, "wave_max": 5.00, "res": 130},
}

# Critical molecular and atomic tracers mapped by SPHEREx
MOLECULAR_TRACERS = {
    "H2O_ICE": {
        "label": "Water Ice (H2O)",
        "center_um": 3.05,
        "width_um": 0.35,
        "description": "Crucial for identifying icy volatile coatings on interstellar grains and sub-stellar brown dwarfs.",
        "target_arrays": [4]
    },
    "CO2_ICE": {
        "label": "Carbon Dioxide Ice/Gas (CO2)",
        "center_um": 4.27,
        "width_um": 0.12,
        "description": "Key tracer of biogenic / volatile ice abundance and planetary atmospheres.",
        "target_arrays": [5]
    },
    "CO_GAS": {
        "label": "Carbon Monoxide (CO)",
        "center_um": 4.67,
        "width_um": 0.15,
        "description": "Diagnostic absorption in stellar/brown dwarf atmospheres and circumstellar disks.",
        "target_arrays": [6]
    },
    "CH4_METHANE": {
        "label": "Methane (CH4)",
        "center_um": 3.32,
        "width_um": 0.20,
        "description": "Hallmark absorption band for T and Y-type brown dwarfs such as WISE 0855 and Epsilon Indi B.",
        "target_arrays": [4]
    },
    "PAH_3_3": {
        "label": "PAH Emission Feature",
        "center_um": 3.30,
        "width_um": 0.08,
        "description": "Polycyclic Aromatic Hydrocarbons marking star formation and interstellar matter.",
        "target_arrays": [4]
    }
}


def generate_spherex_band_table() -> List[Dict[str, Any]]:
    """
    Constructs the full 102-band metadata table with central wavelengths,
    bandwidths, detector array assignments, and sensitivity targets.
    """
    bands = []
    for array_id, info in DETECTOR_ARRAYS.items():
        b_start, b_end = info["bands"]
        num_bands = b_end - b_start + 1
        wavelengths = np.linspace(info["wave_min"], info["wave_max"], num_bands)
        d_wave = (info["wave_max"] - info["wave_min"]) / num_bands

        for idx, (b_num, wave) in enumerate(zip(range(b_start, b_end + 1), wavelengths)):
            # Check molecular association
            associated_tracers = []
            for tracer_key, tracer in MOLECULAR_TRACERS.items():
                if abs(wave - tracer["center_um"]) <= (tracer["width_um"] / 2.0):
                    associated_tracers.append(tracer_key)

            bands.append({
                "band_number": int(b_num),
                "band_id": f"SPHEREx_B{b_num:03d}",
                "array_id": int(array_id),
                "array_name": info["name"],
                "center_wavelength_um": round(float(wave), 4),
                "bandwidth_um": round(float(d_wave), 4),
                "resolving_power": info["res"],
                "tracers": associated_tracers
            })
    return bands


SPHEREX_BANDS = generate_spherex_band_table()


def get_bands_by_tracer(tracer_name: str) -> List[Dict[str, Any]]:
    """Filter SPHEREx bands uniquely sensitive to a specific molecular tracer."""
    tracer_name = tracer_name.upper()
    return [b for b in SPHEREX_BANDS if tracer_name in b["tracers"]]


def get_bands_by_array(array_id: int) -> List[Dict[str, Any]]:
    """Retrieve all spectral bands corresponding to a specific detector array (1 to 6)."""
    return [b for b in SPHEREX_BANDS if b["array_id"] == array_id]


def filter_bands_by_range(min_wave_um: float, max_wave_um: float) -> List[Dict[str, Any]]:
    """Retrieve all SPHEREx channels within an arbitrary wavelength window [um]."""
    return [
        b for b in SPHEREX_BANDS 
        if (b["center_wavelength_um"] >= min_wave_um and b["center_wavelength_um"] <= max_wave_um)
    ]


def group_bands_for_color_composite(red_feature="CO2_ICE", green_feature="H2O_ICE", blue_feature="CONTINUUM_OPTICAL"):
    """
    Selects optimal band sets for false-color RGB near-infrared rendering
    highlighting volatile ice and molecular absorption.
    """
    def find_best_band(center_um):
        return min(SPHEREX_BANDS, key=lambda b: abs(b["center_wavelength_um"] - center_um))

    r_band = find_best_band(4.27)  # CO2 / Red channel
    g_band = find_best_band(3.05)  # H2O / Green channel
    b_band = find_best_band(1.25)  # Near-IR Continuum / Blue channel

    return {
        "red": r_band,
        "green": g_band,
        "blue": b_band,
        "description": "RGB false-color composite targeting CO2 (Red), H2O Ice (Green), and Stellar Continuum (Blue)"
    }
