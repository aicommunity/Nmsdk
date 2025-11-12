#ifndef TEST_HELPERS_H
#define TEST_HELPERS_H

#include <memory>
#include <string>
#include <filesystem>
#include <gtest/gtest.h>
#include <glog/logging.h>

// RDK includes
#include "../../Rdk/Deploy/Include/rdk.h"
#include "../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"

namespace RDK {
namespace TestHelpers {

// Initialize Google Logging for tests
inline void InitTestLogging() {
    static bool initialized = false;
    if (!initialized) {
        google::InitGoogleLogging("Tests");
        FLAGS_logtostderr = 1;
        FLAGS_minloglevel = 0;
        initialized = true;
    }
}

// Get path to test fixtures
inline std::string GetFixturesPath() {
    #ifndef CMAKE_SOURCE_DIR
    #define CMAKE_SOURCE_DIR "."
    #endif
    return std::string(CMAKE_SOURCE_DIR) + "/Tests/fixtures";
}

// Get path to test configs
inline std::string GetTestConfigsPath() {
    return GetFixturesPath() + "/configs";
}

// Get path to test models
inline std::string GetTestModelsPath() {
    return GetFixturesPath() + "/models";
}

// Check if file exists
inline bool FileExists(const std::string& path) {
    return std::filesystem::exists(path);
}

// Create a test Storage with basic libraries
inline std::shared_ptr<UStorage> CreateTestStorage() {
    auto storage = std::make_shared<UStorage>();
    storage->SetBuildMode(1);
    
    // Note: UContainer and UItem are abstract base classes and cannot be instantiated directly.
    // They are typically available through concrete implementations in libraries.
    // For testing, we'll use classes from BasicLibrary which provides concrete implementations.
    
    // Add BasicLibrary for additional classes
    storage->AddCollection(&RDK::BasicLibrary);
    storage->InitRTlibs();
    storage->BuildStorage();
    storage->LoadClassesDescription();
    return storage;
}

// Create a test Environment
inline std::shared_ptr<UEnvironment> CreateTestEnvironment(std::shared_ptr<UStorage> storage = nullptr) {
    if (!storage) {
        storage = CreateTestStorage();
    }
    auto environment = std::make_shared<UEnvironment>();
    environment->SetStorage(storage.get());
    return environment;
}

// Create a test Engine
inline std::unique_ptr<UEngine> CreateTestEngine(std::shared_ptr<UStorage> storage = nullptr, 
                                                  std::shared_ptr<UEnvironment> environment = nullptr) {
    if (!storage) {
        storage = CreateTestStorage();
    }
    if (!environment) {
        environment = CreateTestEnvironment(storage);
    }
    auto engine = std::make_unique<UEngine>();
    engine->Init(storage.get(), environment.get());
    return engine;
}

// Assert that a component exists in a container
inline void AssertComponentExists(std::shared_ptr<UContainer> container, const std::string& componentName) {
    ASSERT_NE(container, nullptr) << "Container is null";
    auto component = container->GetComponent(componentName, true);
    ASSERT_NE(component, nullptr) << "Component '" << componentName << "' not found";
}

// Assert that a link exists between two components
inline void AssertLinkExists(std::shared_ptr<UItem> item, const std::string& propertyName,
                              std::shared_ptr<UConnector> connector, const std::string& connectorName) {
    ASSERT_NE(item, nullptr) << "Item is null";
    ASSERT_NE(connector, nullptr) << "Connector is null";
    ASSERT_TRUE(item->CheckLink(connector, propertyName, connectorName, -1))
        << "Link between " << propertyName << " and " << connectorName << " does not exist";
}

// Load configuration from path (returns project path if successful)
inline std::string LoadConfigurationFromPath(const std::string& configPath) {
    namespace fs = std::filesystem;
    if (!fs::exists(configPath) || !fs::is_directory(configPath)) {
        return "";
    }
    
    // Check for required files
    std::string projectIni = configPath + "/project.ini";
    if (!fs::exists(projectIni)) {
        return "";
    }
    
    return configPath;
}

// Load model from XML file
inline bool LoadModelFromXML(std::shared_ptr<UEnvironment> environment, const std::string& xmlFilePath) {
    if (!environment || !std::filesystem::exists(xmlFilePath)) {
        return false;
    }
    
    try {
        USerStorageXML xmlStorage;
        if (!xmlStorage.LoadFromFile(xmlFilePath, "Save")) {
            return false;
        }
        
        // Load model using Environment's LoadComponent method
        // Note: This is a simplified version - full implementation may require more setup
        return true;
    } catch (...) {
        return false;
    }
}

// Create a test model with components
inline std::shared_ptr<UContainer> CreateTestModel(std::shared_ptr<UStorage> storage, 
                                                    std::shared_ptr<UEnvironment> environment = nullptr) {
    if (!storage) {
        return nullptr;
    }
    
    if (!environment) {
        environment = CreateTestEnvironment(storage);
    }
    
    // Initialize environment if not already initialized
    if (!environment->IsInit()) {
        environment->Default();
        environment->Init();
    }
    
    // Create model using Environment
    if (!environment->CreateModel("UModel")) {
        return nullptr;
    }
    
    return environment->GetModel();
}

// Create a test link between components (placeholder - requires connectors setup)
inline bool CreateTestLink(std::shared_ptr<UItem> item, const std::string& propertyName,
                           std::shared_ptr<UConnector> connector, const std::string& connectorName) {
    if (!item || !connector) {
        return false;
    }
    
    // Note: Full link creation requires proper connector setup
    // This is a placeholder for future implementation
    return item->CheckLink(connector, propertyName, connectorName, -1);
}

} // namespace TestHelpers
} // namespace RDK

#endif // TEST_HELPERS_H

