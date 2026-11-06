# English-Hindi Cross-Lingual Academic RAG Experimentation Platform
# PowerShell Launcher Script

$Host.UI.RawUI.WindowTitle = "English-Hindi Cross-Lingual Academic RAG Platform"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  English-Hindi Cross-Lingual Academic RAG Experimentation Platform" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Resolve path to cross_lingual_rag
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (Test-Path (Join-Path $ScriptDir "cross_lingual_rag\server.py")) {
    Set-Location (Join-Path $ScriptDir "cross_lingual_rag")
}

if (-not (Test-Path "server.py")) {
    Write-Host "[ERROR] server.py not found in current directory: $(Get-Location)" -ForegroundColor Red
    Write-Host "Please ensure the zip file was fully extracted before running." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    Exit 1
}

# 2. Detect Python executable
$PythonCmd = $null
$Candidates = @("python", "py", "python3")

foreach ($cmd in $Candidates) {
    try {
        $test = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -or $test -match "Python \d") {
            $PythonCmd = $cmd
            break
        }
    } catch {
        # ignore
    }
}

if (-not $PythonCmd) {
    Write-Host "[ERROR] Python was not found in your system PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.10+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Important: Check '[X] Add python.exe to PATH' during installation." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    Exit 1
}

Write-Host "[*] Using Python: $PythonCmd" -ForegroundColor Green
& $PythonCmd --version

# 3. Check dependencies
Write-Host "[*] Checking Python dependencies..." -ForegroundColor Gray
$CheckDeps = & $PythonCmd -c "import fastapi, uvicorn, pypdf, sentence_transformers, deep_translator" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[*] Core dependencies verified!" -ForegroundColor Green
} else {
    Write-Host "[*] Installing missing dependencies from requirements.txt..." -ForegroundColor Yellow
    & $PythonCmd -m pip install -r requirements.txt
}

# 4. Check .env
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[*] Created .env configuration file." -ForegroundColor Gray
}

# 5. Launch browser and server
$Port = 8000
$Url = "http://127.0.0.1:$Port"
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  Starting Cross-Lingual Academic RAG Studio on $Url" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host ""

Start-Process $Url

try {
    & $PythonCmd server.py
} catch {
    Write-Host "[ERROR] Failed to run server: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"

