# wxtrain — ML Weather Data Pipeline Plugin

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin for building ML-ready weather training datasets. Powered by [wxtrain](https://github.com/FahrenheitResearch/wxtrain), an all-Rust end-to-end pipeline.

## What It Does

Ask Hermes to build training datasets from operational weather models:

- **"Plan a severe weather dataset for a Swin transformer"** → 25-channel training spec with export format, loss function, and model recipe
- **"Fetch HRRR CAPE data"** → downloads via byte-range .idx subsetting (~500KB instead of 125MB)
- **"Build training arrays from this GRIB file"** → NPY arrays + preview PNGs + manifests
- **"What's the theta-e at 30C, 20C dewpoint, 850mb?"** → instant thermodynamic calculation

## 8 Tools

| Tool | Description |
|------|-------------|
| `wxt_models` | List supported weather models and sources |
| `wxt_fetch` | Download GRIB fields via byte-range .idx |
| `wxt_scan` | List all messages in a GRIB file |
| `wxt_decode` | Decode a GRIB message — stats, grid dimensions, variable info |
| `wxt_calc` | Thermodynamic calculations (theta, theta_e, RH) |
| `wxt_render` | Render a GRIB field as PNG |
| `wxt_plan` | Plan a training dataset for an ML architecture |
| `wxt_build` | Build training arrays from GRIB files |

## Pipeline

```
wxt_plan (architecture + task → channel spec + export format)
    ↓
wxt_fetch (NOAA/ECMWF → byte-range GRIB download)
    ↓
wxt_build (decode → compute derived fields → export NPY/Parquet/WebDataset)
```

## Architecture-Aware Planning

`wxt_plan` knows how to prepare data for different ML architectures:

| Architecture | Channels | Format | Loss |
|---|---|---|---|
| Swin Transformer | 25 (surface + pressure + severe) | WebDataset (96 shards) | smooth_l1 |
| Diffusion | 13 (surface + pressure) | WebDataset | noise_prediction_mse |
| Classical ML | 22 (surface + severe + tabular) | Parquet | MSE/BCE |
| Graph Network | 13 (surface + pressure) | WebDataset | smooth_l1 |

## Feature Profiles

| Profile | Fields |
|---|---|
| `surface_core` | t2m, d2m, u10, v10, mslp |
| `pressure_core` | z500, t850, u850, v850, vort500, div500, theta850, tadv850 |
| `severe_diagnostics` | sbcape, sbcin, mlcape, mlcin, mucape, mucin, srh01, srh03, shear06, stp, scp, pwat |
| `radar_core` | reflectivity, velocity, spectrum_width |
| `thermodynamic_profiles` | theta_e, wet_bulb, lcl_height, lfc_height, dcape |
| `tabular_stats` | channel_min/mean/max, valid_hour_sin/cos |

## Supported Models

| Model | Source | Resolution | Auth |
|---|---|---|---|
| HRRR | NOAA | 3km CONUS | None |
| GFS | NOAA | 0.25° global | None |
| NAM | NOAA | 12km CONUS | None |
| RAP | NOAA | 13km CONUS | None |
| ECMWF IFS | Open Data | 0.25° global | None |
| ERA5 | CDS API | 0.25° reanalysis | CDS key |

## Stack

100% Rust core. No Python, no C, no eccodes, no Fortran.

```
wxtrain binary (22,488 lines of Rust)
├── wx-fetch   — download planning, byte-range fetch, CDS auth
├── wx-grib    — native GRIB1/2 decode (JPEG2000, CCSDS/AEC)
├── wx-calc    — 100+ met calculations (MetPy parity verified)
├── wx-radar   — NEXRAD ingest
├── wx-render  — PNG rendering
├── wx-train   — dataset planning & assembly
├── wx-export  — NPY, Parquet, WebDataset, Zarr
└── wx-types   — shared domain model
```

## Setup

```bash
# 1. Build wxtrain
git clone https://github.com/FahrenheitResearch/wxtrain
cd wxtrain && cargo build --release

# 2. Copy plugin to Hermes
cp -r wxtrain-plugin ~/.hermes/plugins/wxtrain

# 3. (Optional) set binary path
export WXTRAIN_PATH=/path/to/wxtrain/target/release/wxtrain
```

## Output Formats

| Format | Use Case |
|---|---|
| NPY | Quick prototyping, single arrays |
| Parquet | Tabular ML (XGBoost, LightGBM) |
| WebDataset | Distributed training (PyTorch) |
| Zarr | Cloud-native, chunked arrays |

## Companion Plugin

This plugin pairs with the [Hermes Weather Plugin](https://github.com/FahrenheitResearch/hermes-weather-plugin) — use the weather plugin to explore and visualize data, then use wxtrain to build training datasets from the same models.

## Credits

- **wxtrain engine**: Built with Codex
- **Meteorological calculations**: Verified against MetPy test suites
- **Plugin platform**: [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research
