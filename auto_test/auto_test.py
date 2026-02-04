import platform
import subprocess
import sys
import shutil
from pathlib import Path
import logging
import datetime

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "test_run.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout),
    ],
)

def detect_environment():
    system = platform.system()
    docker = False
    try:
        if Path('/.dockerenv').exists():
            docker = True
        else:
            cgroup = Path('/proc/1/cgroup')
            if cgroup.exists():
                docker = 'docker' in cgroup.read_text()
    except Exception:
        docker = False
    return {
        'os': system,
        'is_windows': system == 'Windows',
        'is_docker': docker,
    }


def run_cmd(cmd, cwd=None):
    logging.info("CMD: %s", " ".join(cmd))
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    except Exception as e:
        logging.exception("Failed to run command: %s", e)
        return False
    if proc.stdout:
        logging.info("STDOUT:\n%s", proc.stdout)
    if proc.stderr:
        logging.info("STDERR:\n%s", proc.stderr)
    if proc.returncode != 0:
        logging.error("Command failed with code %s", proc.returncode)
        return False
    return True


def build_sample_csv(python_bin, cwd):
    code = (
        "import pandas as pd; import numpy as np; "
        "df = pd.DataFrame({'target': range(10), 'feature1': [i*2 for i in range(10)], 'feature2': [i*3 for i in range(10)]}); "
        "df.to_csv('sample.csv', index=False); print('sample.csv generated')"
    )
    return run_cmd([str(python_bin), "-c", code], cwd=cwd)


def test_requirements(req_file: Path, venv_name: str, env_info: dict):
    logging.info("===== Testing %s =====", req_file.name)
    venv_path = ROOT / venv_name
    if venv_path.exists():
        shutil.rmtree(venv_path)
    # Create venv
    if not run_cmd([sys.executable, "-m", "venv", str(venv_path)], cwd=ROOT):
        logging.error("Failed to create venv %s", venv_name)
        return False
    python_bin = venv_path / ("Scripts" if env_info['is_windows'] else "bin") / ("python.exe" if env_info['is_windows'] else "python")
    # Upgrade pip and install deps
    if not run_cmd([str(python_bin), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT):
        return False
    if not run_cmd([str(python_bin), "-m", "pip", "install", "-r", str(req_file)], cwd=ROOT):
        return False
    # Generate sample.csv
    if not build_sample_csv(python_bin, cwd=ROOT):
        return False
    # Run app
    if not run_cmd([str(python_bin), "app.py"], cwd=ROOT):
        return False
    logging.info("SUCCESS: %s", req_file.name)
    return True


def main():
    env_info = detect_environment()
    logging.info("Environment detected: %s", env_info)

    req_backup = ROOT / "requirements_backup.txt"
    req_fixed = ROOT / "requirements.txt"

    results = {}
    if req_backup.exists():
        results['requirements_backup'] = test_requirements(req_backup, ".venv_backup", env_info)
    else:
        logging.warning("requirements_backup.txt not found")
        results['requirements_backup'] = None

    if req_fixed.exists():
        results['requirements_fixed'] = test_requirements(req_fixed, ".venv_fixed", env_info)
    else:
        logging.warning("requirements.txt not found")
        results['requirements_fixed'] = None

    logging.info("===== Summary =====")
    for k, v in results.items():
        logging.info("%s: %s", k, v)

    # Exit non-zero if fixed requirements failed
    if results.get('requirements_fixed') is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
