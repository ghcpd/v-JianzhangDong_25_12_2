#!/usr/bin/env python3
"""
Automated Testing Script for Dependency Validation
This script automatically detects the runtime environment and tests both
the original (backup) and corrected requirements files.
"""

import os
import sys
import platform
import subprocess
import shutil
import logging
from pathlib import Path
from datetime import datetime
import json
import tempfile


class EnvironmentDetector:
    """Detects the current runtime environment."""
    
    @staticmethod
    def get_platform():
        """Detect the current platform: Windows, Linux, or Docker."""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Linux":
            # Check if running in Docker
            if os.path.exists("/.dockerenv"):
                return "Docker"
            return "Linux"
        elif system == "Darwin":
            return "macOS"
        return "Unknown"
    
    @staticmethod
    def get_python_version():
        """Get the current Python version."""
        return platform.python_version()
    
    @staticmethod
    def get_system_info():
        """Get comprehensive system information."""
        return {
            "platform": EnvironmentDetector.get_platform(),
            "python_version": EnvironmentDetector.get_python_version(),
            "architecture": platform.architecture(),
            "machine": platform.machine()
        }


class DependencyTester:
    """Tests dependencies in isolated virtual environments."""
    
    def __init__(self, log_file):
        self.log_file = log_file
        self.project_root = Path(__file__).parent.parent
        self.setup_logging()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": EnvironmentDetector.get_system_info(),
            "tests": []
        }
    
    def setup_logging(self):
        """Configure logging to file and console."""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_path = log_dir / self.log_file
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message, level="INFO"):
        """Log a message."""
        getattr(self.logger, level.lower())(message)
    
    def create_venv(self, venv_path):
        """Create a virtual environment."""
        try:
            self.log(f"Creating virtual environment at {venv_path}...")
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True
            )
            self.log("Virtual environment created successfully.")
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to create virtual environment: {e}", "error")
            return False
    
    def get_pip_command(self, venv_path):
        """Get the pip command for the virtual environment."""
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "pip.exe")
        else:
            return str(venv_path / "bin" / "pip")
    
    def get_python_command(self, venv_path):
        """Get the python command for the virtual environment."""
        if platform.system() == "Windows":
            return str(venv_path / "Scripts" / "python.exe")
        else:
            return str(venv_path / "bin" / "python")
    
    def install_dependencies(self, venv_path, requirements_file):
        """Install dependencies in a virtual environment."""
        try:
            pip_cmd = self.get_pip_command(venv_path)
            
            # Upgrade pip
            self.log(f"Upgrading pip in {venv_path}...")
            subprocess.run(
                [pip_cmd, "install", "--upgrade", "pip", "setuptools", "wheel"],
                check=True,
                capture_output=True
            )
            
            # Install requirements
            self.log(f"Installing dependencies from {requirements_file}...")
            result = subprocess.run(
                [pip_cmd, "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log(f"Installation failed:\n{result.stderr}", "error")
                return False, result.stderr
            
            self.log("Dependencies installed successfully.")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Dependency installation error: {e}", "error")
            return False, str(e)
    
    def create_test_data(self, venv_path):
        """Create sample test data."""
        try:
            python_cmd = self.get_python_command(venv_path)
            script = """
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = {
    'target': np.random.rand(50) * 100,
    'feature1': np.random.rand(50) * 50,
    'feature2': np.random.rand(50) * 30,
    'feature3': np.random.rand(50) * 20
}
df = pd.DataFrame(data)
df.to_csv('sample.csv', index=False)
print("Sample CSV created successfully")
"""
            result = subprocess.run(
                [python_cmd, "-c", script],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )
            
            if result.returncode != 0:
                self.log(f"Test data creation failed: {result.stderr}", "warning")
                return False, result.stderr
            
            self.log("Test data created successfully.")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Error creating test data: {e}", "warning")
            return False, str(e)
    
    def run_application(self, venv_path):
        """Run the application with installed dependencies."""
        try:
            python_cmd = self.get_python_command(venv_path)
            self.log("Running application...")
            
            result = subprocess.run(
                [python_cmd, "app.py"],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=60
            )
            
            success = result.returncode == 0
            output = result.stdout
            error = result.stderr
            
            if success:
                self.log("Application ran successfully.")
            else:
                self.log(f"Application failed:\n{error}", "error")
            
            return success, output, error
        except subprocess.TimeoutExpired:
            self.log("Application execution timed out.", "error")
            return False, "", "Timeout"
        except subprocess.CalledProcessError as e:
            self.log(f"Application execution error: {e}", "error")
            return False, "", str(e)
    
    def test_requirements_file(self, requirements_file, test_name):
        """Test a requirements file in isolation."""
        self.log(f"\n{'='*60}")
        self.log(f"Testing: {test_name}")
        self.log(f"Requirements file: {requirements_file}")
        self.log(f"{'='*60}\n")
        
        test_result = {
            "name": test_name,
            "requirements_file": str(requirements_file),
            "status": "failed",
            "steps": [],
            "errors": []
        }
        
        # Create temporary venv
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_path = Path(tmpdir) / "venv"
            
            # Step 1: Create venv
            self.log(f"\n[STEP 1] Creating virtual environment...")
            if not self.create_venv(venv_path):
                test_result["errors"].append("Failed to create virtual environment")
                test_result["steps"].append({"name": "Create venv", "status": "failed"})
                self.test_results["tests"].append(test_result)
                return
            test_result["steps"].append({"name": "Create venv", "status": "passed"})
            
            # Step 2: Install dependencies
            self.log(f"\n[STEP 2] Installing dependencies...")
            success, output = self.install_dependencies(venv_path, requirements_file)
            if not success:
                test_result["errors"].append(f"Dependency installation failed: {output}")
                test_result["steps"].append({"name": "Install dependencies", "status": "failed"})
                self.test_results["tests"].append(test_result)
                return
            test_result["steps"].append({"name": "Install dependencies", "status": "passed"})
            
            # Step 3: Create test data
            self.log(f"\n[STEP 3] Creating test data...")
            success, output = self.create_test_data(venv_path)
            if not success:
                test_result["errors"].append(f"Test data creation failed: {output}")
            test_result["steps"].append({
                "name": "Create test data",
                "status": "passed" if success else "warning"
            })
            
            # Step 4: Run application
            self.log(f"\n[STEP 4] Running application...")
            success, stdout, stderr = self.run_application(venv_path)
            if not success:
                test_result["errors"].append(f"Application failed: {stderr}")
                test_result["steps"].append({"name": "Run application", "status": "failed"})
                self.test_results["tests"].append(test_result)
                return
            test_result["steps"].append({"name": "Run application", "status": "passed"})
            
            # All steps passed
            test_result["status"] = "passed"
            test_result["output"] = stdout
        
        self.test_results["tests"].append(test_result)
    
    def run_all_tests(self):
        """Run tests for both backup and corrected requirements."""
        self.log("\n" + "="*70)
        self.log("AUTOMATED DEPENDENCY TESTING")
        self.log("="*70)
        self.log(f"Platform: {self.test_results['system_info']['platform']}")
        self.log(f"Python: {self.test_results['system_info']['python_version']}")
        self.log(f"Timestamp: {self.test_results['timestamp']}")
        self.log("="*70 + "\n")
        
        backup_file = self.project_root / "requirements_backup.txt"
        updated_file = self.project_root / "requirements.txt"
        
        # Test backup (original with issues)
        if backup_file.exists():
            self.test_requirements_file(
                backup_file,
                "Original Requirements (with issues)"
            )
        else:
            self.log(f"Warning: Backup file not found: {backup_file}", "warning")
        
        # Test updated (corrected)
        if updated_file.exists():
            self.test_requirements_file(
                updated_file,
                "Updated Requirements (corrected)"
            )
        else:
            self.log(f"Warning: Updated file not found: {updated_file}", "error")
        
        # Print summary
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print test summary."""
        self.log("\n" + "="*70)
        self.log("TEST SUMMARY")
        self.log("="*70)
        
        for test in self.test_results["tests"]:
            status_icon = "✓" if test["status"] == "passed" else "✗"
            self.log(f"{status_icon} {test['name']}: {test['status'].upper()}")
            
            for step in test["steps"]:
                step_icon = "  ✓" if step["status"] == "passed" else "  ✗"
                self.log(f"{step_icon} {step['name']}")
            
            if test["errors"]:
                for error in test["errors"]:
                    self.log(f"    Error: {error}", "error")
        
        self.log("="*70 + "\n")
    
    def save_results(self):
        """Save test results as JSON."""
        log_dir = self.project_root / "logs"
        results_file = log_dir / "test_results.json"
        
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log(f"Test results saved to: {results_file}")


def main():
    """Main entry point."""
    tester = DependencyTester("test_run.log")
    tester.run_all_tests()


if __name__ == "__main__":
    main()
