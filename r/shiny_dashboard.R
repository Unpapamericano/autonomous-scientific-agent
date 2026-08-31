#!/usr/bin/env Rscript

install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

required_packages <- c("shiny", "bslib", "ggplot2", "dplyr", "plotly", "reticulate", "DT")
for (pkg in required_packages) {
  install_if_missing(pkg)
}

suppressPackageStartupMessages({
  library(shiny)
  library(bslib)
  library(ggplot2)
  library(dplyr)
  library(plotly)
  library(reticulate)
  library(DT)
})

resolve_data_path <- function(filename) {
  candidates <- c(
    file.path(getwd(), "data", filename),
    file.path(getwd(), "..", "data", filename),
    file.path(getwd(), filename),
    file.path("data", filename)
  )
  existing <- Filter(file.exists, unique(candidates))
  if (length(existing) > 0) existing[[1]] else NULL
}

read_csv_with_polars_if_available <- function(path) {
  if (is.null(path) || !file.exists(path)) {
    return(NULL)
  }
  if (reticulate::py_available() && reticulate::py_module_available("polars")) {
    py <- tryCatch(reticulate::import("polars"), error = function(e) NULL)
    if (!is.null(py)) {
      result <- tryCatch(py$read_csv(path)$to_pandas(), error = function(e) NULL)
      if (!is.null(result) && nrow(result) > 0) {
        return(result)
      }
    }
  }
  tryCatch(read.csv(path, stringsAsFactors = FALSE), error = function(e) NULL)
}

math_summary <- function(df) {
  if (is.null(df) || nrow(df) == 0) {
    return(list(total_questions = 0, pass_rate = 0, avg_error = 0, topic_count = 0))
  }
  df$passed <- tolower(as.character(df$passed)) == "true"
  list(
    total_questions = nrow(df),
    pass_rate = round(mean(df$passed) * 100, 1),
    avg_error = round(mean(as.numeric(df$absolute_error), na.rm = TRUE), 3),
    topic_count = length(unique(df$topic))
  )
}

quantum_summary <- function(df) {
  if (is.null(df) || nrow(df) == 0) {
    return(list(avg_fidelity = 0, avg_noise = 0, avg_drift = 0, avg_quality = 0))
  }
  list(
    avg_fidelity = round(mean(as.numeric(df$fidelity), na.rm = TRUE) * 100, 1),
    avg_noise = round(mean(as.numeric(df$noise), na.rm = TRUE) * 100, 1),
    avg_drift = round(mean(as.numeric(df$drift_index), na.rm = TRUE) * 100, 1),
    avg_quality = round(mean(as.numeric(df$quality), na.rm = TRUE), 1)
  )
}

ui <- page_navbar(
  title = "Scientific Study Observatory",
  theme = bs_theme(version = 5, bootswatch = "flatly"),
  nav_panel(
    "Overview",
    sidebarLayout(
      sidebarPanel(
        width = 3,
        h4("Inputs"),
        fileInput("math_file", "Upload math results (.csv)", accept = ".csv"),
        fileInput("quantum_file", "Upload quantum results (.csv)", accept = ".csv"),
        helpText("The app loads demo data from the repo by default. Use your own CSVs to replace them.")
      ),
      mainPanel(
        width = 9,
        h2("Research dashboard"),
        p("A polished view for study outcomes, benchmark quality, and experimental drift."),
        uiOutput("kpi_cards"),
        br(),
        plotlyOutput("overview_plot", height = "420px"),
        br(),
        tableOutput("study_table")
      )
    )
  ),
  nav_panel(
    "Math Benchmarks",
    sidebarLayout(
      sidebarPanel(
        width = 3,
        selectInput("math_topic_focus", "Topic", choices = c("All", "algebra", "geometry", "calculus", "statistics", "probability"), selected = "All")
      ),
      mainPanel(
        width = 9,
        plotlyOutput("math_error_plot", height = "430px"),
        plotlyOutput("math_pass_plot", height = "300px")
      )
    )
  ),
  nav_panel(
    "Quantum Analysis",
    mainPanel(
      width = 12,
      plotlyOutput("quantum_quality_plot", height = "420px"),
      plotlyOutput("quantum_drift_plot", height = "350px")
    )
  ),
  nav_panel(
    "Data Explorer",
    mainPanel(
      width = 12,
      DT::dataTableOutput("raw_data_table")
    )
  )
)

server <- function(input, output, session) {
  default_math <- reactive({ read_csv_with_polars_if_available(resolve_data_path("math_results.csv")) })
  default_quantum <- reactive({ read_csv_with_polars_if_available(resolve_data_path("quantum_results.csv")) })

  math_df <- reactive({
    path <- input$math_file$datapath
    if (!is.null(path) && file.exists(path)) {
      return(read_csv_with_polars_if_available(path))
    }
    default_math()
  })

  quantum_df <- reactive({
    path <- input$quantum_file$datapath
    if (!is.null(path) && file.exists(path)) {
      return(read_csv_with_polars_if_available(path))
    }
    default_quantum()
  })

  output$kpi_cards <- renderUI({
    m <- math_summary(math_df())
    q <- quantum_summary(quantum_df())
    tagList(
      div(
        style = "display:flex; gap:1rem; flex-wrap:wrap;",
        div(class = "card", style = "min-width:180px; padding:1rem; border-radius:12px; background:#f5f7fa; box-shadow:0 1px 3px rgba(0,0,0,0.08);",
            strong("Questions"), br(), tags$h3(m$total_questions)),
        div(class = "card", style = "min-width:180px; padding:1rem; border-radius:12px; background:#eefcf3; box-shadow:0 1px 3px rgba(0,0,0,0.08);",
            strong("Pass Rate"), br(), tags$h3(paste0(m$pass_rate, "%"))),
        div(class = "card", style = "min-width:180px; padding:1rem; border-radius:12px; background:#eef4ff; box-shadow:0 1px 3px rgba(0,0,0,0.08);",
            strong("Avg Error"), br(), tags$h3(sprintf("%.3f", m$avg_error))),
        div(class = "card", style = "min-width:180px; padding:1rem; border-radius:12px; background:#fff5eb; box-shadow:0 1px 3px rgba(0,0,0,0.08);",
            strong("Fidelity"), br(), tags$h3(paste0(q$avg_fidelity, "%")))
      )
    )
  })

  output$overview_plot <- renderPlotly({
    m <- math_df()
    if (is.null(m) || nrow(m) == 0) {
      return(plot_ly() %>% add_text(text = "No math data available") %>% layout(title = "No data"))
    }
    m$passed <- tolower(as.character(m$passed)) == "true"
    topic_summary <- m %>%
      group_by(topic) %>%
      summarise(mean_error = mean(as.numeric(absolute_error), na.rm = TRUE), pass_rate = mean(passed) * 100, .groups = "drop")

    fig <- plot_ly(topic_summary, x = ~topic, y = ~mean_error, type = "bar", name = "Mean error", marker = list(color = "#3b82f6")) %>%
      add_trace(y = ~pass_rate, type = "scatter", mode = "lines+markers", yaxis = "y2", name = "Pass rate (%)", line = list(color = "#22c55e"), marker = list(color = "#22c55e")) %>%
      layout(
        title = "Topic quality overview",
        xaxis = list(title = "Topic"),
        yaxis = list(title = "Mean absolute error"),
        yaxis2 = list(title = "Pass rate (%)", overlaying = "y", side = "right"),
        legend = list(x = 1.02, y = 1),
        template = "plotly_white"
      )
    fig
  })

  output$math_error_plot <- renderPlotly({
    m <- math_df()
    if (is.null(m) || nrow(m) == 0) {
      return(plot_ly() %>% add_text(text = "No math data available") %>% layout(title = "No data"))
    }
    selected <- m
    if (input$math_topic_focus != "All") {
      selected <- selected[selected$topic == input$math_topic_focus, , drop = FALSE]
    }
    if (nrow(selected) == 0) {
      return(plot_ly() %>% add_text(text = "No data for the selected topic") %>% layout(title = "No data"))
    }
    topic_summary <- selected %>%
      group_by(topic) %>%
      summarise(mean_error = mean(as.numeric(absolute_error), na.rm = TRUE), .groups = "drop")

    plot_ly(topic_summary, x = ~topic, y = ~mean_error, type = "bar", marker = list(color = "#4f46e5")) %>%
      layout(title = "Average absolute error by topic", xaxis = list(title = "Topic"), yaxis = list(title = "Absolute error"), template = "plotly_white")
  })

  output$math_pass_plot <- renderPlotly({
    m <- math_df()
    if (is.null(m) || nrow(m) == 0) {
      return(plot_ly() %>% add_text(text = "No math data available") %>% layout(title = "No data"))
    }
    m$passed <- tolower(as.character(m$passed)) == "true"
    pass_counts <- table(m$passed)
    names(pass_counts) <- c("Failed", "Passed")
    fig <- plot_ly(x = names(pass_counts), y = as.numeric(pass_counts), type = "bar", marker = list(color = c("#ef4444", "#22c55e"))) %>%
      layout(title = "Pass/fail outcomes", xaxis = list(title = "Outcome"), yaxis = list(title = "Questions"), template = "plotly_white")
    fig
  })

  output$quantum_quality_plot <- renderPlotly({
    q <- quantum_df()
    if (is.null(q) || nrow(q) == 0) {
      return(plot_ly() %>% add_text(text = "No quantum data available") %>% layout(title = "No data"))
    }
    fig <- plot_ly(q, x = ~cost, y = ~quality, type = "scatter", mode = "markers+text", text = ~run_id, textposition = "top center", marker = list(size = 12, color = "#0ea5e9", opacity = 0.75)) %>%
      layout(
        title = "Quality vs. cost trade-off",
        xaxis = list(title = "Cost"),
        yaxis = list(title = "Quality score (%)"),
        template = "plotly_white"
      )
    fig
  })

  output$quantum_drift_plot <- renderPlotly({
    q <- quantum_df()
    if (is.null(q) || nrow(q) == 0) {
      return(plot_ly() %>% add_text(text = "No quantum data available") %>% layout(title = "No data"))
    }
    fig <- plot_ly(q, x = ~run_id, y = ~drift_index, type = "bar", marker = list(color = "#f59e0b")) %>%
      layout(title = "Experiment drift index by run", xaxis = list(title = "Run ID"), yaxis = list(title = "Drift index"), template = "plotly_white")
    fig
  })

  output$study_table <- renderTable({
    m <- math_df()
    if (is.null(m) || nrow(m) == 0) {
      return(data.frame(Message = "No data available"))
    }
    summary_df <- m %>%
      group_by(topic) %>%
      summarise(questions = n(), pass_rate = round(mean(tolower(as.character(passed)) == "true") * 100, 1), avg_error = round(mean(as.numeric(absolute_error), na.rm = TRUE), 3), .groups = "drop")
    summary_df
  })

  output$raw_data_table <- DT::renderDataTable({
    combined <- list(math = math_df(), quantum = quantum_df())
    if (!is.null(combined$math) && !is.null(combined$quantum)) {
      dplyr::bind_rows(
        mutate(combined$math, source = "math"),
        mutate(combined$quantum, source = "quantum")
      )
    } else if (!is.null(combined$math)) {
      mutate(combined$math, source = "math")
    } else if (!is.null(combined$quantum)) {
      mutate(combined$quantum, source = "quantum")
    } else {
      data.frame(source = "none", message = "No data")
    }
  }, options = list(pageLength = 10))
}

run_scientific_dashboard <- function(...) {
  shinyApp(ui = ui, server = server, options = list(...))
}

if (sys.nframe() == 0L) {
  run_scientific_dashboard()
}
