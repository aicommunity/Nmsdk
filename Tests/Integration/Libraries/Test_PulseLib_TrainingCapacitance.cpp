#include <gtest/gtest.h>
#include "TimeLearner/TrainingCapacitance.h"
#include "TimeLearner/CapacitanceRegion.h"
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
TEST(TrainingCapacitanceRegion, ClassicSelectsItsOwnPathBeyondFourInputs)
{
    std::vector<InputParameters> p{{7,1,10.},{2,1,10.},{4,1,10.},{1,1,10.},{3,1,10.},{1,1,10.}};
    EXPECT_EQ(SelectCapacitanceRegion(ProbeRouting::ClassicBurst,p,4),(CapacitanceRegion{5,1,3}));
    auto initial=Original();initial.membraneScales["Dendrite1_99"]=.8;
    const auto request=MakeCapacitanceRegionRequest(initial,SelectCapacitanceRegion(ProbeRouting::ClassicBurst,p,4),1.2,3);
    EXPECT_EQ(request.membraneScales.at("Dendrite5_1"),1.2);
    EXPECT_EQ(request.membraneScales.at("Dendrite5_3"),1.2);
    for(const auto& [path,scale]:initial.membraneScales)EXPECT_EQ(request.membraneScales.at(path),scale);
    EXPECT_EQ(request.origin,initial.origin);EXPECT_EQ(request.maximumRelativeChange,initial.maximumRelativeChange);
}
TEST(TrainingCapacitanceRegion, BranchUsesAdjacentIntervalsInsteadOfTheWholeCommonCable)
{
    const std::vector<InputParameters> p{{8,1,10.},{5,1,10.},{5,1,10.},{2,1,10.},{1,1,10.}};
    EXPECT_EQ(SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,p,0),(CapacitanceRegion{1,6,8}));
    EXPECT_EQ(SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,p,2),(CapacitanceRegion{1,3,5}));
    const auto request=MakeCapacitanceRegionRequest(Original(),SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,p,2),1.2,3);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_1"),.9);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_2"),1.1);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_3"),1.2);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_5"),1.2);
    EXPECT_FALSE(request.membraneScales.count("Dendrite1_6"));
}
TEST(TrainingCapacitanceRegion, CoincidentAttachmentsHaveNoCapacitanceControl)
{
    const std::vector<InputParameters> p{{5,1,10.},{5,1,10.},{1,1,10.}};
    const auto region=SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,p,0);
    EXPECT_EQ(region,(CapacitanceRegion{1,6,5}));
    EXPECT_EQ(MakeCapacitanceRegionRequest(Original(),region,1.2,0),Original());
}
TEST(TrainingCapacitanceRegion, AbsoluteRequestsAreIdempotentAndRetainDormantCorrections)
{
    auto initial=Original();initial.membraneScales["Dendrite1_99"]=.8;
    const CapacitanceRegion region{1,1,2};
    const auto request=MakeCapacitanceRegionRequest(initial,region,1.2,2);
    EXPECT_EQ(MakeCapacitanceRegionRequest(request,region,1.2,2),request);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_1"),1.2);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_2"),1.2);
    EXPECT_EQ(request.membraneScales.at("Dendrite1_99"),.8);
    EXPECT_EQ(initial.membraneScales.at("Dendrite1_1"),.9);
}
TEST(TrainingCapacitanceRegion, AnchorAndMalformedGeometryAreNotSearchVariables)
{
    const std::vector<InputParameters> p{{2,1,10.},{1,1,10.}};
    for(const auto routing:{ProbeRouting::ClassicBurst,ProbeRouting::BranchSoloBurst})
    {
        EXPECT_THROW(SelectCapacitanceRegion(routing,p,1),std::invalid_argument);
        EXPECT_THROW(SelectCapacitanceRegion(routing,p,2),std::invalid_argument);
        EXPECT_THROW(SelectCapacitanceRegion(routing,{{1,1,10.}},0),std::invalid_argument);
    }
    EXPECT_THROW(SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,{{1,1,10.},{2,1,10.}},0),std::invalid_argument);
    EXPECT_THROW(SelectCapacitanceRegion(ProbeRouting::ClassicBurst,{{0,1,10.},{1,1,10.}},0),std::invalid_argument);
    EXPECT_THROW(SelectCapacitanceRegion(static_cast<ProbeRouting>(99),p,0),std::invalid_argument);
}
TEST(TrainingCapacitanceRegion, BoundsAndBudgetAreCheckedBeforeExpandingPaths)
{
    const auto initial=Original();
    EXPECT_THROW(MakeCapacitanceRegionRequest(initial,{1,1,3},1.2,2),std::invalid_argument);
    for(double value:{0.,1.4,std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity()})
        EXPECT_THROW(MakeCapacitanceRegionRequest(initial,{1,1,2},value,2),std::invalid_argument);
    for(const auto region:{CapacitanceRegion{0,1,1},CapacitanceRegion{1,0,1},CapacitanceRegion{1,4,1}})
        EXPECT_THROW(MakeCapacitanceRegionRequest(initial,region,1.,2),std::invalid_argument);
    const int limit=std::numeric_limits<int>::max();
    const auto huge=SelectCapacitanceRegion(ProbeRouting::ClassicBurst,{{limit,1,10.},{1,1,10.}},0);
    EXPECT_THROW(MakeCapacitanceRegionRequest(initial,huge,1.,2),std::invalid_argument);
    const auto empty=SelectCapacitanceRegion(ProbeRouting::BranchSoloBurst,{{limit,1,10.},{limit,1,10.}},0);
    EXPECT_EQ(MakeCapacitanceRegionRequest(initial,empty,1.,0),initial);
}
TEST(TrainingCapacitanceRegion, ARequestDoesNotInventC0OrNativeReadbackProof)
{
    const auto initial=Original();const auto request=MakeCapacitanceRegionRequest(initial,{1,3,3},1.2,1);
    EXPECT_EQ(request.origin,initial.origin);
    EXPECT_FALSE(TrainingCapacitanceReadbackMatches(request,initial));
    auto invalid=initial;invalid.origin.clear();
    EXPECT_THROW(MakeCapacitanceRegionRequest(invalid,{1,1,1},1.,1),std::invalid_argument);
}
}
