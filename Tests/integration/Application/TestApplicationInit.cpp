#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include "../../../Rdk/Core/Application/UAppCore.h"
#include <QCoreApplication>

using namespace RDK;
using namespace RDK::TestHelpers;

class ApplicationInitTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        // Initialize Qt application for tests
        static int argc = 1;
        static char* argv[] = {(char*)"test"};
        if (!QCoreApplication::instance()) {
            app = std::make_unique<QCoreApplication>(argc, argv);
        }
    }

    void TearDown() override {
        app.reset();
    }

    std::unique_ptr<QCoreApplication> app;
};

// Test basic application components can be created
TEST_F(ApplicationInitTest, BasicComponentsCreation) {
    auto storage = CreateTestStorage();
    ASSERT_NE(storage, nullptr) << "Storage should be created";
    
    auto environment = CreateTestEnvironment(storage);
    ASSERT_NE(environment, nullptr) << "Environment should be created";
    
    // Verify storage is created (UStorage doesn't have IsInit method)
    EXPECT_NE(storage.get(), nullptr) << "Storage should be created";
    
    // Initialize environment if needed
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    EXPECT_TRUE(environment->IsInit()) << "Environment should be initialized";
}

// Test Storage initialization
TEST_F(ApplicationInitTest, StorageInitialization) {
    auto storage = CreateTestStorage();
    ASSERT_NE(storage, nullptr) << "Storage should be created";
    // Verify storage is created (UStorage doesn't have IsInit method)
    EXPECT_NE(storage.get(), nullptr) << "Storage should be created";
    
    // Check that basic libraries are loaded
    int numClasses = storage->GetNumClasses();
    EXPECT_GT(numClasses, 0) << "Storage should have classes from libraries";
    
    // Verify BasicLib classes are available
    EXPECT_TRUE(storage->CheckClass("UModel")) << "UModel should be available";
}

// Test Environment initialization
TEST_F(ApplicationInitTest, EnvironmentInitialization) {
    auto storage = CreateTestStorage();
    auto environment = CreateTestEnvironment(storage);
    
    ASSERT_NE(environment, nullptr) << "Environment should be created";
    
    // Initialize environment if needed
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    
    EXPECT_TRUE(environment->IsInit()) << "Environment should be initialized";
    
    UStorage* envStorage = environment->GetStorage();
    ASSERT_NE(envStorage, nullptr) << "Environment should have storage";
    EXPECT_EQ(envStorage, storage.get()) << "Environment storage should match test storage";
}

// Test Engine initialization
TEST_F(ApplicationInitTest, EngineInitialization) {
    auto storage = CreateTestStorage();
    auto environment = CreateTestEnvironment(storage);
    
    // Initialize environment if needed
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    
    auto engine = CreateTestEngine(storage, environment);
    
    ASSERT_NE(engine, nullptr) << "Engine should be created";
    
    // UEngine has GetEnvironment() method
    UEnvironment* engineEnvironment = engine->GetEnvironment();
    EXPECT_NE(engineEnvironment, nullptr) << "Engine should have environment";
    EXPECT_EQ(engineEnvironment, environment.get()) << "Engine environment should match test environment";
    
    // Verify storage through environment
    if (engineEnvironment) {
        UStorage* engineStorage = engineEnvironment->GetStorage();
        EXPECT_NE(engineStorage, nullptr) << "Engine should have storage through environment";
        EXPECT_EQ(engineStorage, storage.get()) << "Engine storage should match test storage";
    }
}

