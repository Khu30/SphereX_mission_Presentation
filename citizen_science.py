"""
citizen_science.py
Step 4: Multi-Mission Data Overlays - Citizen Science Discovery Support

Provides automated candidate classification, reference markers, and false-positive
rejection to empower citizen scientists and volunteers searching for:
- Planet X / Trans-Neptunian Objects (TNOs)
- Undiscovered ultra-cold Brown Dwarfs (Y/T spectral types)
- Fast Proper-Motion Stars
- Variable & Transient sources

Cross-checks candidate coordinates against Gaia DR3 and WISE archives to verify
whether a detected shifting source is a novel discovery or a known cataloged object.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from cross_catalog import query_cross_catalogs


# Known reference classes
MARKER_CLASSES = {
    "KNOWN_STAR": {"label": "Known Cataloged Star", "color": "#4da6ff", "shape": "circle"},
    "BROWN_DWARF": {"label": "Known Brown Dwarf", "color": "#ff9933", "shape": "diamond"},
    "COMET_ASTEROID": {"label": "Known Minor Planet / Comet", "color": "#00ffcc", "shape": "triangle"},
    "CANDIDATE_PLANET_X": {"label": "Candidate Planet X / TNO", "color": "#ff00ff", "shape": "cross"},
    "CANDIDATE_BROWN_DWARF": {"label": "Candidate Cold Brown Dwarf", "color": "#ff3366", "shape": "star"},
    "TRANSIENT_VARIABLE": {"label": "Variable / Eruptive Transient", "color": "#ffff00", "shape": "square"},
    "SUSPECTED_ARTIFACT": {"label": "False Positive / Cosmic Ray", "color": "#888888", "shape": "x"}
}


def evaluate_discovery_candidate(
    ra: float,
    dec: float,
    epoch1_flux: float,
    epoch2_flux: float,
    shift_arcsec: float,
    time_delta_years: float = 0.5,
    w1_minus_w2: Optional[float] = None
) -> Dict[str, Any]:
    """
    Evaluates a user-flagged moving or variable source.
    Cross-checks with Gaia and WISE to classify the candidate.
    """
    cross_res = query_cross_catalogs(ra, dec, radius_arcmin=0.3)
    closest_match = None
    min_dist = 999.0

    for src in cross_res.get("sources", []):
        dist = src.get("distance_arcsec", 999.0)
        if dist < min_dist:
            min_dist = dist
            closest_match = src

    proper_motion_mas_yr = (shift_arcsec * 1000.0) / max(time_delta_years, 0.01)
    flux_ratio = (epoch2_flux / max(epoch1_flux, 0.001)) if epoch1_flux > 0 else 1.0

    # Decision logic
    if min_dist < 1.0 and closest_match:
        # Matches a known catalog source
        if "Brown Dwarf" in closest_match.get("object_class", ""):
            classification = "BROWN_DWARF"
            confidence = "VERIFIED_KNOWN"
            notes = f"Matches cataloged brown dwarf {closest_match['source_id']} within {min_dist} arcsec."
        elif "T Tauri" in closest_match.get("object_class", "") or "Mira" in closest_match.get("object_class", ""):
            classification = "TRANSIENT_VARIABLE"
            confidence = "VERIFIED_KNOWN"
            notes = f"Matches known variable star {closest_match['source_id']} (flux ratio {flux_ratio:.2f})."
        else:
            classification = "KNOWN_STAR"
            confidence = "VERIFIED_KNOWN"
            notes = f"Matches known Gaia star {closest_match['source_id']} with parallax {closest_match['gaia'].get('parallax_mas', 'N/A')} mas."
    else:
        # NO close match in Gaia optical catalog!
        if shift_arcsec > 5.0 and time_delta_years <= 0.5:
            # Extreme shift in 6 months -> Solar system object or Planet X
            classification = "CANDIDATE_PLANET_X"
            confidence = "HIGH_PRIORITY_CANDIDATE"
            notes = f"High proper motion ({proper_motion_mas_yr:.0f} mas/yr) with no optical Gaia counterpart. Consistent with distant outer solar system body or Planet X!"
        elif proper_motion_mas_yr > 800.0 or (w1_minus_w2 is not None and w1_minus_w2 > 1.5):
            # Fast infrared mover or very red WISE color
            classification = "CANDIDATE_BROWN_DWARF"
            confidence = "HIGH_PRIORITY_CANDIDATE"
            notes = f"Significant proper motion ({proper_motion_mas_yr:.0f} mas/yr) and red infrared colors. Strong ultra-cold sub-stellar brown dwarf candidate."
        elif abs(epoch2_flux - epoch1_flux) / max(epoch1_flux, 1.0) > 2.0:
            classification = "TRANSIENT_VARIABLE"
            confidence = "INTERESTING_VARIABLE"
            notes = f"Brightness variation of {flux_ratio:.2f}x detected between 6-month SPHEREx mapping cycles."
        else:
            classification = "SUSPECTED_ARTIFACT"
            confidence = "UNCONFIRMED"
            notes = "Uncertain signal. Check quality mask flags for cosmic rays or stray light contamination."

    marker_info = MARKER_CLASSES.get(classification, MARKER_CLASSES["KNOWN_STAR"])

    return {
        "candidate_id": f"SPX-CS-{int(datetime.now(timezone.utc).timestamp())}",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "coordinates": {"ra": round(ra, 6), "dec": round(dec, 6)},
        "classification": classification,
        "marker_display": marker_info,
        "confidence": confidence,
        "metrics": {
            "apparent_shift_arcsec": round(shift_arcsec, 3),
            "proper_motion_mas_yr": round(proper_motion_mas_yr, 1),
            "flux_epoch1": epoch1_flux,
            "flux_epoch2": epoch2_flux,
            "flux_ratio": round(flux_ratio, 3),
            "nearest_catalog_dist_arcsec": round(min_dist, 2)
        },
        "scientific_summary": notes,
        "nearest_cross_match": closest_match
    }


def create_candidate_report(
    candidate_id: str,
    volunteer_name: str,
    ra: float,
    dec: float,
    category: str,
    notes: str
) -> Dict[str, Any]:
    """Formats an official citizen science candidate discovery report for export."""
    return {
        "report_id": f"NASA-SPHEREx-DISCOVERY-{candidate_id}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "submitter": volunteer_name.strip() or "Anonymous Citizen Astronomer",
        "target_coordinates": {"ra": ra, "dec": dec},
        "assigned_category": category,
        "volunteer_notes": notes,
        "status": "QUEUED_FOR_EXPERT_REVIEW",
        "recommended_followup": [
            "Cross-verify with SPHEREx subsequent 6-month data release",
            "Target with Keck/JWST NIRSpec spectroscopy",
            "Check Minor Planet Center (MPC) orbit database"
        ]
    }
