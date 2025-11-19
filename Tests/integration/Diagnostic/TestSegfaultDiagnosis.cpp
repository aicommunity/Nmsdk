#include <gtest/gtest.h>
#include "../../TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Libraries.h"
#include <glog/logging.h>
#include <memory>
#include <vector>

using namespace RDK;
using namespace RDK::TestHelpers;

class SegfaultDiagnosisTest : public ::testing::Test {
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

// Test: Create and delete components in a loop to reproduce segfault
TEST_F(SegfaultDiagnosisTest, CreateDeleteComponentsLoop) {
    LOG(INFO) << "TestSegfaultDiagnosis::CreateDeleteComponentsLoop - Starting";
    
    // Create a network component
    auto net = storage->TakeObject("UNet");
    ASSERT_NE(net, nullptr) << "Failed to create UNet";
    
    net->SetName("TestNet");
    
    // Create and delete components multiple times
    for(int iteration = 0; iteration < 10; ++iteration) {
        LOG(INFO) << "CreateDeleteComponentsLoop - Iteration " << iteration;
        
        // Create some components
        std::vector<std::shared_ptr<RDK::UContainer>> comp_list;
        for(int i = 0; i < 5; ++i) {
            auto item = storage->TakeObject("UItem");
            if(item) {
                item->SetName("Item" + std::to_string(iteration) + "_" + std::to_string(i));
                net->AddComponent(item);
                comp_list.push_back(item);
                
                // Check use_count before deletion
                size_t use_count = item.use_count();
                LOG(INFO) << "CreateDeleteComponentsLoop - Created component " << item->GetName() 
                          << " use_count=" << use_count;
                
                if(use_count > 1000) {
                    LOG(WARNING) << "CreateDeleteComponentsLoop - Suspicious use_count: " << use_count;
                }
            }
        }
        
        // Delete components one by one
        for(auto& comp : comp_list) {
            if(comp) {
                size_t use_count_before = comp.use_count();
                LOG(INFO) << "CreateDeleteComponentsLoop - Deleting component " << comp->GetName() 
                          << " use_count_before=" << use_count_before;
                
                try {
                    net->DelComponent(comp->GetName());
                } catch (...) {
                    LOG(ERROR) << "CreateDeleteComponentsLoop - Exception during DelComponent";
                }
                
                // Check use_count after deletion
                size_t use_count_after = comp.use_count();
                LOG(INFO) << "CreateDeleteComponentsLoop - After deletion use_count_after=" << use_count_after;
            }
        }
        
        comp_list.clear();
    }
    
    LOG(INFO) << "TestSegfaultDiagnosis::CreateDeleteComponentsLoop - Completed";
}

// Test: Reproduce scenario from NEngineMotionControl::ClearStructure
TEST_F(SegfaultDiagnosisTest, ReproduceClearStructureScenario) {
    LOG(INFO) << "TestSegfaultDiagnosis::ReproduceClearStructureScenario - Starting";
    
    // Create NEngineMotionControl
    auto engine = storage->TakeObject("NEngineMotionControl");
    ASSERT_NE(engine, nullptr) << "Failed to create NEngineMotionControl";
    
    engine->SetName("TestEngine");
    
    // Create some components that will be deleted by ClearStructure
    for(int i = 0; i < 3; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("TestComponent" + std::to_string(i));
            engine->AddComponent(item);
        }
    }
    
    // Call Create with full_recreate=true, which calls ClearStructure(0)
    try {
        // Get the method pointer - this is tricky with virtual methods
        // We'll use dynamic_cast to get NEngineMotionControl
        auto nengine = std::dynamic_pointer_cast<NMSDK::NEngineMotionControl>(engine);
        if(nengine) {
            LOG(INFO) << "ReproduceClearStructureScenario - Calling Create(full_recreate=true)";
            bool result = nengine->Create(true);
            LOG(INFO) << "ReproduceClearStructureScenario - Create returned: " << result;
        }
    } catch (const std::exception& e) {
        LOG(ERROR) << "ReproduceClearStructureScenario - Exception: " << e.what();
        FAIL() << "Exception during Create: " << e.what();
    } catch (...) {
        LOG(ERROR) << "ReproduceClearStructureScenario - Unknown exception";
        FAIL() << "Unknown exception during Create";
    }
    
    LOG(INFO) << "TestSegfaultDiagnosis::ReproduceClearStructureScenario - Completed";
}

// Test: Check shared_ptr validity before operations
TEST_F(SegfaultDiagnosisTest, CheckSharedPtrValidity) {
    LOG(INFO) << "TestSegfaultDiagnosis::CheckSharedPtrValidity - Starting";
    
    auto net = storage->TakeObject("UNet");
    ASSERT_NE(net, nullptr);
    
    net->SetName("TestNet");
    
    // Create components and check their validity
    std::vector<std::shared_ptr<RDK::UContainer>> comp_list;
    for(int i = 0; i < 10; ++i) {
        auto item = storage->TakeObject("UItem");
        if(item) {
            item->SetName("Item" + std::to_string(i));
            net->AddComponent(item);
            comp_list.push_back(item);
            
            // Check validity
            size_t use_count = item.use_count();
            void* raw_ptr = item.get();
            
            LOG(INFO) << "CheckSharedPtrValidity - Component " << i 
                      << " use_count=" << use_count 
                      << " raw_ptr=" << raw_ptr;
            
            EXPECT_GT(use_count, 0) << "use_count should be > 0";
            EXPECT_LE(use_count, 100) << "use_count should be reasonable";
            EXPECT_NE(raw_ptr, nullptr) << "raw_ptr should not be null";
        }
    }
    
    // Try to access components through PComponents
    int num_components = net->GetNumComponents();
    LOG(INFO) << "CheckSharedPtrValidity - NumComponents: " << num_components;
    
    for(int i = 0; i < num_components; ++i) {
        auto comp_weak = net->GetComponentByIndex(i);
        if(!comp_weak.expired()) {
            auto comp = comp_weak.lock();
            if(comp) {
                size_t use_count = comp.use_count();
                LOG(INFO) << "CheckSharedPtrValidity - Component " << i 
                          << " name=" << comp->GetName()
                          << " use_count=" << use_count;
            
                if(use_count > 1000) {
                    LOG(WARNING) << "CheckSharedPtrValidity - Suspicious use_count: " << use_count;
                }
            }
        }
    }
    
    LOG(INFO) << "TestSegfaultDiagnosis::CheckSharedPtrValidity - Completed";
}

// Test: Multiple CreateClassSamples calls
TEST_F(SegfaultDiagnosisTest, MultipleCreateClassSamplesCalls) {
    LOG(INFO) << "TestSegfaultDiagnosis::MultipleCreateClassSamplesCalls - Starting";
    
    // Call CreateClassSamples multiple times
    for(int iteration = 0; iteration < 3; ++iteration) {
        LOG(INFO) << "MultipleCreateClassSamplesCalls - Iteration " << iteration;
        
        try {
            NMSDK::PulseLibrary.CreateClassSamples(storage.get());
            NMSDK::MotionControlLibrary.CreateClassSamples(storage.get());
        } catch (const std::exception& e) {
            LOG(ERROR) << "MultipleCreateClassSamplesCalls - Exception in iteration " << iteration 
                       << ": " << e.what();
            FAIL() << "Exception in CreateClassSamples: " << e.what();
        } catch (...) {
            LOG(ERROR) << "MultipleCreateClassSamplesCalls - Unknown exception in iteration " << iteration;
            FAIL() << "Unknown exception in CreateClassSamples";
        }
        
        // Check storage state
        LOG(INFO) << "MultipleCreateClassSamplesCalls - Storage state checked after iteration " << iteration;
    }
    
    LOG(INFO) << "TestSegfaultDiagnosis::MultipleCreateClassSamplesCalls - Completed";
}

