[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$requiredFiles = @(
    "Dockerfile",
    ".github/workflows/docker-image.yml",
    "demos/cloud-pipelines/azure-pipelines.yml",
    "demos/cloud-pipelines/.gitlab-ci.yml",
    "demos/cloud-pipelines/infra/azure/main.tf",
    "demos/cloud-pipelines/infra/azure/variables.tf",
    "demos/cloud-pipelines/infra/azure/outputs.tf",
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
