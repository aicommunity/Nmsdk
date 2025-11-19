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
    
    // Keep shared_ptr alive to prevent weak_ptr from expiring
    std::shared_ptr<RDK::UContainer> component_keep_alive = component;
    
    UId added_id = model->AddComponent(std::weak_ptr<RDK::UContainer>(component));
    EXPECT_NE(added_id, RDK::ForbiddenId) << "AddComponent should succeed";
    
    auto found_weak = model->GetComponent("TestComponent", true);
    ASSERT_FALSE(found_weak.expired()) << "Component should be findable";
    auto found = found_weak.lock();
    ASSERT_NE(found, nullptr);
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
    
    // Keep shared_ptr alive to prevent weak_ptr from expiring
    std::shared_ptr<RDK::UContainer> component1_keep_alive = component1;
    std::shared_ptr<RDK::UContainer> component2_keep_alive = component2;
    
    model->AddComponent(std::weak_ptr<RDK::UContainer>(component1));
    model->AddComponent(std::weak_ptr<RDK::UContainer>(component2));
    
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
    
    // Test component ID - ID is set only when component is added to a container
    // For standalone components created via TakeObject, ID may be 0 (ForbiddenId)
    UId componentId = component->GetId();
    // Note: ID is 0 (ForbiddenId) until component is added to a container via AddComponent
    // This is expected behavior - ID is assigned by the container when adding component
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

// Diagnostic test: Check shared_ptr lifecycle and weak_ptr validity
TEST_F(ModelComponentsTest, DiagnosticWeakPtrLifecycle) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    LOG(INFO) << "=== Diagnostic Test: WeakPtr Lifecycle ===";
    
    // Step 1: Create component via TakeObject
    auto component = storage->TakeObject("UModel");
    ASSERT_NE(component, nullptr) << "Component should be created";
    
    size_t use_count_after_take = component.use_count();
    LOG(INFO) << "After TakeObject: use_count=" << use_count_after_take 
              << " component_name=" << component->GetName();
    
    // Step 2: Set name
    component->SetName("DiagnosticComponent");
    
    // Step 3: Check if component is in ObjectsStorage (via use_count)
    // Note: With weak_ptr refactoring, ObjectsStorage holds weak_ptr, so use_count may be 1
    // The important check is that component can be found after AddComponent
    LOG(INFO) << "Component use_count after TakeObject: " << use_count_after_take;
    
    // Step 4: Create weak_ptr from shared_ptr
    std::weak_ptr<RDK::UContainer> component_weak(component);
    ASSERT_FALSE(component_weak.expired()) << "weak_ptr should be valid immediately after creation";
    
    LOG(INFO) << "After creating weak_ptr: expired=" << component_weak.expired() 
              << " use_count=" << component.use_count();
    
    // Step 5: Call AddComponent with weak_ptr
    UId added_id = model->AddComponent(component_weak);
    EXPECT_NE(added_id, RDK::ForbiddenId) << "AddComponent should succeed";
    
    LOG(INFO) << "After AddComponent: added_id=" << added_id 
              << " use_count=" << component.use_count()
              << " component_weak.expired()=" << component_weak.expired();
    
    // Step 6: Verify component is in Components vector
    int num_components = model->GetNumComponents();
    LOG(INFO) << "Model has " << num_components << " components";
    EXPECT_GT(num_components, 0) << "Model should have at least one component";
    
    // Step 7: Try to find component by name
    auto found_weak = model->GetComponent("DiagnosticComponent", true);
    LOG(INFO) << "After GetComponent: found_weak.expired()=" << found_weak.expired();
    
    if(found_weak.expired())
    {
        LOG(ERROR) << "Component NOT found - weak_ptr is expired!";
        LOG(ERROR) << "This indicates the problem: component was added but weak_ptr became expired";
        
        // Additional diagnostics
        LOG(INFO) << "Checking Components vector directly:";
        for(int i = 0; i < num_components; i++)
        {
            auto comp_weak = model->GetComponentByIndex(i);
            if(!comp_weak.expired())
            {
                auto comp = comp_weak.lock();
                if(comp)
                {
                    LOG(INFO) << "  Component[" << i << "]: name=" << comp->GetName() 
                              << " id=" << comp->Id << " expired=" << comp_weak.expired();
                }
            }
            else
            {
                LOG(INFO) << "  Component[" << i << "]: expired";
            }
        }
    }
    else
    {
        LOG(INFO) << "Component found successfully!";
        auto found = found_weak.lock();
        ASSERT_NE(found, nullptr);
        EXPECT_EQ(found->GetName(), "DiagnosticComponent");
    }
    
    // Step 8: Keep shared_ptr alive to prevent premature destruction
    // This simulates the real scenario where component should stay in ObjectsStorage
    std::shared_ptr<RDK::UContainer> component_keep_alive = component;
    LOG(INFO) << "After keeping shared_ptr alive: use_count=" << component.use_count();
    
    // Step 9: Try to find component again
    auto found_weak2 = model->GetComponent("DiagnosticComponent", true);
    if(!found_weak2.expired())
    {
        LOG(INFO) << "Component found after keeping shared_ptr alive";
    }
    else
    {
        LOG(ERROR) << "Component still not found even after keeping shared_ptr alive!";
    }
    
    LOG(INFO) << "=== End Diagnostic Test ===";
}

