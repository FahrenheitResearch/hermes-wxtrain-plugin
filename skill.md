---
name: wxforge-pipeline
description: Guide for using the wxforge ML weather data pipeline — fetch, decode, compute, plan, and build training datasets
version: 1.0.0
metadata:
  hermes:
    tags: [weather, ML, training, GRIB, pipeline]
    category: ml
---

# wxforge ML Pipeline

You have 8 tools for building ML-ready weather datasets. All powered by pure Rust — no Python, no eccodes.

## Workflow

### Quick: "I want to see some weather data"
1. `wxf_fetch` — download a field (e.g., HRRR CAPE)
2. `wxf_render` — render it as a PNG
3. Done

### Full: "Build me a training dataset"
1. `wxf_plan` — plan the dataset (architecture + task → channels + export format)
2. `wxf_fetch` — download the GRIB data
3. `wxf_build` — extract arrays, compute derived fields, export NPY + manifests
4. Done — training-ready arrays

## Tools

| Tool | Purpose |
|------|---------|
| `wxf_models` | List supported models and sources |
| `wxf_fetch` | Download GRIB fields via byte-range .idx |
| `wxf_scan` | List all messages in a GRIB file |
| `wxf_decode` | Decode a message — show stats (min, max, mean, grid) |
| `wxf_calc` | Compute thermodynamic parameters |
| `wxf_render` | Render a GRIB field as PNG |
| `wxf_plan` | Plan a training dataset for an ML architecture |
| `wxf_build` | Build training arrays from GRIB files |

## Architecture-Aware Planning

`wxf_plan` automatically selects features based on the ML architecture:

| Architecture | Default Features | Export Format | Loss |
|---|---|---|---|
| `swin_transformer` | surface + pressure + severe (25 channels) | WebDataset | smooth_l1 |
| `diffusion` | surface + pressure (13 channels) | WebDataset | noise_prediction_mse |
| `classical_ml` | surface + severe + tabular (22 channels) | Parquet | MSE/BCE |
| `forecast_graph_network` | surface + pressure (13 channels) | WebDataset | smooth_l1 |

## Feature Profiles

| Profile | Channels |
|---|---|
| `surface_core` | t2m, d2m, u10, v10, mslp |
| `pressure_core` | z500, t850, u850, v850, vort500, div500, theta850, tadv850 |
| `severe_diagnostics` | sbcape, sbcin, mlcape, mlcin, mucape, mucin, srh01, srh03, shear06, stp, scp, pwat |
| `radar_core` | reflectivity, velocity, spectrum_width |
| `thermodynamic_profiles` | theta_e, wet_bulb, lcl_height, lfc_height, dcape |
| `tabular_stats` | channel_min, channel_mean, channel_max, valid_hour_sin/cos |

## Supported Models

| Model | Source | Resolution |
|---|---|---|
| HRRR | NOAA NOMADS/AWS | 3km CONUS |
| GFS | NOAA NOMADS/AWS | 0.25° global |
| NAM | NOAA NOMADS/AWS | 12km CONUS |
| RAP | NOAA NOMADS/AWS | 13km CONUS |
| ECMWF IFS | ECMWF Open Data | 0.25° global |
| ERA5 | CDS API (auth required) | 0.25° global reanalysis |

## Examples

**"Fetch HRRR CAPE":**
```json
{"model": "hrrr", "search": "CAPE:surface"}
```

**"Plan a Swin transformer severe weather dataset":**
```json
{"architecture": "swin_transformer", "task": "forecasting", "dataset_name": "hrrr_severe_swin"}
```

**"Build training data from a GRIB file":**
```json
{"file": "/path/to/hrrr.grib2", "output_dir": "/path/to/output"}
```

## Output Formats

- **NPY** — numpy arrays, one per channel
- **Parquet** — tabular, for classical ML
- **WebDataset** — sharded tar files, for distributed training
- **Zarr** — chunked arrays, for cloud-native workflows
