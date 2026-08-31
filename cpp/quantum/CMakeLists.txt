cmake_minimum_required(VERSION 3.16)
project(quantum_result_analyzer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(quantum_analysis quantum_result_analyzer.cpp)
target_include_directories(quantum_analysis PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(quantum_analyzer main.cpp)
target_link_libraries(quantum_analyzer PRIVATE quantum_analysis)

add_executable(quantum_analysis_tests tests.cpp)
target_link_libraries(quantum_analysis_tests PRIVATE quantum_analysis)

enable_testing()
add_test(NAME quantum_analysis_tests COMMAND quantum_analysis_tests)
