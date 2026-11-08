#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/DeclaredWindowBasinAssignment.h"
#include <algorithm>
#include <functional>
#include <limits>

namespace {
using namespace NMSDK::TimeLearner;
using Validity=DeclaredWindowBasinValidity;
struct Fixture {
    DeclaredWindowBasinSpecification specification;
    DeclaredWindowBasinPolicy policy;
    DeclaredWindowBasinWitness witness;
    const std::vector<double> full{2.,2.,3.,5.,3.,2.,3.,6.,3.,2.,2.};
    const std::vector<double> omit0{2.,2.,2.,2.,2.,2.,3.,6.,3.,2.,2.};
    const std::vector<double> omit1{2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.};
    Fixture() {
        specification.inputCount=2;specification.assignedInput=0;specification.windowBegin=0.;
        specification.windowEnd=10.;specification.minimumAmplitude=.5;
        policy.maximumInputs=2;policy.maximumSamples=11;policy.maximumTotalSamples=44;
        for(std::size_t i=0;i<full.size();++i)witness.sampleTimes.push_back(double(i));
        Responses(full,omit0,omit1);
    }
    void Responses(const std::vector<double>& f,const std::vector<double>& o0,const std::vector<double>& o1) {
        witness.fullBefore={2.,f};witness.fullAfter={2.,f};witness.omissions={{0,{2.,o0}},{1,{2.,o1}}};
    }
    DeclaredWindowBasinResult Select() const {return SelectDeclaredWindowBasinMaximum(specification,policy,witness);}
};
void NoMeasurement(const DeclaredWindowBasinResult& result) {
    EXPECT_NE(result.validity,Validity::Valid);EXPECT_FALSE(result.selectedCandidate);EXPECT_FALSE(result.measuredMaximum);
    EXPECT_FALSE(result.reasons.empty());
}
TEST(DeclaredWindowBasinAssignment,SeparatedEarlyVertexSurvivesResidualTailOnHigherLaterVertex) {
    Fixture f;
    const std::vector<double> full{2.,2.,3.,5.,3.,2.5,3.4,6.3,3.2,2.1,2.};
    const std::vector<double> earlyOnly{2.,2.,3.,5.,3.,2.5,2.4,2.3,2.2,2.1,2.};
    f.Responses(full,f.omit0,earlyOnly);const auto result=f.Select();
    ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,3u);EXPECT_DOUBLE_EQ(result.measuredMaximum->rawPotential,5.);
    ASSERT_EQ(result.candidates.size(),2u);EXPECT_EQ(result.candidates[1].necessaryInputs,(std::vector<std::size_t>{1}));
}
TEST(DeclaredWindowBasinAssignment,LaterAssignedMeasurementUsesActualFullPotentialIncludingTail) {
    Fixture f;auto full=f.full;full[7]=6.3;auto early=f.omit1;
    early[5]=2.5;early[6]=2.4;early[7]=2.3;early[8]=2.2;early[9]=2.1;
    f.Responses(full,f.omit0,early);f.specification.assignedInput=1;
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,7u);EXPECT_DOUBLE_EQ(result.measuredMaximum->rawPotential,6.3);
    EXPECT_DOUBLE_EQ(result.measuredMaximum->amplitude,4.3);EXPECT_DOUBLE_EQ(result.measuredMaximum->time,7.);
}
TEST(DeclaredWindowBasinAssignment,LateSharedVertexOutsideDeclaredWindowDoesNotVetoEarlyVertex) {
    Fixture f;f.Responses(f.full,std::vector<double>(11,2.),f.omit1);f.specification.windowEnd=5.;
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_EQ(result.candidates.size(),1u);
    ASSERT_TRUE(result.measuredMaximum);EXPECT_EQ(result.measuredMaximum->firstSample,3u);
}
TEST(DeclaredWindowBasinAssignment,HigherPotentiallyAssignedSharedVertexInsideWindowCannotBeHidden) {
    Fixture f;f.Responses(f.full,std::vector<double>(11,2.),f.omit1);
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Ambiguous);
    ASSERT_EQ(result.candidates.size(),2u);EXPECT_EQ(result.candidates[1].necessaryInputs,(std::vector<std::size_t>{0,1}));
}
TEST(DeclaredWindowBasinAssignment,HigherKnownOtherVertexInsideWindowDoesNotVetoAssignedVertex) {
    Fixture f;const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);
    ASSERT_EQ(result.candidates.size(),2u);EXPECT_GT(result.candidates[1].maximum.amplitude,result.candidates[0].maximum.amplitude);
    EXPECT_EQ(result.candidates[1].necessaryInputs,(std::vector<std::size_t>{1}));
}
TEST(DeclaredWindowBasinAssignment,HigherSharedOtherInputsCannotVetoWhenAssignedControlPreservesIt) {
    Fixture f;f.specification.inputCount=3;f.policy.maximumInputs=3;f.policy.maximumTotalSamples=55;
    f.witness.omissions.push_back({2,{2.,f.omit1}});
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_EQ(result.candidates.size(),2u);
    EXPECT_EQ(result.candidates[1].status,BasinCandidateStatus::SharedNecessary);
    EXPECT_EQ(result.candidates[1].necessaryInputs,(std::vector<std::size_t>{1,2}));
    EXPECT_EQ(result.candidates[1].controls[0],BasinControlPresence::Preserved);
}
TEST(DeclaredWindowBasinAssignment,HigherUnknownOtherControlCannotVetoDefiniteAssignedPreservation) {
    Fixture f;auto other=f.omit1;other[6]=3.;other[7]=2.;other[8]=3.;
    f.Responses(f.full,f.omit0,other);const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);
    ASSERT_EQ(result.candidates.size(),2u);EXPECT_EQ(result.candidates[1].status,BasinCandidateStatus::Unknown);
    EXPECT_EQ(result.candidates[1].controls[0],BasinControlPresence::Preserved);
}
TEST(DeclaredWindowBasinAssignment,HigherUnknownAssignedControlInsideWindowCannotBeHidden) {
    Fixture f;auto assigned=f.omit0;assigned[6]=3.;assigned[7]=2.;assigned[8]=3.;
    f.Responses(f.full,assigned,f.omit1);const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Ambiguous);ASSERT_EQ(result.candidates.size(),2u);
    EXPECT_EQ(result.candidates[1].controls[0],BasinControlPresence::Unknown);
}
TEST(DeclaredWindowBasinAssignment,MissingUnrelatedResponseDoesNotInvalidateAssignedVertex) {
    Fixture f;f.Responses(f.omit1,std::vector<double>(11,2.),f.omit1);
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,3u);
}
TEST(DeclaredWindowBasinAssignment,MergedVertexPreservedInBothSingleSourceControlsHasNoUniqueAssignment) {
    Fixture f;const std::vector<double> merged{2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.};
    f.Responses(merged,merged,merged);const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Ambiguous);ASSERT_EQ(result.candidates.size(),1u);
    EXPECT_EQ(result.candidates[0].status,BasinCandidateStatus::NoNecessaryInput);
}
TEST(DeclaredWindowBasinAssignment,CooperativeMergedVertexDestroyedByBothOmissionsRemainsAmbiguous) {
    Fixture f;f.Responses(f.omit1,std::vector<double>(11,2.),std::vector<double>(11,2.));
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Ambiguous);
    ASSERT_EQ(result.candidates.size(),1u);EXPECT_EQ(result.candidates[0].status,BasinCandidateStatus::SharedNecessary);
}
TEST(DeclaredWindowBasinAssignment,NonlinearHeightIncreaseDoesNotDestroyAnOtherwisePreservedVertex) {
    Fixture f;f.specification.windowEnd=5.;auto other=f.omit1;other[3]=8.;
    f.Responses(f.full,f.omit0,other);const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);
    ASSERT_TRUE(result.measuredMaximum);EXPECT_DOUBLE_EQ(result.measuredMaximum->rawPotential,5.);
}
TEST(DeclaredWindowBasinAssignment,SubFloorControlExtremumIsUnknownInsteadOfAbsent) {
    Fixture f;f.specification.windowEnd=5.;auto control=f.omit0;control[3]=2.25;
    f.Responses(f.full,control,f.omit1);const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Ambiguous);ASSERT_EQ(result.candidates.size(),1u);
    EXPECT_EQ(result.candidates[0].controls[0],BasinControlPresence::Unknown);
}
TEST(DeclaredWindowBasinAssignment,SubFloorFullExtremumCannotBecomeAnAssignedMeasurement) {
    Fixture f;f.specification.windowEnd=5.;auto full=f.full;full[2]=2.1;full[3]=2.25;full[4]=2.1;
    f.Responses(full,f.omit0,full);const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Missing);
}
TEST(DeclaredWindowBasinAssignment,TwoControlMaximaInsideOneFixedBasinAreUnknown) {
    Fixture f;f.specification.windowEnd=5.;auto control=f.omit0;control[2]=3.;control[3]=2.;control[4]=3.;
    f.Responses(f.full,control,f.omit1);const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Ambiguous);ASSERT_EQ(result.candidates.size(),1u);
    EXPECT_EQ(result.candidates[0].controls[0],BasinControlPresence::Unknown);
}
TEST(DeclaredWindowBasinAssignment,ControlPlateauCrossingMeasuredValleyBoundaryIsUnknown) {
    Fixture f;f.specification.windowEnd=5.;auto control=f.omit0;control[4]=control[5]=control[6]=4.;
    f.Responses(f.full,control,f.omit1);const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Ambiguous);
}
TEST(DeclaredWindowBasinAssignment,ConstantBaselineControlHasNoPeakRatherThanAClippedUnknownPlateau) {
    Fixture f;f.specification.windowEnd=5.;const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);
    ASSERT_EQ(result.candidates.size(),1u);EXPECT_EQ(result.candidates[0].controls[0],BasinControlPresence::AbsentWithinFixedBasin);
}
TEST(DeclaredWindowBasinAssignment,PositiveConstantControlCannotBeUsedAsProofOfVertexAbsence) {
    Fixture f;f.specification.windowEnd=5.;f.witness.omissions[0].trace.rawPotential.assign(11,3.);
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Ambiguous);
}
TEST(DeclaredWindowBasinAssignment,ContinuousFullPlateauRetainsActualFirstAndLastSamples) {
    Fixture f;f.specification.windowEnd=5.;auto full=f.full,other=f.omit1;
    full[2]=full[3]=full[4]=5.;other[2]=other[3]=other[4]=5.;f.Responses(full,f.omit0,other);
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,2u);EXPECT_EQ(result.measuredMaximum->lastSample,4u);
    EXPECT_DOUBLE_EQ(result.measuredMaximum->time,2.);EXPECT_DOUBLE_EQ(result.measuredMaximum->plateauEnd,4.);
}
TEST(DeclaredWindowBasinAssignment,MeasuredValleyPlateauIsRecordedWithoutChoosingAnInventedMidpoint) {
    Fixture f;f.specification.windowEnd=4.;
    const std::vector<double> full{2.,2.,5.,3.,2.,2.,2.,3.,6.,3.,2.};
    const std::vector<double> o0{2.,2.,2.,2.,2.,2.,2.,3.,6.,3.,2.};
    const std::vector<double> o1{2.,2.,5.,3.,2.,2.,2.,2.,2.,2.,2.};
    f.Responses(full,o0,o1);const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);
    ASSERT_EQ(result.candidates.size(),1u);EXPECT_EQ(result.candidates[0].right.firstSample,4u);
    EXPECT_EQ(result.candidates[0].right.lastSample,6u);EXPECT_FALSE(result.candidates[0].right.recordEdge);
    EXPECT_TRUE(result.candidates[0].left.recordEdge);
}
TEST(DeclaredWindowBasinAssignment,DeclaredWindowCannotCutTheWitnessSamplesAroundARealPeak) {
    Fixture f;f.specification.windowBegin=3.;f.specification.windowEnd=5.;
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Clipped);
}
TEST(DeclaredWindowBasinAssignment,RecordBoundaryMaximumInsideWindowCannotHideBehindAnInteriorPeak) {
    Fixture f;auto full=f.full;full[0]=9.;f.Responses(full,f.omit0,f.omit1);
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Clipped);
}
TEST(DeclaredWindowBasinAssignment,OutsideWindowBoundaryFeatureDoesNotCreateAGlobalVeto) {
    Fixture f;f.specification.windowEnd=5.;auto full=f.full;full[10]=9.;f.Responses(full,f.omit0,f.omit1);
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_EQ(result.candidates.size(),1u);
}
TEST(DeclaredWindowBasinAssignment,CroppingCannotManufactureAMaximumOnAMonotonicSlope) {
    Fixture f;f.specification.windowBegin=2.;f.specification.windowEnd=5.;
    const std::vector<double> full{2.,2.,3.,4.,5.,6.,7.,8.,7.,6.,5.};
    f.Responses(full,std::vector<double>(11,2.),full);const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Missing);EXPECT_TRUE(result.candidates.empty());
}
TEST(DeclaredWindowBasinAssignment,TiedSeparateAssignedMaximaRemainAmbiguous) {
    Fixture f;f.specification.windowEnd=5.;auto full=f.full,other=f.omit1;
    full[2]=other[2]=5.;full[3]=other[3]=2.;full[4]=other[4]=5.;f.Responses(full,f.omit0,other);
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::Ambiguous);
}
TEST(DeclaredWindowBasinAssignment,SmallerAssignedExtremaPermitTheUniqueHighestActualMaximum) {
    Fixture f;f.specification.windowEnd=5.;auto full=f.full,other=f.omit1;
    full[2]=other[2]=3.;full[3]=other[3]=2.;full[4]=other[4]=5.;f.Responses(full,f.omit0,other);
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,4u);
}
TEST(DeclaredWindowBasinAssignment,FullRepeatAmplitudeFailureDoesNotProduceAMeasurement) {
    Fixture f;f.witness.fullAfter.rawPotential[3]+=.1;
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::NonRepeatable);
}
TEST(DeclaredWindowBasinAssignment,RepeatValleyTopologyMustHoldEvenInsideAmplitudeTolerance) {
    Fixture f;f.policy.repeatabilityAbsolute=.2;f.witness.fullAfter.rawPotential[5]=3.1;
    // The fullBefore valley at5 moves to6 although every change fits this loose
    // engineering repeat tolerance. The declared fixed basin was not repeated.
    f.witness.fullBefore.rawPotential[5]=3.;f.witness.fullBefore.rawPotential[6]=3.1;
    f.witness.fullAfter.rawPotential[6]=3.;
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::NonRepeatable);
}
TEST(DeclaredWindowBasinAssignment,RepeatHighestAssignedVertexCannotSwapWithinAmplitudeTolerance) {
    Fixture f;f.specification.windowEnd=5.;f.policy.repeatabilityAbsolute=.3;auto full=f.full,other=f.omit1;
    full[2]=other[2]=5.;full[3]=other[3]=2.;full[4]=other[4]=4.9;f.Responses(full,f.omit0,other);
    f.witness.fullAfter.rawPotential[2]=4.8;
    const auto result=f.Select();NoMeasurement(result);EXPECT_EQ(result.validity,Validity::NonRepeatable);
}
TEST(DeclaredWindowBasinAssignment,OriginalOmissionOrdinalsAreIndependentOfVectorOrder) {
    Fixture f;std::reverse(f.witness.omissions.begin(),f.witness.omissions.end());
    const auto result=f.Select();ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,3u);
}
TEST(DeclaredWindowBasinAssignment,DimensionsAndNonfiniteOrNonmonotonicDataFailClosed) {
    using Edit=std::function<void(Fixture&)>;
    const std::vector<Edit> edits{
        [](auto& f){f.witness.fullAfter.rawPotential.pop_back();},
        [](auto& f){f.witness.omissions[0].trace.rawPotential.pop_back();},
        [](auto& f){f.witness.omissions[1].omittedInput=0;},
        [](auto& f){f.witness.omissions[1].omittedInput=2;},
        [](auto& f){f.witness.omissions.pop_back();},
        [](auto& f){f.witness.fullBefore.rawPotential[3]=std::numeric_limits<double>::quiet_NaN();},
        [](auto& f){f.witness.omissions[0].trace.baseline=std::numeric_limits<double>::infinity();},
        [](auto& f){f.witness.sampleTimes[3]=f.witness.sampleTimes[2];},
        [](auto& f){f.witness.sampleTimes[3]=std::numeric_limits<double>::infinity();},
        [](auto& f){f.specification.inputCount=std::numeric_limits<std::size_t>::max();f.policy.maximumInputs=f.specification.inputCount;}
    };
    for(std::size_t i=0;i<edits.size();++i){SCOPED_TRACE(i);Fixture f;edits[i](f);NoMeasurement(f.Select());}
}
TEST(DeclaredWindowBasinAssignment,ExplicitBudgetsAreCheckedAtTheirExactBoundary) {
    Fixture exact;EXPECT_EQ(exact.Select().validity,Validity::Valid);
    Fixture samples;samples.policy.maximumSamples=10;EXPECT_EQ(samples.Select().validity,Validity::BudgetExhausted);
    Fixture total;total.policy.maximumTotalSamples=43;EXPECT_EQ(total.Select().validity,Validity::BudgetExhausted);
    Fixture inputs;inputs.policy.maximumInputs=1;EXPECT_EQ(inputs.Select().validity,Validity::BudgetExhausted);
    Fixture missing;missing.policy.maximumTotalSamples=0;NoMeasurement(missing.Select());
}
TEST(DeclaredWindowBasinAssignment,InvalidDeclarationCannotBecomeAnImplicitAutomaticWindow) {
    using Edit=std::function<void(Fixture&)>;
    const std::vector<Edit> edits{
        [](auto& f){f.specification.schemaVersion=2;},[](auto& f){f.policy.schemaVersion=2;},
        [](auto& f){f.specification.windowEnd=f.specification.windowBegin;},
        [](auto& f){f.specification.windowBegin=-1.;},[](auto& f){f.specification.windowEnd=11.;},
        [](auto& f){f.specification.windowEnd=std::numeric_limits<double>::quiet_NaN();},
        [](auto& f){f.specification.minimumAmplitude=0.;},[](auto& f){f.specification.assignedInput=2;},
        [](auto& f){f.policy.repeatabilityAbsolute=-1.;}
    };
    for(std::size_t i=0;i<edits.size();++i){SCOPED_TRACE(i);Fixture f;edits[i](f);NoMeasurement(f.Select());}
}
TEST(DeclaredWindowBasinAssignment,SingleInputRemainsExplicitlyOutsideThisMethod) {
    Fixture f;f.specification.inputCount=1;const auto result=f.Select();NoMeasurement(result);
    EXPECT_EQ(result.validity,Validity::Unsupported);
}
TEST(DeclaredWindowBasinAssignment,MigrationEndpointsReportOnlyTheDeclaredObservableCriterion) {
    Fixture f;f.specification.windowBegin=5.;
    // These endpoint records permit different physical stories: a retained
    // source peak may have migrated to the earlier basin while another peak
    // replaced it. Geometry alone cannot establish that hidden lineage.
    const std::vector<double> earlyOnly{2.,2.,3.,5.,3.,2.,2.,2.,2.,2.,2.};
    const std::vector<double> lateOnly{2.,2.,2.,2.,2.,2.,3.,6.,3.,2.,2.};
    f.Responses(f.full,earlyOnly,lateOnly);const auto result=f.Select();
    ASSERT_EQ(result.validity,Validity::Valid);ASSERT_TRUE(result.measuredMaximum);
    EXPECT_EQ(result.measuredMaximum->firstSample,7u);
    ASSERT_EQ(result.candidates.size(),1u);EXPECT_EQ(result.candidates[0].necessaryInputs,(std::vector<std::size_t>{0}));
    EXPECT_FALSE(DeclaredWindowBasinResult::TrainingCertificateEligible);
    EXPECT_STREQ(DeclaredWindowBasinResult::MethodId(),"declared-window-basin-necessity-v1");
}
}
