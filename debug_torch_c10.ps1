# ============== debug_torch_c10.ps1 ==============

# 0) Activer le venv
Write-Host "== Activate venv (.venv) =="
& .\.venv\Scripts\Activate.ps1

# 1) Versions de base
Write-Host "== Basic versions =="
python --version
pip --version

# 2) Driver et nvcuda.dll
Write-Host "== Check NVIDIA driver and nvcuda.dll =="
nvidia-smi
Write-Host "Looking for nvcuda.dll in System32..."
where nvcuda.dll

# 3) Test import torch brut
Write-Host "== Torch import (raw) =="
$py1 = @"
import sys, torch
print('Python:', sys.version)
print('Torch:', torch.__version__)
print('Torch CUDA version:', torch.version.cuda)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('CC:', torch.cuda.get_device_capability(0))
"@
$tmp1 = Join-Path $env:TEMP ("torch_import_{0}.py" -f ([guid]::NewGuid().ToString('N')))
Set-Content -Path $tmp1 -Value $py1 -Encoding ASCII
python $tmp1
$rawOk = $LASTEXITCODE -eq 0
Remove-Item $tmp1 -ErrorAction SilentlyContinue

if (-not $rawOk) {
    Write-Host "Raw import failed. Retrying with sanitized PATH (remove CUDA toolkits) ..."
    # 4) Nettoyage PATH des toolkits CUDA
    $global:OLDPATH = $env:PATH
    $env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notmatch 'NVIDIA GPU Computing Toolkit\\CUDA' }) -join ';'

    # 5) Retest import torch avec PATH nettoye
    Write-Host "== Torch import (sanitized PATH) =="
    $py2 = @"
import sys, torch
print('Python:', sys.version)
print('Torch:', torch.__version__)
print('Torch CUDA version:', torch.version.cuda)
print('CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
    print('CC:', torch.cuda.get_device_capability(0))
"@
    $tmp2 = Join-Path $env:TEMP ("torch_import_clean_{0}.py" -f ([guid]::NewGuid().ToString('N')))
    Set-Content -Path $tmp2 -Value $py2 -Encoding ASCII
    python $tmp2
    $cleanOk = $LASTEXITCODE -eq 0
    Remove-Item $tmp2 -ErrorAction SilentlyContinue

    # 6) Restaurer PATH
    $env:PATH = $global:OLDPATH

    if ($cleanOk) {
        Write-Host "OK with sanitized PATH. Your global PATH is pulling wrong CUDA DLLs."
        exit 0
    } else {
        Write-Host "Still failing after sanitizing PATH. Likely VC++ runtime or driver mismatch."
        Write-Host "Fixes: repair/install VC++ 2015-2022 x64 and reboot; or clean reinstall NVIDIA driver."
        exit 1
    }
} else {
    Write-Host "Raw import OK. Torch is fine in this shell."
    exit 0
}
# ===================================================
