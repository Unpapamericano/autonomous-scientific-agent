[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$requiredFiles = @(
    "Dockerfile",
    ".github/workflows/docker-image.yml",
    "azure-pipelines.yml",
    ".gitlab-ci.yml",
    "infra/azure/main.tf",
    "infra/azure/variables.tf",
    "infra/azure/outputs.tf",
    "docs/cloud_delivery.md"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Required delivery file is missing: $file"
    }
}

$tracked = git ls-files
$forbidden = $tracked | Where-Object {
    $_ -match '(^|/)(terraform\.tfstate(\.backup)?|terraform\.tfvars)$' -or
    $_ -match '(^|/)\.env$'
}
if ($forbidden) {
    throw "Secret-bearing or state files are tracked: $($forbidden -join ', ')"
}

$dockerfile = Get-Content -Raw -LiteralPath "Dockerfile"
if ($dockerfile -match "COPY\s+configs/") {
    throw "Dockerfile references the obsolete configs/ path."
}

Write-Output "Delivery validation passed: files, paths, and secret safeguards are present."
