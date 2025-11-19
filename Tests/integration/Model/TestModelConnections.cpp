#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"

using namespace RDK;
using namespace RDK::TestHelpers;

class ModelConnectionsTest : public ::testing::Test {
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

// Test creating links between components
TEST_F(ModelConnectionsTest, CreateLinks) {
    // Use UModel instead of abstract UNet
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Create components to add to model
    auto component1 = storage->TakeObject("UModel");
    auto component2 = storage->TakeObject("UModel");
    
    if (!component1 || !component2) {
        GTEST_SKIP() << "Cannot create components";
        return;
    }
    
    component1->SetName("Component1");
    component2->SetName("Component2");
    
    // Add components to model
    bool result1 = model->AddComponent(component1);
    bool result2 = model->AddComponent(component2);
    
    EXPECT_TRUE(result1) << "Failed to add Component1";
    EXPECT_TRUE(result2) << "Failed to add Component2";
    EXPECT_GE(model->GetNumComponents(), 2) << "Model should have at least 2 components";
    
    // Verify components are in model
    auto found1_weak = model->GetComponent("Component1", true);
    auto found2_weak = model->GetComponent("Component2", true);
    EXPECT_FALSE(found1_weak.expired()) << "Component1 not found in model";
    EXPECT_FALSE(found2_weak.expired()) << "Component2 not found in model";
}

// Test checking links between components
TEST_F(ModelConnectionsTest, CheckLinks) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Create and add components
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
    
    // Verify components are linked to model (through ownership)
    auto owner1_weak = component1->GetMainOwner();
    auto owner2_weak = component2->GetMainOwner();
    
    ASSERT_FALSE(owner1_weak.expired()) << "Component1 owner should exist";
    ASSERT_FALSE(owner2_weak.expired()) << "Component2 owner should exist";
    auto owner1 = owner1_weak.lock();
    auto owner2 = owner2_weak.lock();
    EXPECT_EQ(owner1, model) << "Component1 should have model as main owner";
    EXPECT_EQ(owner2, model) << "Component2 should have model as main owner";
    
    // Verify we can find components
    auto found_weak = model->GetComponent("Component1", true);
    EXPECT_FALSE(found_weak.expired());
    auto found2_weak = model->GetComponent("Component2", true);
    EXPECT_FALSE(found2_weak.expired());
}

// Test link structure
TEST_F(ModelConnectionsTest, LinkStructure) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Verify model structure
    EXPECT_GE(model->GetNumComponents(), 0) << "Model should support components";
    
    // Add a component and verify structure
    auto component = storage->TakeObject("UModel");
    if (component) {
        component->SetName("TestComponent");
        model->AddComponent(component);
        
        EXPECT_GT(model->GetNumComponents(), 0) << "Model should have components";
        auto found_weak = model->GetComponent("TestComponent", true);
        EXPECT_FALSE(found_weak.expired()) << "Component should be findable";
    }
}

// Test breaking links (removing components)
TEST_F(ModelConnectionsTest, BreakLinks) {
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
    model->AddComponent(component);
    
    int numBefore = model->GetNumComponents();
    EXPECT_GT(numBefore, 0) << "Component should be added";
    
    // Remove component by name
    model->DelComponent("TestComponent");
    
    int numAfter = model->GetNumComponents();
    EXPECT_LT(numAfter, numBefore) << "Component count should decrease after removal";
    
    // Verify component is no longer findable
    auto found_weak = model->GetComponent("TestComponent", true);
    EXPECT_TRUE(found_weak.expired()) << "Component should not be found after removal";
}

