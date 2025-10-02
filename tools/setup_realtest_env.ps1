# PowerShell script to create a Python virtual environment named realtestextract and install tooling requirements.

param(
    [switch]$Force = $false
)

# Enable strict error handling
$ErrorActionPreference = "Stop"

# Get the root directory (parent of tools directory)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RootDir = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $RootDir "realtestextract"
$RequirementsFile = Join-Path $RootDir "tools\requirements.txt"

Write-Host "Root directory: $RootDir"
Write-Host "Virtual environment path: $VenvPath"
Write-Host "Requirements file: $RequirementsFile"

# Check if requirements file exists
if (-not (Test-Path $RequirementsFile)) {
    Write-Error "Requirements file not found: $RequirementsFile"
    exit 1
}

# Check if virtual environment already exists
if (Test-Path $VenvPath) {
    if ($Force) {
        Write-Host "Removing existing virtual environment..."
        Remove-Item -Path $VenvPath -Recurse -Force
    } else {
        Write-Host "Virtual environment already exists at $VenvPath"
        Write-Host "Use -Force parameter to recreate it."
        exit 0
    }
}

try {
    Write-Host "Creating virtual environment..."
    python -m venv "$VenvPath"
    
    # Determine the executable paths based on OS
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        $PythonExecutable = Join-Path $VenvPath "Scripts\python.exe"
        $PipExecutable = Join-Path $VenvPath "Scripts\pip.exe"
    } else {
        $PythonExecutable = Join-Path $VenvPath "bin\python"
        $PipExecutable = Join-Path $VenvPath "bin\pip"
    }
    
    Write-Host "Upgrading pip..."
    & $PythonExecutable -m pip install --upgrade pip
    
    Write-Host "Installing requirements from $RequirementsFile..."
    & $PipExecutable install -r "$RequirementsFile"
    
    Write-Host ""
    Write-Host "✓ Virtual environment created successfully at: $VenvPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "To activate the environment, run:" -ForegroundColor Yellow
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        Write-Host "  $VenvPath\Scripts\Activate.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "  source $VenvPath/bin/activate" -ForegroundColor Cyan
    }
    Write-Host ""
    Write-Host "To deactivate, run:" -ForegroundColor Yellow
    Write-Host "  deactivate" -ForegroundColor Cyan
    
} catch {
    Write-Error "Failed to create virtual environment: $_"
    exit 1
}