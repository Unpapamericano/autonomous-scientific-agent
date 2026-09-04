# Azure infrastructure template

This Terraform module is a safe, non-secret infrastructure template for the
research platform. It defines a resource group, Azure Virtual Network,
application and private-endpoint subnets, and an HTTPS-only network security
group.

It does not provision anything until an operator explicitly runs Terraform with
an authenticated Azure session.

```powershell
az login
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

For CI, use an Azure DevOps service connection or workload identity. Do not
commit `terraform.tfvars`, state files, client secrets, or certificates.
