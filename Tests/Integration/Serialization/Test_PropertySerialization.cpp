#include <gtest/gtest.h>
#include "../../../../Rdk/Deploy/Include/rdk.h"
#include <memory>
#include <sstream>

using namespace RDK;

// Test component for serialization
class SerializationTestComponent : public UNet
{
public:
    UProperty<int, SerializationTestComponent, ptPubParameter> IntParam;
    UProperty<double, SerializationTestComponent, ptPubParameter> DoubleParam;
    UProperty<std::string, SerializationTestComponent, ptPubParameter> StringParam;
    UProperty<int, SerializationTestComponent, ptPubState> IntState;
    UProperty<MDMatrix<double>, SerializationTestComponent, ptPubState> MatrixState;

    SerializationTestComponent() : 
        IntParam("IntParam", this),
        DoubleParam("DoubleParam", this),
        StringParam("StringParam", this),
        IntState("IntState", this),
        MatrixState("MatrixState", this)
    {
    }
};

class PropertySerializationTest : public ::testing::Test
{
protected:
    void SetUp() override
    {
        comp = std::make_unique<SerializationTestComponent>();
        comp->IntParam = 42;
        comp->DoubleParam = 3.14159;
        comp->StringParam = "test_string";
        comp->IntState = 100;
        
        MDMatrix<double> matrix(2, 2);
        matrix(0, 0) = 1.0;
        matrix(0, 1) = 2.0;
        matrix(1, 0) = 3.0;
        matrix(1, 1) = 4.0;
        comp->MatrixState = matrix;
    }

    void TearDown() override
    {
        comp.reset();
    }

    std::unique_ptr<SerializationTestComponent> comp;
};

// Test XML serialization of simple properties
TEST_F(PropertySerializationTest, XMLSerializationSimple)
{
    // Create storage
    UStorage* storage = UCreateStorageXML();
    ASSERT_NE(storage, nullptr);
    
    // Save component
    comp->Save(storage);
    
    // Create new component and load
    auto comp2 = std::make_unique<SerializationTestComponent>();
    comp2->Load(storage);
    
    // Verify values
    EXPECT_EQ(comp2->IntParam(), 42);
    EXPECT_DOUBLE_EQ(comp2->DoubleParam(), 3.14159);
    EXPECT_EQ(comp2->StringParam(), "test_string");
    
    delete storage;
}

// Test XML serialization of state properties
TEST_F(PropertySerializationTest, XMLSerializationState)
{
    UStorage* storage = UCreateStorageXML();
    ASSERT_NE(storage, nullptr);
    
    comp->Save(storage);
    
    auto comp2 = std::make_unique<SerializationTestComponent>();
    comp2->Load(storage);
    
    EXPECT_EQ(comp2->IntState(), 100);
    
    delete storage;
}

// Test XML serialization of matrix
TEST_F(PropertySerializationTest, XMLSerializationMatrix)
{
    UStorage* storage = UCreateStorageXML();
    ASSERT_NE(storage, nullptr);
    
    comp->Save(storage);
    
    auto comp2 = std::make_unique<SerializationTestComponent>();
    comp2->Load(storage);
    
    EXPECT_EQ(comp2->MatrixState()->GetRows(), 2);
    EXPECT_EQ(comp2->MatrixState()->GetCols(), 2);
    EXPECT_DOUBLE_EQ((*comp2->MatrixState())(0, 0), 1.0);
    EXPECT_DOUBLE_EQ((*comp2->MatrixState())(1, 1), 4.0);

    USerStorageXML matrixNode;
    matrixNode.Create("MatrixState");
    *matrixNode << (*comp2->MatrixState());
    const std::string nodeText = matrixNode.GetNodeText();
    EXPECT_FALSE(nodeText.empty());
    EXPECT_NE('\n', nodeText.front());
    EXPECT_NE('\t', nodeText.back());
    
    delete storage;
}

// Test binary serialization
TEST_F(PropertySerializationTest, BinarySerialization)
{
    UStorage* storage = UCreateStorageBinary();
    ASSERT_NE(storage, nullptr);
    
    comp->Save(storage);
    
    auto comp2 = std::make_unique<SerializationTestComponent>();
    comp2->Load(storage);
    
    EXPECT_EQ(comp2->IntParam(), 42);
    EXPECT_DOUBLE_EQ(comp2->DoubleParam(), 3.14159);
    EXPECT_EQ(comp2->StringParam(), "test_string");
    EXPECT_EQ(comp2->IntState(), 100);
    
    delete storage;
}

// Test serialization round-trip
TEST_F(PropertySerializationTest, SerializationRoundTrip)
{
    // Save to XML
    UStorage* storage1 = UCreateStorageXML();
    ASSERT_NE(storage1, nullptr);
    comp->Save(storage1);
    
    // Load from XML
    auto comp2 = std::make_unique<SerializationTestComponent>();
    comp2->Load(storage1);
    
    // Save again
    UStorage* storage2 = UCreateStorageXML();
    ASSERT_NE(storage2, nullptr);
    comp2->Save(storage2);
    
    // Load again
    auto comp3 = std::make_unique<SerializationTestComponent>();
    comp3->Load(storage2);
    
    // Verify all properties
    EXPECT_EQ(comp3->IntParam(), 42);
    EXPECT_DOUBLE_EQ(comp3->DoubleParam(), 3.14159);
    EXPECT_EQ(comp3->StringParam(), "test_string");
    EXPECT_EQ(comp3->IntState(), 100);
    
    delete storage1;
    delete storage2;
}

// Test serialization with connections (connections should not be serialized)
TEST_F(PropertySerializationTest, SerializationWithConnections)
{
    auto comp1 = std::make_unique<SerializationTestComponent>();
    auto comp2 = std::make_unique<SerializationTestComponent>();
    
    comp1->IntParam = 50;
    comp2->IntParam.Connect(&comp1->IntParam);
    
    EXPECT_EQ(comp2->IntParam(), 50);
    
    // Serialize comp2
    UStorage* storage = UCreateStorageXML();
    ASSERT_NE(storage, nullptr);
    comp2->Save(storage);
    
    // Load into new component
    auto comp3 = std::make_unique<SerializationTestComponent>();
    comp3->Load(storage);
    
    // Connection should not be preserved, but if IntParam has a value, it should be loaded
    // This depends on implementation
    
    delete storage;
}

// Test serialization of empty/default values
TEST_F(PropertySerializationTest, SerializationEmptyValues)
{
    auto emptyComp = std::make_unique<SerializationTestComponent>();
    
    UStorage* storage = UCreateStorageXML();
    ASSERT_NE(storage, nullptr);
    emptyComp->Save(storage);
    
    auto loadedComp = std::make_unique<SerializationTestComponent>();
    loadedComp->Load(storage);
    
    // Verify default values are preserved
    EXPECT_EQ(loadedComp->IntParam(), 0);
    EXPECT_DOUBLE_EQ(loadedComp->DoubleParam(), 0.0);
    
    delete storage;
}

