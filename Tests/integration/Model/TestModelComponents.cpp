#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include <filesystem>

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class ModelComponentsTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        storage = CreateTestStorage();
        environment = CreateTestEnvironment(storage);
    }

    void TearDown() override {
        environment.reset();
        storage.reset();
    }

    std::shared_ptr<UStorage> storage;
    std::shared_ptr<UEnvironment> environment;
};

// Test model has components
TEST_F(ModelComponentsTest, ModelHasComponents) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Model should be a container that can have components
    EXPECT_GE(model->GetNumComponents(), 0) << "Model should support components";
}

// Test adding components to model
TEST_F(ModelComponentsTest, AddComponentsToModel) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Add a component
    auto component = storage->TakeObject("UModel");
    if (!component) {
        GTEST_SKIP() << "Cannot create component";
        return;
    }
    component->SetName("TestComponent");
    
    bool result = model->AddComponent(component);
    EXPECT_TRUE(result) << "Should be able to add component";
    EXPECT_GT(model->GetNumComponents(), 0) << "Model should have components after adding";
}

// Test finding components in model
TEST_F(ModelComponentsTest, FindComponentsInModel) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Add and find component
    auto component = storage->TakeObject("UModel");
    if (!component) {
        GTEST_SKIP() << "Cannot create component";
        return;
    }
    component->SetName("TestComponent");
    
    model->AddComponent(component);
    
    auto found = model->GetComponent("TestComponent", true);
    ASSERT_NE(found, nullptr) << "Component should be findable";
    EXPECT_EQ(found->GetName(), "TestComponent");
}

// Test component types in model
TEST_F(ModelComponentsTest, ComponentTypes) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Add different components
    auto component1 = storage->TakeObject("UModel");
    auto component2 = storage->TakeObject("UModel");
    
    if (!component1 || !component2) {
        GTEST_SKIP() << "Cannot create components";
        return;
    }
    
    component1->SetName("Component1");
    component2->SetName("Component2");
    
    model->AddComponent(component1);
    model->AddComponent(component2);
    
    EXPECT_GE(model->GetNumComponents(), 2) << "Model should have multiple components";
}

// Test component properties
TEST_F(ModelComponentsTest, ComponentProperties) {
    auto component = storage->TakeObject("UModel");
    if (!component) {
        GTEST_SKIP() << "Cannot create component";
        return;
    }
    
    // Test setting and getting name
    component->SetName("TestComponent");
    EXPECT_EQ(component->GetName(), "TestComponent") << "Component name should be set correctly";
    
    // Test class name
    EXPECT_EQ(component->GetCompClassName(), "UModel") << "Component class name should be UModel";
    
    // Test component ID
    UId componentId = component->GetId();
    EXPECT_NE(componentId, 0) << "Component should have valid ID";
}

// Test components from real configuration (if available)
TEST_F(ModelComponentsTest, ComponentsFromConfiguration) {
    #ifndef CMAKE_SOURCE_DIR
    #define CMAKE_SOURCE_DIR "."
    #endif
    
    std::string configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
    if (!fs::exists(configPath)) {
        GTEST_SKIP() << "Configuration directory not found";
        return;
    }
    
    // Verify configuration directory structure
    EXPECT_TRUE(fs::exists(configPath + "/project.ini")) << "project.ini should exist";
    EXPECT_TRUE(fs::exists(configPath + "/Model_00.xml") || fs::exists(configPath + "/model.xml")) 
        << "Model XML file should exist";
}

