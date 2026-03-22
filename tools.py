"""wxforge tool handlers — shell out to the wxforge binary."""

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_EXE = ".exe" if os.name == "nt" else ""
WXFORGE = os.environ.get(
    "WXFORGE_PATH",
    str(Path.home() / "wxforge" / "target" / "release" / f"wxforge{_EXE}")
)

_OUT_DIR = Path.home() / ".hermes" / "wxforge" / "data"
_OUT_DIR.mkdir(parents=True, exist_ok=True)

_IMG_DIR = Path.home() / ".hermes" / "wxforge" / "images"
_IMG_DIR.mkdir(parents=True, exist_ok=True)


def check_wxforge():
    return os.path.isfile(WXFORGE)


def _run(args, timeout=120):
    """Run wxforge command, return stdout."""
    cmd = [WXFORGE] + args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            err = result.stderr.strip() or f"wxforge exited {result.returncode}"
            return json.dumps({"error": err[:500]})
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return json.dumps({"error": f"wxforge timed out ({timeout}s)"})
    except FileNotFoundError:
        return json.dumps({"error": f"wxforge not found at {WXFORGE}"})
    except Exception as e:
        return json.dumps({"error": str(e)[:200]})


def wxf_fetch(args: dict, **kwargs) -> str:
    model = args.get("model", "hrrr")
    search = args.get("search")
    if not search:
        return json.dumps({"error": "search is required"})

    product = args.get("product", "surface")
    fhr = args.get("forecast_hour", 0)
    out_file = str(_OUT_DIR / f"{model}_{search.replace(':', '_').replace(' ', '_')}_f{fhr}.grib2")

    cmd = [
        "fetch", "model-subset",
        "--model", model,
        "--product", product,
        "--forecast-hour", str(fhr),
        "--search", search,
        "--output", out_file,
    ]

    result = _run(cmd, timeout=60)

    # If it returned raw text (not JSON error), wrap it
    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        return json.dumps({
            "file": out_file,
            "model": model,
            "search": search,
            "forecast_hour": fhr,
            "status": "downloaded",
            "details": result[:300],
        })


def wxf_decode(args: dict, **kwargs) -> str:
    f = args.get("file")
    if not f:
        return json.dumps({"error": "file is required"})
    msg = args.get("message", 1)
    return _run(["decode-grib", "--file", f, "--message", str(msg)])


def wxf_scan(args: dict, **kwargs) -> str:
    f = args.get("file")
    if not f:
        return json.dumps({"error": "file is required"})
    result = _run(["scan-grib", "--file", f])
    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        return json.dumps({"scan": result[:1000]})


def wxf_calc(args: dict, **kwargs) -> str:
    t = args.get("temperature_c")
    td = args.get("dewpoint_c")
    p = args.get("pressure_hpa")
    if t is None or td is None or p is None:
        return json.dumps({"error": "temperature_c, dewpoint_c, and pressure_hpa required"})

    result = _run([
        "calc", "thermo",
        "--temperature-c", str(t),
        "--dewpoint-c", str(td),
        "--pressure-hpa", str(p),
    ])

    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        # Parse key=value output
        params = {}
        for line in result.split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                try:
                    params[k.strip()] = float(v.strip())
                except ValueError:
                    params[k.strip()] = v.strip()
        return json.dumps(params)


def wxf_render(args: dict, **kwargs) -> str:
    f = args.get("file")
    if not f:
        return json.dumps({"error": "file is required"})
    msg = args.get("message", 1)
    cmap = args.get("colormap", "heat")

    out_path = str(_IMG_DIR / f"render_{os.path.basename(f)}_{msg}.png")

    result = _run([
        "render", "grib",
        "--file", f,
        "--message", str(msg),
        "--output", out_path,
        "--colormap", cmap,
    ])

    if os.path.isfile(out_path):
        return json.dumps({
            "image_path": out_path,
            "image_file": os.path.basename(out_path),
            "colormap": cmap,
            "details": result[:200] if result else "",
        })

    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        return json.dumps({"status": result[:300]})


def wxf_plan(args: dict, **kwargs) -> str:
    arch = args.get("architecture")
    task = args.get("task")
    name = args.get("dataset_name")
    if not all([arch, task, name]):
        return json.dumps({"error": "architecture, task, and dataset_name required"})

    # Create job spec
    spec_path = str(_OUT_DIR / f"{name}_spec.json")
    init_result = _run([
        "train", "job-init",
        "--output", spec_path,
        "--architecture", arch.replace("_", "-"),
        "--task", task.replace("_", "-"),
        "--dataset-name", name,
    ])

    if not os.path.isfile(spec_path):
        return json.dumps({"error": f"job-init failed: {init_result[:200]}"})

    # Plan the job
    plan_result = _run(["train", "job-plan", "--spec", spec_path])

    try:
        plan = json.loads(plan_result)
        plan["spec_file"] = spec_path
        return json.dumps(plan)
    except json.JSONDecodeError:
        return json.dumps({"spec_file": spec_path, "plan_output": plan_result[:500]})


def wxf_build(args: dict, **kwargs) -> str:
    f = args.get("file")
    if not f:
        return json.dumps({"error": "file is required"})

    out_dir = args.get("output_dir", str(_OUT_DIR / "build"))
    cmap = args.get("colormap", "heat")

    result = _run([
        "train", "build-grib-sample",
        "--file", f,
        "--output-dir", out_dir,
        "--colormap", cmap,
    ])

    # List outputs
    outputs = []
    if os.path.isdir(out_dir):
        for fname in os.listdir(out_dir):
            fpath = os.path.join(out_dir, fname)
            outputs.append({
                "file": fname,
                "size_kb": round(os.path.getsize(fpath) / 1024, 1),
            })

    try:
        json.loads(result)
        parsed = json.loads(result)
        parsed["outputs"] = outputs
        return json.dumps(parsed)
    except json.JSONDecodeError:
        return json.dumps({
            "output_dir": out_dir,
            "details": result[:300],
            "outputs": outputs,
        })


def wxf_models(args: dict, **kwargs) -> str:
    result = _run(["models"])
    try:
        json.loads(result)
        return result
    except json.JSONDecodeError:
        return json.dumps({"models": result[:1000]})
