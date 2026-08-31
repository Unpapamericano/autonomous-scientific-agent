#include "math_test.hpp"

#include <iostream>

int main(int argc, char** argv) {
    const std::string output_path = argc == 2 ? argv[1] : "math_results.csv";
    try {
        const auto results = math_test::grade({
            {"algebra_1", "algebra", 42.0, 42.0},
            {"geometry_1", "geometry", 25.0, 24.5},
            {"calculus_1", "calculus", 2.0 / 3.0, 0.6666666667},
            {"statistics_1", "statistics", 0.8, 0.8},
        });
        math_test::write_csv(output_path, results);
        std::cout << math_test::to_json(results) << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}
