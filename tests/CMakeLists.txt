project(ModernRefactoringTests LANGUAGES CXX)

# Find Google Test
find_package(GTest REQUIRED)

# Create test executable
add_executable(ModernRefactoringTests
    ModernRefactoringTests.cpp
    SimplifiedBasicLibTests.cpp
    NmsdkPulseLibTests.cpp
    NmsdkMotionControlLibTests.cpp
    RdkCvBasicLibTests.cpp
    RdkHardwareLibTests.cpp
    ApplicationsTests.cpp
    ../Rdk/Core/Engine/ModernContainers.cpp
)

# Include directories
target_include_directories(ModernRefactoringTests PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/Rdk/Core/Engine
    ${CMAKE_SOURCE_DIR}/Rdk/Core/System
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-BasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-PulseLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Nmsdk-MotionControlLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-CvBasicLib/Core
    ${CMAKE_SOURCE_DIR}/Libraries/Rdk-HardwareLib/Core
    ${CMAKE_SOURCE_DIR}/Rdk/Deploy/Include
)

# Find Threads
find_package(Threads REQUIRED)

# Link libraries
target_link_libraries(ModernRefactoringTests PRIVATE
    GTest::gtest
    GTest::gtest_main
    Threads::Threads
)

# Compile definitions
target_compile_definitions(ModernRefactoringTests PRIVATE
    RDK_LIB_CVS_REVISION=0
    RDK_QT
)

# Enable C++20 features
target_compile_features(ModernRefactoringTests PRIVATE cxx_std_20)