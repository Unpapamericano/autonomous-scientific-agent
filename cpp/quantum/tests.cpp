#include "quantum_result_analyzer.hpp"

#include <cmath>
#include <cassert>
#include <fstream>

int main() {
    const auto summaries = quantum::summarize({
        {"bell", 100, 50, 50},
        {"bell", 100, 60, 40},
        {"biased", 100, 80, 20},
    });
    assert(summaries.size() == 2);

    const auto bell = summaries[0].experiment == "bell" ? summaries[0] : summaries[1];
    assert(bell.shots == 200);
    assert(std::abs(bell.expectation_z - 0.1) < 1e-12);
    assert(bell.standard_error > 0.0);

    const auto biased = summaries[0].experiment == "biased" ? summaries[0] : summaries[1];
    assert(quantum::drift_score(bell, biased) > 1.0);

    const auto json = quantum::to_json({bell});
    assert(json.find("\"expectation_z\":0.1") != std::string::npos);
    const auto escaped = quantum::summarize({{"quote\"slash\\", 10, 6, 4}});
    assert(quantum::to_json(escaped).find("quote\\\"slash\\\\") != std::string::npos);

    const char* path = "quantum_test_results.csv";
    {
        std::ofstream output(path);
        output << "experiment,shots,zeros,ones\nbell,10,6,4\n";
    }
    const auto records = quantum::read_csv(path);
    assert(records.size() == 1);
    std::remove(path);
    return 0;
}
