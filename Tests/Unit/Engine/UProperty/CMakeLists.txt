cmake_minimum_required(VERSION 3.16)

# Базовые тесты для UProperty
add_executable(Test_UProperty_Basic Test_UProperty_Basic.cpp)

target_include_directories(Test_UProperty_Basic PRIVATE
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
    ${CMAKE_SOURCE_DIR}/Rdk/Core
)

target_link_libraries(Test_UProperty_Basic PRIVATE
    GTest::gtest
    GTest::gtest_main
    rdk.static.qt
)

target_compile_definitions(Test_UProperty_Basic PRIVATE
    RDK_QT
    RDK_LIB_TYPE=
    RDK_CALL=
)

# Добавляем тест в CTest
add_test(NAME UProperty_Basic COMMAND Test_UProperty_Basic)
