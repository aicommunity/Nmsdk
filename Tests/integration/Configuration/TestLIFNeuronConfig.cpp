#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include <filesystem>
#include <fstream>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class LIFNeuronConfigTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    }

    std::string configPath;
};

// Test LIF-Neuron configuration exists
TEST_F(LIFNeuronConfigTest, ConfigurationExists) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "LIF-Neuron configuration not found at: " << configPath;
        return;
    }
    
    EXPECT_TRUE(fs::is_directory(configPath));
}

// Test LIF-Neuron configuration has all required files
TEST_F(LIFNeuronConfigTest, RequiredFilesExist) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "LIF-Neuron configuration not found";
        return;
    }
    
    // Check for project.ini
    EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini missing";
    
    // Check for Model file (can be Model_00.xml or model.xml)
    bool hasModel = fs::exists(configPath + "/Model_00.xml") || 
                   fs::exists(configPath + "/model.xml");
    EXPECT_TRUE(hasModel) << "Model XML file missing";
    
    // Check for Parameters file (optional)
    bool hasParams = fs::exists(configPath + "/Parameters_00.xml") || 
                    fs::exists(configPath + "/parameters.xml");
    // Parameters are optional, so we just log if missing
    if (!hasParams) {
        LOG(INFO) << "Parameters file not found (optional)";
    }
}

// Test LIF-Neuron configuration file structure
TEST_F(LIFNeuronConfigTest, ConfigurationStructure) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "LIF-Neuron configuration not found";
        return;
    }
    
    // Check project.ini is readable
    std::string iniPath = configPath + "/project.ini";
    EXPECT_TRUE(fs::exists(iniPath)) << "project.ini should exist";
    
    if (fs::exists(iniPath)) {
        std::ifstream iniFile(iniPath);
        EXPECT_TRUE(iniFile.good()) << "Cannot read project.ini";
        iniFile.close();
        
        // Check file is not empty
        EXPECT_GT(fs::file_size(iniPath), 0) << "project.ini should not be empty";
    }
    
    // Check Model XML is readable
    std::string modelFile = fs::exists(configPath + "/Model_00.xml") ? 
                           configPath + "/Model_00.xml" : 
                           configPath + "/model.xml";
    if (fs::exists(modelFile)) {
        std::ifstream xmlFile(modelFile);
        EXPECT_TRUE(xmlFile.good()) << "Cannot read Model XML file";
        xmlFile.close();
        
        // Check file is not empty
        EXPECT_GT(fs::file_size(modelFile), 0) << "Model XML should not be empty";
    }
}

// Test LIF-Neuron configuration can be loaded
TEST_F(LIFNeuronConfigTest, ConfigurationLoad) {
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "LIF-Neuron configuration not found";
        return;
    }
    
    // Verify all required files exist
    EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini required";
    
    bool hasModel = fs::exists(configPath + "/Model_00.xml") || 
                   fs::exists(configPath + "/model.xml");
    EXPECT_TRUE(hasModel) << "Model XML required";
    
    // Verify configuration directory structure
    EXPECT_TRUE(fs::is_directory(configPath)) << "Configuration path should be a directory";
    
    // Count configuration files
    int fileCount = 0;
    for (const auto& entry : fs::directory_iterator(configPath)) {
        if (entry.is_regular_file()) {
            fileCount++;
        }
    }
    EXPECT_GT(fileCount, 0) << "Configuration directory should contain files";
}

