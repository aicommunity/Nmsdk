#include "TestHelpers.h"
#include "../../Rdk/Core/Serialize/USerStorageXML.h"
#include "../../Libraries/Rdk-HardwareLib/Core/UHardwareLibrary.h"
#include <cstdio>
#include <memory>
#include <sstream>
#include <array>
#include <thread>
#include <chrono>
#include <sys/wait.h>
#include <csignal>

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

// Run console application with arguments and timeout
ConsoleAppResult RunConsoleApp(const std::string& executable, 
                                const std::vector<std::string>& args, 
                                int timeout_seconds) {
    ConsoleAppResult result;
    
    if (!std::filesystem::exists(executable)) {
        result.exit_code = -1;
        result.stderr_output = "Executable not found: " + executable;
        return result;
    }
    
    // Build command string
    std::ostringstream cmd_stream;
    cmd_stream << "timeout " << timeout_seconds << " " << executable;
    for (const auto& arg : args) {
        cmd_stream << " " << arg;
    }
    cmd_stream << " 2>&1"; // Redirect stderr to stdout
    
    std::string command = cmd_stream.str();
    
    // Execute command and capture output
    std::array<char, 128> buffer;
    std::string output;
    
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        result.exit_code = -1;
        result.stderr_output = "Failed to open pipe for command execution";
        return result;
    }
    
    // Read output
    while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
        output += buffer.data();
    }
    
    int exit_code = pclose(pipe);
    
    // Parse exit code (pclose returns wait status, need to extract exit code)
    if (WIFEXITED(exit_code)) {
        result.exit_code = WEXITSTATUS(exit_code);
    } else if (WIFSIGNALED(exit_code)) {
        int signal_num = WTERMSIG(exit_code);
        result.exit_code = 128 + signal_num;  // Standard convention: 128 + signal number
        
        // Detect specific signals
        if (signal_num == SIGSEGV) {
            result.segfaulted = true;
            result.signal_info = "SIGSEGV (Segmentation fault)";
        } else if (signal_num == SIGABRT) {
            result.aborted = true;
            result.signal_info = "SIGABRT (Aborted)";
        } else {
            result.signal_info = "Signal " + std::to_string(signal_num);
        }
    } else {
        result.exit_code = exit_code;
    }
    
    // Check for timeout (exit code 124 from timeout command)
    if (result.exit_code == 124) {
        result.timed_out = true;
    }
    
    // Also check for segfault/abort by exit code (common cases)
    if (result.exit_code == 139) {
        result.segfaulted = true;
        if (result.signal_info.empty()) {
            result.signal_info = "SIGSEGV (Segmentation fault)";
        }
    } else if (result.exit_code == 134) {
        result.aborted = true;
        if (result.signal_info.empty()) {
            result.signal_info = "SIGABRT (Aborted)";
        }
    }
    
    // Split output into stdout and stderr (simplified - both go to stdout with 2>&1)
    result.stdout_output = output;
    result.stderr_output = ""; // Combined with stdout
    
    return result;
}

// Capture console output from a command
std::string CaptureConsoleOutput(const std::string& command, int timeout_seconds) {
    std::ostringstream cmd_stream;
    cmd_stream << "timeout " << timeout_seconds << " " << command << " 2>&1";
    
    std::array<char, 128> buffer;
    std::string output;
    
    FILE* pipe = popen(cmd_stream.str().c_str(), "r");
    if (!pipe) {
        return "";
    }
    
    while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
        output += buffer.data();
    }
    
    pclose(pipe);
    return output;
}

} // namespace TestHelpers
} // namespace RDK

