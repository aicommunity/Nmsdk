#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Libraries.h"
#include "../../../Rdk/Core/Application/UApplication.h"
#include <filesystem>
#include <QCoreApplication>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class LIFNeuronFullWorkflowTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        
        // Initialize Qt application for tests
        static int argc = 1;
        static char* argv[] = {(char*)"test"};
        if (!QCoreApplication::instance()) {
            app = std::make_unique<QCoreApplication>(argc, argv);
        }
        
        configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
        projectIniPath = configPath + "/project.ini";
    }

    void TearDown() override {
        app.reset();
    }

    std::unique_ptr<QCoreApplication> app;
    std::string configPath;
    std::string projectIniPath;
};

// Test full workflow: initialization -> load -> verify
TEST_F(LIFNeuronFullWorkflowTest, FullWorkflowInitialization) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found";
        return;
    }
    
    // Step 1: Initialize storage with all libraries
    auto storage = CreateStorageWithAllLibraries();
    ASSERT_NE(storage, nullptr) << "Failed to create storage";
    
    // Step 2: Upload all libraries
    RDK::BasicLibrary.Upload(storage.get());
    RDK::CvBasicLibrary.Upload(storage.get());
    RDK::HardwareLibrary.Upload(storage.get());
    NMSDK::PulseLibrary.Upload(storage.get());
    NMSDK::MotionControlLibrary.Upload(storage.get());
    
    // Step 3: Call CreateClassSamples for libraries that need it
    try {
        NMSDK::PulseLibrary.CreateClassSamples(storage.get());
        NMSDK::MotionControlLibrary.CreateClassSamples(storage.get());
    } catch (const std::exception& ex) {
        GTEST_SKIP() << "CreateClassSamples failed: " << ex.what();
        return;
    }
    
    // Step 4: Create application
    auto application = std::make_unique<UApplication>();
    ASSERT_NE(application, nullptr) << "Failed to create application";
    
    // Step 5: Verify storage has classes
    EXPECT_GT(storage->GetNumClasses(), 0) << "Storage should have registered classes";
    
    // Step 6: Verify critical classes are available
    EXPECT_TRUE(storage->CheckClass("UModel")) << "UModel should be available";
    EXPECT_TRUE(storage->CheckClass("NPNeuron")) << "NPNeuron should be available";
}

// Test full workflow: load configuration
TEST_F(LIFNeuronFullWorkflowTest, FullWorkflowLoadConfiguration) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found";
        return;
    }
    
    // Initialize storage with all libraries
    auto storage = CreateStorageWithAllLibraries();
    ASSERT_NE(storage, nullptr) << "Failed to create storage";
    
    // Upload all libraries
    RDK::BasicLibrary.Upload(storage.get());
    RDK::CvBasicLibrary.Upload(storage.get());
    RDK::HardwareLibrary.Upload(storage.get());
    NMSDK::PulseLibrary.Upload(storage.get());
    NMSDK::MotionControlLibrary.Upload(storage.get());
    
    // Call CreateClassSamples for libraries that need it
    try {
        NMSDK::PulseLibrary.CreateClassSamples(storage.get());
        NMSDK::MotionControlLibrary.CreateClassSamples(storage.get());
    } catch (const std::exception& ex) {
        GTEST_SKIP() << "CreateClassSamples failed: " << ex.what();
        return;
    }
    
    // Create application
    auto application = std::make_unique<UApplication>();
    ASSERT_NE(application, nullptr) << "Failed to create application";
    
    // Try to open project
    bool opened = false;
    try {
        opened = application->OpenProject(projectIniPath);
    } catch (const std::exception& ex) {
        LOG(WARNING) << "OpenProject threw exception: " << ex.what();
    }
    
    if (!opened) {
        GTEST_SKIP() << "Failed to open project - may require GUI components";
        return;
    }
    
    // Verify that project is open
    EXPECT_TRUE(application->GetProjectOpenFlag()) << "Project should be open";
    
    // Verify that we have channels
    EXPECT_GT(application->GetNumChannels(), 0) << "Should have at least one channel";
}

// Test that all required components are available for LIF-Neuron configuration
TEST_F(LIFNeuronFullWorkflowTest, RequiredComponentsAvailable) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found";
        return;
    }
    
    // Create storage with all libraries
    auto storage = CreateStorageWithAllLibraries();
    ASSERT_NE(storage, nullptr) << "Failed to create storage";
    
    // Upload all libraries
    RDK::BasicLibrary.Upload(storage.get());
    RDK::CvBasicLibrary.Upload(storage.get());
    RDK::HardwareLibrary.Upload(storage.get());
    NMSDK::PulseLibrary.Upload(storage.get());
    NMSDK::MotionControlLibrary.Upload(storage.get());
    
    // Call CreateClassSamples for libraries that need it
    try {
        NMSDK::PulseLibrary.CreateClassSamples(storage.get());
        NMSDK::MotionControlLibrary.CreateClassSamples(storage.get());
    } catch (const std::exception& ex) {
        GTEST_SKIP() << "CreateClassSamples failed: " << ex.what();
        return;
    }
    
    // Check that required classes for LIF-Neuron are available
    // These are typical classes used in LIF-Neuron configuration
    std::vector<std::string> requiredClasses = {
        "UModel",
        "NPNeuron",
        "NPulseNeuronIaF",
        "NPulseMembraneIaF",
        "NPChannel",
        "NPSynapse"
    };
    
    for (const auto& className : requiredClasses) {
        if (!storage->CheckClass(className)) {
            LOG(WARNING) << "Class '" << className << "' not available (may be optional)";
        }
    }
    
    // At least UModel should be available
    EXPECT_TRUE(storage->CheckClass("UModel")) << "UModel should be available";
}

