output "resource_group_name" {
  value = azurerm_resource_group.research.name
}

output "virtual_network_id" {
  value = azurerm_virtual_network.research.id
}

output "app_subnet_id" {
  value = azurerm_subnet.app.id
}

output "private_endpoint_subnet_id" {
  value = azurerm_subnet.private_endpoints.id
}
