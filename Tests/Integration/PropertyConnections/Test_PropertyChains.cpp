#include <gtest/gtest.h>
#include "../../../../Rdk/Deploy/Include/rdk.h"
#include <memory>
#include <vector>

using namespace RDK;

// Test component for property chains
class ChainTestComponent : public UNet
{
public:
    UProperty<int, ChainTestComponent, ptPubOutput> Output;
    UProperty<int, ChainTestComponent, ptPubInput> Input;
    UProperty<int, ChainTestComponent, ptPubState> State;

    ChainTestComponent() : 
        Output("Output", this),
        Input("Input", this),
        State("State", this)
    {
    }

protected:
    virtual bool ACalculate(void) override
    {
        if (Input.IsConnected())
        {
            Output = Input();
        }
        else
        {
            Output = State();
        }
        return true;
    }
};

class PropertyChainsTest : public ::testing::Test
{
protected:
    void SetUp() override
    {
        comp1 = std::make_unique<ChainTestComponent>();
        comp2 = std::make_unique<ChainTestComponent>();
        comp3 = std::make_unique<ChainTestComponent>();
        comp4 = std::make_unique<ChainTestComponent>();
    }

    void TearDown() override
    {
        comp1.reset();
        comp2.reset();
        comp3.reset();
        comp4.reset();
    }

    std::unique_ptr<ChainTestComponent> comp1;
    std::unique_ptr<ChainTestComponent> comp2;
    std::unique_ptr<ChainTestComponent> comp3;
    std::unique_ptr<ChainTestComponent> comp4;
};

// Test simple property chain
TEST_F(PropertyChainsTest, SimpleChain)
{
    // Chain: comp1 -> comp2 -> comp3
    comp1->Output = 10;
    comp2->Input.Connect(&comp1->Output);
    comp3->Input.Connect(&comp2->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    
    EXPECT_EQ(comp3->Input(), 10);
}

// Test long property chain
TEST_F(PropertyChainsTest, LongChain)
{
    // Chain: comp1 -> comp2 -> comp3 -> comp4
    comp1->Output = 42;
    comp2->Input.Connect(&comp1->Output);
    comp3->Input.Connect(&comp2->Output);
    comp4->Input.Connect(&comp3->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    comp4->Default();
    comp4->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    comp4->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    comp4->Calculate();
    
    EXPECT_EQ(comp4->Input(), 42);
}

// Test chain with data modification
TEST_F(PropertyChainsTest, ChainWithModification)
{
    comp1->Output = 5;
    comp2->Input.Connect(&comp1->Output);
    comp2->State = 2; // comp2 will add 2 to input
    comp3->Input.Connect(&comp2->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    
    comp1->Calculate();
    comp2->Calculate(); // Output = Input + State = 5 + 2 = 7
    comp3->Calculate();
    
    EXPECT_EQ(comp3->Input(), 7);
}

// Test breaking chain
TEST_F(PropertyChainsTest, BreakChain)
{
    comp1->Output = 100;
    comp2->Input.Connect(&comp1->Output);
    comp3->Input.Connect(&comp2->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    
    EXPECT_EQ(comp3->Input(), 100);
    
    // Break chain in the middle
    comp2->Input.DetachFrom(&comp1->Output);
    comp2->State = 50;
    
    comp2->Calculate();
    comp3->Calculate();
    
    // comp3 should now get comp2's output based on State
    EXPECT_EQ(comp3->Input(), 50);
}

// Test chain with multiple branches
TEST_F(PropertyChainsTest, ChainWithBranches)
{
    comp1->Output = 20;
    comp2->Input.Connect(&comp1->Output);
    comp3->Input.Connect(&comp1->Output); // Branch
    comp4->Input.Connect(&comp2->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    comp4->Default();
    comp4->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    comp4->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    comp4->Calculate();
    
    EXPECT_EQ(comp2->Input(), 20);
    EXPECT_EQ(comp3->Input(), 20);
    EXPECT_EQ(comp4->Input(), 20);
}

// Test chain update propagation
TEST_F(PropertyChainsTest, ChainUpdatePropagation)
{
    comp1->Output = 1;
    comp2->Input.Connect(&comp1->Output);
    comp3->Input.Connect(&comp2->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    EXPECT_EQ(comp3->Input(), 1);
    
    // Update source
    comp1->Output = 99;
    comp1->Calculate();
    comp2->Calculate();
    comp3->Calculate();
    EXPECT_EQ(comp3->Input(), 99);
}

// Test chain with disconnected components
TEST_F(PropertyChainsTest, ChainWithDisconnected)
{
    comp1->Output = 10;
    comp2->Input.Connect(&comp1->Output);
    // comp3 not connected
    comp4->Input.Connect(&comp3->Output);
    
    comp1->Default();
    comp1->Build();
    comp2->Default();
    comp2->Build();
    comp3->Default();
    comp3->Build();
    comp4->Default();
    comp4->Build();
    
    comp1->Reset();
    comp2->Reset();
    comp3->Reset();
    comp4->Reset();
    
    comp1->Calculate();
    comp2->Calculate();
    comp3->State = 30;
    comp3->Calculate();
    comp4->Calculate();
    
    EXPECT_EQ(comp2->Input(), 10);
    EXPECT_EQ(comp4->Input(), 30); // From comp3's State
}

