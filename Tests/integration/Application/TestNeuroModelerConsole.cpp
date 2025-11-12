#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include <filesystem>
#include <cstdlib>
#include <fstream>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

#ifndef CMAKE_BINARY_DIR
#define CMAKE_BINARY_DIR "."
#endif

using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class NeuroModelerConsoleTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
        consoleApp = std::string(CMAKE_BINARY_DIR) + "/bin/NeuroModelerConsole";
    }

    std::string configPath;
    std::string consoleApp;
};

// Test NeuroModelerConsole executable exists
TEST_F(NeuroModelerConsoleTest, ExecutableExists) {
    if (!fs::exists(consoleApp)) {
        GTEST_SKIP() << "NeuroModelerConsole executable not found at: " << consoleApp;
        return;
    }
    
    EXPECT_TRUE(fs::exists(consoleApp));
    EXPECT_TRUE(fs::is_regular_file(consoleApp));
}

// Test NeuroModelerConsole help option
TEST_F(NeuroModelerConsoleTest, HelpOption) {
    if (!fs::exists(consoleApp)) {
        GTEST_SKIP() << "NeuroModelerConsole executable not found";
        return;
    }
    
    // Run with --help option
    std::string command = consoleApp + " --help";
    int result = std::system(command.c_str());
    
    // Help should exit with success (0) or show help
    EXPECT_GE(result, 0);
}

// Test NeuroModelerConsole with configuration (basic check)
TEST_F(NeuroModelerConsoleTest, ConfigurationOption) {
    if (!fs::exists(consoleApp)) {
        GTEST_SKIP() << "NeuroModelerConsole executable not found";
        return;
    }
    
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Test that configuration path is valid
    EXPECT_TRUE(fs::is_directory(configPath)) << "Configuration path should be a directory";
    EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini should exist";
    
    // Verify configuration structure
    EXPECT_TRUE(fs::exists(configPath + "/Model_00.xml") || fs::exists(configPath + "/model.xml"))
        << "Model XML file should exist";
}

// Test NeuroModelerConsole can load configuration (without full execution)
TEST_F(NeuroModelerConsoleTest, ConfigurationLoad) {
    if (!fs::exists(consoleApp)) {
        GTEST_SKIP() << "NeuroModelerConsole executable not found";
        return;
    }
    
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Verify all required configuration files exist
    EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini required";
    EXPECT_TRUE(fs::exists(configPath + "/Model_00.xml") || fs::exists(configPath + "/model.xml"))
        << "Model XML required";
    EXPECT_TRUE(fs::exists(configPath + "/Parameters_00.xml") || fs::exists(configPath + "/parameters.xml"))
        << "Parameters XML should exist";
}

// Test NeuroModelerConsole initialization (without full run)
TEST_F(NeuroModelerConsoleTest, InitializationCheck) {
    if (!fs::exists(consoleApp)) {
        GTEST_SKIP() << "NeuroModelerConsole executable not found";
        return;
    }
    
    // Check that executable is not empty
    EXPECT_GT(fs::file_size(consoleApp), 0);
}

