#include <gtest/gtest.h>
#include "TimeLearner/TrainingCapacitance.h"
#include <limits>
#include <stdexcept>

namespace {
using namespace NMSDK::TimeLearner;
TrainingCapacitance Original()
{return {std::string(64,'a'),.3,{{"Dendrite1_1",.9},{"Dendrite1_2",1.1},{"Dendrite2_1",1.}}};}
TEST(TrainingCapacitanceState, GrowthExtendsInventoryWithoutInventingANewTrim)
{
    const auto before=Original();auto grown=before;grown.membraneScales["Dendrite1_3"]=1.;
    EXPECT_TRUE(TrainingCapacitanceReadbackMatches(before,grown));
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches(grown,before));
    EXPECT_TRUE(EquivalentTrainingCapacitance(before,grown));
    grown.membraneScales["Dendrite1_3"]=.95;
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches(before,grown));
    EXPECT_FALSE(EquivalentTrainingCapacitance(before,grown));
}
TEST(TrainingCapacitanceState, HistoricalRestoreRetainsNewC0ButClearsLaterCorrection)
{
    auto historical=Original(),current=historical;
    current.membraneScales["Dendrite1_1"]=1.2;current.membraneScales["Dendrite1_3"]=.8;
    const auto restored=RestoreTrainingCapacitance(historical,current);ASSERT_TRUE(restored);
    EXPECT_DOUBLE_EQ(restored->membraneScales.at("Dendrite1_1"),.9);
    EXPECT_DOUBLE_EQ(restored->membraneScales.at("Dendrite1_3"),1.);
    EXPECT_EQ(restored->origin,historical.origin);EXPECT_EQ(restored->maximumRelativeChange,historical.maximumRelativeChange);
}
TEST(TrainingCapacitanceState, OriginPolicyAndKnownPathLossCannotBeHidden)
{
    const auto original=Original();auto changed=original;changed.origin=std::string(64,'b');
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches(original,changed));
    EXPECT_THROW(RestoreTrainingCapacitance(original,changed),std::invalid_argument);
    changed=original;changed.maximumRelativeChange=.4;
    EXPECT_FALSE(EquivalentTrainingCapacitance(original,changed));
    EXPECT_THROW(RestoreTrainingCapacitance(original,changed),std::invalid_argument);
    changed=original;changed.membraneScales.erase("Dendrite2_1");
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches(original,changed));
    EXPECT_THROW(RestoreTrainingCapacitance(original,changed),std::invalid_argument);
}
TEST(TrainingCapacitanceState, UnknownProvenanceIsNotAnInventedUnitBaseline)
{
    EXPECT_TRUE(EquivalentTrainingCapacitance({},{}));EXPECT_TRUE(TrainingCapacitanceReadbackMatches({},{}));
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches({},Original()));EXPECT_FALSE(TrainingCapacitanceReadbackMatches(Original(),{}));
    EXPECT_THROW(RestoreTrainingCapacitance({},Original()),std::invalid_argument);
    EXPECT_THROW(RestoreTrainingCapacitance(Original(),{}),std::invalid_argument);
}
TEST(TrainingCapacitanceState, CanonicalDendriticPathsAndOriginalBoundsAreRequired)
{
    for(const auto path:{"Soma","LTMembrane","Dendrite01_2","Dendrite1_0","Dendrite1_2.ExcChannel","Dendrite1_2_3"})
    {auto state=Original();state.membraneScales[path]=1.;EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument)<<path;}
    auto state=Original();state.membraneScales["Dendrite1_1"]=0.;
    EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
    state=Original();state.membraneScales["Dendrite1_1"]=1.31;
    EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
}
TEST(TrainingCapacitanceState, NonfiniteOrEmptyMetadataCannotEnterControllerState)
{
    auto state=Original();state.origin="a";EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
    state=Original();state.maximumRelativeChange=std::numeric_limits<double>::infinity();
    EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
    state=Original();state.membraneScales.clear();EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
    state=Original();state.membraneScales["Dendrite1_1"]=std::numeric_limits<double>::quiet_NaN();
    EXPECT_THROW(ValidateTrainingCapacitance(state),std::invalid_argument);
}
}
