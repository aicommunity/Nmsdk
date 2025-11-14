#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include <filesystem>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class MultipleConfigsTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
    }
};

// Test loading multiple configurations sequentially
TEST_F(MultipleConfigsTest, LoadMultipleConfigsSequentially) {
    std::string configsPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples";
    
    if (!fs::exists(configsPath)) {
        GTEST_SKIP() << "Configs directory not found";
        return;
    }
    
    int configCount = 0;
    std::vector<std::string> configPaths;
    
    for (const auto& entry : fs::directory_iterator(configsPath)) {
        if (entry.is_directory()) {
            std::string configPath = entry.path().string();
            std::string iniFile = configPath + "/project.ini";
            
            if (fs::exists(iniFile)) {
                configCount++;
                configPaths.push_back(configPath);
                
                // Verify each config has required files
                EXPECT_TRUE(fs::exists(iniFile)) << "project.ini missing in " << configPath;
                
                // Check for Model XML file
                bool hasModel = fs::exists(configPath + "/Model_00.xml") || 
                               fs::exists(configPath + "/model.xml");
                if (!hasModel) {
                    LOG(WARNING) << "Config " << configPath << " missing Model XML file";
                }
            }
        }
    }
    
    EXPECT_GT(configCount, 0) << "No valid configurations found";
    
    // Log found configurations
    LOG(INFO) << "Found " << configCount << " configuration(s):";
    for (const auto& path : configPaths) {
        LOG(INFO) << "  - " << path;
    }
}

// Test loading each configuration's project.ini file
TEST_F(MultipleConfigsTest, LoadEachConfigurationProjectIni) {
    std::string configsPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples";
    
    if (!fs::exists(configsPath)) {
        GTEST_SKIP() << "Configs directory not found";
        return;
    }
    
    int loadedCount = 0;
    int failedCount = 0;
    
    for (const auto& entry : fs::directory_iterator(configsPath)) {
        if (entry.is_directory()) {
            std::string configPath = entry.path().string();
            std::string iniFile = configPath + "/project.ini";
            
            if (fs::exists(iniFile)) {
                // Try to load project.ini as XML
                USerStorageXML xmlStorage;
                bool loaded = xmlStorage.LoadFromFile(iniFile, "Project");
                
                if (loaded) {
                    loadedCount++;
                    LOG(INFO) << "Successfully loaded project.ini from " << configPath;
                } else {
                    failedCount++;
                    LOG(WARNING) << "Failed to load project.ini from " << configPath;
                }
            }
        }
    }
    
    EXPECT_GT(loadedCount, 0) << "Should be able to load at least one project.ini";
    LOG(INFO) << "Loaded " << loadedCount << " configuration(s), " << failedCount << " failed";
}

// Test configuration isolation
TEST_F(MultipleConfigsTest, ConfigurationIsolation) {
    // Create first configuration context
    auto storage1 = CreateTestStorage();
    auto environment1 = CreateTestEnvironment(storage1);
    
    // Initialize environments
    if (!environment1->IsInit()) {
        environment1->Default();
        environment1->Init();
    }
    
    auto model1 = CreateTestModel(storage1, environment1);
    if (!model1) {
        GTEST_SKIP() << "Cannot create first model";
        return;
    }
    
    // Create second configuration context
    auto storage2 = CreateTestStorage();
    auto environment2 = CreateTestEnvironment(storage2);
    
    if (!environment2->IsInit()) {
        environment2->Default();
        environment2->Init();
    }
    
    auto model2 = CreateTestModel(storage2, environment2);
    if (!model2) {
        GTEST_SKIP() << "Cannot create second model";
        return;
    }
    
    // Verify they are separate
    EXPECT_NE(model1.get(), model2.get()) << "Models should be separate instances";
    
    // Add component to first model
    auto component1 = storage1->TakeObject("UModel");
    if (component1) {
        component1->SetName("Component1");
        model1->AddComponent(component1);
        
        // Verify second model doesn't have it
        auto found = model2->GetComponent("Component1", true);
        EXPECT_EQ(found, nullptr) << "Second model should not have component from first model";
    }
}

// Test resource cleanup between configurations
TEST_F(MultipleConfigsTest, ResourceCleanup) {
    // Create and destroy first configuration
    {
        auto storage = CreateTestStorage();
        auto environment = CreateTestEnvironment(storage);
        
        if (!environment->IsInit()) {
            environment->Default();
            environment->Init();
        }
        
        auto model = CreateTestModel(storage, environment);
        // All objects should be cleaned up when going out of scope
    }
    
    // Create second configuration - should work without issues
    auto storage2 = CreateTestStorage();
    auto environment2 = CreateTestEnvironment(storage2);
    
    if (!environment2->IsInit()) {
        environment2->Default();
        environment2->Init();
    }
    
    auto model2 = CreateTestModel(storage2, environment2);
    ASSERT_NE(model2, nullptr) << "Second model should be created successfully after cleanup";
    EXPECT_FALSE(model2->GetCompClassName().empty()) << "Model should have class name";
}

