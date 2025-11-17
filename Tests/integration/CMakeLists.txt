# Integration Tests CMake Configuration
cmake_minimum_required(VERSION 3.16)

# Configuration tests
add_subdirectory(Configuration)

# Application tests
add_subdirectory(Application)

# Model tests
add_subdirectory(Model)

# End-to-end tests
add_subdirectory(EndToEnd)

# Diagnostic tests
add_subdirectory(Diagnostic)

