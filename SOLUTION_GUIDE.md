# NASA Space Apps Challenge: Planet X and SPHEREx
## Complete 5-Step Solution Architecture & Execution Guide

### Overview
NASA’s SPHEREx mission is mapping the entire sky every six months across **102 near-infrared spectral bands (0.75 to 5.0 µm)**. This project provides a public-facing, interactive web platform that ingests, renders, analyzes, and compares multi-epoch sky imagery to discover shifting celestial objects: **Planet X / Kuiper Belt Objects, ultra-cold sub-stellar Brown Dwarfs, High Proper-Motion Runaway Stars, and Variable Stars**.

---

### Challenge Breakdown & 5-Step Implementation

#### Step 1: Data Ingestion & Query Architecture
- **Coordinate & URL Query Interface**:
  - `coordinate.py`: Standardizes RA and Dec coordinates across degrees and sexagesimal formats (HMS/DMS) using Astropy `SkyCoord`.
  - `api.py`: Implements URL parameter binding (`?ra=...&dec=...&fov=...`) enabling direct bookmarking, linking, and embedding across external sites.
- **SPHEREx Pipeline Integration**:
  - `archive_connector.py`: Integrates with NASA/IPAC IRSA SIA2 service (`spherex_dr1`, `spherex_qr3`, etc.).
  - `qr4.py` & `releases.yaml`: Dynamic configuration engine that seamlessly incorporates new NASA data releases as they are published.
  - `access_url.py` & `synchronised.py`: Automated retrieval and registration of new observation epochs.
- **Array Signal Co-Adding**:
  - `image_and-variance_information.py`: Extracts FITS primary science images and inverse variance maps.
  - `align_observations.py`: Reprojects multi-epoch observation headers onto a common target WCS grid using `reproject_interp`.
  - `inverse_variance_weights.py`: Implements optimal inverse-variance weighted co-addition ($\sum w_i I_i / \sum w_i$) across SPHEREx's 6 detector arrays to maximize signal-to-noise for ultra-faint objects.

---

#### Step 2: Time-Series Visualizer & Interactive Controls
- **Astronomical Rendering Engine**:
  - Embedded CDS **Aladin Lite** sky visualizer supporting dynamic pan, zoom, coordinate reticles, and multi-survey layers.
- **Time-Series Video & Blink Player**:
  - Cycles sequential observations across 6-month survey cycles (Epoch 1: 2025-06, Epoch 2: 2025-12, Epoch 3: 2026-06).
  - Looping playback controls (Play / Pause, Step Forward / Backward, FPS speed slider from 0.5 to 4.0 fps).
- **Dynamic Field of View (FOV)**:
  - User-adjustable FOV slider from $0.02^\circ$ (narrow deep tracking) up to $5.0^\circ$ (wide-angle rapid search).
- **Epoch Image Arithmetic**:
  - `epoch_arithmetic.py`: Computes difference imaging ($\Delta I = I_{Epoch2} - I_{Epoch1}$) and inverse-variance addition.
  - Interactive HTML5 canvas visualizer highlighting dipole signals of moving targets while cancelling static background stars.

---

#### Step 3: Spectral Analysis & Metadata Layer
- **102-Band Near-Infrared Handling**:
  - `spectral_bands.py`: Full specification of SPHEREx's 6 detector arrays:
    - **Array 1 (D1)**: 0.75 – 1.11 µm (Bands 1–17, $R \approx 41$)
    - **Array 2 (D2)**: 1.11 – 1.64 µm (Bands 18–34, $R \approx 41$)
    - **Array 3 (D3)**: 1.64 – 2.42 µm (Bands 35–51, $R \approx 41$)
    - **Array 4 (D4)**: 2.42 – 3.82 µm (Bands 52–68, $R \approx 35$)
    - **Array 5 (D5)**: 3.82 – 4.42 µm (Bands 69–85, $R \approx 130$)
    - **Array 6 (D6)**: 4.42 – 5.00 µm (Bands 86–102, $R \approx 130$)
  - Molecular tracer filters for **Water Ice ($H_2O$ @ 3.05 µm)**, **Carbon Dioxide ($CO_2$ @ 4.27 µm)**, **Carbon Monoxide ($CO$ @ 4.67 µm)**, and **Methane ($CH_4$ @ 3.32 µm)**.
- **On-the-Fly Spectra Generation**:
  - `spectra_generator.py`: Generates calibrated Spectral Energy Distributions (SED) across all 102 channels with interactive Chart.js plotting and automatic molecular absorption detection.
- **Quality & Contamination Overlay**:
  - `quality_contamination.py`: Decodes 16-bit data quality masks (cosmic ray strikes, saturation, solar/lunar stray light glints, hot/dead pixels, persistence latency) alongside observational timestamps (UTC & MJD).

---

#### Step 4: Multi-Mission Data Overlays
- **Cross-Catalog Integration**:
  - `cross_catalog.py`: Integrates NASA **WISE** ($W1, W2, W3, W4$ infrared photometry and $W1-W2$ color index) and ESA **Gaia DR3** ($G$-band magnitude, proper motion vectors $\vec{\mu}$, parallax, distance).
  - Toggles visual overlays directly over SPHEREx imagery.
- **Citizen Science Discovery Support**:
  - `citizen_science.py`: Automated classification engine that tests user-flagged moving sources against Gaia/WISE to differentiate candidate Planet X / brown dwarfs from known stars or artifacts.
  - Interactive "Report Candidate" modal with automatic NASA discovery ticket export (JSON).

---

#### Step 5: Verification & Target Benchmark Suite
- `benchmark_suite.py` & `test_benchmarks.py`: Automated validation suite testing performance against the hackathon's required benchmark objects:
  1. **Barnard's Star**: Verifies detection and tracking of high proper-motion stars ($\mu = 10,390\,\text{mas/yr}$, 5.19" shift per 6-month cycle).
  2. **Epsilon Indi B**: Verifies visual resolution and near-infrared spectral methane/water absorption in brown dwarf binary systems (T1 + T6).
  3. **WISE 0855** (RA 08h55m10.831s, Dec -7d14m42.53s): Verifies tracking of ultra-fast moving, coldest known sub-stellar brown dwarf (~250 K) with dramatic 4.5 µm infrared excess.
  4. **RW Aurigae**: Verifies time-series photometric brightness tracking for young eruptive T Tauri stars experiencing dust obscuration ($\Delta m > 2.0\,\text{mag}$).
  5. **R Draconis**: Verifies periodic infrared amplitude tracking for pulsating Mira variable stars ($P \approx 245.5$ days).

---

### How to Run the Web Application

1. **Start the API & Web Server**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```
2. **Open in Browser**:
   Navigate to [http://localhost:8000](http://localhost:8000) or open `static/index.html`.

3. **Run the Benchmark Test Suite**:
   ```bash
   python test_benchmarks.py
   ```
