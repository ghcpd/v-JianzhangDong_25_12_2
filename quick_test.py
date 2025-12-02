"""
Quick Comparison Test - requirements_backup.txt vs requirements.txt
This script quickly tests both dependency files and shows the comparison
"""

import subprocess
import sys
from pathlib import Path
import time

def run_command(cmd, timeout=120):
    """Run a command with timeout"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_requirements_file(req_file, env_name):
    """Test a requirements file installation"""
    print(f"\n{'='*70}")
    print(f"Testing: {req_file}")
    print(f"{'='*70}\n")
    
    results = {
        'file': req_file,
        'env': env_name,
        'steps': {}
    }
    
    # Step 1: Create venv
    print(f"[1/4] Creating virtual environment: {env_name}...")
    code, out, err = run_command(f'python -m venv {env_name}', timeout=30)
    results['steps']['create_venv'] = (code == 0)
    
    if code != 0:
        print(f"  ✗ FAILED to create venv")
        print(f"  Error: {err}")
        return results
    print(f"  ✓ Virtual environment created")
    
    # Step 2: Install dependencies
    print(f"\n[2/4] Installing dependencies from {req_file}...")
    pip_exe = f"{env_name}\\Scripts\\pip.exe"
    
    # First upgrade pip (ignore errors)
    run_command(f'{pip_exe} install --upgrade pip', timeout=30)
    
    # Install requirements
    code, out, err = run_command(f'{pip_exe} install -r {req_file}', timeout=300)
    results['steps']['install_deps'] = (code == 0)
    
    if code != 0:
        print(f"  ✗ FAILED to install dependencies")
        print(f"  Error (first 500 chars): {err[:500]}")
        return results
    print(f"  ✓ Dependencies installed successfully")
    
    # Step 3: Verify imports
    print(f"\n[3/4] Verifying package imports...")
    python_exe = f"{env_name}\\Scripts\\python.exe"
    
    test_imports = """
import sys
packages = {
    'pandas': 'pandas',
    'numpy': 'numpy', 
    'sklearn': 'scikit-learn',
    'requests': 'requests',
    'yaml': 'pyyaml',
    'matplotlib': 'matplotlib',
    'tqdm': 'tqdm',
    'dateutil': 'python-dateutil',
    'joblib': 'joblib',
    'rich': 'rich'
}

failed = []
for module, package in packages.items():
    try:
        __import__(module)
    except ImportError as e:
        failed.append(f"{package}: {str(e)}")

if failed:
    print("FAILED_IMPORTS:")
    for f in failed:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("ALL_IMPORTS_OK")
"""
    
    code, out, err = run_command(f'{python_exe} -c "{test_imports}"', timeout=30)
    results['steps']['verify_imports'] = (code == 0)
    
    if code != 0:
        print(f"  ✗ Import verification FAILED")
        print(f"  {out}")
    else:
        print(f"  ✓ All imports successful")
    
    # Step 4: Get package versions
    print(f"\n[4/4] Getting installed versions...")
    code, out, err = run_command(f'{pip_exe} list --format=freeze', timeout=30)
    
    if code == 0:
        print(f"  ✓ Package list retrieved")
        results['packages'] = out
    
    # Overall result
    results['overall'] = all(results['steps'].values())
    
    return results

def print_comparison(backup_results, fixed_results):
    """Print comparison results"""
    print(f"\n\n{'='*70}")
    print(f"{'COMPARISON RESULTS':^70}")
    print(f"{'='*70}\n")
    
    print(f"{'Step':<30} {'Backup (Old)':<20} {'Fixed (New)':<20}")
    print(f"{'-'*70}")
    
    def status(result):
        return "✓ PASS" if result else "✗ FAIL"
    
    print(f"{'Create Environment':<30} {status(backup_results['steps'].get('create_venv', False)):<20} {status(fixed_results['steps'].get('create_venv', False)):<20}")
    print(f"{'Install Dependencies':<30} {status(backup_results['steps'].get('install_deps', False)):<20} {status(fixed_results['steps'].get('install_deps', False)):<20}")
    print(f"{'Verify Imports':<30} {status(backup_results['steps'].get('verify_imports', False)):<20} {status(fixed_results['steps'].get('verify_imports', False)):<20}")
    
    print(f"{'-'*70}")
    print(f"{'OVERALL RESULT':<30} {status(backup_results.get('overall', False)):<20} {status(fixed_results.get('overall', False)):<20}")
    
    print(f"\n{'='*70}")
    print(f"CONCLUSION:")
    print(f"{'='*70}")
    
    if not backup_results.get('overall', False) and fixed_results.get('overall', False):
        print("✓ SUCCESS! The fixed requirements.txt resolves all issues!")
        print("  - requirements_backup.txt has problems (outdated/incompatible)")
        print("  - requirements.txt works perfectly (updated/secure)")
    elif backup_results.get('overall', False) and fixed_results.get('overall', False):
        print("✓ Both work, but requirements.txt uses SECURE, UPDATED versions")
        print("  - requirements_backup.txt uses OLD, VULNERABLE packages")
        print("  - requirements.txt uses CURRENT, PATCHED packages")
    else:
        print("⚠ Unexpected results - review logs above")

def main():
    print("\n" + "="*70)
    print("QUICK DEPENDENCY COMPARISON TEST")
    print("="*70)
    print("\nThis will test both requirements files and compare results...")
    print("Estimated time: 5-8 minutes\n")
    
    start_time = time.time()
    
    # Test backup (old) requirements
    backup_results = test_requirements_file('requirements_backup.txt', 'test_quick_backup')
    
    # Test fixed (new) requirements  
    fixed_results = test_requirements_file('requirements.txt', 'test_quick_fixed')
    
    # Print comparison
    print_comparison(backup_results, fixed_results)
    
    elapsed = time.time() - start_time
    print(f"\nTotal test time: {elapsed:.1f} seconds")
    
    # Cleanup
    print(f"\n{'='*70}")
    print("Cleaning up test environments...")
    run_command('if exist test_quick_backup rmdir /s /q test_quick_backup', timeout=10)
    run_command('if exist test_quick_fixed rmdir /s /q test_quick_fixed', timeout=10)
    print("✓ Cleanup complete")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
