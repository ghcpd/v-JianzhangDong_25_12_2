<#
Simple PowerShell helper to detect presence of Windows build tools commonly required to compile Python packages
that need a C/C++ compiler (eg. NumPy older versions building from source).

Checks performed:
- 'cl.exe' (Microsoft Visual C++ compiler) available in PATH
- 'vswhere.exe' presence (installed with Visual Studio / Build Tools)

This script only detects availability and prints brief steps to install Visual Studio Build Tools using Chocolatey or the web installer.
#>

Write-Host "Checking for Windows C/C++ Build Tools..." -ForegroundColor Cyan

$cl = Get-Command cl -ErrorAction SilentlyContinue
$vswhere = Get-Command vswhere -ErrorAction SilentlyContinue

if ($cl) {
    Write-Host "cl.exe found at:" $cl.Path -ForegroundColor Green
} else {
    Write-Host "cl.exe not found in PATH." -ForegroundColor Yellow
}

if ($vswhere) {
    Write-Host "vswhere found at:" $vswhere.Path -ForegroundColor Green
} else {
    Write-Host "vswhere not found (Visual Studio Build Tools may not be installed)." -ForegroundColor Yellow
}

if (-not $cl -or -not $vswhere) {
    Write-Host "\nRecommended options to add build tools:" -ForegroundColor Cyan
    Write-Host "1) Install Visual Studio Build Tools (recommended) via Chocolatey (if you have choco):" -ForegroundColor White
    Write-Host "   choco install visualstudio2022buildtools --package-parameters \"--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive\" -y" -ForegroundColor Gray
    Write-Host "2) Or download directly from Microsoft:" -ForegroundColor White
    Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
    Write-Host "3) Alternatively use WSL or Docker to run tests in Linux where wheels might be available." -ForegroundColor Gray
}

Write-Host "\nAfter installing, open a new terminal and run: python -m pip install --upgrade pip setuptools wheel" -ForegroundColor Cyan
