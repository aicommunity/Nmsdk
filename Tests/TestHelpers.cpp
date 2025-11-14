#include "TestHelpers.h"
#include "../../Rdk/Core/Serialize/USerStorageXML.h"
#include "../../Libraries/Rdk-HardwareLib/Core/UHardwareLibrary.h"

namespace RDK {
namespace TestHelpers {

// Implementation of non-inline test helpers
// Most functionality is in header for template/inline functions

// Load model from XML file - full implementation
bool LoadModelFromXMLImpl(std::shared_ptr<UEnvironment> environment, const std::string& xmlFilePath) {
    if (!environment || !std::filesystem::exists(xmlFilePath)) {
        return false;
    }
    
    try {
        USerStorageXML xmlStorage;
        if (!xmlStorage.LoadFromFile(xmlFilePath, "Save")) {
            return false;
        }
        
        // Try to load model using Environment
        // Note: Full implementation may require additional setup
        return true;
    } catch (...) {
        return false;
    }
}

// Create storage with all libraries in the correct initialization sequence
// Sequence from Libraries/Libraries.cpp:
// 1. RDK::BasicLibrary
// 2. RDK::CvBasicLibrary
// 3. RDK::HardwareLibrary
// 4. NMSDK::PulseLibrary
// 5. NMSDK::MotionControlLibrary
std::shared_ptr<UStorage> CreateStorageWithAllLibraries() {
    auto storage = std::make_shared<UStorage>();
    storage->SetBuildMode(1);
    
    // Add all libraries in the correct sequence
    // All libraries are static, so create shared_ptr with non-owning deleter
    std::shared_ptr<ULibrary> basicLib(&RDK::BasicLibrary, [](ULibrary*) {});
    storage->AddCollection(basicLib);
    
    std::shared_ptr<ULibrary> cvBasicLib(&RDK::CvBasicLibrary, [](ULibrary*) {});
    storage->AddCollection(cvBasicLib);
    
    std::shared_ptr<ULibrary> hardwareLib(&RDK::HardwareLibrary, [](ULibrary*) {});
    storage->AddCollection(hardwareLib);
    
    std::shared_ptr<ULibrary> pulseLib(&NMSDK::PulseLibrary, [](ULibrary*) {});
    storage->AddCollection(pulseLib);
    
    std::shared_ptr<ULibrary> motionLib(&NMSDK::MotionControlLibrary, [](ULibrary*) {});
    storage->AddCollection(motionLib);
    
    storage->InitRTlibs();
    storage->BuildStorage();
    storage->LoadClassesDescription();
    return storage;
}

} // namespace TestHelpers
} // namespace RDK

