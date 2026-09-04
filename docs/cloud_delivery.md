# Cloud CI/CD and infrastructure delivery

## Purpose

This project now includes a demonstrable delivery track for the requested
enterprise skills:

| Requirement | Repository implementation |
|---|---|
| Microsoft Azure DevOps | `demos/cloud-pipelines/azure-pipelines.yml` |
| Terraform IaC | `demos/cloud-pipelines/infra/azure/` |
| GitLab CI/CD | `demos/cloud-pipelines/.gitlab-ci.yml` |
| Azure Virtual Networks | Terraform VNet, app subnet, private-endpoint subnet, NSG |
| Microsoft Entra ID | CI authentication through service connection/workload identity |
| Microsoft PowerShell | `ops/Validate-Delivery.ps1` |

## Pipeline flow

```text
Pull request / push
        ↓
Python tests + Terraform format/validate
        ↓
PowerShell delivery and secret checks
        ↓
Human-approved infrastructure plan/apply
        ↓
Observe, review, and evolve
```

The templates intentionally stop at validation and plan boundaries. Cloud
provisioning requires an explicitly configured Azure identity and approval.

## Entra ID authentication

Use a Microsoft Entra ID service principal, federated workload identity, or
Azure DevOps service connection. Store credentials only in the provider's
secret/identity system. The repository contains no tenant IDs, client secrets,
certificates, or subscription credentials.

Recommended permissions:

- scope access to one resource group where possible
- use least-privilege roles
- separate plan and apply identities
- require approval for production apply
- rotate or federate credentials

## Validation commands

```bash
pytest -q
terraform -chdir=demos/cloud-pipelines/infra/azure init -backend=false
terraform -chdir=demos/cloud-pipelines/infra/azure fmt -check
terraform -chdir=demos/cloud-pipelines/infra/azure validate
pwsh -File ops/Validate-Delivery.ps1
```

The Azure VNet is an example architecture for a scientific API/dashboard
deployment. It is not a production security certification. Network rules,
identity roles, private endpoints, logging, backups, and compliance controls
must be reviewed for the target environment.
