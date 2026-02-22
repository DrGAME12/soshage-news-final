param(
  [string]$InputDir = "out\pdf",
  [string]$OutputDir = "out\pdf_logo_overlay",
  [string]$LogoPath = "",
  [switch]$FirstPageOnly,
  [switch]$EraseUnder,
  [double]$WidthRatio = 0.135,
  [double]$MarginXRatio = 0.018,
  [double]$MarginYRatio = 0.015,
  [string]$EraseColor = "#ffffff",
  [int]$Limit = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = (Resolve-Path ".").Path
$python = Join-Path $root ".venv\Scripts\python.exe"
$script = Join-Path $root "scripts\overlay_logo_on_pdfs.py"

if (-not (Test-Path -LiteralPath $script)) {
  throw "Script not found: $script"
}
if (-not (Test-Path -LiteralPath $python)) {
  $python = "python"
}
if ([string]::IsNullOrWhiteSpace($LogoPath)) {
  throw "Specify -LogoPath (PNG recommended)."
}

$args = @(
  $script,
  "--input-dir", (Join-Path $root $InputDir),
  "--output-dir", (Join-Path $root $OutputDir),
  "--logo", $LogoPath,
  "--width-ratio", $WidthRatio,
  "--margin-x-ratio", $MarginXRatio,
  "--margin-y-ratio", $MarginYRatio,
  "--erase-color", $EraseColor
)

if ($FirstPageOnly) { $args += "--first-page-only" }
if ($EraseUnder) { $args += "--erase-under" }
if ($Limit -gt 0) { $args += @("--limit", $Limit) }

& $python @args
if ($LASTEXITCODE -ne 0) {
  throw "overlay_logo_on_pdfs.py failed with exit code $LASTEXITCODE"
}
