#pragma once

#include <string>
#include <vector>

namespace math_test {

struct TestCase {
    std::string id;
    std::string topic;
    double expected{};
    double answer{};
};

struct TestResult {
    std::string id;
    std::string topic;
    double expected{};
    double answer{};
    double absolute_error{};
    bool passed{};
};

std::vector<TestResult> grade(const std::vector<TestCase>& cases, double tolerance = 1e-9);
void write_csv(const std::string& path, const std::vector<TestResult>& results);
std::string to_json(const std::vector<TestResult>& results);

}  // namespace math_test
