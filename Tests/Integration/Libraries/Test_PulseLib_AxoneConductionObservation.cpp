#include <gtest/gtest.h>
#include "TimeLearner/AxoneConductionObservation.h"
#include <limits>
#include <stdexcept>
#include <vector>

namespace {
using namespace NMSDK::TimeLearner;

AxonePulseEvent Pulse(std::size_t tick) { return {tick,tick+1,1.,false}; }

TEST(AxoneConductionObservation, RetainsPeakThresholdWidthAndRightCensoring)
{
    const auto events = ExtractAxonePulseEvents({0.,1.,2.,0.,0.,1.}, .5);
    ASSERT_EQ(events.size(), 2u);
    EXPECT_EQ(events[0].onsetTick, 1u);
    EXPECT_EQ(events[0].endTick, 3u);
    EXPECT_DOUBLE_EQ(events[0].peak, 2.);
    EXPECT_FALSE(events[0].rightCensored);
    EXPECT_EQ(events[1].onsetTick, 5u);
    EXPECT_EQ(events[1].endTick, 6u);
    EXPECT_TRUE(events[1].rightCensored);
}

TEST(AxoneConductionObservation, RejectsNonfiniteSignalsAndThreshold)
{
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double infinity = std::numeric_limits<double>::infinity();
    EXPECT_THROW(ExtractAxonePulseEvents({0.,nan}, .5), std::invalid_argument);
    EXPECT_THROW(ExtractAxonePulseEvents({infinity}, .5), std::invalid_argument);
    EXPECT_THROW(ExtractAxonePulseEvents({0.,1.}, nan), std::invalid_argument);
}

TEST(AxoneConductionObservation, AssociatesExactDelayForEveryEvent)
{
    const auto result = AssignAxoneConductionEvents(
        {Pulse(10),Pulse(20),Pulse(30)}, {Pulse(12),Pulse(22),Pulse(32)}, 2,2);
    EXPECT_TRUE(result.completeOneToOne);
    EXPECT_FALSE(result.ambiguous);
    EXPECT_EQ(result.maximumMatched, 3u);
    ASSERT_EQ(result.certainPairs.size(), 3u);
    for(std::size_t index = 0; index < result.certainPairs.size(); ++index) {
        EXPECT_EQ(result.certainPairs[index].input, index);
        EXPECT_EQ(result.certainPairs[index].output, index);
        EXPECT_EQ(result.certainPairs[index].lagTicks, 2u);
    }
}

TEST(AxoneConductionObservation, MissingMiddleDoesNotShiftLaterEventOwnership)
{
    const auto result = AssignAxoneConductionEvents(
        {Pulse(10),Pulse(20),Pulse(30)}, {Pulse(12),Pulse(32)}, 2,2);
    EXPECT_FALSE(result.completeOneToOne);
    EXPECT_FALSE(result.ambiguous);
    EXPECT_EQ(result.maximumMatched, 2u);
    ASSERT_EQ(result.certainPairs.size(), 2u);
    EXPECT_EQ(result.certainPairs[1].input, 2u);
    EXPECT_EQ(result.certainPairs[1].output, 1u);
    EXPECT_TRUE(result.possibleOutputs[1].empty());
    EXPECT_TRUE(result.inputCanBeUnmatched[1]);
}

TEST(AxoneConductionObservation, AmbiguousSingleOutputIsNotAssignedGreedily)
{
    const auto result = AssignAxoneConductionEvents(
        {Pulse(10),Pulse(20)}, {Pulse(25)}, 0,20);
    EXPECT_EQ(result.maximumMatched, 1u);
    EXPECT_TRUE(result.ambiguous);
    EXPECT_FALSE(result.completeOneToOne);
    EXPECT_TRUE(result.certainPairs.empty());
    ASSERT_EQ(result.possibleInputs[0].size(), 2u);
    EXPECT_TRUE(result.inputCanBeUnmatched[0]);
    EXPECT_TRUE(result.inputCanBeUnmatched[1]);
    EXPECT_FALSE(result.outputCanBeUnmatched[0]);
}

TEST(AxoneConductionObservation, PreservesCertainPairAndReportsExtraOutput)
{
    const auto result = AssignAxoneConductionEvents({Pulse(10)}, {Pulse(12),Pulse(50)}, 2,2);
    EXPECT_EQ(result.maximumMatched, 1u);
    EXPECT_FALSE(result.ambiguous);
    EXPECT_FALSE(result.completeOneToOne);
    ASSERT_EQ(result.certainPairs.size(), 1u);
    EXPECT_EQ(result.certainPairs[0].output, 0u);
    EXPECT_TRUE(result.possibleInputs[1].empty());
    EXPECT_TRUE(result.outputCanBeUnmatched[1]);
}

TEST(AxoneConductionObservation, EqualCountsDoNotProveConduction)
{
    const auto result = AssignAxoneConductionEvents(
        {Pulse(10),Pulse(20)}, {Pulse(5),Pulse(12)}, 0,4);
    EXPECT_EQ(result.maximumMatched, 1u);
    EXPECT_FALSE(result.completeOneToOne);
    EXPECT_TRUE(result.inputCanBeUnmatched[1]);
    EXPECT_TRUE(result.outputCanBeUnmatched[0]);
}

TEST(AxoneConductionObservation, SilenceIsAnExplicitMissingResponse)
{
    const auto result = AssignAxoneConductionEvents({Pulse(10),Pulse(20)}, {}, 0,10);
    EXPECT_EQ(result.maximumMatched, 0u);
    EXPECT_FALSE(result.completeOneToOne);
    EXPECT_FALSE(result.ambiguous);
    EXPECT_TRUE(result.certainPairs.empty());
    EXPECT_TRUE(result.inputCanBeUnmatched[0]);
    EXPECT_TRUE(result.inputCanBeUnmatched[1]);
}

TEST(AxoneConductionObservation, RejectsUnorderedEventsAndInvalidBounds)
{
    EXPECT_THROW(AssignAxoneConductionEvents({Pulse(20),Pulse(10)}, {}, 0,10), std::invalid_argument);
    EXPECT_THROW(AssignAxoneConductionEvents({Pulse(10)}, {Pulse(20)}, 4,2), std::invalid_argument);
    EXPECT_THROW(AssignAxoneConductionEvents({}, {Pulse(20)}, 0,10), std::invalid_argument);
    auto invalid = Pulse(10);
    invalid.peak = std::numeric_limits<double>::infinity();
    EXPECT_THROW(AssignAxoneConductionEvents({invalid}, {}, 0,10), std::invalid_argument);
}

TEST(AxoneConductionObservation, BoundsAssignmentMemoryBeforeAllocatingTables)
{
    std::vector<AxonePulseEvent> events;
    for(std::size_t index = 0; index < 2048; ++index) events.push_back(Pulse(index*2));
    EXPECT_THROW(AssignAxoneConductionEvents(events,events,0,100), std::invalid_argument);
}
} // namespace
