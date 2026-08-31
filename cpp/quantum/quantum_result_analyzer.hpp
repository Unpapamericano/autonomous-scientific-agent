#pragma once

#include <cstddef>
#include <string>
#include <vector>

namespace quantum {

struct ExperimentRecord {
    std::string experiment;
    std::size_t shots{};
    std::size_t zeros{};
    std::size_t ones{};
};

struct ExperimentSummary {
    std::string experiment;
    std::size_t shots{};
    double expectation_z{};
    double standard_error{};
    double zero_rate{};
};

std::vector<ExperimentRecord> read_csv(const std::string& path);
std::vector<ExperimentSummary> summarize(const std::vector<ExperimentRecord>& records);
double drift_score(const ExperimentSummary& baseline, const ExperimentSummary& current);
std::string to_json(const std::vector<ExperimentSummary>& summaries);

}  // namespace quantum
