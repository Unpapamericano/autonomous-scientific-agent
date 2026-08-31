#include "math_test.hpp"

#include <cassert>
#include <cmath>

int main() {
    const auto results = math_test::grade({
        {"correct", "algebra", 4.0, 4.0},
        {"wrong", "algebra", 4.0, 5.0},
        {"close", "calculus", 2.0 / 3.0, 0.6666666667},
    });
    assert(results.size() == 3);
    assert(results[0].passed);
    assert(!results[1].passed);
    assert(results[2].passed);
    assert(std::abs(results[1].absolute_error - 1.0) < 1e-12);
    return 0;
}
