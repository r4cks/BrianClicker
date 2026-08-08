```powershell
# ============================================================
# BRIAN CLICKER - BUILD SCRIPT
# ============================================================

Write-Host ""
Write-Host "========================================"
Write-Host "       BRIAN CLICKER BUILD"
Write-Host "========================================"
Write-Host ""

# ------------------------------------------------------------
# Check required files
# ------------------------------------------------------------

if (!(Test-Path ".\BrianClicker.py")) {
    Write-Host "ERROR: BrianClicker.py was not found."
    Read-Host "Press Enter to exit"
    exit
}

if (!(Test-Path ".\icon.ico")) {
    Write-Host "ERROR: icon.ico was not found."
    Read-Host "Press Enter to exit"
    exit
}

if (!(Test-Path ".\logo.png")) {
    Write-Host "ERROR: logo.png was not found."
    Read-Host "Press Enter to exit"
    exit
}

# ------------------------------------------------------------
# Remove old build files
# ------------------------------------------------------------

Write-Host "Cleaning old build files..."

if (Test-Path ".\build") {
    Remove-Item ".\build" -Recurse -Force
}

if (Test-Path ".\dist") {
    Remove-Item ".\dist" -Recurse -Force
}

if (Test-Path ".\BrianClicker.spec") {
    Remove-Item ".\BrianClicker.spec" -Force
}

# ------------------------------------------------------------
# Build arguments
# ------------------------------------------------------------

$pyinstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--onefile",
    "--windowed",
    "--name",
    "BrianClicker",
    "--icon",
    ".\icon.ico"
)

# ------------------------------------------------------------
# Include logo.png
# ------------------------------------------------------------

$pyinstallerArgs += "--add-data"
$pyinstallerArgs += ".\logo.png;."

# ------------------------------------------------------------
# Include icon.ico
# ------------------------------------------------------------

$pyinstallerArgs += "--add-data"
$pyinstallerArgs += ".\icon.ico;."

# ------------------------------------------------------------
# Python script
# ------------------------------------------------------------

$pyinstallerArgs += ".\BrianClicker.py"

# ------------------------------------------------------------
# Build
# ------------------------------------------------------------

Write-Host ""
Write-Host "Building Brian Clicker..."
Write-Host ""

python -m PyInstaller @pyinstallerArgs

# ------------------------------------------------------------
# Check result
# ------------------------------------------------------------

if (Test-Path ".\dist\BrianClicker.exe") {

    Write-Host ""
    Write-Host "========================================"
    Write-Host "          BUILD SUCCESSFUL"
    Write-Host "========================================"
    Write-Host ""

    Write-Host "EXE created at:"
    Write-Host ""
    Write-Host "dist\BrianClicker.exe"
    Write-Host ""

} else {

    Write-Host ""
    Write-Host "========================================"
    Write-Host "             BUILD FAILED"
    Write-Host "========================================"
    Write-Host ""
}

Read-Host "Press Enter to exit"
```
