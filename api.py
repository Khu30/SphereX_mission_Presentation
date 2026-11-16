"""
api.py
NASA Space Apps Hackathon - Planet X & SPHEREx Integrated Web API
Unifies all 5 challenge pipeline steps:
- Step 1: Data Ingestion & Query Architecture (Coordinates, SIA2 releases, Co-adding)
- Step 2: Time-Series Visualizer & Interactive Controls (Epochs, Blinker, Arithmetic)
- Step 3: Spectral Analysis & Metadata Layer (102 NIR bands, On-the-fly SED, Quality Flags)
- Step 4: Multi-Mission Data Overlays (WISE & Gaia catalogs, Citizen Science Discovery)
- Step 5: Verification & Target Benchmark Suite (Barnard's Star, eps Indi B, WISE 0855, RW Aur, R Dra)
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Project Modules
from coordinate import validate_coordinates
from qr4 import load_releases
from spectral_bands import (
    SPHEREX_BANDS,
    MOLECULAR_TRACERS,
    get_bands_by_tracer,
    get_bands_by_array,
    filter_bands_by_range,
    group_bands_for_color_composite
)
from spectra_generator import generate_object_spectrum
from quality_contamination import generate_metadata_overlay, decode_pixel_flag, DQ_FLAGS
from epoch_arithmetic import subtract_epochs, add_epochs, simulate_epoch_pair_difference
from cross_catalog import query_cross_catalogs, CATALOG_BENCHMARKS
from citizen_science import evaluate_discovery_candidate, create_candidate_report, MARKER_CLASSES
from benchmark_suite import BENCHMARK_TARGETS, run_full_benchmark_suite, verify_barnards_star, verify_epsilon_indi_b, verify_wise_0855, verify_rw_aurigae, verify_r_draconis

app = FastAPI(
    title="NASA SPHEREx Planet X Explorer API",
    description="Backend API powering the public-facing SPHEREx time-series and spectral analysis web tool.",
    version="2.0.0"
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


# =====================================================================
# STEP 1: Coordinate & Query Architecture
# =====================================================================

@app.get("/api/coordinates/validate")
async def api_validate_coords(ra: str, dec: str, unit: str = "deg"):
    """Accepts RA & Dec in degrees or HMS/DMS sexagesimal, returns standardized ICRS degrees."""
    result = validate_coordinates(ra, dec, unit=unit)
    if not result.get("valid"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result


@app.get("/api/releases")
async def api_get_releases():
    """Returns currently available SPHEREx data releases and collections."""
    try:
        active = load_releases()
        return {"status": "success", "active_collections": active}
    except Exception as e:
        return {"status": "fallback", "active_collections": ["spherex_dr1", "spherex_qr3"]}


@app.get("/api/observations")
async def api_get_observations(
    ra: float = Query(..., ge=0.0, lt=360.0, description="Right Ascension in degrees"),
    dec: float = Query(..., ge=-90.0, le=90.0, description="Declination in degrees"),
    fov: float = Query(default=0.5, gt=0.0, le=15.0, description="Field of View in degrees"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Core sky query interface supporting direct URL parameters (?ra=...&dec=...&fov=...)
    for seamless bookmarking and external linking.
    """
    epochs = [
        {"epoch_id": 1, "cycle": "Survey Cycle 1", "date": "2025-06-15", "release": "DR1"},
        {"epoch_id": 2, "cycle": "Survey Cycle 2", "date": "2025-12-15", "release": "DR1"},
        {"epoch_id": 3, "cycle": "Survey Cycle 3", "date": "2026-06-15", "release": "DR2"}
    ]
    return {
        "status": "success",
        "coordinates": {"ra": ra, "dec": dec},
        "fov_deg": fov,
        "available_epochs": epochs,
        "total_epochs": len(epochs),
        "total_bands": 102,
        "detectors": ["Array 1", "Array 2", "Array 3", "Array 4", "Array 5", "Array 6"]
    }


# =====================================================================
# STEP 2: Time-Series Visualizer & Epoch Arithmetic
# =====================================================================

@app.get("/api/timeseries/epochs")
async def api_get_timeseries_epochs(ra: float, dec: float):
    """Provides time-series observation frames for the looping video and blink player."""
    return {
        "status": "success",
        "ra": ra,
        "dec": dec,
        "epochs": [
            {
                "epoch_index": 0,
                "label": "2025-06 (Cycle 1)",
                "date": "2025-06-15T12:00:00Z",
                "mjd": 60841.5,
                "exposure_sec": 120
            },
            {
                "epoch_index": 1,
                "label": "2025-12 (Cycle 2)",
                "date": "2025-12-15T12:00:00Z",
                "mjd": 61024.5,
                "exposure_sec": 120
            },
            {
                "epoch_index": 2,
                "label": "2026-06 (Cycle 3)",
                "date": "2026-06-15T12:00:00Z",
                "mjd": 61207.5,
                "exposure_sec": 120
            }
        ]
    }


@app.get("/api/epoch/arithmetic/simulate")
async def api_simulate_epoch_arithmetic(target_type: str = Query("moving_object", enum=["moving_object", "variable_star", "nominal_field"])):
    """Simulates epoch difference imaging (Epoch2 - Epoch1) to demonstrate transient and moving object isolation."""
    result = simulate_epoch_pair_difference(target_type=target_type, size=64)
    return result


# =====================================================================
# STEP 3: Spectral Analysis & Metadata Layer
# =====================================================================

@app.get("/api/spectral/bands")
async def api_get_spectral_bands(
    array_id: Optional[int] = Query(None, ge=1, le=6),
    tracer: Optional[str] = None
):
    """Retrieves SPHEREx's 102 spectral channels with filtering by detector array or molecular tracer."""
    if tracer:
        return {"status": "success", "filter": f"tracer:{tracer}", "bands": get_bands_by_tracer(tracer)}
    if array_id:
        return {"status": "success", "filter": f"array:{array_id}", "bands": get_bands_by_array(array_id)}
    return {"status": "success", "total_bands": len(SPHEREX_BANDS), "bands": SPHEREX_BANDS}


@app.get("/api/spectral/tracers")
async def api_get_tracers():
    """Lists key diagnostic molecular absorption and emission features (H2O, CO2, CO, CH4, PAH)."""
    return {"status": "success", "tracers": MOLECULAR_TRACERS}


@app.get("/api/spectral/composite-plan")
async def api_get_composite_plan():
    """Provides recommended 3-band false-color RGB grouping for molecular discovery."""
    return group_bands_for_color_composite()


@app.get("/api/spectral/spectrum")
async def api_get_object_spectrum(
    ra: float = Query(...),
    dec: float = Query(...),
    object_type: str = Query("auto", description="auto, wise0855, eps_indi, barnard, rw_aur, r_dra, planet_x")
):
    """On-the-fly spectra extraction across all 102 NIR bands with molecular absorption detection."""
    spec = generate_object_spectrum(ra, dec, object_type=object_type)
    return spec


@app.get("/api/metadata/overlay")
async def api_get_metadata_overlay(
    ra: float = Query(...),
    dec: float = Query(...),
    observation_id: str = Query("SPX-OBS-2025-001"),
    detector_id: int = Query(1, ge=1, le=6),
    band_id: str = Query("SPHEREx_B024")
):
    """Provides observational metadata, timestamps, pointing jitter, and 16-bit quality contamination metrics."""
    return generate_metadata_overlay(
        observation_id=observation_id,
        date_obs="2025-07-15T14:32:00Z",
        detector_id=detector_id,
        band_id=band_id,
        ra=ra,
        dec=dec
    )


# =====================================================================
# STEP 4: Multi-Mission Data Overlays & Citizen Science
# =====================================================================

@app.get("/api/catalogs/cross-match")
async def api_cross_catalog(
    ra: float = Query(...),
    dec: float = Query(...),
    radius_arcmin: float = Query(5.0, gt=0, le=30.0)
):
    """Retrieves cross-catalog overlays from WISE (W1-W4) and Gaia (DR3 proper motions & parallaxes)."""
    return query_cross_catalogs(ra, dec, radius_arcmin=radius_arcmin)


class CandidateEvalRequest(BaseModel):
    ra: float
    dec: float
    epoch1_flux: float
    epoch2_flux: float
    shift_arcsec: float
    time_delta_years: float = 0.5
    w1_minus_w2: Optional[float] = None


@app.post("/api/citizen-science/evaluate")
async def api_evaluate_candidate(req: CandidateEvalRequest):
    """Automated evaluation of volunteer-flagged anomalies (Planet X candidate vs Brown Dwarf vs Known Star)."""
    eval_result = evaluate_discovery_candidate(
        ra=req.ra,
        dec=req.dec,
        epoch1_flux=req.epoch1_flux,
        epoch2_flux=req.epoch2_flux,
        shift_arcsec=req.shift_arcsec,
        time_delta_years=req.time_delta_years,
        w1_minus_w2=req.w1_minus_w2
    )
    return eval_result


class CandidateReportRequest(BaseModel):
    candidate_id: str
    volunteer_name: str
    ra: float
    dec: float
    category: str
    notes: str


@app.post("/api/citizen-science/report")
async def api_submit_report(req: CandidateReportRequest):
    """Generates official citizen science candidate discovery ticket for external review."""
    report = create_candidate_report(
        candidate_id=req.candidate_id,
        volunteer_name=req.volunteer_name,
        ra=req.ra,
        dec=req.dec,
        category=req.category,
        notes=req.notes
    )
    return {"status": "submitted", "report": report}


# =====================================================================
# STEP 5: Verification & Target Benchmark Suite
# =====================================================================

@app.get("/api/benchmarks")
async def api_get_all_benchmarks():
    """Lists the five required hackathon verification targets and their expected astronomical parameters."""
    return {"status": "success", "targets": BENCHMARK_TARGETS}


@app.get("/api/benchmarks/run-suite")
async def api_run_benchmarks():
    """Executes automated verification suite across all five benchmark targets."""
    return run_full_benchmark_suite()


@app.get("/api/benchmarks/{target_id}")
async def api_verify_single_benchmark(target_id: str):
    """Runs verification for an individual benchmark target."""
    if target_id == "barnards_star":
        return verify_barnards_star()
    elif target_id == "epsilon_indi_b":
        return verify_epsilon_indi_b()
    elif target_id == "wise_0855":
        return verify_wise_0855()
    elif target_id == "rw_aurigae":
        return verify_rw_aurigae()
    elif target_id == "r_draconis":
        return verify_r_draconis()
    else:
        raise HTTPException(status_code=404, detail="Benchmark target not found")


# =====================================================================
# Static Web Tool Serving
# =====================================================================

# Serve static files (HTML, JS, CSS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    """Serves the main interactive web dashboard."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NASA SPHEREx Planet X Explorer API is running. UI loading..."}
