cmake_minimum_required(VERSION 3.16)
project(math_test_app LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(math_test math_test.cpp)
target_include_directories(math_test PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

add_executable(math_test_app main.cpp)
target_link_libraries(math_test_app PRIVATE math_test)

add_executable(math_test_tests tests.cpp)
target_link_libraries(math_test_tests PRIVATE math_test)

enable_testing()
add_test(NAME math_test_tests COMMAND math_test_tests)
