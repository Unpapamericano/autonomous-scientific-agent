# Shiny App: Defense Intelligence ROI & KPI Dashboard
## Enterprise Decision Support System for BWI GmbH

This Shiny application provides real-time monitoring of the Defense Intelligence Platform's ROI, budget, and KPIs across all phases and deployment scenarios.

---

## Features Overview

### 1. Dashboard Tabs
- **Executive Summary** - High-level metrics and KPIs
- **Budget Analysis** - Cost tracking and forecasting
- **Performance Metrics** - System performance and SLAs
- **Resource Allocation** - Team and infrastructure costs
- **ROI Projection** - Business value calculations
- **Risk Management** - Potential issues and mitigation

### 2. Key Metrics Tracked
- **Cost per Transaction** (€/req)
- **System Uptime** (%)
- **API Latency** (ms)
- **Test Coverage** (%)
- **Deployment Success Rate** (%)
- **Team Productivity** (tickets/week)
- **Security Incidents** (count)

### 3. Real-Time Data
- Live performance metrics
- Budget burn rate
- Resource utilization
- KPI trends

---

## Installation & Setup

### Requirements
```r
# Required packages
install.packages(c(
  "shiny",
  "shinydashboard",
  "ggplot2",
  "plotly",
  "dplyr",
  "DT",
  "lubridate",
  "shinycssloaders",
  "shinyjs"
))
```

### Run the App
```r
# Option 1: Run from file
shiny::runApp("r/shiny_dashboard.R")

# Option 2: Run from directory
setwd("r")
shiny::runApp()

# Option 3: From project root
Rscript r/shiny_dashboard.R
```

---

## Installation Instructions

See the complete R Shiny implementation file: `r/shiny_dashboard.R`

The app includes:
- Complete dashboard UI
- Real-time data generation
- Interactive charts
- KPI monitoring
- Budget tracking
- Performance analysis
- Risk assessment
