#ifndef TEST_HELPERS_H
#define TEST_HELPERS_H

#include <initializer_list>
#include <memory>
#include <string>
#include <filesystem>
#include <gtest/gtest.h>
#include <glog/logging.h>

// RDK includes
#include "../../Rdk/Deploy/Include/rdk.h"
#include "../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include "../../Libraries/Rdk-CvBasicLib/Deploy/Include/Lib.h"
// HardwareLibrary requires Qt, so we'll use forward declaration and include in .cpp
// #include "../../Libraries/Rdk-HardwareLib/Core/UHardwareLibrary.h"
#include "../../Libraries/Nmsdk-PulseLib/Deploy/Include/Lib.h"
#include "../../Libraries/Nmsdk-MotionControlLib/Deploy/Include/Lib.h"

// Forward declarations for libraries that require Qt
namespace RDK {
    class UHardwareLibrary;
    extern RDK_LIB_TYPE UHardwareLibrary HardwareLibrary;
}

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
    // BasicLibrary is a static library, so create shared_ptr with non-owning deleter
    std::shared_ptr<ULibrary> basicLib(&RDK::BasicLibrary, [](ULibrary*) {});
    storage->AddCollection(basicLib);
    storage->InitRTlibs();
    storage->BuildStorage();
    storage->LoadClassesDescription();
    return storage;
}

// Create storage and register additional libraries (always includes BasicLibrary)
inline std::shared_ptr<UStorage> CreateStorageWithLibraries(std::initializer_list<ULibrary*> extraLibraries) {
    auto storage = std::make_shared<UStorage>();
    storage->SetBuildMode(1);

    // BasicLibrary is a static library, so create shared_ptr with non-owning deleter
    std::shared_ptr<ULibrary> basicLib(&RDK::BasicLibrary, [](ULibrary*) {});
    storage->AddCollection(basicLib);
    for (auto* library : extraLibraries) {
        if (library && library != &RDK::BasicLibrary) {
            // Create shared_ptr with non-owning deleter for static libraries
            std::shared_ptr<ULibrary> libPtr(library, [](ULibrary*) {});
            storage->AddCollection(libPtr);
        }
    }

    storage->InitRTlibs();
    storage->BuildStorage();
    storage->LoadClassesDescription();
    return storage;
}

// Create storage with all libraries in the correct initialization sequence
// Sequence from Libraries/Libraries.cpp:
// 1. RDK::BasicLibrary
// 2. RDK::CvBasicLibrary
// 3. RDK::HardwareLibrary
// 4. NMSDK::PulseLibrary
// 5. NMSDK::MotionControlLibrary
// Note: Implementation is in TestHelpers.cpp to avoid Qt dependencies in header
std::shared_ptr<UStorage> CreateStorageWithAllLibraries();

// Helper function to filter classes by prefix (for library-specific class lists)
inline std::vector<std::string> FilterClassesByPrefix(const std::vector<std::string>& allClasses, 
                                                       const std::string& prefix) {
    std::vector<std::string> filtered;
    for (const auto& className : allClasses) {
        if (className.find(prefix) == 0) {
            filtered.push_back(className);
        }
    }
    return filtered;
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

// Structure to hold console application execution result
struct ConsoleAppResult {
    int exit_code;
    std::string stdout_output;
    std::string stderr_output;
    bool timed_out;
    bool segfaulted;  // SIGSEGV (exit code 139)
    bool aborted;     // SIGABRT (exit code 134)
    std::string signal_info;  // Information about signal if crashed
    
    ConsoleAppResult() : exit_code(-1), timed_out(false), segfaulted(false), aborted(false) {}
};

// Run console application with arguments and timeout
// Returns execution result with exit code and captured output
ConsoleAppResult RunConsoleApp(const std::string& executable, 
                                const std::vector<std::string>& args, 
                                int timeout_seconds = 30);

// Capture console output from a command
std::string CaptureConsoleOutput(const std::string& command, int timeout_seconds = 30);

// Check exit code matches expected value
inline bool CheckExitCode(int exit_code, int expected_code) {
    return exit_code == expected_code;
}

// Parse console output for specific patterns
inline bool ParseConsoleOutput(const std::string& output, const std::string& pattern) {
    return output.find(pattern) != std::string::npos;
}

// Diagnostic helper: Check shared_ptr validity
inline bool CheckSharedPtrValidity(std::shared_ptr<UContainer> ptr, const std::string& context = "") {
    if(!ptr) {
        LOG(WARNING) << "CheckSharedPtrValidity" << (context.empty() ? "" : " [" + context + "]") 
                     << " - ptr is null";
        return false;
    }
    
    try {
        size_t use_count = ptr.use_count();
        void* raw_ptr = ptr.get();
        
        if(use_count > 1000) {
            LOG(WARNING) << "CheckSharedPtrValidity" << (context.empty() ? "" : " [" + context + "]") 
                         << " - Suspicious use_count: " << use_count 
                         << " raw_ptr=" << raw_ptr;
            return false;
        }
        
        if(!raw_ptr) {
            LOG(WARNING) << "CheckSharedPtrValidity" << (context.empty() ? "" : " [" + context + "]") 
                         << " - raw_ptr is null";
            return false;
        }
        
        LOG(INFO) << "CheckSharedPtrValidity" << (context.empty() ? "" : " [" + context + "]") 
                  << " - Valid: use_count=" << use_count << " raw_ptr=" << raw_ptr;
        return true;
    } catch (...) {
        LOG(ERROR) << "CheckSharedPtrValidity" << (context.empty() ? "" : " [" + context + "]") 
                   << " - Exception checking validity";
        return false;
    }
}

// Diagnostic helper: Log component information
inline void LogComponentInfo(std::shared_ptr<UContainer> comp, const std::string& context = "") {
    if(!comp) {
        LOG(WARNING) << "LogComponentInfo" << (context.empty() ? "" : " [" + context + "]") 
                     << " - Component is null";
        return;
    }
    
    try {
        std::string name = comp->GetName();
        size_t use_count = comp.use_count();
        void* raw_ptr = comp.get();
        
        LOG(INFO) << "LogComponentInfo" << (context.empty() ? "" : " [" + context + "]") 
                  << " - name=" << name 
                  << " use_count=" << use_count 
                  << " raw_ptr=" << raw_ptr;
    } catch (...) {
        LOG(ERROR) << "LogComponentInfo" << (context.empty() ? "" : " [" + context + "]") 
                   << " - Exception getting component info";
    }
}

} // namespace TestHelpers
} // namespace RDK

#endif // TEST_HELPERS_H

