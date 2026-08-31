#include "math_test.hpp"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>

namespace math_test {

std::vector<TestResult> grade(const std::vector<TestCase>& cases, double tolerance) {
    if (tolerance < 0.0) {
        throw std::invalid_argument("tolerance must not be negative");
    }
    std::vector<TestResult> results;
    results.reserve(cases.size());
    for (const auto& test : cases) {
        const double error = std::abs(test.expected - test.answer);
        results.push_back({test.id, test.topic, test.expected, test.answer, error,
                           error <= tolerance});
    }
    return results;
}

void write_csv(const std::string& path, const std::vector<TestResult>& results) {
    std::ofstream output(path);
    if (!output) {
        throw std::runtime_error("Unable to write mathematics results file: " + path);
    }
    output << "id,topic,expected,answer,absolute_error,passed\n";
    output << std::setprecision(12);
    for (const auto& result : results) {
        output << result.id << "," << result.topic << "," << result.expected << ","
               << result.answer << "," << result.absolute_error << ","
               << (result.passed ? "true" : "false") << "\n";
    }
}

std::string to_json(const std::vector<TestResult>& results) {
    std::ostringstream output;
    output << std::setprecision(12) << "[";
    for (std::size_t i = 0; i < results.size(); ++i) {
        if (i > 0) {
            output << ",";
        }
        const auto& result = results[i];
        output << "{\"id\":\"" << result.id << "\",\"topic\":\"" << result.topic
               << "\",\"expected\":" << result.expected << ",\"answer\":" << result.answer
               << ",\"absolute_error\":" << result.absolute_error
               << ",\"passed\":" << (result.passed ? "true" : "false") << "}";
    }
    output << "]";
    return output.str();
}

}  // namespace math_test
