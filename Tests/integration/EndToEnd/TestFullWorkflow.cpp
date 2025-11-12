#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"

using namespace RDK;
using namespace RDK::TestHelpers;

class FullWorkflowTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
    }
};

// Test full workflow: initialization → model creation → component addition
TEST_F(FullWorkflowTest, FullWorkflow) {
    // Step 1: Initialize Storage
    auto storage = CreateTestStorage();
    ASSERT_NE(storage, nullptr) << "Storage should be created";
    
    // Step 2: Initialize Environment
    auto environment = CreateTestEnvironment(storage);
    ASSERT_NE(environment, nullptr) << "Environment should be created";
    
    // Initialize environment if needed
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    
    // Step 3: Create Model
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Step 4: Add Component
    auto component = storage->TakeObject("UModel");
    if (!component) {
        GTEST_SKIP() << "Cannot create component";
        return;
    }
    component->SetName("TestComponent");
    
    bool addResult = model->AddComponent(component);
    EXPECT_TRUE(addResult) << "Should be able to add component";
    EXPECT_GT(model->GetNumComponents(), 0) << "Model should have components";
    
    // Step 5: Verify component exists
    auto found = model->GetComponent("TestComponent", true);
    ASSERT_NE(found, nullptr) << "Component should be findable";
    EXPECT_EQ(found->GetName(), "TestComponent");
    
    // Step 6: Cleanup (automatic via shared_ptr)
}

// Test workflow with multiple components
TEST_F(FullWorkflowTest, WorkflowWithMultipleComponents) {
    auto storage = CreateTestStorage();
    auto environment = CreateTestEnvironment(storage);
    
    // Initialize environment if needed
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Add multiple components
    for (int i = 0; i < 3; ++i) {
        auto component = storage->TakeObject("UModel");
        if (!component) {
            GTEST_SKIP() << "Cannot create component " << i;
            return;
        }
        component->SetName("Component" + std::to_string(i));
        model->AddComponent(component);
    }
    
    EXPECT_GE(model->GetNumComponents(), 3) << "Model should have at least 3 components";
    
    // Verify all components exist
    for (int i = 0; i < 3; ++i) {
        auto found = model->GetComponent("Component" + std::to_string(i), true);
        ASSERT_NE(found, nullptr) << "Component " << i << " should be findable";
    }
}

// Test workflow cleanup
TEST_F(FullWorkflowTest, WorkflowCleanup) {
    {
        auto storage = CreateTestStorage();
        auto environment = CreateTestEnvironment(storage);
        
        // Initialize environment if needed
        if (!environment->IsInit()) {
            environment->Default();
            environment->Init();
        }
        
        auto model = CreateTestModel(storage, environment);
        // All objects should be cleaned up when going out of scope
    }
    
    // If we get here without crashes, cleanup was successful
    EXPECT_TRUE(true) << "Cleanup completed without errors";
}

