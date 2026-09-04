variable "resource_group_name" {
  description = "Azure resource group for the research platform."
  type        = string
  default     = "rg-autonomous-scientific-agent"
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "westeurope"
}

variable "name_prefix" {
  description = "Lowercase resource name prefix."
  type        = string
  default     = "asa"
}

variable "vnet_address_space" {
  description = "Virtual network CIDR."
  type        = string
  default     = "10.20.0.0/16"
}

variable "app_subnet_address_space" {
  description = "Application subnet CIDR."
  type        = string
  default     = "10.20.1.0/24"
}

variable "private_endpoint_address_space" {
  description = "Private endpoint subnet CIDR."
  type        = string
  default     = "10.20.2.0/24"
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default = {
    application = "autonomous-scientific-agent"
    environment = "demo"
    managed_by  = "terraform"
  }
}
