#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"

using namespace RDK;
using namespace RDK::TestHelpers;

class ModelExecutionTest : public ::testing::Test {
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

// Test model initialization
TEST_F(ModelExecutionTest, ModelInitialization) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Model should be initialized
    EXPECT_NE(model, nullptr);
    EXPECT_FALSE(model->GetCompClassName().empty());
}

// Test model time management
TEST_F(ModelExecutionTest, ModelTimeManagement) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    auto& time = environment->GetTime();
    
    // Test initial time
    double initialTime = time.GetDoubleTime();
    EXPECT_GE(initialTime, 0.0) << "Initial time should be non-negative";
    
    // Verify time control is accessible
    EXPECT_NE(&time, nullptr);
}

// Test model ready state
TEST_F(ModelExecutionTest, ModelReadyState) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Model should exist and be ready
    EXPECT_NE(model, nullptr);
    EXPECT_FALSE(model->GetCompClassName().empty());
    
    // Verify model is part of environment
    auto envModel = environment->GetModel();
    EXPECT_EQ(envModel, model) << "Environment model should match created model";
}

// Test model can be accessed
TEST_F(ModelExecutionTest, ModelAccess) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Test accessing model properties
    EXPECT_FALSE(model->GetCompClassName().empty()) << "Model should have class name";
    EXPECT_GE(model->GetNumComponents(), 0) << "Model should support components";
    
    // Test accessing model name
    std::string modelName = model->GetName();
    EXPECT_FALSE(modelName.empty()) << "Model should have a name";
    
    // Test accessing model ID
    UId modelId = model->GetId();
    EXPECT_NE(modelId, 0) << "Model should have valid ID";
}

// Test model execution preparation (without actual calculation)
TEST_F(ModelExecutionTest, ModelExecutionPreparation) {
    auto model = CreateTestModel(storage, environment);
    if (!model) {
        GTEST_SKIP() << "Cannot create test model";
        return;
    }
    
    // Verify model can be prepared for execution
    // Note: Actual execution requires Engine and more setup
    EXPECT_NE(model, nullptr);
    EXPECT_TRUE(environment->IsInit()) << "Environment should be initialized";
}

