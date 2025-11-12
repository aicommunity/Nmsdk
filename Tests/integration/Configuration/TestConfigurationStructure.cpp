#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include <filesystem>
#include <fstream>
#include <sstream>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class ConfigurationStructureTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    }

    std::string configPath;
};

// Test project.ini exists
TEST_F(ConfigurationStructureTest, ProjectIniExists) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    std::string iniPath = configPath + "/project.ini";
    EXPECT_TRUE(fs::exists(iniPath)) << "project.ini not found";
    
    if (fs::exists(iniPath)) {
        EXPECT_GT(fs::file_size(iniPath), 0) << "project.ini is empty";
    }
}

// Test Model XML files exist
TEST_F(ConfigurationStructureTest, ModelXmlExists) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Check for Model_00.xml or model.xml
    bool hasModel00 = fs::exists(configPath + "/Model_00.xml");
    bool hasModel = fs::exists(configPath + "/model.xml");
    
    EXPECT_TRUE(hasModel00 || hasModel) << "Model XML file not found";
    
    if (hasModel00) {
        EXPECT_GT(fs::file_size(configPath + "/Model_00.xml"), 0);
    }
    if (hasModel) {
        EXPECT_GT(fs::file_size(configPath + "/model.xml"), 0);
    }
}

// Test Parameters XML files exist (optional)
TEST_F(ConfigurationStructureTest, ParametersXmlExists) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Parameters are optional
    bool hasParams00 = fs::exists(configPath + "/Parameters_00.xml");
    bool hasParams = fs::exists(configPath + "/parameters.xml");
    
    if (hasParams00 || hasParams) {
        if (hasParams00) {
            EXPECT_GT(fs::file_size(configPath + "/Parameters_00.xml"), 0);
        }
        if (hasParams) {
            EXPECT_GT(fs::file_size(configPath + "/parameters.xml"), 0);
        }
    } else {
        LOG(INFO) << "Parameters XML file not found (optional)";
    }
}

// Test Interface.xml exists (optional)
TEST_F(ConfigurationStructureTest, InterfaceXmlExists) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Interface.xml is optional
    if (fs::exists(configPath + "/Interface.xml")) {
        EXPECT_GT(fs::file_size(configPath + "/Interface.xml"), 0);
    } else {
        LOG(INFO) << "Interface.xml not found (optional)";
    }
}

// Test configuration directory structure
TEST_F(ConfigurationStructureTest, DirectoryStructure) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    EXPECT_TRUE(fs::is_directory(configPath));
    
    // Count files in directory
    int fileCount = 0;
    for (const auto& entry : fs::directory_iterator(configPath)) {
        if (entry.is_regular_file()) {
            fileCount++;
        }
    }
    
    EXPECT_GT(fileCount, 0) << "Configuration directory is empty";
}

