#include "quantum_result_analyzer.hpp"

#include <iostream>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: quantum_analyzer <results.csv>\n";
        return 2;
    }
    try {
        std::cout << quantum::to_json(quantum::summarize(quantum::read_csv(argv[1]))) << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << "\n";
        return 1;
    }
}
