#include "quantum_result_analyzer.hpp"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <unordered_map>

namespace quantum {
namespace {

std::string escape_json(const std::string& value) {
    std::ostringstream escaped;
    for (const char character : value) {
        switch (character) {
            case '"':
                escaped << "\\\"";
                break;
            case '\\':
                escaped << "\\\\";
                break;
            case '\b':
                escaped << "\\b";
                break;
            case '\f':
                escaped << "\\f";
                break;
            case '\n':
                escaped << "\\n";
                break;
            case '\r':
                escaped << "\\r";
                break;
            case '\t':
                escaped << "\\t";
                break;
            default:
                if (static_cast<unsigned char>(character) < 0x20) {
                    escaped << "\\u00" << std::hex << std::setw(2) << std::setfill('0')
                            << static_cast<int>(static_cast<unsigned char>(character))
                            << std::dec << std::setfill(' ');
                } else {
                    escaped << character;
                }
        }
    }
    return escaped.str();
}

std::vector<std::string> split(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream stream(line);
    std::string field;
    while (std::getline(stream, field, ',')) {
        fields.push_back(field);
    }
    return fields;
}

std::size_t parse_count(const std::string& value, const char* field) {
    try {
        const auto parsed = std::stoull(value);
        return static_cast<std::size_t>(parsed);
    } catch (const std::exception&) {
        throw std::invalid_argument(std::string("Invalid ") + field + " count: " + value);
    }
}

}  // namespace

std::vector<ExperimentRecord> read_csv(const std::string& path) {
    std::ifstream input(path);
    if (!input) {
        throw std::runtime_error("Unable to open quantum results file: " + path);
    }

    std::vector<ExperimentRecord> records;
    std::string line;
    bool header = true;
    while (std::getline(input, line)) {
        if (line.empty()) {
            continue;
        }
        if (header) {
            header = false;
            continue;
        }
        const auto fields = split(line);
        if (fields.size() != 4 || fields[0].empty()) {
            throw std::invalid_argument("Expected experiment,shots,zeros,ones CSV columns");
        }
        const auto shots = parse_count(fields[1], "shots");
        const auto zeros = parse_count(fields[2], "zeros");
        const auto ones = parse_count(fields[3], "ones");
        if (shots == 0 || zeros + ones != shots) {
            throw std::invalid_argument("Each row must have shots > 0 and zeros + ones == shots");
        }
        records.push_back({fields[0], shots, zeros, ones});
    }
    return records;
}

std::vector<ExperimentSummary> summarize(const std::vector<ExperimentRecord>& records) {
    struct Counts {
        std::size_t shots{};
        std::size_t zeros{};
        std::size_t ones{};
    };
    std::unordered_map<std::string, Counts> grouped;
    for (const auto& record : records) {
        auto& counts = grouped[record.experiment];
        counts.shots += record.shots;
        counts.zeros += record.zeros;
        counts.ones += record.ones;
    }

    std::vector<ExperimentSummary> summaries;
    summaries.reserve(grouped.size());
    for (const auto& [experiment, counts] : grouped) {
        const double zero_rate = static_cast<double>(counts.zeros) / counts.shots;
        const double expectation = 2.0 * zero_rate - 1.0;
        const double standard_error =
            std::sqrt(std::max(0.0, 1.0 - expectation * expectation) / counts.shots);
        summaries.push_back({experiment, counts.shots, expectation, standard_error, zero_rate});
    }
    return summaries;
}

double drift_score(const ExperimentSummary& baseline, const ExperimentSummary& current) {
    if (baseline.experiment != current.experiment) {
        throw std::invalid_argument("Drift comparisons require the same experiment");
    }
    const double combined_error =
        std::sqrt(baseline.standard_error * baseline.standard_error +
                  current.standard_error * current.standard_error);
    if (combined_error == 0.0) {
        return baseline.expectation_z == current.expectation_z ? 0.0 : INFINITY;
    }
    return std::abs(current.expectation_z - baseline.expectation_z) / combined_error;
}

std::string to_json(const std::vector<ExperimentSummary>& summaries) {
    std::ostringstream output;
    output << std::setprecision(10) << "[";
    for (std::size_t i = 0; i < summaries.size(); ++i) {
        if (i > 0) {
            output << ",";
        }
        const auto& summary = summaries[i];
        output << "{\"experiment\":\"" << escape_json(summary.experiment)
               << "\",\"shots\":" << summary.shots
               << ",\"expectation_z\":" << summary.expectation_z
               << ",\"standard_error\":" << summary.standard_error
               << ",\"zero_rate\":" << summary.zero_rate << "}";
    }
    output << "]";
    return output.str();
}

}  // namespace quantum
