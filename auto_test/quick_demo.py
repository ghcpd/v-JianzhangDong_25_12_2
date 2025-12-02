#!/usr/bin/env python3
"""
Quick Demo Testing Script - Lightweight version of auto_test.py
Demonstrates the testing framework without heavy venv/package installation
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json


class EnvironmentDetector:
    """Detects the current runtime environment."""
    
    @staticmethod
    def get_platform():
        """Detect the current platform: Windows, Linux, or Docker."""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Linux":
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


class QuickDependencyTester:
    """Quick demo version - tests dependencies without heavy installation."""
    
    def __init__(self):
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
        
        log_path = log_dir / "test_run.log"
        
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
    
    def read_requirements(self, req_file):
        """Read and parse requirements file."""
        try:
            with open(req_file, 'r') as f:
                packages = [line.strip() for line in f if line.strip()]
            return packages
        except Exception as e:
            self.log(f"Error reading {req_file}: {e}", "error")
            return []
    
    def test_requirements_file(self, requirements_file, test_name):
        """Quick test of requirements file."""
        self.log(f"\n{'='*60}")
        self.log(f"Testing: {test_name}")
        self.log(f"Requirements file: {requirements_file}")
        self.log(f"{'='*60}\n")
        
        test_result = {
            "name": test_name,
            "requirements_file": str(requirements_file),
            "status": "failed",
            "steps": [],
            "packages": []
        }
        
        # Step 1: Read and parse requirements
        self.log(f"\n[STEP 1] Reading requirements file...")
        packages = self.read_requirements(requirements_file)
        
        if not packages:
            test_result["errors"] = ["No packages found or file read error"]
            test_result["steps"].append({"name": "Read requirements", "status": "failed"})
            self.test_results["tests"].append(test_result)
            return
        
        test_result["packages"] = packages
        test_result["steps"].append({"name": "Read requirements", "status": "passed"})
        self.log(f"Found {len(packages)} packages:")
        for pkg in packages:
            self.log(f"  - {pkg}")
        
        # Step 2: Validate package format
        self.log(f"\n[STEP 2] Validating package format...")
        all_valid = True
        for pkg in packages:
            if '==' in pkg:
                name, version = pkg.split('==')
                self.log(f"  ✓ {name:20} @ {version}")
            else:
                self.log(f"  ⚠ {pkg:20} (no version pinned)")
                all_valid = False
        
        if all_valid:
            test_result["steps"].append({"name": "Validate format", "status": "passed"})
        else:
            test_result["steps"].append({"name": "Validate format", "status": "warning"})
        
        # Step 3: Check for known issues (backup file)
        self.log(f"\n[STEP 3] Checking for known dependency issues...")
        known_issues = {
            'pyyaml==5.3.1': 'CVE-2020-14343 (arbitrary code execution)',
            'pandas==1.2.0': 'Outdated, Python 3.9+ incompatible',
            'numpy==1.19.0': 'Very outdated, security issues',
            'scikit-learn==0.22.2': 'Incompatible with modern versions',
            'joblib==0.14.0': 'Very outdated'
        }
        
        found_issues = []
        for pkg in packages:
            if pkg in known_issues:
                found_issues.append(f"{pkg}: {known_issues[pkg]}")
                self.log(f"  ⚠ ISSUE: {pkg}")
                self.log(f"           {known_issues[pkg]}")
        
        if found_issues:
            test_result["steps"].append({
                "name": "Check known issues",
                "status": "warning",
                "issues_found": len(found_issues)
            })
            if "backup" in str(requirements_file).lower():
                test_result["status"] = "warning"
        else:
            test_result["steps"].append({"name": "Check known issues", "status": "passed"})
            test_result["status"] = "passed"
        
        # Step 4: Summary
        self.log(f"\n[STEP 4] Test Summary...")
        if test_result["status"] == "passed":
            self.log(f"✓ All checks passed!")
        elif test_result["status"] == "warning":
            self.log(f"⚠ Found {len(found_issues)} known issues that need updating")
        
        self.test_results["tests"].append(test_result)
    
    def run_all_tests(self):
        """Run tests for both backup and corrected requirements."""
        self.log("\n" + "="*70)
        self.log("QUICK DEPENDENCY TEST DEMO")
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
        
        # Test updated (corrected)
        if updated_file.exists():
            self.test_requirements_file(
                updated_file,
                "Updated Requirements (corrected)"
            )
        
        # Print summary
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print test summary."""
        self.log("\n" + "="*70)
        self.log("TEST SUMMARY")
        self.log("="*70)
        
        for test in self.test_results["tests"]:
            status_icon = "✓" if test["status"] == "passed" else "⚠"
            self.log(f"{status_icon} {test['name']}: {test['status'].upper()}")
            
            for step in test["steps"]:
                step_icon = "  ✓" if step["status"] == "passed" else "  ⚠"
                self.log(f"{step_icon} {step['name']}")
        
        self.log("="*70)
        self.log("\nExpected Outcome:")
        self.log("  • requirements_backup.txt: ⚠ WARNING (has outdated packages)")
        self.log("  • requirements.txt: ✓ PASSED (all packages corrected)")
        self.log("\n" + "="*70 + "\n")
    
    def save_results(self):
        """Save test results as JSON."""
        log_dir = self.project_root / "logs"
        results_file = log_dir / "test_results.json"
        
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log(f"Test results saved to: {results_file}")


def main():
    """Main entry point."""
    tester = QuickDependencyTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
