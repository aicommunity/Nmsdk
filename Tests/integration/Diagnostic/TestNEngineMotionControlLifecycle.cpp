#include <gtest/gtest.h>
#include "../../TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Libraries.h"
#include "../../../Libraries/Nmsdk-MotionControlLib/Core/NEngineMotionControl.h"
#include <glog/logging.h>
#include <memory>

using namespace RDK;
using namespace RDK::TestHelpers;
using namespace NMSDK;

class NEngineMotionControlLifecycleTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        storage = CreateStorageWithAllLibraries();
        ASSERT_NE(storage, nullptr) << "Failed to create storage with all libraries";
    }

    void TearDown() override {
        storage.reset();
    }

    std::shared_ptr<UStorage> storage;
};

// Test: NEngineMotionControl::Create with full_recreate=true
TEST_F(NEngineMotionControlLifecycleTest, CreateFullRecreate) {
    LOG(INFO) << "TestNEngineMotionControlLifecycle::CreateFullRecreate - Starting";
    
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr) << "Failed to create NEngineMotionControl";
    
    engine->SetName("TestEngine");
    
    auto nengine = std::dynamic_pointer_cast<NEngineMotionControl>(engine);
    ASSERT_NE(nengine, nullptr) << "Failed to cast to NEngineMotionControl";
    
    // Call Create with full_recreate=true
    LOG(INFO) << "CreateFullRecreate - Calling Create(full_recreate=true)";
    try {
        bool result = nengine->Create(true);
        LOG(INFO) << "CreateFullRecreate - Create returned: " << result;
        EXPECT_TRUE(result) << "Create should return true";
    } catch (const std::exception& e) {
        LOG(ERROR) << "CreateFullRecreate - Exception: " << e.what();
        FAIL() << "Exception during Create: " << e.what();
    } catch (...) {
        LOG(ERROR) << "CreateFullRecreate - Unknown exception";
        FAIL() << "Unknown exception during Create";
    }
    
    LOG(INFO) << "TestNEngineMotionControlLifecycle::CreateFullRecreate - Completed";
}

// Test: NEngineMotionControl::ClearStructure with different parameters
TEST_F(NEngineMotionControlLifecycleTest, ClearStructureDifferentParams) {
    LOG(INFO) << "TestNEngineMotionControlLifecycle::ClearStructureDifferentParams - Starting";
    
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr);
    
    engine->SetName("TestEngine");
    
    auto nengine = std::dynamic_pointer_cast<NEngineMotionControl>(engine);
    ASSERT_NE(nengine, nullptr);
    
    // Add some components first
    for(int i = 0; i < 5; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("TestComponent" + std::to_string(i));
            engine->AddComponent(item);
        }
    }
    
    // Test ClearStructure with different expected_num_motion_elements
    std::vector<int> test_values = {0, 1, 2, 5, 10};
    
    for(int expected : test_values) {
        LOG(INFO) << "ClearStructureDifferentParams - Testing with expected_num_motion_elements=" << expected;
        
        int num_components_before = engine->GetNumComponents();
        LOG(INFO) << "ClearStructureDifferentParams - NumComponents before: " << num_components_before;
        
        // Check PComponents validity before ClearStructure
        for(int i = 0; i < num_components_before; ++i) {
            auto comp_weak = engine->GetComponentByIndex(i);
            if(!comp_weak.expired()) {
                auto comp = comp_weak.lock();
                if(comp) {
                    size_t use_count = comp.use_count();
                    LOG(INFO) << "ClearStructureDifferentParams - Component " << i 
                              << " name=" << comp->GetName()
                              << " use_count=" << use_count;
                    
                    if(use_count > 1000) {
                        LOG(WARNING) << "ClearStructureDifferentParams - Suspicious use_count before ClearStructure: " << use_count;
                    }
                }
            }
        }
        
        try {
            bool result = nengine->ClearStructure(expected);
            LOG(INFO) << "ClearStructureDifferentParams - ClearStructure returned: " << result;
            EXPECT_TRUE(result) << "ClearStructure should return true";
        } catch (const std::exception& e) {
            LOG(ERROR) << "ClearStructureDifferentParams - Exception: " << e.what();
            FAIL() << "Exception during ClearStructure: " << e.what();
        } catch (...) {
            LOG(ERROR) << "ClearStructureDifferentParams - Unknown exception";
            FAIL() << "Unknown exception during ClearStructure";
        }
        
        int num_components_after = engine->GetNumComponents();
        LOG(INFO) << "ClearStructureDifferentParams - NumComponents after: " << num_components_after;
    }
    
    LOG(INFO) << "TestNEngineMotionControlLifecycle::ClearStructureDifferentParams - Completed";
}

// Test: Multiple Create/ClearStructure calls
TEST_F(NEngineMotionControlLifecycleTest, MultipleCreateClearStructureCalls) {
    LOG(INFO) << "TestNEngineMotionControlLifecycle::MultipleCreateClearStructureCalls - Starting";
    
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr);
    
    engine->SetName("TestEngine");
    
    auto nengine = std::dynamic_pointer_cast<NEngineMotionControl>(engine);
    ASSERT_NE(nengine, nullptr);
    
    // Multiple iterations of Create/ClearStructure
    for(int iteration = 0; iteration < 5; ++iteration) {
        LOG(INFO) << "MultipleCreateClearStructureCalls - Iteration " << iteration;
        
        // Create
        try {
            bool result = nengine->Create(true);
            LOG(INFO) << "MultipleCreateClearStructureCalls - Create returned: " << result;
        } catch (const std::exception& e) {
            LOG(ERROR) << "MultipleCreateClearStructureCalls - Exception in Create: " << e.what();
            FAIL() << "Exception in Create: " << e.what();
        }
        
        // Check components
        int num_components = engine->GetNumComponents();
        LOG(INFO) << "MultipleCreateClearStructureCalls - NumComponents after Create: " << num_components;
        
        // ClearStructure
        try {
            bool result = nengine->ClearStructure(0);
            LOG(INFO) << "MultipleCreateClearStructureCalls - ClearStructure returned: " << result;
        } catch (const std::exception& e) {
            LOG(ERROR) << "MultipleCreateClearStructureCalls - Exception in ClearStructure: " << e.what();
            FAIL() << "Exception in ClearStructure: " << e.what();
        }
        
        num_components = engine->GetNumComponents();
        LOG(INFO) << "MultipleCreateClearStructureCalls - NumComponents after ClearStructure: " << num_components;
    }
    
    LOG(INFO) << "TestNEngineMotionControlLifecycle::MultipleCreateClearStructureCalls - Completed";
}

// Test: Check PComponents validity before deletion
TEST_F(NEngineMotionControlLifecycleTest, CheckPComponentsValidityBeforeDeletion) {
    LOG(INFO) << "TestNEngineMotionControlLifecycle::CheckPComponentsValidityBeforeDeletion - Starting";
    
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr);
    
    engine->SetName("TestEngine");
    
    // Add components
    for(int i = 0; i < 10; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("Component" + std::to_string(i));
            engine->AddComponent(item);
        }
    }
    
    int num_components = engine->GetNumComponents();
    LOG(INFO) << "CheckPComponentsValidityBeforeDeletion - NumComponents: " << num_components;
    
    // Check validity of each component before deletion
    for(int i = 0; i < num_components; ++i) {
        auto comp_weak = engine->GetComponentByIndex(i);
        if(!comp_weak.expired()) {
            auto comp = comp_weak.lock();
            if(comp) {
                size_t use_count = comp.use_count();
                void* raw_ptr = comp.get();
                
                LOG(INFO) << "CheckPComponentsValidityBeforeDeletion - Component " << i 
                          << " name=" << comp->GetName()
                          << " use_count=" << use_count
                          << " raw_ptr=" << raw_ptr;
                
                // Check if use_count is suspicious
                if(use_count > 1000) {
                    LOG(WARNING) << "CheckPComponentsValidityBeforeDeletion - Suspicious use_count: " << use_count;
                }
                
                // Try to delete component
                try {
                    engine->DelComponent(comp->GetName());
                    LOG(INFO) << "CheckPComponentsValidityBeforeDeletion - Successfully deleted component " << i;
                } catch (const std::exception& e) {
                    LOG(ERROR) << "CheckPComponentsValidityBeforeDeletion - Exception deleting component " << i 
                           << ": " << e.what();
                } catch (...) {
                    LOG(ERROR) << "CheckPComponentsValidityBeforeDeletion - Unknown exception deleting component " << i;
                }
            }
        }
    }
    
    LOG(INFO) << "TestNEngineMotionControlLifecycle::CheckPComponentsValidityBeforeDeletion - Completed";
}

