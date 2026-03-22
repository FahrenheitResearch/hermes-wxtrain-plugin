"""Tool schemas for the wxforge ML pipeline plugin."""

WXF_FETCH = {
    "name": "wxf_fetch",
    "description": (
        "Download weather model data via byte-range .idx subsetting. "
        "Fetches specific GRIB fields from NOAA operational models. "
        "Supports HRRR, GFS, NAM, RAP, ECMWF IFS, ERA5. "
        "Example: fetch HRRR 2m temperature for the latest cycle."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "model": {
                "type": "string",
                "enum": ["hrrr", "gfs", "nam", "rap", "ecmwf", "era5"],
                "description": "NWP model to fetch from",
            },
            "search": {
                "type": "string",
                "description": (
                    "GRIB field search string. Examples: 'TMP:2 m', 'CAPE:surface', "
                    "'REFC:entire atmosphere', 'UGRD:10 m', 'HGT:500 mb'"
                ),
            },
            "product": {
                "type": "string",
                "description": "Model product (default: surface). Options: surface, pressure",
            },
            "forecast_hour": {
                "type": "integer",
                "description": "Forecast hour (default: 0)",
            },
        },
        "required": ["model", "search"],
    },
}

WXF_DECODE = {
    "name": "wxf_decode",
    "description": (
        "Decode a GRIB file and return field statistics — min, max, mean, grid dimensions, "
        "variable name, level, reference time. Pure Rust GRIB1/2 decoder (no eccodes)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to GRIB file to decode",
            },
            "message": {
                "type": "integer",
                "description": "Message number to decode (default: 1)",
            },
        },
        "required": ["file"],
    },
}

WXF_SCAN = {
    "name": "wxf_scan",
    "description": (
        "Scan a GRIB file and list all messages — variable, level, grid dimensions, "
        "reference time. Useful for exploring what fields are in a file."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to GRIB file to scan",
            },
        },
        "required": ["file"],
    },
}

WXF_CALC = {
    "name": "wxf_calc",
    "description": (
        "Run meteorological calculations — thermodynamics (theta, theta_e, RH, LCL), "
        "kinematics, severe weather indices. All verified against MetPy."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "temperature_c": {"type": "number", "description": "Temperature in Celsius"},
            "dewpoint_c": {"type": "number", "description": "Dewpoint in Celsius"},
            "pressure_hpa": {"type": "number", "description": "Pressure in hPa"},
        },
        "required": ["temperature_c", "dewpoint_c", "pressure_hpa"],
    },
}

WXF_RENDER = {
    "name": "wxf_render",
    "description": (
        "Render a GRIB field as a PNG image with colormap. "
        "Produces a heat/cool/viridis-colored visualization of the data."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to GRIB file",
            },
            "message": {
                "type": "integer",
                "description": "Message number (default: 1)",
            },
            "colormap": {
                "type": "string",
                "enum": ["heat", "cool", "viridis", "turbo"],
                "description": "Colormap (default: heat)",
            },
        },
        "required": ["file"],
    },
}

WXF_PLAN = {
    "name": "wxf_plan",
    "description": (
        "Plan a training dataset for a specific ML architecture. "
        "Given an architecture (swin_transformer, diffusion, classical_ml, forecast_graph_network) "
        "and task (forecasting, binary_classification, segmentation), generates a full training plan "
        "with channel list, labels, export format, shard count, and model recipe. "
        "This is the main entry point for building ML training datasets."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "architecture": {
                "type": "string",
                "enum": ["swin_transformer", "diffusion", "classical_ml", "forecast_graph_network", "custom"],
                "description": "ML architecture to plan for",
            },
            "task": {
                "type": "string",
                "enum": ["forecasting", "binary_classification", "multiclass_classification", "segmentation", "denoising"],
                "description": "Learning task",
            },
            "dataset_name": {
                "type": "string",
                "description": "Name for the output dataset",
            },
            "features": {
                "type": "string",
                "description": (
                    "Comma-separated feature profiles. Options: surface_core, pressure_core, "
                    "severe_diagnostics, radar_core, thermodynamic_profiles, tabular_stats. "
                    "Default: auto-selected based on architecture."
                ),
            },
        },
        "required": ["architecture", "task", "dataset_name"],
    },
}

WXF_BUILD = {
    "name": "wxf_build",
    "description": (
        "Build a training dataset from GRIB files — extracts fields, computes derived channels, "
        "renders previews, and exports NPY arrays with manifests. "
        "Use wxf_fetch first to download data, then wxf_build to process it."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Path to GRIB file to build from",
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory for the dataset",
            },
            "colormap": {
                "type": "string",
                "description": "Colormap for preview PNGs (default: heat)",
            },
        },
        "required": ["file"],
    },
}

WXF_MODELS = {
    "name": "wxf_models",
    "description": (
        "List all supported weather models with their sources, products, "
        "and forecast hour ranges."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

ALL_SCHEMAS = [
    WXF_FETCH, WXF_DECODE, WXF_SCAN, WXF_CALC, WXF_RENDER,
    WXF_PLAN, WXF_BUILD, WXF_MODELS,
]
