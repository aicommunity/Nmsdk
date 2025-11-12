#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include "../../../Rdk/Core/Application/UApplication.h"
#include <filesystem>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class ConfigurationLoadTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
    }
};

// Test loading configuration from file path
TEST_F(ConfigurationLoadTest, LoadConfigurationFromPath) {
    // Try alternative path first (more reliable)
    std::string configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    
    // Check if configuration directory exists
    if (!fs::exists(configPath)) {
        // Try fixtures path
        configPath = GetTestConfigsPath() + "/samples/LIF-Neuron";
    }
    
    if (fs::exists(configPath)) {
        EXPECT_TRUE(fs::is_directory(configPath));
        
        // Check for required files
        EXPECT_TRUE(fs::exists(configPath + "/project.ini"));
    } else {
        GTEST_SKIP() << "Configuration directory not found: " << configPath;
    }
}

// Test configuration file structure
TEST_F(ConfigurationLoadTest, ConfigurationFileStructure) {
    std::string configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    
    if (fs::exists(configPath)) {
        // Check for project.ini
        EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini not found";
        
        // Check for Model files
        bool hasModel = fs::exists(configPath + "/Model_00.xml") || 
                       fs::exists(configPath + "/model.xml");
        EXPECT_TRUE(hasModel) << "Model XML file not found";
    } else {
        GTEST_SKIP() << "Configuration directory not found";
    }
}

// Test configuration validation
TEST_F(ConfigurationLoadTest, ValidateConfiguration) {
    std::string configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    
    if (fs::exists(configPath)) {
        // Basic validation - directory exists and has required files
        EXPECT_TRUE(fs::is_directory(configPath));
        EXPECT_TRUE(fs::exists(configPath + "/project.ini"));
    } else {
        GTEST_SKIP() << "Configuration directory not found";
    }
}

