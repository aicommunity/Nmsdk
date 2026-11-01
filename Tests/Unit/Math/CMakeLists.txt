cmake_minimum_required(VERSION 3.16)

message(STATUS "Math tests directory created")

add_executable(Test_MDMatrixResize Test_MDMatrixResize.cpp)
target_link_libraries(Test_MDMatrixResize PRIVATE rdk.static.qt GTest::gtest GTest::gtest_main)
add_test(NAME Math_MDMatrixResize COMMAND Test_MDMatrixResize)

