terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "research" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_virtual_network" "research" {
  name                = "${var.name_prefix}-vnet"
  location            = azurerm_resource_group.research.location
  resource_group_name = azurerm_resource_group.research.name
  address_space       = [var.vnet_address_space]
  tags                = var.tags
}

resource "azurerm_subnet" "app" {
  name                 = "${var.name_prefix}-app-subnet"
  resource_group_name  = azurerm_resource_group.research.name
  virtual_network_name = azurerm_virtual_network.research.name
  address_prefixes     = [var.app_subnet_address_space]
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "${var.name_prefix}-private-endpoints"
  resource_group_name  = azurerm_resource_group.research.name
  virtual_network_name = azurerm_virtual_network.research.name
  address_prefixes     = [var.private_endpoint_address_space]
}

resource "azurerm_network_security_group" "app" {
  name                = "${var.name_prefix}-app-nsg"
  location            = azurerm_resource_group.research.location
  resource_group_name = azurerm_resource_group.research.name
  tags                = var.tags

  security_rule {
    name                       = "AllowHttpsInbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "Internet"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.app.id
  network_security_group_id = azurerm_network_security_group.app.id
}
