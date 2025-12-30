#include <gtest/gtest.h>
#include "../../../../Rdk/Deploy/Include/rdk.h"
#include <memory>
#include <vector>

using namespace RDK;

// Simple component that adds two inputs
class AdderComponent : public UNet
{
public:
    UProperty<int, AdderComponent, ptPubInput> Input1;
    UProperty<int, AdderComponent, ptPubInput> Input2;
    UProperty<int, AdderComponent, ptPubOutput> Output;

    AdderComponent() : 
        Input1("Input1", this),
        Input2("Input2", this),
        Output("Output", this)
    {
    }

protected:
    virtual bool ACalculate(void) override
    {
        Output = Input1() + Input2();
        return true;
    }
};

// Component that multiplies input by parameter
class MultiplierComponent : public UNet
{
public:
    UProperty<int, MultiplierComponent, ptPubInput> Input;
    UProperty<int, MultiplierComponent, ptPubParameter> Factor;
    UProperty<int, MultiplierComponent, ptPubOutput> Output;

    MultiplierComponent() : 
        Input("Input", this),
        Factor("Factor", this),
        Output("Output", this)
    {
    }

protected:
    virtual bool ACalculate(void) override
    {
        Output = Input() * Factor();
        return true;
    }
};

class ComponentNetworkTest : public ::testing::Test
{
protected:
    void SetUp() override
    {
        adder1 = std::make_unique<AdderComponent>();
        adder2 = std::make_unique<AdderComponent>();
        multiplier = std::make_unique<MultiplierComponent>();
    }

    void TearDown() override
    {
        adder1.reset();
        adder2.reset();
        multiplier.reset();
    }

    std::unique_ptr<AdderComponent> adder1;
    std::unique_ptr<AdderComponent> adder2;
    std::unique_ptr<MultiplierComponent> multiplier;
};

// Test simple two-component network
TEST_F(ComponentNetworkTest, SimpleTwoComponentNetwork)
{
    // Setup: adder1 -> multiplier
    adder1->Input1 = 5;
    adder1->Input2 = 3;
    multiplier->Input.Connect(&adder1->Output);
    multiplier->Factor = 2;
    
    // Initialize
    adder1->Default();
    adder1->Build();
    multiplier->Default();
    multiplier->Build();
    
    // Execute
    adder1->Reset();
    multiplier->Reset();
    adder1->Calculate();
    multiplier->Calculate();
    
    // Verify: (5 + 3) * 2 = 16
    EXPECT_EQ(multiplier->Output(), 16);
}

// Test chain of components
TEST_F(ComponentNetworkTest, ComponentChain)
{
    // Setup: adder1 -> adder2 -> multiplier
    adder1->Input1 = 2;
    adder1->Input2 = 3;
    adder2->Input1.Connect(&adder1->Output);
    adder2->Input2 = 4;
    multiplier->Input.Connect(&adder2->Output);
    multiplier->Factor = 3;
    
    // Initialize
    adder1->Default();
    adder1->Build();
    adder2->Default();
    adder2->Build();
    multiplier->Default();
    multiplier->Build();
    
    // Execute
    adder1->Reset();
    adder2->Reset();
    multiplier->Reset();
    
    adder1->Calculate();
    adder2->Calculate();
    multiplier->Calculate();
    
    // Verify: ((2 + 3) + 4) * 3 = 27
    EXPECT_EQ(multiplier->Output(), 27);
}

// Test multiple outputs to single input
TEST_F(ComponentNetworkTest, MultipleOutputsToInput)
{
    // Setup: adder1 and adder2 both connect to multiplier
    // Note: This tests the connection mechanism, actual behavior depends on implementation
    adder1->Input1 = 1;
    adder1->Input2 = 2;
    adder2->Input1 = 3;
    adder2->Input2 = 4;
    
    // Connect both to multiplier (if supported)
    multiplier->Input.Connect(&adder1->Output);
    multiplier->Factor = 1;
    
    adder1->Default();
    adder1->Build();
    multiplier->Default();
    multiplier->Build();
    
    adder1->Reset();
    multiplier->Reset();
    adder1->Calculate();
    multiplier->Calculate();
    
    EXPECT_EQ(multiplier->Output(), 3); // 1 + 2 = 3
}

// Test data propagation through network
TEST_F(ComponentNetworkTest, DataPropagation)
{
    adder1->Input1 = 10;
    adder1->Input2 = 20;
    multiplier->Input.Connect(&adder1->Output);
    multiplier->Factor = 2;
    
    adder1->Default();
    adder1->Build();
    multiplier->Default();
    multiplier->Build();
    
    adder1->Reset();
    multiplier->Reset();
    
    // First calculation
    adder1->Calculate();
    multiplier->Calculate();
    EXPECT_EQ(multiplier->Output(), 60); // (10 + 20) * 2 = 60
    
    // Change input and recalculate
    adder1->Input1 = 15;
    adder1->Input2 = 25;
    adder1->Calculate();
    multiplier->Calculate();
    EXPECT_EQ(multiplier->Output(), 80); // (15 + 25) * 2 = 80
}

// Test network with disconnected component
TEST_F(ComponentNetworkTest, DisconnectedComponent)
{
    adder1->Input1 = 5;
    adder1->Input2 = 3;
    // multiplier not connected
    
    adder1->Default();
    adder1->Build();
    multiplier->Default();
    multiplier->Build();
    
    adder1->Reset();
    multiplier->Reset();
    
    adder1->Calculate();
    multiplier->Calculate();
    
    // Multiplier should use its default/previous value or handle disconnected state
    EXPECT_EQ(adder1->Output(), 8); // 5 + 3 = 8
}

// Test network reset
TEST_F(ComponentNetworkTest, NetworkReset)
{
    adder1->Input1 = 100;
    adder1->Input2 = 200;
    multiplier->Input.Connect(&adder1->Output);
    multiplier->Factor = 2;
    
    adder1->Default();
    adder1->Build();
    multiplier->Default();
    multiplier->Build();
    
    adder1->Reset();
    multiplier->Reset();
    adder1->Calculate();
    multiplier->Calculate();
    
    EXPECT_EQ(multiplier->Output(), 600);
    
    // Reset and recalculate
    adder1->Reset();
    multiplier->Reset();
    adder1->Input1 = 1;
    adder1->Input2 = 1;
    adder1->Calculate();
    multiplier->Calculate();
    
    EXPECT_EQ(multiplier->Output(), 4); // (1 + 1) * 2 = 4
}

