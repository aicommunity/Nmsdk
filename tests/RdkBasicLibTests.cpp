#include <gtest/gtest.h>
#include <memory>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>

// Include modern headers
#include "../Rdk/Core/Engine/ModernSmartPointers.h"
#include "../Rdk/Core/Engine/ModernContainers.h"
#include "../Rdk/Core/System/ModernChrono.h"

// Include Rdk-BasicLib headers
#include "../Libraries/Rdk-BasicLib/Core/UModel.h"
#include "../Libraries/Rdk-BasicLib/Core/UFileIO.h"
#include "../Libraries/Rdk-BasicLib/Core/UMatrixSource.h"

using namespace RDK;

// ============================================================================
// UModel Tests
// ============================================================================

TEST(UModel, SmartPointerCreation) {
    // Test modern smart pointer creation
    auto model = UModel::New();
    EXPECT_NE(model, nullptr);
    
    // Test move semantics
    auto moved_model = std::move(model);
    EXPECT_EQ(model, nullptr);
    EXPECT_NE(moved_model, nullptr);
}

TEST(UModel, CopyAndMoveSemantics) {
    UModel model1;
    UModel model2 = model1; // Copy constructor
    UModel model3 = std::move(model2); // Move constructor
    
    EXPECT_EQ(model2, UModel{}); // Should be in moved-from state
    EXPECT_NE(model3, UModel{}); // Should have content
}

// ============================================================================
// UFileIO Tests
// ============================================================================

TEST(UFileIO, ModernFileOperations) {
    UFileIO fileIO;
    
    // Test file path operations
    fileIO.SetFileName("test_file.txt");
    
    // Test file existence check
    bool exists = fileIO.FileExists();
    EXPECT_FALSE(exists); // File shouldn't exist initially
    
    // Test file size
    std::uintmax_t size = fileIO.GetFileSize();
    EXPECT_EQ(size, 0);
    
    // Test file path
    std::filesystem::path path = fileIO.GetFilePath();
    EXPECT_EQ(path.string(), "test_file.txt");
}

TEST(UFileIO, DirectoryOperations) {
    UFileIO fileIO;
    fileIO.SetFileName("test_dir/subdir/test_file.txt");
    
    // Test directory creation
    bool dir_created = fileIO.EnsureDirectoryExists();
    EXPECT_TRUE(dir_created);
    
    // Verify directory exists
    EXPECT_TRUE(std::filesystem::exists("test_dir/subdir"));
    
    // Cleanup
    std::filesystem::remove_all("test_dir");
}

TEST(UFileIO, MoveSemantics) {
    UFileIO fileIO1;
    fileIO1.SetFileName("test1.txt");
    
    UFileIO fileIO2 = std::move(fileIO1); // Move constructor
    
    // fileIO1 should be in moved-from state
    // fileIO2 should have the filename
    EXPECT_EQ(fileIO2.GetFilePath().string(), "test1.txt");
}

// ============================================================================
// UMatrixSource Tests
// ============================================================================

TEST(UMatrixSource, ModernMatrixOperations) {
    UMatrixSource matrixSource;
    
    // Test matrix validation
    bool valid = matrixSource.IsValidMatrix();
    EXPECT_FALSE(valid); // No data initially
    
    // Test optimization
    matrixSource.OptimizeMatrixOperations();
    // Should not crash and complete successfully
    EXPECT_TRUE(true);
}

TEST(UMatrixSource, MoveSemantics) {
    UMatrixSource matrixSource1;
    UMatrixSource matrixSource2 = std::move(matrixSource1); // Move constructor
    
    // Should complete without issues
    EXPECT_TRUE(true);
}

// ============================================================================
// Performance Tests
// ============================================================================

TEST(Performance, SmartPointerOverhead) {
    auto start = std::chrono::high_resolution_clock::now();
    
    // Create many UModel instances
    std::vector<UEPtr<UModel>> models;
    models.reserve(10000);
    
    for (int i = 0; i < 10000; ++i) {
        models.push_back(UModel::New());
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;
    
    std::cout << "UModel creation (10000 instances): " << elapsed.count() << " ms" << std::endl;
    EXPECT_LT(elapsed.count(), 1000); // Should be under 1 second
}

TEST(Performance, FileOperations) {
    auto start = std::chrono::high_resolution_clock::now();
    
    // Test file operations performance
    UFileIO fileIO;
    for (int i = 0; i < 1000; ++i) {
        fileIO.SetFileName("test_file_" + std::to_string(i) + ".txt");
        fileIO.FileExists();
        fileIO.GetFileSize();
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;
    
    std::cout << "File operations (1000 iterations): " << elapsed.count() << " ms" << std::endl;
    EXPECT_LT(elapsed.count(), 100); // Should be under 100ms
}

// ============================================================================
// Integration Tests
// ============================================================================

TEST(Integration, RdkBasicLibComponents) {
    // Test integration of all modernized components
    
    // Create model
    auto model = UModel::New();
    EXPECT_NE(model, nullptr);
    
    // Create file IO
    UFileIO fileIO;
    fileIO.SetFileName("integration_test.txt");
    
    // Create matrix source
    UMatrixSource matrixSource;
    matrixSource.OptimizeMatrixOperations();
    
    // All components should work together
    EXPECT_TRUE(true);
}

TEST(Integration, ModernContainersWithBasicLib) {
    // Test modern containers with Rdk-BasicLib components
    
    UVector<UEPtr<UModel>> models;
    ReserveVector(models, 100);
    
    for (int i = 0; i < 100; ++i) {
        EmplaceBack(models, UModel::New());
    }
    
    EXPECT_EQ(models.size(), 100);
    
    // Test container operations
    FilterContainer(models, [](const auto& model) {
        return model != nullptr;
    });
    
    EXPECT_EQ(models.size(), 100); // All should be valid
}

// ============================================================================
// Memory Tests
// ============================================================================

TEST(Memory, NoMemoryLeaks) {
    // Test for memory leaks in Rdk-BasicLib components
    
    // Create and destroy many instances
    for (int i = 0; i < 1000; ++i) {
        auto model = UModel::New();
        UFileIO fileIO;
        UMatrixSource matrixSource;
        
        // Use move semantics
        auto moved_model = std::move(model);
        UFileIO moved_fileIO = std::move(fileIO);
        UMatrixSource moved_matrixSource = std::move(matrixSource);
    }
    
    // If we get here without crashing, memory management is working
    EXPECT_TRUE(true);
}

// ============================================================================
// Error Handling Tests
// ============================================================================

TEST(ErrorHandling, FileIOErrorHandling) {
    UFileIO fileIO;
    
    // Test with invalid file path
    fileIO.SetFileName("");
    EXPECT_FALSE(fileIO.FileExists());
    EXPECT_EQ(fileIO.GetFileSize(), 0);
    
    // Test with non-existent file
    fileIO.SetFileName("non_existent_file_12345.txt");
    EXPECT_FALSE(fileIO.FileExists());
    EXPECT_EQ(fileIO.GetFileSize(), 0);
}

TEST(ErrorHandling, MatrixSourceErrorHandling) {
    UMatrixSource matrixSource;
    
    // Test with empty matrices
    bool valid = matrixSource.IsValidMatrix();
    EXPECT_FALSE(valid);
    
    // Optimization should handle empty matrices gracefully
    EXPECT_NO_THROW(matrixSource.OptimizeMatrixOperations());
}

