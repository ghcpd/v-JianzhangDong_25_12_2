import argparse
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT_DIR / "logs"
LOG_FILE = LOGS_DIR / "test_run.log"
ENV_BASE_DIR = ROOT_DIR / ".venv_tests"

DEPENDENCY_FILES = {
    "backup": ROOT_DIR / "requirements_backup.txt",
    "corrected": ROOT_DIR / "requirements.txt",
}

NIGHTLY_INDEX = os.environ.get(
    "AUTO_TEST_NIGHTLY_INDEX",
    "https://pypi.anaconda.org/scientific-python-nightly-wheels/simple",
)


def detect_environment():
    pyver = sys.version_info
    system = platform.system()
    is_windows = system == "Windows"
    is_docker = Path("/.dockerenv").exists() or os.environ.get("RUNNING_IN_DOCKER") == "true" or os.environ.get("container") == "docker"
    return {
        "platform": platform.platform(),
        "python_version": sys.version.replace("\n", " "),
        "python_version_info": list(pyver[:3]),
        "is_windows": is_windows,
        "is_docker": is_docker,
    }


def setup_logging():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def run_command(cmd, cwd=None, env=None):
    logging.info("Running command: %s", " ".join(map(str, cmd)))
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        logging.info("Command exit code: %s", result.returncode)
        if result.stdout:
            logging.info("Output:\n%s", result.stdout)
        return result.returncode, result.stdout
    except Exception as exc:
        logging.exception("Command failed: %s", exc)
        return -1, str(exc)


def create_venv(env_dir: Path):
    if env_dir.exists():
        shutil.rmtree(env_dir)
    env_dir.parent.mkdir(parents=True, exist_ok=True)
    logging.info("Creating virtual environment at %s", env_dir)
    result = subprocess.run([sys.executable, "-m", "venv", str(env_dir)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create venv at {env_dir}: {result.stdout}")


def get_python_bin(env_dir: Path, is_windows: bool):
    if is_windows:
        return env_dir / "Scripts" / "python.exe"
    return env_dir / "bin" / "python"


def ensure_sample_csv(root: Path):
    sample = root / "sample.csv"
    if sample.exists():
        return sample
    import csv

    logging.info("Creating sample.csv for app demonstration")
    rows = [
        ["target", "feature1", "feature2"],
        [1.0, 2.0, 3.0],
        [2.0, 3.0, 4.0],
        [3.0, 4.0, 5.0],
        [4.0, 5.0, 6.0],
    ]
    with sample.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return sample


def compute_pip_args(pyver_tuple, target_name):
    """Return extra pip install args for the given Python version.

    For Python >= 3.14 we enable pre-release and nightly wheels to avoid building
    large scientific packages from source on Windows.
    """
    args = []
    if pyver_tuple >= (3, 14):
        # Allow pre-release, prefer binaries, and add nightly index
        args.extend([
            "--pre",
            "--prefer-binary",
            "--only-binary",
            ":all:",
            "--extra-index-url",
            NIGHTLY_INDEX,
        ])
        logging.info("[pip] Using nightly wheels index for %s on Python %s", target_name, pyver_tuple)
    return args


def test_environment(name: str, req_file: Path, is_windows: bool, pyver_tuple):
    logging.info("================= Testing %s =================", name)
    if not req_file.exists():
        logging.error("Requirements file not found: %s", req_file)
        return {"name": name, "status": "missing", "details": f"Missing requirements file {req_file}"}

    env_dir = ENV_BASE_DIR / name
    try:
        create_venv(env_dir)
        py = get_python_bin(env_dir, is_windows)
        # upgrade pip
        run_command([str(py), "-m", "pip", "install", "--upgrade", "pip"])
        # install requirements
        pip_args = compute_pip_args(pyver_tuple, name)
        rc, out = run_command([str(py), "-m", "pip", "install", "-r", str(req_file)] + pip_args)
        if rc != 0:
            logging.warning("Installation failed for %s", name)
            return {"name": name, "status": "install_failed", "details": out}

        # prepare sample data
        ensure_sample_csv(ROOT_DIR)

        # run app.py
        rc_app, out_app = run_command([str(py), "app.py"], cwd=str(ROOT_DIR))
        status = "success" if rc_app == 0 else "run_failed"
        return {"name": name, "status": status, "details": out_app}
    except Exception as exc:
        logging.exception("Error testing %s", name)
        return {"name": name, "status": "error", "details": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Automated dependency environment tester")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--both", action="store_true", help="Test both backup and corrected requirements (default)")
    grp.add_argument("--backup-only", action="store_true", help="Test only the backup requirements")
    grp.add_argument("--corrected-only", action="store_true", help="Test only the corrected requirements")
    args = parser.parse_args()

    setup_logging()
    env_info = detect_environment()
    logging.info("Environment info: %s", json.dumps(env_info))

    # Determine which to run
    targets = []
    if args.backup_only:
        targets = ["backup"]
    elif args.corrected_only:
        targets = ["corrected"]
    else:
        targets = ["backup", "corrected"]

    results = []
    for target in targets:
        res = test_environment(target, DEPENDENCY_FILES[target], env_info["is_windows"], tuple(env_info["python_version_info"]))
        results.append(res)

    logging.info("Summary: %s", json.dumps(results, indent=2))

    # Optionally write a JSON summary alongside the log
    summary_path = LOGS_DIR / "test_run_summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.utcnow().isoformat() + "Z", "results": results, "environment": env_info}, f, indent=2)

    # Exit with non-zero if corrected failed
    corrected = next((r for r in results if r["name"] == "corrected"), None)
    if corrected and corrected["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
