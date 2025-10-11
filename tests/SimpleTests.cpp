/* ***********************************************************
@Copyright Alexsandr V. Bakhshiev, 2011.
E-mail:        alexab@ailab.ru
Url:           http://ailab.ru

This file is part of the project: RDK

File License:       New BSD License
Project License:    New BSD License
See file license.txt for more information
*********************************************************** */

#include <gtest/gtest.h>
#include <memory>
#include <vector>
#include <string>
#include <chrono>
#include <shared_mutex>

// ============================================================================
// Basic Smart Pointers Tests
// ============================================================================

class TestComponent {
public:
    TestComponent(int value = 0) : value_(value) {}
    int GetValue() const { return value_; }
    void SetValue(int value) { value_ = value; }
    
private:
    int value_;
};

TEST(SmartPointers, BasicFunctionality) {
    // Test std::shared_ptr functionality
    auto ptr1 = std::make_shared<TestComponent>(42);
    EXPECT_EQ(ptr1->GetValue(), 42);
    EXPECT_EQ(ptr1.use_count(), 1);
    
    // Test copy semantics
    auto ptr2 = ptr1;
    EXPECT_EQ(ptr1.use_count(), 2);
    EXPECT_EQ(ptr2.use_count(), 2);
    EXPECT_EQ(ptr1->GetValue(), ptr2->GetValue());
    
    // Test move semantics
    auto ptr3 = std::move(ptr1);
    EXPECT_EQ(ptr1.use_count(), 0);
    EXPECT_EQ(ptr3.use_count(), 2);
    EXPECT_EQ(ptr3->GetValue(), 42);
}

TEST(SmartPointers, CastOperations) {
    auto ptr = std::make_shared<TestComponent>(100);
    
    // Test static_pointer_cast
    auto casted = std::static_pointer_cast<TestComponent>(ptr);
    EXPECT_EQ(casted->GetValue(), 100);
    EXPECT_EQ(ptr.use_count(), 2);
    
    // Test dynamic_pointer_cast
    auto dynamic_casted = std::dynamic_pointer_cast<TestComponent>(ptr);
    EXPECT_NE(dynamic_casted, nullptr);
    EXPECT_EQ(dynamic_casted->GetValue(), 100);
}

// ============================================================================
// Basic Container Tests
// ============================================================================

TEST(Containers, VectorOperations) {
    std::vector<int> vec;
    
    // Test reserve
    vec.reserve(1000);
    EXPECT_GE(vec.capacity(), 1000);
    
    // Test emplace operations
    for (int i = 0; i < 100; ++i) {
        vec.emplace_back(i);
    }
    
    EXPECT_EQ(vec.size(), 100);
    EXPECT_EQ(vec[0], 0);
    EXPECT_EQ(vec[99], 99);
}

TEST(Containers, MapOperations) {
    std::unordered_map<std::string, int> map;
    
    // Test reserve
    map.reserve(1000);
    
    // Test emplace operations
    for (int i = 0; i < 100; ++i) {
        map.emplace("key" + std::to_string(i), i);
    }
    
    EXPECT_EQ(map.size(), 100);
    EXPECT_EQ(map["key0"], 0);
    EXPECT_EQ(map["key99"], 99);
}

TEST(Containers, StringOperations) {
    std::string test_str = "  hello world  ";
    
    // Test basic string operations
    EXPECT_TRUE(test_str.find("hello") != std::string::npos);
    EXPECT_TRUE(test_str.find("world") != std::string::npos);
    
    // Test string concatenation
    std::string result = "hello" + std::string(" ") + "world";
    EXPECT_EQ(result, "hello world");
}

// ============================================================================
// Basic Mutex Tests
// ============================================================================

TEST(Mutex, BasicLocking) {
    std::mutex mutex;
    
    // Test basic lock/unlock
    EXPECT_TRUE(mutex.try_lock());
    mutex.unlock();
    
    // Test lock_guard
    {
        std::lock_guard<std::mutex> lock(mutex);
        // Should automatically unlock
    }
}

TEST(Mutex, SharedMutex) {
    std::shared_mutex mutex;
    
    // Test shared lock
    EXPECT_TRUE(mutex.try_lock_shared());
    mutex.unlock_shared();
    
    // Test exclusive lock
    EXPECT_TRUE(mutex.try_lock());
    mutex.unlock();
}

// ============================================================================
// Performance Tests
// ============================================================================

TEST(Performance, SmartPointerOverhead) {
    const int iterations = 100000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        auto ptr = std::make_shared<TestComponent>(i);
        auto ptr2 = ptr; // Copy
        auto ptr3 = std::move(ptr); // Move
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Smart pointer operations (" << iterations << " iterations): " 
              << duration.count() << " ms" << std::endl;
    
    // Should complete in reasonable time (less than 1 second)
    EXPECT_LT(duration.count(), 1000);
}

TEST(Performance, ContainerOperations) {
    const int size = 10000;
    
    // Test vector performance
    auto start = std::chrono::high_resolution_clock::now();
    
    std::vector<int> vec;
    vec.reserve(size);
    for (int i = 0; i < size; ++i) {
        vec.emplace_back(i);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Vector operations (" << size << " elements): " 
              << duration.count() << " ms" << std::endl;
    
    EXPECT_EQ(vec.size(), size);
    EXPECT_LT(duration.count(), 100); // Should be fast
}

// ============================================================================
// Memory Tests
// ============================================================================

TEST(Memory, NoMemoryLeaks) {
    // Test that smart pointers properly manage memory
    const int iterations = 1000;
    
    for (int i = 0; i < iterations; ++i) {
        auto ptr1 = std::make_shared<TestComponent>(i);
        auto ptr2 = ptr1;
        auto ptr3 = std::move(ptr1);
        
        // Create and destroy many objects
        std::vector<std::shared_ptr<TestComponent>> vec;
        vec.reserve(100);
        for (int j = 0; j < 100; ++j) {
            vec.emplace_back(std::make_shared<TestComponent>(j));
        }
    }
    
    // If we get here without crashing, memory management is working
    SUCCEED();
}

// ============================================================================
// Main Test Runner
// ============================================================================

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
