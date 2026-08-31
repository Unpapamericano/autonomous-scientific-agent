#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
input_path <- if (length(args) >= 1) args[[1]] else "math_results.csv"
output_path <- if (length(args) >= 2) args[[2]] else "math_results.png"

results <- read.csv(input_path, stringsAsFactors = FALSE)
required <- c("topic", "absolute_error", "passed")
missing <- setdiff(required, names(results))
if (length(missing) > 0) {
  stop(sprintf("Missing required columns: %s", paste(missing, collapse = ", ")))
}

png(output_path, width = 1200, height = 800, res = 140)
par(mfrow = c(1, 2), mar = c(7, 4, 4, 1))

pass_counts <- table(factor(results$passed, levels = c("true", "false")))
barplot(pass_counts,
        names.arg = c("Passed", "Failed"),
        col = c("#2ca02c", "#d62728"),
        main = "Mathematics Test Outcomes",
        ylab = "Number of questions")

topic_error <- aggregate(absolute_error ~ topic, data = results, FUN = mean)
barplot(topic_error$absolute_error,
        names.arg = topic_error$topic,
        las = 2,
        col = "#1f77b4",
        main = "Mean Absolute Error by Topic",
        ylab = "Absolute error")
dev.off()

cat(sprintf("Wrote visualization to %s\n", output_path))
