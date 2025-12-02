#!/usr/bin/env python3
"""
Auto-test harness to compare installing dependencies from two files and exercising the project.

Functionality:
- Detect runtime environment (Windows / Linux / Docker)
- For each requirements file (requirements_backup.txt and requirements.txt):
    - create a clean venv under auto_test/venvs/
    - pip install -r <file>
    - run quick verification checks (import some packages + print versions)
    - attempt to run app.py (if present) and capture stdout/stderr
    - write detailed results into logs/test_run.log

This script is intended to be run from the repository root.
"""

from __future__ import annotations

import os
import sys
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO_DIR = Path(__file__).resolve().parent
VENV_DIR = AUTO_DIR / "venvs"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "test_run.log"

DEFAULT_FILES = [ROOT / "requirements_backup.txt", ROOT / "requirements.txt"]
CHECK_PACKAGES = ["numpy", "pandas", "sklearn", "requests", "pyyaml", "matplotlib", "tqdm", "dateutil", "joblib", "rich"]


def detect_environment() -> str:
    if os.name == "nt":
        return "Windows"
    # Detect docker by cgroup or /.dockerenv
    try:
        if Path("/.dockerenv").exists():
            return "Docker"
        with open("/proc/1/cgroup", "rt") as f:
            if "docker" in f.read() or "kubepods" in f.read():
                return "Docker"
    except Exception:
        pass
    return "Linux"


def log(msg: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.utcnow().isoformat() + "Z"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def run_subprocess(args, env=None, timeout=300):
    try:
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, timeout=timeout)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return 2, "", f"Exception running subprocess: {e}"


def create_venv(venv_path: Path) -> Path:
    if venv_path.exists():
        shutil.rmtree(venv_path)
    venv_path.mkdir(parents=True)
    # Use sys.executable to create the venv
    code, out, err = run_subprocess([sys.executable, "-m", "venv", str(venv_path)])
    return venv_path


def get_venv_python(venv_path: Path) -> str:
    if os.name == "nt":
        return str(venv_path / "Scripts" / "python.exe")
    return str(venv_path / "bin" / "python")


def install_requirements(venv_python: str, requirements_file: Path) -> tuple[int, str, str]:
    # upgrade pip, then install
    install_cmd = [venv_python, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
    code, out, err = run_subprocess(install_cmd, timeout=600)
    if code != 0:
        return code, out, err

    cmd = [venv_python, "-m", "pip", "install", "-r", str(requirements_file)]
    return run_subprocess(cmd, timeout=1200)


def verify_imports(venv_python: str) -> dict:
    results = {}
    for pkg in CHECK_PACKAGES:
        code, out, err = run_subprocess([venv_python, "-c", f"import {pkg}; print(getattr({pkg}, '__version__', 'unknown'))"], timeout=60)
        results[pkg] = {"code": code, "stdout": out.strip(), "stderr": err.strip()}
    return results


def run_app(venv_python: str, project_root: Path) -> tuple[int, str, str]:
    app_py = project_root / "app.py"
    if not app_py.exists():
        return 0, "app.py not present - skipping execution", ""
    return run_subprocess([venv_python, str(app_py)], timeout=120)


def test_for_requirements(req_file: Path) -> dict:
    # name the test case by filename
    name = req_file.name
    venv_path = VENV_DIR / name
    result: dict = {"name": name, "requirements_file": str(req_file), "venv": str(venv_path), "start": datetime.utcnow().isoformat() + "Z"}

    try:
        create_venv(venv_path)
        venv_python = get_venv_python(venv_path)

        log(f"[{name}] Installing from {req_file}")
        code, out, err = install_requirements(venv_python, req_file)
        result["install"] = {"returncode": code, "stdout": out, "stderr": err}

        if code != 0:
            result["status"] = "install_failed"
            return result

        log(f"[{name}] Running import checks")
        imports = verify_imports(venv_python)
        result["imports"] = imports

        log(f"[{name}] Running app.py (if present)")
        code, out, err = run_app(venv_python, ROOT)
        result["app_run"] = {"returncode": code, "stdout": out, "stderr": err}
        result["status"] = "ok"

    except Exception as exc:  # catch and log inexplicable errors
        result["status"] = "error"
        result["exception"] = str(exc)

    result["end"] = datetime.utcnow().isoformat() + "Z"
    return result


def main(req_files: list[Path] | None = None):
    req_files = req_files or DEFAULT_FILES
    env = detect_environment()

    header = {"time": datetime.utcnow().isoformat() + "Z", "environment": env, "files": [str(p) for p in req_files]}
    # On Windows, detect whether Visual C++ build tools are available (cl.exe)
    if env == "Windows":
        cl_path = shutil.which("cl")
        vswhere_path = shutil.which("vswhere")
        header["build_tools"] = {"cl_present": bool(cl_path), "cl_path": cl_path or "", "vswhere_present": bool(vswhere_path), "vswhere_path": vswhere_path or ""}
        if not cl_path:
            log("WARNING: cl.exe not found — Visual C++ build tools appear missing. Installing them (or using a Python with wheels) is required to build some packages like older NumPy releases.")
    log(f"START AUTO_TEST: {json.dumps(header)}")

    results = {"meta": header, "runs": []}

    VENV_DIR.mkdir(exist_ok=True)
    for p in req_files:
        if not p.exists():
            log(f"ERROR: requirements file not found: {p}")
            results["runs"].append({"name": p.name, "status": "missing", "file": str(p)})
            continue
        log(f"--- Testing {p} ---")
        r = test_for_requirements(p)
        results["runs"].append(r)
        # write partial progress to log
        log(json.dumps(r, indent=2))

    # save JSON summary
    summary_file = LOG_DIR / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    log(f"AUTO_TEST completed. Summary written to {summary_file}")
    print("Auto-test completed. See logs/test_run.log and logs/summary.json for details.")


if __name__ == "__main__":
    files = []
    # allow override via command line
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            files.append(Path(arg))
    else:
        files = DEFAULT_FILES

    main(files)
