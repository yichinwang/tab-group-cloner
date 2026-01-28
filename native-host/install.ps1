# Installation script for Tab Group Cloner Native Messaging Host (Windows)
# Run this in PowerShell with: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Tab Group Cloner - Native Host Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "tab_cloner_host.py"

Write-Host "Script location: $ScriptDir" -ForegroundColor Green
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $PythonVersion = & python --version 2>&1
    Write-Host "Found: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed. Please install Python 3.8 or higher." -ForegroundColor Red
    Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"
& pip install -r $RequirementsFile
Write-Host ""

# Create manifest directory
$ManifestDir = "$env:APPDATA\Google\Chrome\NativeMessagingHosts"
Write-Host "Creating manifest directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $ManifestDir | Out-Null
Write-Host ""

# Create the manifest file
Write-Host "Creating native messaging host manifest..." -ForegroundColor Yellow
$ManifestFile = Join-Path $ManifestDir "com.tabcloner.host.json"

# Escape backslashes for JSON
$PythonScriptEscaped = $PythonScript -replace '\\', '\\'

$ManifestContent = @"
{
  "name": "com.tabcloner.host",
  "description": "Tab Group Cloner Native Messaging Host",
  "path": "$PythonScriptEscaped",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://EXTENSION_ID_PLACEHOLDER/"
  ]
}
"@

$ManifestContent | Out-File -FilePath $ManifestFile -Encoding utf8
Write-Host "Manifest created at: $ManifestFile" -ForegroundColor Green
Write-Host ""

# Create registry entry
Write-Host "Creating registry entry..." -ForegroundColor Yellow
$RegPath = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\com.tabcloner.host"
New-Item -Path $RegPath -Force | Out-Null
New-ItemProperty -Path $RegPath -Name "(Default)" -Value $ManifestFile -PropertyType String -Force | Out-Null
Write-Host "Registry entry created" -ForegroundColor Green
Write-Host ""

# Final instructions
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install the Chrome extension"
Write-Host "2. Note the extension ID from chrome://extensions"
Write-Host "3. Edit the manifest file and replace EXTENSION_ID_PLACEHOLDER with your actual extension ID:"
Write-Host "   $ManifestFile"
Write-Host ""
Write-Host "4. Install Sidekick browser from https://www.meetsidekick.com/"
Write-Host "5. Download ChromeDriver from https://chromedriver.chromium.org/ and add to PATH"
Write-Host ""
Write-Host "Logs will be written to: $env:USERPROFILE\tab_cloner_host.log"
Write-Host ""
