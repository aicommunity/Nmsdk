#include <gtest/gtest.h>
#include "../../TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Libraries.h"
#include <glog/logging.h>
#include <memory>
#include <vector>

using namespace RDK;
using namespace RDK::TestHelpers;

class ComponentDeletionTest : public ::testing::Test {
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

// Test: Delete components during parent destruction
TEST_F(ComponentDeletionTest, DeleteComponentsDuringDestruction) {
    LOG(INFO) << "TestComponentDeletion::DeleteComponentsDuringDestruction - Starting";
    
    {
        // Create network in a scope
        auto net = storage->TakeObject("UNet");
        ASSERT_NE(net, nullptr);
        
        net->SetName("TestNet");
        
        // Add components
        std::vector<std::shared_ptr<RDK::UContainer>> comp_list;
        for(int i = 0; i < 5; ++i) {
            auto item = storage->TakeObject("UItem");
            if(item) {
                item->SetName("Item" + std::to_string(i));
                net->AddComponent(item);
                comp_list.push_back(item);
                
                LOG(INFO) << "DeleteComponentsDuringDestruction - Added component " << i 
                          << " use_count=" << item.use_count();
            }
        }
        
        // Check components before destruction
        int num_components = net->GetNumComponents();
        LOG(INFO) << "DeleteComponentsDuringDestruction - NumComponents before destruction: " << num_components;
        
        // net will be destroyed here, which should trigger component deletion
        // Components should be deleted safely
    }
    
    LOG(INFO) << "TestComponentDeletion::DeleteComponentsDuringDestruction - Completed";
}

// Test: Delete components with potentially corrupted vtable
TEST_F(ComponentDeletionTest, DeleteComponentsWithCorruptedVtable) {
    LOG(INFO) << "TestComponentDeletion::DeleteComponentsWithCorruptedVtable - Starting";
    
    auto net = storage->TakeObject("UNet");
    ASSERT_NE(net, nullptr);
    
    net->SetName("TestNet");
    
    // Create and add components
    std::vector<std::shared_ptr<RDK::UContainer>> comp_list;
    for(int i = 0; i < 10; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("Item" + std::to_string(i));
            net->AddComponent(item);
            comp_list.push_back(item);
        }
    }
    
    // Try to delete components one by one, checking for issues
    for(size_t i = 0; i < comp_list.size(); ++i) {
        auto& comp = comp_list[i];
        if(comp) {
            LOG(INFO) << "DeleteComponentsWithCorruptedVtable - Deleting component " << i 
                      << " name=" << comp->GetName()
                      << " use_count=" << comp.use_count();
            
            // Check use_count before deletion
            size_t use_count_before = comp.use_count();
            if(use_count_before > 1000) {
                LOG(WARNING) << "DeleteComponentsWithCorruptedVtable - Suspicious use_count before deletion: " << use_count_before;
            }
            
            // Try dynamic_pointer_cast before deletion to check vtable
            try {
                auto item = std::dynamic_pointer_cast<UItem>(comp);
                if(item) {
                    LOG(INFO) << "DeleteComponentsWithCorruptedVtable - dynamic_pointer_cast<UItem> succeeded";
                }
            } catch (const std::exception& e) {
                LOG(ERROR) << "DeleteComponentsWithCorruptedVtable - Exception in dynamic_pointer_cast: " << e.what();
            } catch (...) {
                LOG(ERROR) << "DeleteComponentsWithCorruptedVtable - Unknown exception in dynamic_pointer_cast";
            }
            
            // Delete component
            try {
                net->DelComponent(comp->GetName());
                LOG(INFO) << "DeleteComponentsWithCorruptedVtable - Successfully deleted component " << i;
            } catch (const std::exception& e) {
                LOG(ERROR) << "DeleteComponentsWithCorruptedVtable - Exception during DelComponent: " << e.what();
            } catch (...) {
                LOG(ERROR) << "DeleteComponentsWithCorruptedVtable - Unknown exception during DelComponent";
            }
        }
    }
    
    LOG(INFO) << "TestComponentDeletion::DeleteComponentsWithCorruptedVtable - Completed";
}

// Test: Full lifecycle - CreateClassSamples -> Create -> ClearStructure -> Create
TEST_F(ComponentDeletionTest, FullLifecycleTest) {
    LOG(INFO) << "TestComponentDeletion::FullLifecycleTest - Starting";
    
    // Step 1: CreateClassSamples
    LOG(INFO) << "FullLifecycleTest - Step 1: CreateClassSamples";
    try {
        NMSDK::PulseLibrary.CreateClassSamples(storage.get());
        NMSDK::MotionControlLibrary.CreateClassSamples(storage.get());
        LOG(INFO) << "FullLifecycleTest - CreateClassSamples completed";
    } catch (const std::exception& e) {
        LOG(ERROR) << "FullLifecycleTest - Exception in CreateClassSamples: " << e.what();
        FAIL() << "Exception in CreateClassSamples: " << e.what();
    }
    
    // Step 2: Create NEngineMotionControl and call Create
    LOG(INFO) << "FullLifecycleTest - Step 2: Create NEngineMotionControl";
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr);
    
    engine->SetName("TestEngine");
    
    auto nengine = std::dynamic_pointer_cast<NMSDK::NEngineMotionControl>(engine);
    ASSERT_NE(nengine, nullptr);
    
    LOG(INFO) << "FullLifecycleTest - Step 3: Call Create(full_recreate=true)";
    try {
        bool result = nengine->Create(true);
        LOG(INFO) << "FullLifecycleTest - Create returned: " << result;
        EXPECT_TRUE(result);
    } catch (const std::exception& e) {
        LOG(ERROR) << "FullLifecycleTest - Exception in Create: " << e.what();
        FAIL() << "Exception in Create: " << e.what();
    }
    
    // Step 4: ClearStructure
    LOG(INFO) << "FullLifecycleTest - Step 4: Call ClearStructure(0)";
    try {
        bool result = nengine->ClearStructure(0);
        LOG(INFO) << "FullLifecycleTest - ClearStructure returned: " << result;
        EXPECT_TRUE(result);
    } catch (const std::exception& e) {
        LOG(ERROR) << "FullLifecycleTest - Exception in ClearStructure: " << e.what();
        FAIL() << "Exception in ClearStructure: " << e.what();
    }
    
    // Step 5: Create again
    LOG(INFO) << "FullLifecycleTest - Step 5: Call Create(full_recreate=true) again";
    try {
        bool result = nengine->Create(true);
        LOG(INFO) << "FullLifecycleTest - Second Create returned: " << result;
        EXPECT_TRUE(result);
    } catch (const std::exception& e) {
        LOG(ERROR) << "FullLifecycleTest - Exception in second Create: " << e.what();
        FAIL() << "Exception in second Create: " << e.what();
    }
    
    LOG(INFO) << "TestComponentDeletion::FullLifecycleTest - Completed";
}

// Test: Check shared_ptr validity after various operations
TEST_F(ComponentDeletionTest, CheckSharedPtrValidityAfterOperations) {
    LOG(INFO) << "TestComponentDeletion::CheckSharedPtrValidityAfterOperations - Starting";
    
    auto net = storage->TakeObject("UNet");
    ASSERT_NE(net, nullptr);
    
    net->SetName("TestNet");
    
    // Create components
    std::vector<std::shared_ptr<RDK::UContainer>> comp_list;
    for(int i = 0; i < 5; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("Item" + std::to_string(i));
            net->AddComponent(item);
            comp_list.push_back(item);
        }
    }
    
    // Check validity after AddComponent
    for(size_t i = 0; i < comp_list.size(); ++i) {
        auto& comp = comp_list[i];
        if(comp) {
            size_t use_count = comp.use_count();
            LOG(INFO) << "CheckSharedPtrValidityAfterOperations - After AddComponent " << i 
                      << " use_count=" << use_count;
            
            EXPECT_GT(use_count, 0);
            EXPECT_LE(use_count, 100);
        }
    }
    
    // Delete one component and check others
    if(!comp_list.empty()) {
        net->DelComponent(comp_list[0]->GetName());
        
        // Check remaining components
        for(size_t i = 1; i < comp_list.size(); ++i) {
            auto& comp = comp_list[i];
            if(comp) {
                size_t use_count = comp.use_count();
                LOG(INFO) << "CheckSharedPtrValidityAfterOperations - After DelComponent " << i 
                          << " use_count=" << use_count;
                
                EXPECT_GT(use_count, 0);
                if(use_count > 1000) {
                    LOG(WARNING) << "CheckSharedPtrValidityAfterOperations - Suspicious use_count: " << use_count;
                }
            }
        }
    }
    
    LOG(INFO) << "TestComponentDeletion::CheckSharedPtrValidityAfterOperations - Completed";
}

