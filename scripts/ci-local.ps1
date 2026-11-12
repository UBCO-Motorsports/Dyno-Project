# Runs the same steps as .github/workflows/tests.yml (one Python version).
# Usage: .\scripts\ci-local.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

function Step([string]$Name, [scriptblock]$Block) {
    Write-Host "==> $Name"
    & $Block
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
        throw "FAILED step: $Name (exit $LASTEXITCODE)"
    }
}

$py = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

Step "pip install -e .[dev]" { & $py -m pip install -e ".[dev]" }
Step "ruff check ." { & $py -m ruff check . }
Step "pytest -q" { & $py -m pytest -q }

Write-Host "==> guardrails"
$guard = Join-Path $PSScriptRoot "check_guardrails.sh"
if (Get-Command bash -ErrorAction SilentlyContinue) {
    bash $guard
    if ($LASTEXITCODE -ne 0) { throw "FAILED step: guardrails" }
} else {
    # PowerShell fallback of scripts/check_guardrails.sh
    $hits = Get-ChildItem -Path "src\dyno" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue |
        Select-String -Pattern 'serial\.Serial\(|can\.interface\.Bus\(|can\.Bus\(|python-can|tractive.?battery|spin_motor\(|drive_valve\(|set_valve_position\('
    if ($hits) {
        $hits | ForEach-Object { Write-Host $_.Line }
        throw "FAILED step: guardrails (src/dyno must not open live hardware or actuate the rig)"
    }
    Write-Host "guardrails: ok"
}

Write-Host "ci-local: all steps passed"
