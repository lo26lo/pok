# ================================================================
# Install PyTorch Nightly (CUDA 12.8) + auto-fix VC++ Redist
# Safe ASCII version (no accents/ampersand)
# ================================================================

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
               ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "Elevation to Administrator is required. Relaunching..."
        $psi = @{
            FilePath    = "powershell.exe"
            ArgumentList = "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
            Verb        = "RunAs"
            WindowStyle = "Normal"
        }
        Start-Process @psi
        exit
    }
}

function Get-VCppState {
    $key = "HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
    $state = @{ Installed = $false; Version = $null }
    if (Test-Path $key) {
        $p = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
        if ($p -and $p.Installed -eq 1) { $state.Installed = $true; $state.Version = $p.Version }
    }
    return $state
}

function Install-VCpp {
    param([string]$Url = "https://aka.ms/vs/17/release/vc_redist.x64.exe")
    $dst = Join-Path $env:TEMP "vc_redist.x64.exe"
    Write-Host "Downloading VC++ Redistributable x64..."
    try { Invoke-WebRequest -Uri $Url -OutFile $dst }
    catch { Write-Host "Download failed: $($_.Exception.Message)" -ForegroundColor Red; throw }
    Write-Host "Installing VC++ Redistributable silently..."
    $proc = Start-Process -FilePath $dst -ArgumentList "/install","/quiet","/norestart" -Wait -PassThru
    if ($proc.ExitCode -ne 0) { Write-Host "VC++ installer exit code: $($proc.ExitCode)." -ForegroundColor Yellow }
}

Ensure-Admin

Write-Host "== 1) Check/Install VC++ 2015-2022 x64 =="
$vc = Get-VCppState
if ($vc.Installed) { Write-Host "VC++ present. Version: $($vc.Version)" }
else {
    Write-Host "VC++ missing -> installing..."
    Install-VCpp
    $vc2 = Get-VCppState
    if (-not $vc2.Installed) { Write-Host "Warning: VC++ not detected after installer." -ForegroundColor Yellow }
    else { Write-Host "VC++ installed. Version: $($vc2.Version)" }
}

Write-Host "== 2) Create/Activate .venv with Python 3.12 =="
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Creating venv (.venv)..."
    py -3.12 -m venv .venv
}
& .\.venv\Scripts\Activate.ps1

Write-Host "Updating pip/setuptools/wheel..."
python -m pip install -U pip setuptools wheel

Write-Host "== 3) Uninstall potentially conflicting packages =="
pip uninstall -y torch torchvision torchaudio torch-directml onnxruntime onnxruntime-gpu | Out-Null

Write-Host "== 4) Temporarily remove CUDA toolkits from PATH =="
$global:OLDPATH = $env:PATH
$env:PATH = ($env:PATH -split ';' | Where-Object {$_ -notmatch 'NVIDIA GPU Computing Toolkit\\CUDA'}) -join ';'

Write-Host "== 5) Install torch stable cu124 (forced, no cache) =="
pip install --index-url https://download.pytorch.org/whl/cu124 torch torchvision torchaudio --upgrade --force-reinstall --no-cache-dir
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR installing torch" -ForegroundColor Red; $env:PATH=$global:OLDPATH; exit 1 }

Write-Host "== 6) Test torch import and CUDA =="
$pyTest = @"
import torch
print('Torch version:', torch.__version__)
print('CUDA version in torch:', torch.version.cuda)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('Compute Capability:', torch.cuda.get_device_capability(0))
"@

# Write test to a temp file and run it
$tmpPy = Join-Path $env:TEMP ("torch_test_{0}.py" -f ([System.Guid]::NewGuid().ToString("N")))
Set-Content -Path $tmpPy -Value $pyTest -Encoding ASCII
python $tmpPy
$torchOk = $LASTEXITCODE -eq 0
Remove-Item $tmpPy -ErrorAction SilentlyContinue

if (-not $torchOk) {
    Write-Host "Warning: torch import failed (possibly c10.dll). Try rebooting Windows, then rerun this script." -ForegroundColor Yellow
}

Write-Host "== 7) Restore original PATH =="
$env:PATH = $global:OLDPATH

Write-Host "Done."
