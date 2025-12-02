"""
Automated Testing Script
This script automatically detects the runtime environment (Windows/Linux/Docker)
and tests both the original (requirements_backup.txt) and fixed (requirements.txt)
dependency configurations.
"""

import os
import sys
import platform
import subprocess
import logging
import json
from pathlib import Path
from datetime import datetime
import shutil


class AutoTester:
    """Automated testing for dependency configurations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.log_dir = self.project_root / "logs"
        self.log_file = self.log_dir / "test_run.log"
        self.env_type = self.detect_environment()
        
        # Ensure logs directory exists
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging to both file and console"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def detect_environment(self):
        """Detect the current runtime environment"""
        if os.path.exists('/.dockerenv'):
            return 'Docker'
        elif platform.system() == 'Windows':
            return 'Windows'
        elif platform.system() in ['Linux', 'Darwin']:
            return 'Linux/macOS'
        else:
            return 'Unknown'
    
    def log_separator(self, title):
        """Log a formatted separator"""
        self.logger.info("=" * 80)
        self.logger.info(f"  {title}")
        self.logger.info("=" * 80)
    
    def run_command(self, cmd, cwd=None, timeout=300):
        """Run a shell command and return the result"""
        try:
            if isinstance(cmd, str):
                shell = True
            else:
                shell = False
                
            result = subprocess.run(
                cmd,
                cwd=cwd,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)
    
    def get_python_executable(self, venv_path):
        """Get the Python executable path for the virtual environment"""
        if self.env_type == 'Windows':
            return venv_path / "Scripts" / "python.exe"
        else:
            return venv_path / "bin" / "python"
    
    def get_pip_executable(self, venv_path):
        """Get the pip executable path for the virtual environment"""
        if self.env_type == 'Windows':
            return venv_path / "Scripts" / "pip.exe"
        else:
            return venv_path / "bin" / "pip"
    
    def create_virtual_environment(self, env_name):
        """Create a clean virtual environment"""
        venv_path = self.project_root / env_name
        
        # Remove existing environment
        if venv_path.exists():
            self.logger.info(f"Removing existing environment: {env_name}")
            shutil.rmtree(venv_path)
        
        self.logger.info(f"Creating virtual environment: {env_name}")
        returncode, stdout, stderr = self.run_command([sys.executable, "-m", "venv", str(venv_path)])
        
        if returncode != 0:
            self.logger.error(f"Failed to create virtual environment: {stderr}")
            return None
        
        self.logger.info(f"Virtual environment created successfully: {env_name}")
        return venv_path
    
    def install_dependencies(self, venv_path, requirements_file):
        """Install dependencies in the virtual environment"""
        pip_exe = self.get_pip_executable(venv_path)
        req_file = self.project_root / requirements_file
        
        if not req_file.exists():
            self.logger.error(f"Requirements file not found: {requirements_file}")
            return False
        
        self.logger.info(f"Installing dependencies from {requirements_file}...")
        
        # Upgrade pip first
        returncode, stdout, stderr = self.run_command(
            [str(pip_exe), "install", "--upgrade", "pip"],
            timeout=120
        )
        
        if returncode != 0:
            self.logger.warning(f"Pip upgrade warning: {stderr}")
        
        # Install dependencies
        returncode, stdout, stderr = self.run_command(
            [str(pip_exe), "install", "-r", str(req_file)],
            timeout=600
        )
        
        if returncode != 0:
            self.logger.error(f"Failed to install dependencies: {stderr}")
            self.logger.error(f"stdout: {stdout}")
            return False
        
        self.logger.info("Dependencies installed successfully")
        self.logger.info(f"Installation output:\n{stdout}")
        return True
    
    def create_test_data(self):
        """Create sample CSV data for testing"""
        sample_csv = self.project_root / "sample.csv"
        
        if sample_csv.exists():
            self.logger.info("Sample data already exists")
            return True
        
        self.logger.info("Creating sample test data...")
        
        csv_content = """target,feature1,feature2,feature3
10.5,1.2,3.4,5.6
20.3,2.1,4.5,6.7
15.7,1.8,3.9,5.2
25.1,2.5,5.1,7.3
18.9,2.0,4.2,6.1
30.2,3.1,5.8,8.2
12.4,1.5,3.7,5.9
22.8,2.3,4.8,7.1
17.6,1.9,4.1,6.3
28.3,2.8,5.4,7.8
"""
        
        try:
            with open(sample_csv, 'w') as f:
                f.write(csv_content)
            self.logger.info("Sample data created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create sample data: {e}")
            return False
    
    def run_application_test(self, venv_path, test_name):
        """Run the application in the given virtual environment"""
        python_exe = self.get_python_executable(venv_path)
        app_file = self.project_root / "app.py"
        
        if not app_file.exists():
            self.logger.error("app.py not found")
            return False
        
        self.logger.info(f"Running application test: {test_name}")
        
        returncode, stdout, stderr = self.run_command(
            [str(python_exe), str(app_file)],
            cwd=str(self.project_root),
            timeout=60
        )
        
        if returncode != 0:
            self.logger.error(f"Application test failed: {test_name}")
            self.logger.error(f"Error output:\n{stderr}")
            if stdout:
                self.logger.error(f"stdout:\n{stdout}")
            return False
        
        self.logger.info(f"Application test passed: {test_name}")
        self.logger.info(f"Output:\n{stdout}")
        return True
    
    def verify_imports(self, venv_path, test_name):
        """Verify that all required packages can be imported"""
        python_exe = self.get_python_executable(venv_path)
        
        test_script = """
import sys
import json

packages_to_test = [
    'pandas',
    'numpy',
    'sklearn',
    'requests',
    'yaml',
    'matplotlib',
    'tqdm',
    'dateutil',
    'joblib',
    'rich'
]

results = {}
for package in packages_to_test:
    try:
        __import__(package)
        results[package] = 'SUCCESS'
    except ImportError as e:
        results[package] = f'FAILED: {str(e)}'

print(json.dumps(results, indent=2))
"""
        
        self.logger.info(f"Verifying package imports: {test_name}")
        
        returncode, stdout, stderr = self.run_command(
            [str(python_exe), "-c", test_script],
            timeout=30
        )
        
        if returncode != 0:
            self.logger.error(f"Import verification failed: {test_name}")
            self.logger.error(f"Error: {stderr}")
            return False
        
        try:
            import_results = json.loads(stdout)
            all_success = all(result == 'SUCCESS' for result in import_results.values())
            
            self.logger.info(f"Import verification results:")
            for package, status in import_results.items():
                self.logger.info(f"  {package}: {status}")
            
            return all_success
        except Exception as e:
            self.logger.error(f"Failed to parse import results: {e}")
            return False
    
    def test_environment(self, env_name, requirements_file):
        """Test a complete environment setup"""
        self.log_separator(f"Testing Environment: {env_name}")
        
        results = {
            'environment': env_name,
            'requirements_file': requirements_file,
            'timestamp': datetime.now().isoformat(),
            'platform': self.env_type,
            'steps': {}
        }
        
        # Step 1: Create virtual environment
        venv_path = self.create_virtual_environment(env_name)
        results['steps']['create_venv'] = venv_path is not None
        
        if not venv_path:
            self.logger.error(f"Failed to create environment: {env_name}")
            results['overall_success'] = False
            return results
        
        # Step 2: Install dependencies
        install_success = self.install_dependencies(venv_path, requirements_file)
        results['steps']['install_dependencies'] = install_success
        
        if not install_success:
            self.logger.error(f"Failed to install dependencies for: {env_name}")
            results['overall_success'] = False
            return results
        
        # Step 3: Verify imports
        imports_success = self.verify_imports(venv_path, env_name)
        results['steps']['verify_imports'] = imports_success
        
        # Step 4: Create test data
        test_data_success = self.create_test_data()
        results['steps']['create_test_data'] = test_data_success
        
        # Step 5: Run application
        app_success = self.run_application_test(venv_path, env_name)
        results['steps']['run_application'] = app_success
        
        # Overall result
        results['overall_success'] = all(results['steps'].values())
        
        if results['overall_success']:
            self.logger.info(f"✓ Environment test PASSED: {env_name}")
        else:
            self.logger.error(f"✗ Environment test FAILED: {env_name}")
        
        return results
    
    def cleanup_environments(self):
        """Clean up test virtual environments"""
        self.logger.info("Cleaning up test environments...")
        
        for env_name in ['test_env_backup', 'test_env_fixed']:
            venv_path = self.project_root / env_name
            if venv_path.exists():
                try:
                    shutil.rmtree(venv_path)
                    self.logger.info(f"Removed: {env_name}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {env_name}: {e}")
    
    def generate_summary_report(self, backup_results, fixed_results):
        """Generate a summary comparison report"""
        self.log_separator("TEST SUMMARY REPORT")
        
        self.logger.info(f"Environment Type: {self.env_type}")
        self.logger.info(f"Test Timestamp: {datetime.now().isoformat()}")
        self.logger.info("")
        
        # Backup environment results
        self.logger.info("BACKUP ENVIRONMENT (requirements_backup.txt):")
        self.logger.info(f"  Overall Result: {'PASSED ✓' if backup_results['overall_success'] else 'FAILED ✗'}")
        for step, result in backup_results['steps'].items():
            status = 'PASSED ✓' if result else 'FAILED ✗'
            self.logger.info(f"  - {step}: {status}")
        
        self.logger.info("")
        
        # Fixed environment results
        self.logger.info("FIXED ENVIRONMENT (requirements.txt):")
        self.logger.info(f"  Overall Result: {'PASSED ✓' if fixed_results['overall_success'] else 'FAILED ✗'}")
        for step, result in fixed_results['steps'].items():
            status = 'PASSED ✓' if result else 'FAILED ✗'
            self.logger.info(f"  - {step}: {status}")
        
        self.logger.info("")
        
        # Conclusion
        if not backup_results['overall_success'] and fixed_results['overall_success']:
            self.logger.info("CONCLUSION: ✓ Dependency fixes RESOLVED the issues!")
            self.logger.info("The updated requirements.txt successfully fixes the problems")
            self.logger.info("present in the original requirements_backup.txt.")
        elif backup_results['overall_success'] and fixed_results['overall_success']:
            self.logger.info("CONCLUSION: ✓ Both environments work correctly.")
            self.logger.info("The updated requirements.txt maintains compatibility")
            self.logger.info("while using more secure and up-to-date packages.")
        else:
            self.logger.warning("CONCLUSION: ⚠ Further investigation needed.")
            self.logger.warning("Please review the detailed logs above.")
        
        # Save JSON report
        report_file = self.log_dir / "test_results.json"
        report_data = {
            'environment_type': self.env_type,
            'timestamp': datetime.now().isoformat(),
            'backup_environment': backup_results,
            'fixed_environment': fixed_results
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"\nDetailed JSON report saved to: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save JSON report: {e}")
    
    def run_all_tests(self):
        """Run all automated tests"""
        self.log_separator("AUTOMATED DEPENDENCY TESTING")
        self.logger.info(f"Detected Environment: {self.env_type}")
        self.logger.info(f"Project Root: {self.project_root}")
        self.logger.info(f"Log File: {self.log_file}")
        self.logger.info("")
        
        # Test backup environment (should fail or have issues)
        backup_results = self.test_environment('test_env_backup', 'requirements_backup.txt')
        
        self.logger.info("")
        
        # Test fixed environment (should succeed)
        fixed_results = self.test_environment('test_env_fixed', 'requirements.txt')
        
        self.logger.info("")
        
        # Generate summary
        self.generate_summary_report(backup_results, fixed_results)
        
        # Cleanup
        self.logger.info("")
        self.cleanup_environments()
        
        self.log_separator("TESTING COMPLETE")
        self.logger.info(f"Full logs available at: {self.log_file}")
        
        return fixed_results['overall_success']


def main():
    """Main entry point"""
    try:
        tester = AutoTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
