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

# Расширенные настройки отладки для тестов
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(ModernRefactoringTests PRIVATE
        -g3                    # Максимальная отладочная информация
        -O0                    # Отключение оптимизации
        -fno-omit-frame-pointer # Сохранение указателей фреймов
        -fno-inline           # Отключение инлайнинга для лучшей отладки
        -fno-optimize-sibling-calls # Отключение оптимизации хвостовых вызовов
        -rdynamic              # Экспорт всех символов для отладки
        -DDEBUG                # Определение DEBUG
        -D_DEBUG               # Определение _DEBUG
    )
    
    # Дополнительные флаги для детальной отладки
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        target_compile_options(ModernRefactoringTests PRIVATE
            -ggdb3              # Расширенная отладочная информация для GDB
            -fno-eliminate-unused-debug-symbols # Сохранение неиспользуемых символов
            -fno-merge-debug-strings # Отключение слияния строк отладки
        )
    endif()
    
    # Настройки для лучшей работы с отладчиком
    target_compile_definitions(ModernRefactoringTests PRIVATE
        RDK_DEBUG=1
        RDK_VERBOSE_DEBUG=1
        RDK_ENABLE_ASSERTIONS=1
        TEST_DEBUG=1
        GTEST_DEBUG=1
    )
endif()

# Настройки для RelWithDebInfo
if(CMAKE_BUILD_TYPE STREQUAL "RelWithDebInfo")
    target_compile_options(ModernRefactoringTests PRIVATE
        -g                    # Отладочная информация
        -O2                   # Умеренная оптимизация
        -fno-omit-frame-pointer
        -rdynamic
    )
    
    target_compile_definitions(ModernRefactoringTests PRIVATE
        RDK_DEBUG=1
        TEST_DEBUG=1
    )
endif()