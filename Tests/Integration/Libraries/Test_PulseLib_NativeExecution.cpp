#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/BoundedTraining.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NativeResponseDomainCapture.h"
#include "TimeLearner/MatchedOmissionEvidenceJson.h"
#include "TimeLearner/NativeMatchedOmissionGroup.h"
#include "TimeLearner/NativeDeclaredWindowBasinAssignment.h"
#include "TimeLearner/ResponseDomainEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <type_traits>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <locale>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <limits>
#include <functional>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
class NativeLearnerExecution : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
enum class Interference { None,PhysicalReset,SourceAmplitude,SourceFrequency,Pattern,DeleteSynapse,ExternalStop,OwnerBuild,NoopOwnerBuild,PrepareFailure,SampleFailure,RevisionFailure,OwnerUnInit,TinySourceAmplitude,WrongObservationChannel,WrongSoloSelector,TinyPhysicalCapacitance };

QJsonObject BoundedProbeArtifact(const PreparedVerificationProbe& context,const ProbeObservation& observation)
{
    const auto& s=observation.specification;QJsonArray stimuli,windows,peaks,assignments,baseline;
    for(const auto& event:observation.stimuli)stimuli.append(QJsonObject{{"id",QString::fromStdString(event.id)},{"time",event.time}});
    for(double value:s.baseline)baseline.append(value);
    for(const auto& window:s.windows)windows.append(QJsonObject{{"input_id",QString::fromStdString(window.inputId)},
        {"stimulus_id",QString::fromStdString(window.stimulusId)},{"channel",int(window.channel)},
        {"begin",window.begin},{"end",window.end}});
    for(const auto& peak:observation.peaks)peaks.append(QJsonObject{{"input_id",QString::fromStdString(peak.inputId)},
        {"stimulus_id",QString::fromStdString(peak.stimulusId)},{"validity",PeakValidityName(peak.validity)},
        {"raw",peak.rawPotential?QJsonValue(*peak.rawPotential):QJsonValue(QJsonValue::Null)},
        {"amplitude",peak.amplitude?QJsonValue(*peak.amplitude):QJsonValue(QJsonValue::Null)},
        {"time",peak.time?QJsonValue(*peak.time):QJsonValue(QJsonValue::Null)},
        {"plateau_end",peak.plateauEnd?QJsonValue(*peak.plateauEnd):QJsonValue(QJsonValue::Null)}});
    for(const auto& assignment:observation.burstAssignments)
    {
        QJsonArray waves;
        for(const auto& wave:assignment.waves)waves.append(QJsonObject{{"stimulus_id",QString::fromStdString(wave.stimulusId)},
            {"raw",wave.rawPotential},{"amplitude",wave.amplitude},{"time",wave.time},{"plateau_end",wave.plateauEnd}});
        assignments.append(QJsonObject{{"channel",int(assignment.channel)},{"validity",PeakValidityName(assignment.validity)},{"waves",waves}});
    }
    return {{"schema",int(observation.schemaVersion)},{"run_id",QString::fromStdString(s.runId)},
        {"trial_id",QString::fromStdString(s.trialId)},{"sample_id",QString::fromStdString(s.sampleId)},
        {"pattern_hash",QString::fromStdString(s.patternHash)},{"base_model_revision",QString::fromStdString(context.baseModelRevision)},
        {"effective_model_revision",QString::fromStdString(context.effectiveModelRevision)},{"epoch",int(context.modelEpoch)},
        {"protocol_revision",QString::fromStdString(context.protocolRevision)},
        {"selected_input_index",context.selectedInputIndex?QJsonValue(int(*context.selectedInputIndex)):QJsonValue(QJsonValue::Null)},
        {"complete",observation.complete},{"valid",observation.valid},{"begin",s.begin},{"end",s.end},
        {"maximum_sample_gap",s.maximumSampleGap},{"minimum_amplitude",s.minimumAmplitude},
        {"sample_count",int(observation.sampleCount)},{"baseline",baseline},{"windows",windows},
        {"actual_stimuli",stimuli},{"peaks",peaks},{"burst_assignments",assignments}};
}

template<class Learner> void ExecuteProbeThroughLearner(unsigned frequency,Interference interference=Interference::None,unsigned inputCount=2,unsigned observationSchema=2,bool mergedBurst=false,bool boundedTraining=false,bool sharedVertex=false,std::vector<std::size_t> sourceOrdinals={},bool missingSubsetSink=false,bool captureDomains=false,bool fullRevisionProvider=false,bool matchedOmission=false,bool separatedOmission=false,bool declaredBasin=false,int assignedOverride=-1)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    ASSERT_GE(inputCount,1u);ASSERT_LE(inputCount,6u);
    std::string subsetSuffix;
    if(observationSchema==6)for(auto index:sourceOrdinals)subsetSuffix+="_"+std::to_string(index);
    const std::string profileName=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+"_N"+std::to_string(inputCount)+"_native_executor"+
        (interference==Interference::None?"":"_fault"+std::to_string(int(interference)))+
        (observationSchema==3?"_whole_burst":"")+(mergedBurst?"_merged_burst":"")+(boundedTraining?"_bounded":"")+(sharedVertex?"_shared_vertex":"")+
        (observationSchema==6?"_subset"+subsetSuffix:"")+(missingSubsetSink?"_missing_sink":"")+
        (captureDomains?"_domain_capture":"")+(matchedOmission?"_matched_omission":"")+(separatedOmission?"_separated_control":"")+
        (declaredBasin?"_declared_basin_i"+std::to_string(assignedOverride):"");
    // Reader A/B changes artifact identity only, never the storage class names
    // included in the semantic model identity.
    const std::string name=profileName+(fullRevisionProvider?"_full_revision":"");
    StorageProfileSpec profile;profile.name=profileName;profile.frequencyHz=frequency;
    profile.neuronBaseClass="NSPNeuronGen";profile.initialThreshold=1.;
    const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(learner);learner->Name="Learner";learner->StructureBuildMode=1;
    learner->NumInputDendrite=inputCount;learner->NeuronClassName=registered.neuronClass;
    std::vector<int> lengths;for(unsigned i=0;i<inputCount;++i)lengths.push_back(int(inputCount-i));
    learner->DendriteLength=lengths;
    learner->CalculateMode=1;learner->NormalizationMode=1;
    learner->EnablePostTrainTuning=false;learner->AutoCalibrateFixedLTZThreshold=false;
    double gaps[]{.01,.08,.16,.24,.32,.40};
    if(mergedBurst){ASSERT_EQ(inputCount,2u);gaps[1]=.001;}
    if(separatedOmission){ASSERT_TRUE(matchedOmission);ASSERT_EQ(inputCount,2u);gaps[1]=.5;}
    std::vector<double> isi,onsets;double onset=0.;QJsonArray configuredPattern;
    MDMatrix<double> pattern;pattern.Assign(inputCount,1,0.);
    for(unsigned i=0;i<inputCount;++i)
    {pattern(i,0)=gaps[i];isi.push_back(gaps[i]);onset+=gaps[i];onsets.push_back(onset);configuredPattern.append(gaps[i]);}
    learner->InputPattern=pattern;const double duration=onset+.08;
    UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();model->Reset();
    model->Calculate();core.environment->IncreaseModelTimeByStep();
    auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
    ASSERT_EQ(learner->DendriteLength.GetData(),lengths);
    ASSERT_TRUE(neuron->template GetComponentL<NPulseMembrane>("Dendrite1_"+std::to_string(inputCount),true));
    // A revision changes only if preparation changes semantic routing.  The
    // declared-input override can already equal the initial one-hot routing.
    std::vector<bool> initialBranchRouting;
    if(branch)for(unsigned input=0;input<inputCount;++input)
    {
        auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(
            "Dendrite1_"+std::to_string(inputCount-input)+".ExcSynapse1",true);
        ASSERT_TRUE(synapse);initialBranchRouting.push_back(synapse->Input.IsConnected());
    }
    int active=0;
    if(branch && inputCount>1)
    {
        auto point0=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_"+std::to_string(inputCount)+".ExcSynapse1",true);
        auto point1=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_"+std::to_string(inputCount-1)+".ExcSynapse1",true);
        ASSERT_TRUE(point0);ASSERT_TRUE(point1);
        if(point0->Input.IsConnected() && !point1->Input.IsConnected())active=1;
    }
    if(declaredBasin){ASSERT_TRUE(matchedOmission);ASSERT_GE(assignedOverride,0);ASSERT_LT(unsigned(assignedOverride),inputCount);active=assignedOverride;}
    const auto phase=learner->TrainingPhase.GetData();const auto need=learner->IsNeedToTrain.GetData();
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    NmsdkTools::ModelRevisionObserver revisionObserver;
    std::size_t revisionReads=0,tickRevisionReads=0,fullBoundaryReads=0;bool revisionFailure=false;
    const auto readRevision=[&]() {
        ++revisionReads;if(revisionFailure)throw std::runtime_error("injected_revision_failure");
        const auto identity=NmsdkTools::IdentifyModel(neuron,ports);
        if(!identity["valid"].toBool())throw std::runtime_error("invalid_native_identity");
        return identity["sha256"].toString().toStdString();
    };
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(before["valid"].toBool());
    const auto base=readRevision();bool armed=false;
    NativeResponseDomainCapture domainCapture;
    std::ostringstream trace;trace.imbue(std::locale::classic());
    trace<<std::setprecision(17)<<"native_tick_start_s,stimulus";
    for(unsigned i=0;i<(branch?1u:inputCount);++i)trace<<",raw_soma_"<<i;trace<<'\n';
    unsigned sampled=0,sourceEvents=0;
    NativeProbeRequest request;request.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
    request.activeInput=active;request.inputId="input"+std::to_string(active);request.protocolRevision="native_burst_N"+std::to_string(inputCount)+"_v1";
    if(observationSchema==3)request.protocolRevision="native_ordered_burst_N"+std::to_string(inputCount)+"_v2";
    request.baseModelRevision=base;request.expectedInputIsi=isi;
    // Match the production adapter: inspect actual typed graph inputs on every
    // Before/After tick, retaining independent full captures at the boundaries.
    // The explicit Full provider remains an A/B control for the same physics.
    request.readModelRevision=[&]() {
        ++tickRevisionReads;
        if(fullRevisionProvider)return readRevision();
        ++revisionReads;if(revisionFailure)throw std::runtime_error("injected_revision_failure");
        return revisionObserver.Read(neuron,ports).toStdString();
    };
    request.readFullModelRevision=[&]() {++fullBoundaryReads;return readRevision();};
    auto& spec=request.specification;spec.runId=name;spec.trialId=name+"/probe0";spec.sampleId="sample0";
    spec.schemaVersion=observationSchema;
    if(observationSchema==3)spec.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;
    spec.patternHash=NmsdkTools::CanonicalModelDataSha256(configuredPattern).toStdString();
    spec.end=duration;spec.maximumSampleGap=1./frequency;spec.maximumSamples=std::size_t((duration+.1)*frequency);
    for(unsigned i=0;i<inputCount;++i)
    {
        const auto id="pulse"+std::to_string(i);spec.expectedStimulusIds.push_back(id);
        if(!branch || int(i)==active)spec.windows.push_back({"input"+std::to_string(i),branch?0u:i,onsets[i]-.001,onsets[i]+.06,id});
    }
    if(observationSchema==6)
    {
        ASSERT_FALSE(mergedBurst);ASSERT_FALSE(boundedTraining);ASSERT_FALSE(sharedVertex);
        ASSERT_TRUE(interference==Interference::None || interference==Interference::ExternalStop);
        request.protocolRevision="native_subset_waveform_N"+std::to_string(inputCount)+"_v1";
        spec.stimulusSubset=StimulusSubsetCharacterization{spec.patternHash,inputCount,sourceOrdinals};
        const auto plan=PlanStimulusSubset(isi,sourceOrdinals);QJsonArray presented;
        for(double gap:plan.presentedIsi)presented.append(gap);
        spec.patternHash=NmsdkTools::CanonicalModelDataSha256(presented).toStdString();
        spec.windows.clear();spec.expectedStimulusIds.clear();
        for(auto index:sourceOrdinals)spec.expectedStimulusIds.push_back("pulse"+std::to_string(index));
    }
    if(sharedVertex)
    {
        ASSERT_FALSE(branch);ASSERT_TRUE(mergedBurst);ASSERT_EQ(observationSchema,2u);ASSERT_EQ(inputCount,2u);
        // Observe one real soma twice under different pulse labels. The
        // historical recorder remains diagnostic; certification must refuse.
        spec.windows[1].channel=0;
    }
    if(interference==Interference::WrongObservationChannel)spec.windows[0].channel=1;
    if(interference==Interference::WrongSoloSelector)request.activeInput=1-active;
    request.onPrepared=[&](const PreparedVerificationProbe& declaration,const ProbeSpec& actual) {
        if(interference==Interference::PrepareFailure)throw std::runtime_error("injected_prepare_failure");
        armed=true;EXPECT_EQ(declaration.baseModelRevision,base);
        EXPECT_EQ(actual.modelRevision,declaration.effectiveModelRevision);
        EXPECT_GE(actual.begin,1./frequency);
        EXPECT_EQ(actual.baseline.size(),branch?1u:inputCount);
        if(captureDomains) {
            std::vector<std::string> paths;
            for(std::size_t i=0;i<actual.baseline.size();++i) {
                const auto path="Soma"+std::to_string(i+1);
                ASSERT_TRUE(neuron->template GetComponentL<NPulseMembrane>(path,true));
                paths.push_back(path);
            }
            domainCapture.Arm(declaration,actual,std::move(paths));
        }
        if(observationSchema==3)
        {
            if(branch)EXPECT_EQ(declaration.selectedInputIndex,std::optional<std::size_t>(active));
            else EXPECT_FALSE(declaration.selectedInputIndex);
        }
        if(branch)
        {
            bool routingChanged=false;
            for(unsigned input=0;input<inputCount;++input)
            {
                auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(
                    "Dendrite1_"+std::to_string(inputCount-input)+".ExcSynapse1",true);
                ASSERT_TRUE(synapse);EXPECT_EQ(synapse->Input.IsConnected(),int(input)==active);
                routingChanged=routingChanged || initialBranchRouting.at(input)!=(int(input)==active);
            }
            EXPECT_EQ(readRevision(),declaration.effectiveModelRevision);
            if(routingChanged)EXPECT_NE(declaration.effectiveModelRevision,base);
            else EXPECT_EQ(declaration.effectiveModelRevision,base);
        }
    };
    request.onSample=[&](const NativeProbeSample& sample) {
        if(interference==Interference::SampleFailure && sampled==10)throw std::runtime_error("injected_sample_failure");
        ++sampled;sourceEvents+=unsigned(sample.newStimuli.size());
        if(captureDomains)domainCapture.Append(sample);
        trace<<sample.time<<','<<sample.stimulus;
        for(const auto value:sample.potentials)trace<<','<<value;trace<<'\n';
    };
    if(missingSubsetSink)
    {ASSERT_EQ(observationSchema,6u);request.onSample={};}
    if(matchedOmission) {
        ASSERT_EQ(observationSchema,3u);ASSERT_FALSE(captureDomains);ASSERT_EQ(inputCount,2u);
        ASSERT_TRUE(interference==Interference::None || interference==Interference::ExternalStop || interference==Interference::TinyPhysicalCapacitance);
        NativeProbeBindings bindings;bindings.owner=learner.Get();bindings.neuron=neuron;
        bindings.dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        bindings.inputCount=int(inputCount);bindings.branch=branch;
        for(unsigned i=0;i<(branch?1u:inputCount);++i)
            bindings.somas.push_back(neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true));
        spec.stimulusProfile=StimulusProfile{generator->GetCompClassName(),generator->Amplitude.GetData(),
            generator->PulseLength.GetData(),double(generator->GetTimeStep()),generator->FrequencyDeviation.GetData(),
            generator->UseTransitSignal.GetData(),generator->UsePatternOutput.GetData()};
        NativeMatchedOmissionPlan groupPlan;groupPlan.fullBurst=request;groupPlan.groupId=name+"/group0";
        groupPlan.channel=branch?0u:std::size_t(active);
        for(const auto& soma:bindings.somas) {ASSERT_TRUE(soma);groupPlan.physicalChannelPaths.push_back(soma->GetLongName(learner.Get()));}
        // Measurement-group tolerances are explicit, independent of Train tolerances.
        groupPlan.policy.timeComparisonTolerance=1e-10;groupPlan.policy.baselineAbsolute=1e-12;
        groupPlan.policy.repeatabilityAbsolute=1e-10;groupPlan.policy.repeatabilityRelative=0.;
        groupPlan.policy.influenceAbsolute=1e-6;groupPlan.policy.influenceRelative=0.;
        groupPlan.policy.maximumSamples=spec.maximumSamples;groupPlan.policy.maximumTotalSamples=spec.maximumSamples*(inputCount+2);
        groupPlan.policy.maximumNativeProbes=inputCount+2;
        groupPlan.maximumModelSeconds=(duration+.1)*(inputCount+2);groupPlan.maximumWallSeconds=600.;
        NativeMatchedOmissionGroup group;bool requested=true,injected=false;
        NativeMatchedOmissionAdapter driver;
        driver.queue=[&](auto value){learner->QueueNativeProbe(std::move(value));};
        driver.probeState=[&](){return learner->NativeProbeState();};
        driver.takeResult=[&](){return learner->TakeNativeProbeResult();};
        driver.cancel=[&](const auto& reason){learner->CancelNativeProbe(reason);};
        driver.readModelRevision=readRevision;driver.requested=[&](){return requested;};
        const auto modelTime=[&](){return core.environment->GetTime().GetDoubleTime();};
        const auto wallTime=[](){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();};
        group.Start(groupPlan,bindings,modelTime(),wallTime());unsigned groupTicks=0;
        while(group.State()==NativeMatchedOmissionState::Running) {
            ASSERT_LT(groupTicks++,unsigned(groupPlan.maximumModelSeconds*frequency)+10u);
            if(!injected && group.Result().packets.size()==1 && interference!=Interference::None) {
                injected=true;
                if(interference==Interference::ExternalStop)requested=false;
                else {
                    auto channel=neuron->template GetComponentL<NPulseChannel>("Dendrite1_"+std::to_string(inputCount)+".ExcChannel",true);
                    ASSERT_TRUE(channel);channel->Capacity=std::nextafter(channel->Capacity.GetData(),std::numeric_limits<double>::infinity());
                }
            }
            group.BeforeTick(driver,modelTime(),wallTime());
            if(group.State()!=NativeMatchedOmissionState::Running)break;
            model->Calculate();group.AfterTick(driver,modelTime(),wallTime());core.environment->IncreaseModelTimeByStep();
        }
        const auto& closed=group.Result();
        if(interference==Interference::None) {
            ASSERT_EQ(group.State(),NativeMatchedOmissionState::Completed)<<closed.reason;
            ASSERT_EQ(group.IssuedNativeProbes(),inputCount+2);ASSERT_EQ(closed.packets.size(),inputCount+2);
            ASSERT_EQ(closed.witness.omitEachInput.size(),inputCount);ASSERT_TRUE(closed.assignment);
            if(!declaredBasin) {
                if(separatedOmission)EXPECT_EQ(closed.assignment->validity,MatchedOmissionValidity::Valid);
                else EXPECT_EQ(closed.assignment->validity,MatchedOmissionValidity::Ambiguous);
            }
            EXPECT_EQ(closed.specification.baseModelRevision,base);EXPECT_EQ(readRevision(),base);
            EXPECT_TRUE(closed.witness.fullBefore.fullMaskRestored);EXPECT_TRUE(closed.witness.fullAfter.fullMaskRestored);
            for(const auto& trace:closed.witness.omitEachInput)EXPECT_TRUE(trace.fullMaskRestored);
        }
        else {
            EXPECT_TRUE(injected);EXPECT_EQ(group.IssuedNativeProbes(),1u);EXPECT_EQ(closed.packets.size(),1u);
            EXPECT_FALSE(closed.assignment);
            EXPECT_EQ(group.State(),interference==Interference::ExternalStop?NativeMatchedOmissionState::Cancelled:NativeMatchedOmissionState::Rejected);
        }
        std::optional<QJsonObject> basinArtifact;
        if(declaredBasin) {
            NativeDeclaredWindowBasinSpecification declared;declared.groupId=groupPlan.groupId;
            declared.inputId=request.inputId;declared.assignedInput=std::size_t(active);declared.channel=groupPlan.channel;
            // Fixed fixture declaration from source onsets, before looking at
            // response maxima; no post-hoc peak centering or predictor proof.
            declared.windowBeginOffset=onsets[std::size_t(active)]-.001;
            declared.windowEndOffset=onsets[std::size_t(active)]+.06;
            DeclaredWindowBasinPolicy geometryPolicy;geometryPolicy.maximumInputs=inputCount;
            geometryPolicy.maximumSamples=groupPlan.policy.maximumSamples;
            geometryPolicy.maximumTotalSamples=groupPlan.policy.maximumTotalSamples;
            geometryPolicy.repeatabilityAbsolute=groupPlan.policy.repeatabilityAbsolute;
            const auto timeBefore=modelTime();const auto revisionBefore=readRevision();const auto stateBefore=learner->NativeProbeState();
            const auto selected=SelectNativeDeclaredWindowBasinMaximum(declared,geometryPolicy,closed);
            EXPECT_EQ(modelTime(),timeBefore);EXPECT_EQ(readRevision(),revisionBefore);EXPECT_EQ(learner->NativeProbeState(),stateBefore);
            EXPECT_FALSE(NativeDeclaredWindowBasinResult::TrainingCertificateEligible);
            std::size_t rejectedTampering=0;
            if(interference!=Interference::None) {
                EXPECT_EQ(selected.status,NativeDeclaredWindowBasinStatus::Rejected);EXPECT_FALSE(selected.geometry);
                EXPECT_FALSE(selected.reasons.empty());
            }
            else {
                ASSERT_EQ(selected.status,NativeDeclaredWindowBasinStatus::Completed);
                ASSERT_TRUE(selected.geometry);EXPECT_TRUE(selected.reasons.empty());
                auto withoutV1Assignment=closed;withoutV1Assignment.assignment.reset();
                const auto independent=SelectNativeDeclaredWindowBasinMaximum(declared,geometryPolicy,withoutV1Assignment);
                ASSERT_EQ(independent.status,NativeDeclaredWindowBasinStatus::Completed);ASSERT_TRUE(independent.geometry);
                EXPECT_EQ(independent.geometry->validity,selected.geometry->validity);
                if(mergedBurst) {
                    EXPECT_EQ(selected.geometry->validity,DeclaredWindowBasinValidity::Ambiguous);
                    EXPECT_FALSE(selected.geometry->measuredMaximum);
                }
                else {
                    ASSERT_EQ(selected.geometry->validity,DeclaredWindowBasinValidity::Valid);
                    ASSERT_TRUE(selected.geometry->measuredMaximum);ASSERT_TRUE(selected.actualAssignedOnset);
                    EXPECT_GE(selected.geometry->measuredMaximum->time,*selected.actualAssignedOnset);
                    EXPECT_GE(selected.geometry->measuredMaximum->firstSample,
                        std::size_t(std::llround((*selected.actualAssignedOnset-closed.witness.fullBefore.observation.begin)*frequency)));
                    const auto& actual=closed.witness.fullBefore.observation.channels[groupPlan.channel].samples[
                        selected.geometry->measuredMaximum->firstSample];
                    EXPECT_EQ(selected.geometry->measuredMaximum->time,actual.time);
                    EXPECT_EQ(selected.geometry->measuredMaximum->rawPotential,actual.rawPotential);
                }
                using Edit=std::function<void(NativeMatchedOmissionResult&)>;
                const std::vector<Edit> edits{
                    [](auto& value){value.reason="cancelled";},
                    [](auto& value){value.packets.pop_back();},
                    [](auto& value){value.sourceIsi[0]+=.001;},
                    [](auto& value){value.appliedSourceIsi[0]+=.001;},
                    [](auto& value){value.appliedPresentedIsi[1][0]+=.001;},
                    [](auto& value){value.witness.omitEachInput[0].prepared.effectiveModelRevision="tampered";},
                    [](auto& value){value.witness.omitEachInput[0].resetBinding="tampered";},
                    [](auto& value){value.witness.omitEachInput[0].stimulusSamples[0]=1.;},
                    [](auto& value){value.packets[1].observation->specification.maximumSamples=value.policy.maximumSamples+1;},
                    [](auto& value){value.packets[1].observation->stimuli[0].time+=.001;},
                    [](auto& value){value.packets[1].requestedSpecification->stimulusSubset->sourceTrainingPatternHash="tampered";}
                };
                for(std::size_t i=0;i<edits.size();++i) {
                    SCOPED_TRACE(i);auto tampered=closed;edits[i](tampered);
                    const auto rejected=SelectNativeDeclaredWindowBasinMaximum(declared,geometryPolicy,tampered);
                    EXPECT_EQ(rejected.status,NativeDeclaredWindowBasinStatus::Rejected);EXPECT_FALSE(rejected.geometry);
                    EXPECT_FALSE(rejected.reasons.empty());++rejectedTampering;
                }
                for(bool method:{false,true}) {
                    auto changed=declared;if(method)changed.methodId="matched-omission-assigned-maximum-v1";else changed.groupId+="/other";
                    const auto rejected=SelectNativeDeclaredWindowBasinMaximum(changed,geometryPolicy,closed);
                    EXPECT_EQ(rejected.status,NativeDeclaredWindowBasinStatus::Rejected);EXPECT_FALSE(rejected.geometry);++rejectedTampering;
                }
                // Adversarial PACKET replay control, deliberately not a native
                // physical response: replace soma samples and regenerate the
                // closed recorder evidence using production ProbeRecorder.
                // A well-formed geometry/packet can still be pre-causal, so it
                // must not be promoted by the native-to-geometry bridge.
                auto synthetic=closed;std::vector<MatchedOmissionTrace*> syntheticTraces{&synthetic.witness.fullBefore};
                for(auto& value:synthetic.witness.omitEachInput)syntheticTraces.push_back(&value);
                syntheticTraces.push_back(&synthetic.witness.fullAfter);
                for(std::size_t i=0;i<syntheticTraces.size();++i) {
                    auto& response=*syntheticTraces[i];const bool retained=std::find(response.presentedOrdinals.begin(),
                        response.presentedOrdinals.end(),std::size_t(active))!=response.presentedOrdinals.end();
                    for(auto& channel:response.observation.channels)for(std::size_t frame=0;frame<channel.samples.size();++frame)
                        channel.samples[frame].rawPotential=channel.baseline+(retained && channel.channel==groupPlan.channel && frame==1?.001:0.);
                    auto& packet=synthetic.packets[i];ProbeRecorder recorder(packet.observation->specification);std::size_t event=0;
                    const auto frames=response.stimulusSamples.size();
                    for(std::size_t frame=0;frame<frames;++frame) {
                        const double time=response.observation.channels.front().samples[frame].time;
                        while(event<response.observation.events.size() && !NMSDK::TimeLearner::Detail::After(response.observation.events[event].time,time)) {
                            const auto& stimulus=response.observation.events[event++];recorder.RecordStimulus(stimulus.id,stimulus.time);
                        }
                        std::vector<double> values;for(const auto& channel:response.observation.channels)values.push_back(channel.samples[frame].rawPotential);
                        recorder.Observe(time,values,response.prepared.effectiveModelRevision);
                    }
                    packet.observation=recorder.Close(response.observation.channels.front().samples.back().time,
                        response.prepared.effectiveModelRevision,"window_closed");
                    ASSERT_TRUE(packet.observation->valid);ASSERT_TRUE(packet.observation->complete);
                }
                auto broad=declared;broad.windowBeginOffset=0.;broad.windowEndOffset=duration;
                const auto causalRejection=SelectNativeDeclaredWindowBasinMaximum(broad,geometryPolicy,synthetic);
                EXPECT_EQ(causalRejection.status,NativeDeclaredWindowBasinStatus::CausalityRejected);
                EXPECT_FALSE(causalRejection.geometry);EXPECT_FALSE(causalRejection.reasons.empty());
            }
            EXPECT_EQ(modelTime(),timeBefore);EXPECT_EQ(readRevision(),revisionBefore);EXPECT_EQ(learner->NativeProbeState(),stateBefore);
            if(std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                QJsonArray reasons;for(const auto& reason:selected.reasons)reasons.append(QString::fromStdString(reason));
                const char* status=selected.status==NativeDeclaredWindowBasinStatus::Completed?"completed":
                    selected.status==NativeDeclaredWindowBasinStatus::CausalityRejected?"causality_rejected":"rejected";
                QJsonObject record{{"kind","native_declared_window_basin_diagnostic"},{"schema_version",1},
                    {"method",NativeDeclaredWindowBasinResult::MethodId()},{"group_id",QString::fromStdString(declared.groupId)},
                    {"assigned_input",active},{"channel",double(declared.channel)},
                    {"window_begin_offset",declared.windowBeginOffset},{"window_end_offset",declared.windowEndOffset},
                    {"specification",QJsonObject{{"schema_version",int(declared.schemaVersion)},{"method_id",QString::fromStdString(declared.methodId)},
                        {"group_id",QString::fromStdString(declared.groupId)},{"input_id",QString::fromStdString(declared.inputId)},
                        {"assigned_input",double(declared.assignedInput)},{"channel",double(declared.channel)},
                        {"window_begin_offset",declared.windowBeginOffset},{"window_end_offset",declared.windowEndOffset}}},
                    {"geometry_policy",QJsonObject{{"schema_version",int(geometryPolicy.schemaVersion)},
                        {"maximum_inputs",double(geometryPolicy.maximumInputs)},{"maximum_samples",double(geometryPolicy.maximumSamples)},
                        {"maximum_total_samples",double(geometryPolicy.maximumTotalSamples)},{"repeatability_absolute",geometryPolicy.repeatabilityAbsolute}}},
                    {"minimum_amplitude",closed.specification.minimumAmplitude},
                    {"status",status},{"status_enum",int(selected.status)},{"reasons",reasons},{"rejected_tampering",double(rejectedTampering)},
                    {"actual_assigned_onset",selected.actualAssignedOnset?QJsonValue(*selected.actualAssignedOnset):QJsonValue(QJsonValue::Null)},
                    {"geometry_validity",selected.geometry?QJsonValue(DeclaredWindowBasinValidityName(selected.geometry->validity)):QJsonValue(QJsonValue::Null)},
                    {"geometry",QJsonValue(QJsonValue::Null)},{"measured_maximum",QJsonValue(QJsonValue::Null)},
                    {"diagnostic_only",true},{"training_certificate_eligible",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
                const auto encodeMaximum=[](const ResponseMaximum& maximum) {
                    return QJsonObject{{"first_sample",double(maximum.firstSample)},{"last_sample",double(maximum.lastSample)},
                        {"raw_potential",maximum.rawPotential},{"amplitude",maximum.amplitude},{"time",maximum.time},{"plateau_end",maximum.plateauEnd}};
                };
                if(selected.geometry) {
                    const auto& geometry=*selected.geometry;QJsonArray candidates,geometryReasons;
                    for(const auto& reason:geometry.reasons)geometryReasons.append(QString::fromStdString(reason));
                    for(const auto& candidate:geometry.candidates) {
                        const auto anchor=[](const BasinAnchor& value) {return QJsonObject{{"first_sample",double(value.firstSample)},
                            {"last_sample",double(value.lastSample)},{"record_edge",value.recordEdge}};};
                        QJsonArray controls,necessary,candidateReasons;
                        for(auto state:candidate.controls)controls.append(BasinControlPresenceName(state));
                        for(auto input:candidate.necessaryInputs)necessary.append(double(input));
                        for(const auto& reason:candidate.reasons)candidateReasons.append(QString::fromStdString(reason));
                        candidates.append(QJsonObject{{"maximum",encodeMaximum(candidate.maximum)},{"left",anchor(candidate.left)},
                            {"right",anchor(candidate.right)},{"status",BasinCandidateStatusName(candidate.status)},
                            {"controls",controls},{"necessary_inputs",necessary},{"reasons",candidateReasons}});
                    }
                    record["geometry"]=QJsonObject{{"validity",DeclaredWindowBasinValidityName(geometry.validity)},{"reasons",geometryReasons},
                        {"candidates",candidates},{"selected_candidate",geometry.selectedCandidate?QJsonValue(double(*geometry.selectedCandidate)):QJsonValue(QJsonValue::Null)},
                        {"measured_maximum",geometry.measuredMaximum?QJsonValue(encodeMaximum(*geometry.measuredMaximum)):QJsonValue(QJsonValue::Null)}};
                }
                if(selected.geometry && selected.geometry->measuredMaximum) {
                    record["measured_maximum"]=encodeMaximum(*selected.geometry->measuredMaximum);
                }
                basinArtifact=std::move(record);
            }
        }
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
            const QString directory=QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name);
            ASSERT_TRUE(QDir().mkpath(directory));QJsonArray packets,traceFiles;
            MatchedOmissionPrimary portablePrimary;std::vector<QString> portablePaths;
            for(const auto& packet:closed.packets)packets.append(EncodeNativeProbeEvidence(packet));
            if(closed.witness.fullBefore.nativeCompleted) {
                std::vector<const MatchedOmissionTrace*> traces{&closed.witness.fullBefore};
                for(const auto& omitted:closed.witness.omitEachInput)traces.push_back(&omitted);
                if(closed.witness.fullAfter.nativeCompleted)traces.push_back(&closed.witness.fullAfter);
                for(std::size_t i=0;i<traces.size();++i) {
                    const auto& trace=*traces[i];const auto& native=closed.packets.at(i);
                    NativeResponseDomainCapture proof;proof.Arm(trace.prepared,native.observation->specification,trace.physicalChannelPaths);
                    std::size_t event=0;
                    for(std::size_t frame=0;frame<trace.stimulusSamples.size();++frame) {
                        NativeProbeSample sample;sample.time=trace.observation.channels.front().samples.at(frame).time;
                        sample.stimulus=trace.stimulusSamples[frame];sample.effectiveModelRevision=trace.prepared.effectiveModelRevision;
                        for(const auto& channel:trace.observation.channels)sample.potentials.push_back(channel.samples.at(frame).rawPotential);
                        while(event<trace.observation.events.size() && trace.observation.events[event].time<=sample.time) {
                            const auto& emitted=trace.observation.events[event++];sample.newStimuli.push_back({emitted.id,emitted.time});
                        }
                        proof.Append(sample);
                    }
                    proof.CloseNative(native);const auto csv=EncodeNativeResponseDomainTrace(proof);
                    const auto fileName="native-"+QString::number(i)+".csv";QFile file(directory+"/"+fileName);
                    ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));ASSERT_EQ(file.write(csv),csv.size());file.close();
                    portablePaths.push_back(fileName);portablePrimary.emplace(fileName,csv);
                    QJsonArray mask;for(auto ordinal:trace.presentedOrdinals)mask.append(int(ordinal));
                    traceFiles.append(QJsonObject{{"path",fileName},{"presented_ordinals",mask},{"sha256",QString::fromLatin1(QCryptographicHash::hash(csv,QCryptographicHash::Sha256).toHex())}});
                }
            }
            QJsonArray assignmentReasons,maxima,paths;
            for(const auto& path:closed.specification.physicalChannelPaths)paths.append(QString::fromStdString(path));
            if(closed.assignment) {
                for(const auto& reason:closed.assignment->reasons)assignmentReasons.append(QString::fromStdString(reason));
                for(const auto& peak:closed.assignment->maxima) {
                    QJsonArray support,influences;
                    for(auto input:peak.supportedInputs)support.append(int(input));
                    for(auto influence:peak.influenceByInput)influences.append(OmissionInfluenceName(influence));
                    maxima.append(QJsonObject{{"first_sample",int(peak.maximum.firstSample)},{"last_sample",int(peak.maximum.lastSample)},
                        {"raw_potential",peak.maximum.rawPotential},{"amplitude",peak.maximum.amplitude},
                        {"time",peak.maximum.time},{"plateau_end",peak.maximum.plateauEnd},
                        {"supported_inputs",support},{"influence_by_input",influences},{"unknown",peak.unknown},
                        {"clipped",peak.clipped},{"precedes_assigned_stimulus",peak.precedesAssignedStimulus}});
                }
            }
            QJsonObject summary{{"schema_version",1},{"kind","native_matched_omission_fixture"},
                {"method",MatchedOmissionResult::MethodId()},{"group_id",QString::fromStdString(groupPlan.groupId)},
                {"native_probes",int(group.IssuedNativeProbes())},{"packets",packets},{"traces",traceFiles},
                {"source_pattern_sha256",QString::fromStdString(closed.specification.patternHash)},
                {"reset_binding",QString::fromStdString(closed.specification.resetBinding)},
                {"model_instance_binding",QString::fromStdString(closed.specification.modelInstanceBinding)},
                {"physical_channel_paths",paths},{"assigned_input",int(closed.specification.assignedInput)},
                {"assigned_channel",int(closed.specification.channel)},
                {"policy",QJsonObject{{"comparison_radius_ticks",int(groupPlan.policy.comparisonRadiusTicks)},
                    {"time_comparison_tolerance",groupPlan.policy.timeComparisonTolerance},
                    {"baseline_absolute",groupPlan.policy.baselineAbsolute},
                    {"repeatability_absolute",groupPlan.policy.repeatabilityAbsolute},
                    {"repeatability_relative",groupPlan.policy.repeatabilityRelative},
                    {"influence_absolute",groupPlan.policy.influenceAbsolute},
                    {"influence_relative",groupPlan.policy.influenceRelative}}},
                {"assignment_reasons",assignmentReasons},{"maxima",maxima},
                {"selected_full_maximum",closed.assignment && closed.assignment->selectedFullMaximum?
                    QJsonValue(int(*closed.assignment->selectedFullMaximum)):QJsonValue(QJsonValue::Null)},
                {"reason",QString::fromStdString(closed.reason)},
                {"assignment_validity",closed.assignment?MatchedOmissionValidityName(closed.assignment->validity):"not_available"},
                {"training_certificate_eligible",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
            QFile file(directory+"/group.json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(summary).toJson();ASSERT_EQ(file.write(bytes),bytes.size());ASSERT_TRUE(file.flush());
            QJsonValue portableReference(QJsonValue::Null),sourceSpecificationHash(QJsonValue::Null);
            if(interference==Interference::None) {
                const auto portable=EncodeMatchedOmissionEvidence(closed,portablePaths,portablePrimary);
                const auto encoded=QJsonDocument(portable).toJson();
                const auto imported=DecodeMatchedOmissionEvidence(encoded,portablePrimary);
                EXPECT_EQ(EncodeMatchedOmissionEvidence(imported,portablePaths,portablePrimary),portable);
                QFile outputFile(directory+"/matched-witness.json");
                ASSERT_TRUE(outputFile.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                ASSERT_EQ(outputFile.write(encoded),encoded.size());ASSERT_TRUE(outputFile.flush());
                portableReference=QJsonObject{{"relative_path","matched-witness.json"},{"bytes",double(encoded.size())},
                    {"sha256",QString::fromLatin1(QCryptographicHash::hash(encoded,QCryptographicHash::Sha256).toHex())}};
                sourceSpecificationHash=NmsdkTools::CanonicalModelDataSha256(portable["specification"]);
            }
            else EXPECT_THROW(EncodeMatchedOmissionEvidence(closed,portablePaths,portablePrimary),std::invalid_argument);
            if(basinArtifact) {
                (*basinArtifact)["witness_binding"]=QJsonObject{{"complete_group",portableReference.isObject()},
                    {"group_id",QString::fromStdString(closed.specification.groupId)},
                    {"source_pattern_sha256",QString::fromStdString(closed.specification.patternHash)},
                    {"source_specification_sha256",sourceSpecificationHash},
                    {"base_model_revision",QString::fromStdString(closed.specification.baseModelRevision)},
                    {"effective_model_revision",QString::fromStdString(closed.specification.effectiveModelRevision)},
                    {"protocol_revision",QString::fromStdString(closed.specification.protocolRevision)},
                    {"group",QJsonObject{{"relative_path","group.json"},{"bytes",double(bytes.size())},
                        {"sha256",QString::fromLatin1(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())}}},
                    {"portable",portableReference}};
                QFile artifact(directory+"/declared-window-basin-diagnostic.json");ASSERT_TRUE(artifact.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                const auto encoded=QJsonDocument(*basinArtifact).toJson();ASSERT_EQ(artifact.write(encoded),encoded.size());ASSERT_TRUE(artifact.flush());
            }
        }
        core.environment->DestroyModel();return;
    }
    const auto prototype=request;
    const auto firstProbeStarted=std::chrono::steady_clock::now();
    learner->QueueNativeProbe(std::move(request));ASSERT_TRUE(learner->NativeProbeOwnsControl());
    unsigned ticks=0;
    while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
    {
        ASSERT_LT(ticks++,unsigned((duration+.1)*frequency));
        model->Calculate();core.environment->IncreaseModelTimeByStep();
        if(interference!=Interference::None && ticks==frequency/25)
        {
            switch(interference)
            {
            case Interference::PhysicalReset:
            {
                const auto physicalBefore=readRevision();neuron->Reset();
                EXPECT_EQ(readRevision(),physicalBefore); // Same spec, different physical history.
                break;
            }
            case Interference::SourceAmplitude:generator->Amplitude=1.5;break;
            case Interference::TinySourceAmplitude:generator->Amplitude=1.+1e-12;break;
            case Interference::TinyPhysicalCapacitance:
            {
                auto channel=neuron->template GetComponentL<NPulseChannel>("Dendrite1_"+std::to_string(inputCount)+".ExcChannel",true);
                ASSERT_TRUE(channel);ASSERT_TRUE(channel->IsReady());
                const auto previousRevision=readRevision();
                const auto previous=channel->Capacity.GetData();
                channel->Capacity=std::nextafter(previous,std::numeric_limits<double>::infinity());
                EXPECT_NE(channel->Capacity.GetData(),previous);EXPECT_TRUE(channel->IsReady());
                EXPECT_NE(readRevision(),previousRevision);break;
            }
            case Interference::SourceFrequency:generator->Frequency=100.;break;
            case Interference::Pattern:
                learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true)->MatrixData(0,0)=.02;break;
            case Interference::DeleteSynapse:
                neuron->template GetComponentL<NPulseMembrane>("Dendrite1_1",true)->DelComponent("ExcSynapse1",true);break;
            case Interference::ExternalStop:
                learner->IsNeedToTrain=false;EXPECT_EQ(learner->InputPattern(0,0),.01);
                EXPECT_EQ(learner->TrainingPhase.GetData(),phase);EXPECT_EQ(readRevision(),base);break;
            case Interference::OwnerBuild:
                learner->DendriteLength=std::vector<int>{3,1};ASSERT_FALSE(learner->IsReady());learner->Build();break;
            case Interference::NoopOwnerBuild:learner->Build();break;
            case Interference::RevisionFailure:revisionFailure=true;break;
            case Interference::OwnerUnInit:learner->UnInit();break;
            case Interference::PrepareFailure:case Interference::SampleFailure:
            case Interference::WrongObservationChannel:case Interference::WrongSoloSelector:break;
            case Interference::None:break;
            }
        }
    }
    const auto result=learner->TakeNativeProbeResult();ASSERT_TRUE(result);
    // Freeze accounting before any artifact reads, references or final probes.
    const auto firstProbeTickRevisionReads=tickRevisionReads,firstProbeFullBoundaryReads=fullBoundaryReads;
    const auto firstProbeObserverFullReads=revisionObserver.FullReads(),firstProbeObserverCacheHits=revisionObserver.CacheHits();
    const double firstProbeWallSeconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-firstProbeStarted).count();
    std::optional<ResponseDomainSpec> capturedDomains;
    if(captureDomains) {
        const auto& captured=domainCapture.Observation();
        ResponseDomainSpec domains;domains.modelRevision=captured.modelRevision;
        domains.protocolRevision=captured.protocolRevision;domains.patternHash=captured.patternHash;
        for(const auto& e:captured.events)domains.stimulusIds.push_back(e.id);
        for(const auto& channel:captured.channels) {
            domains.channelIds.push_back(channel.channel);
            for(const auto& e:captured.events)
                domains.domains.push_back({channel.channel,e.id,e.time,captured.end});
        }
        const auto diagnostic=domainCapture.Close(*result,domains);
        EXPECT_TRUE(domainCapture.Observation().complete);
        EXPECT_EQ(domainCapture.StimulusSamples().size(),sampled);
        EXPECT_EQ(diagnostic.associations.size(),captured.channels.size()*captured.events.size());
        EXPECT_EQ(diagnostic.channels.size(),captured.channels.size());
        EXPECT_FALSE(diagnostic.TrainingCertificateEligible());
        EXPECT_TRUE(diagnostic.reasons.empty());
        capturedDomains=domains;
        // Broad competing domains intentionally do not prove causal origin.
        EXPECT_THROW(domainCapture.Close(*result,domains),std::invalid_argument);
    }
    for(const auto& reason:result->reasons)std::cout<<name<<" adapter_reason="<<reason<<std::endl;
    if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        QJsonArray events,reasons,peaks,adapterReasons,assignments;
        for(const auto& reason:result->reasons)adapterReasons.append(QString::fromStdString(reason));
        if(result->observation)
        {
            const auto& observed=*result->observation;
            for(const auto& event:observed.stimuli)events.append(QJsonObject{{"id",QString::fromStdString(event.id)},{"time",event.time}});
            for(const auto& reason:observed.reasons)reasons.append(QString::fromStdString(reason));
            for(const auto& peak:observed.peaks)peaks.append(QJsonObject{{"input_id",QString::fromStdString(peak.inputId)},
                {"validity",PeakValidityName(peak.validity)},{"raw_potential",peak.rawPotential?QJsonValue(*peak.rawPotential):QJsonValue(QJsonValue::Null)}});
            for(const auto& assignment:observed.burstAssignments)
            {
                QJsonArray waves;
                for(const auto& wave:assignment.waves)waves.append(QJsonObject{{"stimulus_id",QString::fromStdString(wave.stimulusId)},
                    {"time",wave.time},{"plateau_end",wave.plateauEnd},{"raw_potential",wave.rawPotential},{"amplitude",wave.amplitude}});
                assignments.append(QJsonObject{{"channel",int(assignment.channel)},
                    {"validity",PeakValidityName(assignment.validity)},{"waves",waves}});
            }
        }
        QJsonValue source=QJsonValue(QJsonValue::Null);
        if(result->observation && result->observation->specification.stimulusProfile)
        {
            const auto& p=*result->observation->specification.stimulusProfile;
            source=QJsonObject{{"class",QString::fromStdString(p.generatorClass)},
                {"amplitude",p.amplitude},{"pulse_length_s",p.pulseLength},{"frequency_hz",p.frequencyHz},
                {"frequency_deviation",p.frequencyDeviation},{"transit",p.useTransitSignal},{"pattern_output",p.usePatternOutput}};
        }
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile counts(directory+"/"+QString::fromStdString(name)+".revision_reads.json");
        ASSERT_TRUE(counts.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto countBytes=QJsonDocument(QJsonObject{{"schema_version",1},{"kind","native_probe_revision_reads"},
            {"scope","first_probe"},{"revision_provider",fullRevisionProvider?"full":"typed"},
            {"storage_profile",QString::fromStdString(profileName)},{"run_id",QString::fromStdString(prototype.specification.runId)},
            {"trial_id",QString::fromStdString(prototype.specification.trialId)},
            {"native_ticks",int(ticks)},{"sampled_frames",int(sampled)},{"wall_seconds",firstProbeWallSeconds},
            {"tick_revision_reads",double(firstProbeTickRevisionReads)},{"full_boundary_reads",double(firstProbeFullBoundaryReads)},
            {"observer_full_reads",double(firstProbeObserverFullReads)},{"observer_cache_hits",double(firstProbeObserverCacheHits)},
            {"scientific_training_result",false}}).toJson();
        ASSERT_EQ(counts.write(countBytes),countBytes.size());
        QFile csv(directory+"/"+QString::fromStdString(name)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto wave=QByteArray::fromStdString(trace.str());ASSERT_EQ(csv.write(wave),wave.size());
        if(captureDomains) {
            ASSERT_TRUE(capturedDomains);const auto domainWave=EncodeNativeResponseDomainTrace(domainCapture);
            const auto traceName=QString::fromStdString(name)+".domains.csv";
            QFile domainCsv(directory+"/"+traceName);ASSERT_TRUE(domainCsv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            ASSERT_EQ(domainCsv.write(domainWave),domainWave.size());ASSERT_TRUE(domainCsv.flush());domainCsv.close();
            ASSERT_TRUE(domainCsv.open(QIODevice::ReadOnly));const auto readback=domainCsv.readAll();ASSERT_EQ(readback,domainWave);
            const auto packet=EncodeNativeResponseDomainEvidence(domainCapture,*capturedDomains,traceName,readback);
            QFile domainJson(directory+"/"+QString::fromStdString(name)+".domains.json");
            ASSERT_TRUE(domainJson.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(packet).toJson();ASSERT_EQ(domainJson.write(bytes),bytes.size());
        }
        QFile file(directory+"/"+QString::fromStdString(name)+".json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const bool normal=interference==Interference::None || interference==Interference::NoopOwnerBuild;
        const auto bytes=QJsonDocument(QJsonObject{{"schema_version",1},{"kind","native_learner_probe_execution"},
            {"model_before",before},{"model_after",normal?QJsonValue(NmsdkTools::IdentifyModel(neuron,ports)):QJsonValue(QJsonValue::Null)},
            {"effective_revision",result->prepared?QJsonValue(QString::fromStdString(result->prepared->effectiveModelRevision)):QJsonValue(QJsonValue::Null)},
            {"selected_input_index",result->prepared && result->prepared->selectedInputIndex?QJsonValue(int(*result->prepared->selectedInputIndex)):QJsonValue(QJsonValue::Null)},
            {"current_base_revision",QString::fromStdString(result->currentBaseRevision)},
            {"input_count",int(inputCount)},{"frequency_hz",int(frequency)},
            {"observation_schema",result->observation?int(result->observation->schemaVersion):0},{"stimulus_profile",source},
            {"status",NativeProbeStatusName(result->status)},{"adapter_reasons",adapterReasons},
            {"requires_fresh_verification",result->requiresFreshVerification},
            {"complete",result->observation && result->observation->complete},
            {"burst_assignments",assignments},
            {"valid",result->observation && result->observation->valid},{"reasons",reasons},{"peaks",peaks},
            {"actual_stimuli",events},{"native_ticks",int(ticks)},{"sampled_frames",int(sampled)},
            {"revision_reads",int(revisionReads)},{"scientific_training_result",false}}).toJson();
        ASSERT_EQ(file.write(bytes),bytes.size());
    }
    if(missingSubsetSink)
    {
        EXPECT_EQ(result->status,NativeProbeStatus::Rejected);
        EXPECT_NE(std::find(result->reasons.begin(),result->reasons.end(),"missing_native_stimulus_subset_sample_sink"),result->reasons.end());
        EXPECT_FALSE(armed);EXPECT_EQ(sampled,0u);EXPECT_EQ(sourceEvents,0u);
        auto dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
        ASSERT_EQ(dataset->MatrixData.GetRows(),int(inputCount));
        for(unsigned i=0;i<inputCount;++i)EXPECT_EQ(dataset->MatrixData(i,0),isi[i]);
        EXPECT_EQ(readRevision(),base);
        learner->Reset();dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    if(interference!=Interference::None && interference!=Interference::NoopOwnerBuild)
    {
        const auto expected=interference==Interference::ExternalStop || interference==Interference::OwnerBuild || interference==Interference::OwnerUnInit
            ?NativeProbeStatus::Cancelled:NativeProbeStatus::Rejected;
        EXPECT_EQ(result->status,expected);
        if(result->observation)EXPECT_FALSE(result->observation->valid);
        EXPECT_TRUE(result->requiresFreshVerification);
        EXPECT_TRUE(learner->NativeProbeOwnsControl());
        if(interference==Interference::WrongObservationChannel || interference==Interference::WrongSoloSelector)
        {
            const std::string expectedReason=interference==Interference::WrongObservationChannel?
                "native_input_channel_mismatch":"native_solo_selector_mismatch";
            EXPECT_NE(std::find(result->reasons.begin(),result->reasons.end(),expectedReason),result->reasons.end());
            EXPECT_FALSE(armed);EXPECT_EQ(sampled,0u);
        }
        if(observationSchema==6 && interference==Interference::ExternalStop)
        {
            auto dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
            ASSERT_EQ(dataset->MatrixData.GetRows(),int(inputCount));
            for(unsigned i=0;i<inputCount;++i)EXPECT_EQ(dataset->MatrixData(i,0),isi[i]);
            EXPECT_EQ(readRevision(),base);EXPECT_EQ(learner->DendriteLength.GetData(),lengths);
        }
        if(interference==Interference::DeleteSynapse)EXPECT_TRUE(result->currentBaseRevision.empty());
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    ASSERT_EQ(result->status,NativeProbeStatus::Completed);
    EXPECT_GE(firstProbeFullBoundaryReads,6u);
    ASSERT_TRUE(result->observation);const auto& observed=*result->observation;
    for(const auto& reason:observed.reasons)std::cout<<name<<" observation_reason="<<reason<<std::endl;
    if(observationSchema==6)
    {
        ASSERT_TRUE(armed);ASSERT_TRUE(observed.complete);ASSERT_TRUE(observed.valid);ASSERT_TRUE(result->prepared);
        ASSERT_EQ(observed.stimuli.size(),sourceOrdinals.size());EXPECT_EQ(sourceEvents,sourceOrdinals.size());
        EXPECT_TRUE(observed.peaks.empty());EXPECT_TRUE(observed.burstAssignments.empty());
        EXPECT_EQ(observed.sampleCount,ticks);EXPECT_EQ(sampled,ticks);
        EXPECT_EQ(result->currentBaseRevision,base);EXPECT_EQ(readRevision(),base);
        EXPECT_EQ(learner->TrainingPhase.GetData(),phase);EXPECT_EQ(learner->IsNeedToTrain.GetData(),need);
        auto dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
        ASSERT_EQ(dataset->MatrixData.GetRows(),int(inputCount));
        ASSERT_EQ(learner->InputPattern.GetRows(),int(inputCount));
        for(unsigned i=0;i<inputCount;++i)
        {EXPECT_EQ(dataset->MatrixData(i,0),isi[i]);EXPECT_EQ(learner->InputPattern(i,0),isi[i]);}
        EXPECT_EQ(learner->DendriteLength.GetData(),lengths);
        for(std::size_t i=0;i<sourceOrdinals.size();++i)
        {
            EXPECT_EQ(observed.stimuli[i].id,"pulse"+std::to_string(sourceOrdinals[i]));
            EXPECT_EQ(std::llround((observed.stimuli[i].time-observed.specification.begin)*frequency),
                      std::llround(onsets[sourceOrdinals[i]]*frequency));
        }
        const auto encoded=EncodeNativeProbeEvidence(*result);
        const auto decoded=DecodeNativeProbeEvidence(encoded);
        ASSERT_TRUE(decoded.observation);EXPECT_EQ(decoded.observation->specification.stimulusSubset,observed.specification.stimulusSubset);
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            QJsonArray trainingAfter,datasetAfter;
            for(unsigned i=0;i<inputCount;++i)
            {trainingAfter.append(learner->InputPattern(i,0));datasetAfter.append(dataset->MatrixData(i,0));}
            QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_subset.json");
            ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(QJsonObject{{"kind","native_stimulus_subset_diagnostic"},{"schema_version",2},
                {"source_pattern",configuredPattern},{"evidence",encoded},{"model_before",before},
                {"model_after",NmsdkTools::IdentifyModel(neuron,ports)},
                {"training_pattern_after",trainingAfter},{"dataset_pattern_after",datasetAfter},
                {"physical_input_count_after",learner->NumInputDendrite.GetData()},
                {"training_target_restored",trainingAfter==configuredPattern && datasetAfter==configuredPattern},
                {"scientific_training_result",false}}).toJson();
            ASSERT_EQ(file.write(bytes),bytes.size());
        }
        learner->Reset();EXPECT_FALSE(learner->NativeProbeOwnsControl());
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    if(mergedBurst)
    {
        ASSERT_TRUE(observed.complete);ASSERT_EQ(observed.stimuli.size(),2u);
        EXPECT_EQ(result->currentBaseRevision,base);EXPECT_EQ(readRevision(),base);
        if(observationSchema==2)
        {
            // Two real emissions have merged into one physical response wave.
            // WindowOnly labels that same response independently for each input.
            EXPECT_TRUE(observed.valid);EXPECT_TRUE(observed.burstAssignments.empty());
            if(sharedVertex)
            {
                ASSERT_TRUE(observed.valid);ASSERT_TRUE(result->prepared);ASSERT_EQ(observed.peaks.size(),2u);
                ASSERT_EQ(observed.peaks[0].time,observed.peaks[1].time);
                ASSERT_EQ(observed.peaks[0].plateauEnd,observed.peaks[1].plateauEnd);
                VerificationProtocol protocol;protocol.schemaVersion=2;protocol.routing=ProbeRouting::ClassicBurst;
                protocol.revision=prototype.protocolRevision;protocol.sampleId=observed.specification.sampleId;
                protocol.patternHash=observed.specification.patternHash;protocol.originStimulusId="pulse0";
                protocol.maximumSampleGap=1./frequency;protocol.stimulusProfile=observed.specification.stimulusProfile;
                protocol.stimulusIds={"pulse0","pulse1"};protocol.inputs={{"input0","pulse0"},{"input1","pulse1"}};
                std::string rejection;
                try{ValidateProbeMeasurement(protocol,0,*result->prepared,observed);}
                catch(const std::invalid_argument& error){rejection=error.what();}
                EXPECT_EQ(rejection,"shared_measured_peak_between_stimuli");
                std::vector<ReferenceEvidence> evidence;
                for(const auto& input:protocol.inputs)
                {auto context=*result->prepared;context.inputId=input.id;evidence.push_back({context,observed});}
                EXPECT_THROW(CapturedReferences::Capture(protocol,evidence),std::invalid_argument);
                if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
                {
                    QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_certificate_guard.json");
                    ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                    const auto bytes=QJsonDocument(QJsonObject{{"kind","native_shared_vertex_certificate_guard"},
                        {"schema_version",1},{"observation",BoundedProbeArtifact(*result->prepared,observed)},
                        {"rejection",QString::fromStdString(rejection)},{"native_pattern",configuredPattern},
                        {"model_revision",QString::fromStdString(base)},{"scientific_training_result",false}}).toJson();
                    ASSERT_EQ(file.write(bytes),bytes.size());
                }
            }
        }
        else
        {
            EXPECT_FALSE(observed.valid);ASSERT_FALSE(observed.burstAssignments.empty());
            for(const auto& assignment:observed.burstAssignments)
            {EXPECT_EQ(assignment.validity,PeakValidity::Missing);EXPECT_LT(assignment.waves.size(),2u);}
        }
        learner->Reset();EXPECT_FALSE(learner->NativeProbeOwnsControl());
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    EXPECT_TRUE(armed);ASSERT_TRUE(observed.complete);ASSERT_TRUE(observed.valid);
    EXPECT_EQ(observed.stimuli.size(),inputCount);EXPECT_EQ(observed.sampleCount,ticks);
    EXPECT_EQ(sampled,ticks);EXPECT_EQ(sourceEvents,inputCount);
    EXPECT_GE(revisionReads,2*ticks);
    EXPECT_EQ(result->currentBaseRevision,base);
    EXPECT_EQ(readRevision(),base);
    EXPECT_EQ(learner->TrainingPhase.GetData(),phase);EXPECT_EQ(learner->IsNeedToTrain.GetData(),need);
    EXPECT_TRUE(learner->NativeProbeOwnsControl()); // No implicit legacy resume.
    if(interference==Interference::None && inputCount<=2)
    {
        VerificationProtocol protocol;protocol.routing=prototype.routing;protocol.revision=prototype.protocolRevision;
        protocol.schemaVersion=observed.schemaVersion;protocol.stimulusProfile=observed.specification.stimulusProfile;
        protocol.waveAssignment=observed.specification.waveAssignment;
        protocol.sampleId=observed.specification.sampleId;protocol.patternHash=observed.specification.patternHash;
        protocol.originStimulusId="pulse0";protocol.maximumSampleGap=1./frequency;
        protocol.stimulusIds=observed.specification.expectedStimulusIds;
        std::vector<ReferenceEvidence> evidence;
        for(unsigned i=0;i<inputCount;++i)
        {
            const auto id="input"+std::to_string(i);protocol.inputs.push_back({id,"pulse"+std::to_string(i)});
            auto declaration=*result->prepared;declaration.inputId=id;
            if(!branch || int(i)==active)
                evidence.push_back({declaration,observed}); // Only Classic shares the full reference burst.
            else
            {
                // Branch references require a real isolated probe of each attachment.
                // Relabelling the active input's observation would hide routing errors.
                auto reference=prototype;reference.activeInput=int(i);reference.inputId=id;
                reference.specification.trialId=name+"/reference/"+id;
                reference.specification.stimulusProfile=protocol.stimulusProfile;
                reference.specification.windows={{id,0u,onsets[i]-.001,onsets[i]+.06,"pulse"+std::to_string(i)}};
                std::optional<PreparedVerificationProbe> prepared;
                reference.onPrepared=[&](const PreparedVerificationProbe& actual,const ProbeSpec&) {
                    prepared=actual;EXPECT_EQ(actual.inputId,id);
                    for(unsigned input=0;input<inputCount;++input)
                    {
                        auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(
                            "Dendrite1_"+std::to_string(inputCount-input)+".ExcSynapse1",true);
                        ASSERT_TRUE(synapse);EXPECT_EQ(synapse->Input.IsConnected(),input==i);
                    }
                };
                std::ostringstream referenceTrace;referenceTrace.imbue(std::locale::classic());
                referenceTrace<<std::setprecision(17)<<"native_tick_start_s,stimulus,raw_soma_0\n";
                reference.onSample=[&](const NativeProbeSample& sample) {
                    ASSERT_EQ(sample.potentials.size(),1u);
                    referenceTrace<<sample.time<<','<<sample.stimulus<<','<<sample.potentials[0]<<'\n';
                };
                learner->QueueNativeProbe(std::move(reference));unsigned referenceTicks=0;
                while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
                {
                    ASSERT_LT(referenceTicks++,unsigned((duration+.1)*frequency));
                    model->Calculate();core.environment->IncreaseModelTimeByStep();
                }
                const auto captured=learner->TakeNativeProbeResult();ASSERT_TRUE(captured);ASSERT_TRUE(prepared);
                ASSERT_EQ(captured->status,NativeProbeStatus::Completed);ASSERT_TRUE(captured->observation);
                ASSERT_TRUE(captured->observation->complete);ASSERT_TRUE(captured->observation->valid);
                ASSERT_EQ(captured->currentBaseRevision,base);
                evidence.push_back({*prepared,*captured->observation});
                if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
                {
                    QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_reference_"+QString::number(i)+".csv");
                    ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                    const auto bytes=QByteArray::fromStdString(referenceTrace.str());ASSERT_EQ(file.write(bytes),bytes.size());
                }
            }
        }
        const auto references=CapturedReferences::Capture(protocol,evidence);
        VerificationConfig configuration;configuration.runId=name+"/final_verification";
        configuration.currentModelRevision=base;configuration.maximumProbes=inputCount;
        FinalVerificationSession verification(references,configuration);unsigned completed=0;
        while(const auto next=verification.NextRequest())
        {
            auto fresh=prototype;fresh.specification.runId=next->runId;fresh.specification.trialId=next->trialId;
            fresh.specification.stimulusProfile=protocol.stimulusProfile;
            fresh.inputId=next->inputId;fresh.protocolRevision=next->protocolRevision;fresh.modelEpoch=next->epoch;
            if(branch)
            {
                const auto position=std::find_if(protocol.inputs.begin(),protocol.inputs.end(),[&](const auto& input) {return input.id==next->inputId;});
                ASSERT_NE(position,protocol.inputs.end());const auto index=unsigned(position-protocol.inputs.begin());
                fresh.activeInput=int(index);
                fresh.specification.windows={{next->inputId,0u,onsets[index]-.001,onsets[index]+.06,"pulse"+std::to_string(index)}};
            }
            fresh.onPrepared=[&](const PreparedVerificationProbe& actual,const ProbeSpec&) {
                verification.Arm(actual);EXPECT_TRUE(verification.WaitingForObservation());
            };
            std::ostringstream verificationTrace;verificationTrace.imbue(std::locale::classic());
            verificationTrace<<std::setprecision(17)<<"native_tick_start_s,stimulus";
            for(unsigned i=0;i<(branch?1u:inputCount);++i)verificationTrace<<",raw_soma_"<<i;verificationTrace<<'\n';
            fresh.onSample=[&](const NativeProbeSample& sample) {
                verificationTrace<<sample.time<<','<<sample.stimulus;
                for(double value:sample.potentials)verificationTrace<<','<<value;verificationTrace<<'\n';
            };
            learner->QueueNativeProbe(std::move(fresh));unsigned verificationTicks=0;
            while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
            {
                ASSERT_LT(verificationTicks++,unsigned((duration+.1)*frequency));
                model->Calculate();core.environment->IncreaseModelTimeByStep();
            }
            const auto measured=learner->TakeNativeProbeResult();ASSERT_TRUE(measured);
            ASSERT_EQ(measured->status,NativeProbeStatus::Completed);ASSERT_TRUE(measured->observation);
            ASSERT_TRUE(measured->observation->complete);ASSERT_TRUE(measured->observation->valid);
            verification.Consume(*measured->observation,measured->currentBaseRevision);
            if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
            {
                QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_verify_"+QString::number(completed)+".csv");
                ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                const auto bytes=QByteArray::fromStdString(verificationTrace.str());ASSERT_EQ(file.write(bytes),bytes.size());
            }
            ++completed;
        }
        ASSERT_EQ(completed,inputCount);ASSERT_TRUE(verification.Certificate());
        const auto& certificate=*verification.Certificate();
        EXPECT_EQ(verification.Status(),inputCount==1?VerificationStatus::Exact:VerificationStatus::OutsideTolerance);
        EXPECT_EQ(certificate.Exact(),inputCount==1);
        EXPECT_TRUE(certificate.Matches(base,references,configuration.tolerances,ModelStateKind::LearnedSolo,verification.ModelEpoch()));
        EXPECT_FALSE(certificate.Matches(base,references,configuration.tolerances,ModelStateKind::Recognition,verification.ModelEpoch()));
        for(const auto& residual:certificate.Residuals())EXPECT_LE(std::abs(residual.amplitudeResidual),1e-12);
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            QJsonArray residuals;
            for(const auto& residual:certificate.Residuals())residuals.append(QJsonObject{
                {"input_id",QString::fromStdString(residual.inputId)},{"trial_id",QString::fromStdString(residual.trialId)},
                {"target_raw_potential",residual.targetRawPotential},{"measured_raw_potential",residual.measuredRawPotential},
                {"amplitude_residual",residual.amplitudeResidual},{"timing_low",residual.timingResidualLow},{"timing_high",residual.timingResidualHigh}});
            QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_certificate.json");
            ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(QJsonObject{{"kind","native_executor_final_verification"},
                {"status",VerificationStatusName(verification.Status())},{"exact",certificate.Exact()},
                {"model_revision",QString::fromStdString(base)},{"input_count",int(inputCount)},
                {"residuals",residuals},{"scientific_training_result",false}}).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
        }
    }
    if(boundedTraining)
    {
        ASSERT_EQ(inputCount,2u);ASSERT_EQ(observationSchema,3u);ASSERT_FALSE(mergedBurst);
        VerificationProtocol protocol;protocol.schemaVersion=3;protocol.routing=prototype.routing;
        protocol.revision=prototype.protocolRevision;protocol.stimulusProfile=observed.specification.stimulusProfile;
        protocol.waveAssignment=WaveAssignmentPolicy::OrderedWholeBurst;protocol.originStimulusId="pulse0";
        protocol.sampleId=observed.specification.sampleId;protocol.patternHash=observed.specification.patternHash;
        protocol.maximumSampleGap=1./frequency;protocol.stimulusIds=observed.specification.expectedStimulusIds;
        for(unsigned i=0;i<inputCount;++i)protocol.inputs.push_back({"input"+std::to_string(i),"pulse"+std::to_string(i)});
        std::vector<ReferenceEvidence> captured;QJsonArray referenceArtifacts;
        std::vector<UEPtr<NPulseSynapseCommon>> physicalSynapses;
        std::vector<InputParameters> parameters;
        for(unsigned i=0;i<inputCount;++i)
        {
            const auto path="Dendrite"+std::to_string(branch?1:i+1)+"_"+std::to_string(lengths[i])+".ExcSynapse1";
            const auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(path,true);ASSERT_TRUE(synapse);
            physicalSynapses.push_back(synapse);parameters.push_back({lengths[i],1,synapse->Resistance.GetData()});
            // Capture every reference through a new, actual native burst.
            auto reference=prototype;reference.inputId=protocol.inputs[i].id;reference.activeInput=int(i);
            reference.specification.trialId=name+"/bounded_reference/"+std::to_string(i);
            reference.specification.stimulusProfile=protocol.stimulusProfile;
            reference.specification.windows={{reference.inputId,branch?0u:i,onsets[i]-.001,onsets[i]+.06,"pulse"+std::to_string(i)}};
            std::optional<PreparedVerificationProbe> prepared;
            reference.onPrepared=[&](const auto& actual,const ProbeSpec&){prepared=actual;};
            std::ostringstream referenceSamples;referenceSamples.imbue(std::locale::classic());
            referenceSamples<<std::setprecision(17)<<"time,stimulus";
            for(unsigned channel=0;channel<(branch?1u:inputCount);++channel)referenceSamples<<",soma"<<channel;
            referenceSamples<<'\n';
            reference.onSample=[&](const NativeProbeSample& sample) {
                referenceSamples<<sample.time<<','<<sample.stimulus;
                for(double value:sample.potentials)referenceSamples<<','<<value;referenceSamples<<'\n';
            };
            learner->QueueNativeProbe(std::move(reference));unsigned steps=0;
            while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
            {ASSERT_LT(steps++,unsigned((duration+.1)*frequency));model->Calculate();core.environment->IncreaseModelTimeByStep();}
            const auto referenceResult=learner->TakeNativeProbeResult();ASSERT_TRUE(referenceResult);ASSERT_TRUE(prepared);
            ASSERT_EQ(referenceResult->status,NativeProbeStatus::Completed);ASSERT_TRUE(referenceResult->observation);
            ASSERT_TRUE(referenceResult->observation->valid);captured.push_back({*prepared,*referenceResult->observation});
            referenceArtifacts.append(BoundedProbeArtifact(*prepared,*referenceResult->observation));
            if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
            {
                QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_train_reference_"+QString::number(i)+".csv");
                ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QByteArray::fromStdString(referenceSamples.str());
                ASSERT_EQ(file.write(bytes),bytes.size());
            }
        }
        const auto references=CapturedReferences::Capture(protocol,captured);
        BoundedTrainingConfig cfg;cfg.runId=name+"/bounded_training";cfg.normalization=Normalization::TipResistance;
        cfg.maximumProbes=64;cfg.maximumEdits=16;cfg.maximumCandidatesPerInput=8;cfg.resistanceSubdivisionDepth=2;
        // This adapter integration isolates R normalization. Fixed lengths do
        // not synchronize the fixture at the production default .02 seconds.
        cfg.tolerances.sync=.2;
        for(const auto& p:parameters)cfg.bounds.push_back({p.length,p.length,1,1,p.resistance,p.resistance*2.});
        physicalSynapses[0]->Resistance=parameters[0].resistance*2.;
        parameters[0].resistance=physicalSynapses[0]->Resistance.GetData();
        auto declared=learner->TipSynapseResistance.GetData();declared[0]=parameters[0].resistance;
        learner->TipSynapseResistance.SetDataDirect(declared);
        cfg.initialModelRevision=readRevision();ASSERT_NE(cfg.initialModelRevision,base);
        BoundedTrainingSession training(references,cfg,parameters);QJsonArray actions;
        while(const auto action=training.NextAction())
        {
            ASSERT_LT(actions.size(),100);
            if(action->kind==TrainingActionKind::Edit)
            {
                for(unsigned i=0;i<inputCount;++i)
                {
                    EXPECT_EQ(action->parameters[i].length,lengths[i]);EXPECT_EQ(action->parameters[i].synapses,1);
                    physicalSynapses[i]->Resistance=action->parameters[i].resistance;
                    parameters[i].resistance=physicalSynapses[i]->Resistance.GetData();declared[i]=parameters[i].resistance;
                }
                learner->TipSynapseResistance.SetDataDirect(declared);
                training.Applied(action->serial,parameters,readRevision());
                actions.append(QJsonObject{{"serial",int(action->serial)},{"kind","edit"},{"model_revision",QString::fromStdString(readRevision())}});
                continue;
            }
            auto probe=prototype;probe.inputId=protocol.inputs[action->inputIndex].id;
            probe.activeInput=int(action->inputIndex);probe.baseModelRevision=action->baseModelRevision;probe.modelEpoch=action->modelEpoch;
            probe.specification.runId=action->runId;probe.specification.trialId=action->trialId;
            probe.specification.stimulusProfile=protocol.stimulusProfile;
            probe.specification.windows={{probe.inputId,branch?0u:action->inputIndex,
                onsets[action->inputIndex]-.001,onsets[action->inputIndex]+.06,protocol.stimulusIds[action->inputIndex]}};
            probe.onPrepared=[&](const auto& prepared,const ProbeSpec&){training.Arm(action->serial,prepared);};
            std::ostringstream samples;samples.imbue(std::locale::classic());samples<<std::setprecision(17)<<"time,stimulus";
            for(unsigned i=0;i<(branch?1u:inputCount);++i)samples<<",soma"<<i;samples<<'\n';
            probe.onSample=[&](const NativeProbeSample& sample) {
                samples<<sample.time<<','<<sample.stimulus;for(double value:sample.potentials)samples<<','<<value;samples<<'\n';
            };
            learner->QueueNativeProbe(std::move(probe));unsigned steps=0;
            while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running)
            {ASSERT_LT(steps++,unsigned((duration+.1)*frequency));model->Calculate();core.environment->IncreaseModelTimeByStep();}
            const auto measured=learner->TakeNativeProbeResult();ASSERT_TRUE(measured);
            ASSERT_EQ(measured->status,NativeProbeStatus::Completed);ASSERT_TRUE(measured->observation);
            ASSERT_TRUE(measured->observation->valid);
            training.Consume(*measured->observation,measured->currentBaseRevision);
            actions.append(QJsonObject{{"serial",int(action->serial)},{"kind","probe"},{"input",int(action->inputIndex)},
                {"final",action->finalVerification},{"model_revision",QString::fromStdString(measured->currentBaseRevision)},
                {"observation",BoundedProbeArtifact(*measured->prepared,*measured->observation)},
                {"valid",measured->observation->valid},{"complete",measured->observation->complete}});
            if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
            {
                QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_train_"+QString::number(action->serial)+".csv");
                ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QByteArray::fromStdString(samples.str());
                ASSERT_EQ(file.write(bytes),bytes.size());
            }
        }
        ASSERT_EQ(training.Status(),TrainingStatus::Exact);ASSERT_TRUE(training.Certificate());
        EXPECT_GE(training.AppliedEdits(),1u);EXPECT_EQ(readRevision(),base);
        EXPECT_TRUE(training.Certificate()->Matches(base,references,cfg.tolerances,ModelStateKind::LearnedSolo,training.ModelEpoch()));
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            QJsonArray residuals;
            for(const auto& residual:training.Certificate()->Residuals())residuals.append(QJsonObject{
                {"input_id",QString::fromStdString(residual.inputId)},{"trial_id",QString::fromStdString(residual.trialId)},
                {"target_raw",residual.targetRawPotential},{"measured_raw",residual.measuredRawPotential},
                {"amplitude_residual",residual.amplitudeResidual},{"amplitude_tolerance",residual.amplitudeTolerance},
                {"timing_low",residual.timingResidualLow},{"timing_high",residual.timingResidualHigh}});
            QFile file(QString::fromLocal8Bit(output)+"/"+QString::fromStdString(name)+"_bounded_training.json");
            ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QJsonDocument(QJsonObject{
                {"status",TrainingStatusName(training.Status())},{"sync_tolerance",cfg.tolerances.sync},
                {"amplitude_absolute",cfg.tolerances.amplitudeAbsolute},{"probes",int(training.IssuedProbes())},
                {"initial_model_revision",QString::fromStdString(cfg.initialModelRevision)},
                {"reference_model_revision",QString::fromStdString(references.InitialModelRevision())},
                {"final_model_revision",QString::fromStdString(training.ModelRevision())},{"final_model_epoch",int(training.ModelEpoch())},
                {"edits",int(training.AppliedEdits())},{"actions",actions},{"references",referenceArtifacts},
                {"residuals",residuals},{"scientific_training_result",false}}).toJson();
            ASSERT_EQ(file.write(bytes),bytes.size());
        }
    }
    // Native Reset releases control and preserves the learned physical graph.
    learner->Reset();EXPECT_FALSE(learner->NativeProbeOwnsControl());
    EXPECT_EQ(learner->NativeProbeState(),NativeProbeStatus::Idle);
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}
TEST_P(NativeLearnerExecution, QueueUsesNativeSchedulerAndRestoresModel)
{
    if(GetParam().first)ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(GetParam().second);
    else ExecuteProbeThroughLearner<NNeuronTimeLearner>(GetParam().second);
}
TEST(NativeBurstAssignment, Classic2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3);}
TEST(NativeBurstAssignment, Branch2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3);}
TEST(NativeBurstAssignment, Classic20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3);}
TEST(NativeBurstAssignment, Branch20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3);}
TEST(NativeBurstAssignment, MergedClassicWindowOnly2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,2,true);}
TEST(NativeBurstAssignment, SharedClassicVertexCannotCertify2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,2,true,false,true);}
TEST(NativeBurstAssignment, MergedClassicWholeBurst2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,true);}
TEST(NativeBurstAssignment, MergedBranchWindowOnly2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,2,true);}
TEST(NativeBurstAssignment, MergedBranchWholeBurst2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,true);}
TEST(NativeBurstAssignment, ClassicSingle2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,1,3);}
TEST(NativeBurstAssignment, BranchSingle2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,1,3);}
TEST(NativeBurstAssignment, ClassicFour2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4,3);}
TEST(NativeBurstAssignment, BranchFour2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,4,3);}
TEST(NativeBurstAssignment, ClassicSix2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,6,3);}
TEST(NativeBurstAssignment, BranchSix2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,6,3);}
TEST(NativeBurstAssignment, ClassicWrongPhysicalChannel)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::WrongObservationChannel,2,3);}
TEST(NativeBurstAssignment, BranchWrongPhysicalSelector)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::WrongSoloSelector,2,3);}
TEST(NativeBoundedTraining, Classic2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,false,true);}
TEST(StimulusSubsetNative, ClassicOmitInterior2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4,6,false,false,false,{0,2,3});}
TEST(StimulusSubsetNative, MissingSampleSinkRejectsBeforePresentation)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4,6,false,false,false,{0,2,3},true);}
TEST(StimulusSubsetNative, BranchOmitInterior2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,4,6,false,false,false,{0,2,3});}
TEST(StimulusSubsetNative, ClassicLaterSingle2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4,6,false,false,false,{3});}
TEST(StimulusSubsetNative, BranchLaterSingle2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,4,6,false,false,false,{3});}
TEST(StimulusSubsetNative, ClassicFullControl2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4,6,false,false,false,{0,1,2,3});}
TEST(StimulusSubsetNative, BranchFullControl2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,4,6,false,false,false,{0,1,2,3});}
TEST(StimulusSubsetNative, ClassicCancelRestoresPattern2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::ExternalStop,4,6,false,false,false,{0,2,3});}
TEST(StimulusSubsetNative, ClassicLaterSingle20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,4,6,false,false,false,{3});}
TEST(StimulusSubsetNative, BranchOmitInterior20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,4,6,false,false,false,{0,2,3});}
TEST(NativeBoundedTraining, Branch2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,true);}
TEST(NativeBoundedTraining, Classic20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3,false,true);}
TEST(NativeBoundedTraining, Branch20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3,false,true);}

TEST(NativeBranchAliasing, CoincidentLabelsExposeOneEffectivePhysicalBank)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    core.environment->SetUseIndTimeStepFlag(false);
    for(int normalization:{0,1})
    {
        ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
        StorageProfileSpec profile;profile.name="BranchAlias_N"+std::to_string(normalization);
        profile.frequencyHz=2000;profile.neuronBaseClass="NSPNeuronGen";profile.initialThreshold=1.;
        const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
        auto learner=dynamic_pointer_cast<NNeuronTimeLearnerBranch>(core.storage->TakeObject("NNeuronTimeLearnerBranch"));
        ASSERT_TRUE(learner);learner->Name="Learner";learner->StructureBuildMode=1;
        learner->NumInputDendrite=2;learner->NeuronClassName=registered.neuronClass;
        learner->DendriteLength=std::vector<int>{1,1};learner->NormalizationMode=normalization;
        learner->NumSynapse=std::vector<int>{1,normalization==0?2:1};
        learner->TipSynapseResistance=std::vector<double>{86e6,43e6};learner->CalculateMode=1;
        learner->EnablePostTrainTuning=false;learner->AutoCalibrateFixedLTZThreshold=false;
        MDMatrix<double> pattern;pattern.Assign(2,1,0.);pattern(0,0)=.01;pattern(1,0)=.08;learner->InputPattern=pattern;
        UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
        model->SetGlobalTimeStep(2000);model->Init();model->Reset();
        auto neuron=learner->GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
        auto membrane=neuron->GetComponentL<NPulseMembrane>("Dendrite1_1",true);ASSERT_TRUE(membrane);
        auto physical=membrane->GetComponentL<NPulseSynapseCommon>("ExcSynapse1",true);ASSERT_TRUE(physical);
        EXPECT_EQ(learner->DendriteLength.GetData(),(std::vector<int>{1,1}));
        if(normalization==0)
        {
            EXPECT_EQ(membrane->NumExcitatorySynapses.GetData(),2);
            EXPECT_EQ(learner->NumSynapse.GetData(),(std::vector<int>{1,2}));
            // Both input labels resolve this same bank; requested Ns[0]=1 is
            // not an independently implemented count for physical input 0.
            EXPECT_NE(membrane->NumExcitatorySynapses.GetData(),learner->NumSynapse[0]);
        }
        else
        {
            EXPECT_EQ(membrane->NumExcitatorySynapses.GetData(),1);
            const auto requested=learner->TipSynapseResistance.GetData();ASSERT_EQ(requested.size(),2u);
            EXPECT_NE(requested[0],requested[1]);
            auto input0=neuron->GetComponentL<NPulseSynapseCommon>("Dendrite1_"+
                std::to_string(learner->DendriteLength[0])+".ExcSynapse1",true);
            auto input1=neuron->GetComponentL<NPulseSynapseCommon>("Dendrite1_"+
                std::to_string(learner->DendriteLength[1])+".ExcSynapse1",true);
            ASSERT_TRUE(input0);ASSERT_TRUE(input1);ASSERT_EQ(input0.Get(),input1.Get());
            const std::vector<double> effective{input0->Resistance.GetData(),input1->Resistance.GetData()};
            EXPECT_NE(effective,requested);
            // Reset/mute may select a different last writer; that phase detail
            // cannot turn a single physical resistance into two independent R.
            const auto saved=input0->Resistance.GetData();input0->Resistance=requested[1];
            EXPECT_EQ(input1->Resistance.GetData(),requested[1]);input0->Resistance=saved;
        }
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            QJsonArray requestedCounts,requestedResistances;
            for(int value:learner->NumSynapse.GetData())requestedCounts.append(value);
            for(double value:learner->TipSynapseResistance.GetData())requestedResistances.append(value);
            QFile file(QString::fromLocal8Bit(output)+"/BranchAlias_N"+QString::number(normalization)+".json");
            ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));const auto bytes=QJsonDocument(QJsonObject{
                {"requested_counts",requestedCounts},{"requested_resistances",requestedResistances},
                {"physical_bank","Neuron.Dendrite1_1"},{"physical_count",membrane->NumExcitatorySynapses.GetData()},
                {"physical_first_resistance",physical->Resistance.GetData()},{"scientific_training_result",false}}).toJson();
            ASSERT_EQ(file.write(bytes),bytes.size());
        }
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
    }
}
INSTANTIATE_TEST_SUITE_P(TopologiesAndRates,NativeLearnerExecution,::testing::Values(
    std::make_pair(false,2000u),std::make_pair(true,2000u),
    std::make_pair(false,20000u),std::make_pair(true,20000u)));
TEST(NativeLearnerProbeInvalidation, ClassicPhysicalResetWithUnchangedModelHash)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::PhysicalReset); }
TEST(NativeLearnerProbeInvalidation, BranchPhysicalResetWithUnchangedModelHash)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::PhysicalReset); }
TEST(NativeLearnerProbeInvalidation, ClassicSourceAmplitudeChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::SourceAmplitude); }
TEST(NativeLearnerProbeInvalidation, BranchSourceAmplitudeChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::SourceAmplitude); }
TEST(NativeLearnerProbeInvalidation, ClassicSourceFrequencyChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::SourceFrequency); }
TEST(NativeLearnerProbeInvalidation, BranchPatternChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::Pattern); }
TEST(NativeLearnerProbeInvalidation, ClassicDeletedSynapse)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::DeleteSynapse); }
TEST(NativeLearnerProbeInvalidation, BranchDeletedSynapse)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::DeleteSynapse); }
TEST(NativeLearnerProbeInvalidation, ClassicExternalStopPreservesTargetAndThreshold)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::ExternalStop); }
TEST(NativeLearnerProbeInvalidation, BranchExternalStopPreservesTargetAndThreshold)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::ExternalStop); }
TEST(NativeLearnerProbeInvalidation, ClassicImplicitResetDuringBuildKeepsControl)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::OwnerBuild); }
TEST(NativeLearnerProbeInvalidation, BranchImplicitResetDuringBuildKeepsControl)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::OwnerBuild); }
TEST(NativeLearnerProbeInvalidation, ClassicNoopBuildDoesNotInvalidateProbe)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::NoopOwnerBuild); }
TEST(NativeLearnerProbeInvalidation, BranchNoopBuildDoesNotInvalidateProbe)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::NoopOwnerBuild); }
TEST(NativeLearnerDimensions, ClassicSingleInput2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,1); }
TEST(NativeLearnerDimensions, BranchSingleInput2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,1); }
TEST(NativeLearnerDimensions, ClassicSingleInput20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,1); }
TEST(NativeLearnerDimensions, BranchSingleInput20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,1); }
TEST(NativeLearnerDimensions, ClassicFourInputs2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,4); }
TEST(NativeLearnerDimensions, BranchFourInputs2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,4); }
TEST(NativeLearnerDimensions, ClassicFourInputs20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,4); }
TEST(NativeLearnerDimensions, BranchFourInputs20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,4); }
TEST(NativeLearnerDimensions, ClassicSixInputs2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,6); }
TEST(NativeLearnerDimensions, BranchSixInputs2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,6); }
TEST(NativeLearnerProbeInvalidation, ClassicPreparationCallbackFailure)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::PrepareFailure); }
TEST(NativeLearnerProbeInvalidation, BranchSampleSinkFailure)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::SampleFailure); }
TEST(NativeLearnerProbeInvalidation, ClassicRevisionProviderFailure)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::RevisionFailure); }
TEST(NativeLearnerProbeInvalidation, ClassicOwnerUnInitCancelsProbe)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::OwnerUnInit); }
TEST(NativeLearnerProbeInvalidation, BranchOwnerUnInitCancelsProbe)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::OwnerUnInit); }
TEST(NativeLearnerProbeInvalidation, BranchTinySourceChangeCannotHideInFormattedSnapshot)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::TinySourceAmplitude); }
TEST(NativeLearnerProbeInvalidation,ClassicOneUlpPhysicalCapacitanceChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::TinyPhysicalCapacitance); }
TEST(NativeLearnerProbeInvalidation,BranchOneUlpPhysicalCapacitanceChange)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::TinyPhysicalCapacitance); }
TEST(NativeResponseDomainBridge,Classic2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,false,false,false,{},false,true); }
TEST(NativeResponseDomainBridge,Branch2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,false,false,{},false,true); }
TEST(NativeResponseDomainBridge,Classic20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3,false,false,false,{},false,true); }
TEST(NativeResponseDomainBridge,Branch20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3,false,false,false,{},false,true); }
TEST(NativeResponseDomainBridge,ClassicFullRevision2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,false,false,false,{},false,true,true); }
TEST(NativeResponseDomainBridge,BranchFullRevision2000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,false,false,{},false,true,true); }
TEST(NativeResponseDomainBridge,ClassicFullRevision20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3,false,false,false,{},false,true,true); }
TEST(NativeResponseDomainBridge,BranchFullRevision20000)
{ ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3,false,false,false,{},false,true,true); }

struct DomainCaptureFixture {
    NativeResponseDomainCapture capture;
    ProbeSpec spec;
    PreparedVerificationProbe context;
    std::vector<NativeProbeSample> frames;
    ResponseDomainSpec domains;
    DomainCaptureFixture() {
        spec.runId="capture";spec.trialId="capture/trial";spec.sampleId="sample";
        spec.patternHash="pattern";spec.modelRevision="effective";spec.begin=0.;spec.end=.5;
        spec.maximumSampleGap=.1;spec.maximumSamples=6;spec.baseline={0.};
        spec.expectedStimulusIds={"pulse0"};spec.windows={{"input0",0,0.,.5,"pulse0"}};
        context.baseModelRevision="base";context.effectiveModelRevision="effective";
        context.protocolRevision="protocol";context.inputId="input0";
        capture.Arm(context,spec,{"Soma1"});
        const double values[]{0.,0.,2.,0.,0.,0.};
        for(std::size_t i=0;i<6;++i) {
            NativeProbeSample f;f.time=double(i)*.1;f.potentials={values[i]};
            f.effectiveModelRevision="effective";if(i==1)f.newStimuli={{"pulse0",.1}};
            frames.push_back(f);
        }
        domains.modelRevision="effective";domains.protocolRevision="protocol";domains.patternHash="pattern";
        domains.channelIds={0};domains.stimulusIds={"pulse0"};domains.domains={{0,"pulse0",.1,.5}};
    }
    void AppendAll(){for(const auto& frame:frames)capture.Append(frame);}
    NativeProbeResult Result() const {
        ProbeRecorder recorder(spec);
        for(const auto& frame:frames) {
            for(const auto& e:frame.newStimuli)recorder.RecordStimulus(e.id,e.time);
            recorder.Observe(frame.time,frame.potentials,frame.effectiveModelRevision);
        }
        NativeProbeResult r;r.status=NativeProbeStatus::Completed;r.prepared=context;
        r.currentBaseRevision="base";r.observation=recorder.Close(.5,"effective","window_closed");return r;
    }
};
TEST(NativeResponseDomainCapture,ClosedRecordBindsActualEventsAndDistinctBaseRevision)
{
    DomainCaptureFixture f;f.AppendAll();const auto result=f.capture.Close(f.Result(),f.domains);
    ASSERT_EQ(result.associations.size(),1u);EXPECT_EQ(result.associations[0].status,DomainAssociationStatus::Hypothesis);
    EXPECT_TRUE(f.capture.Observation().complete);EXPECT_FALSE(result.TrainingCertificateEligible());
}
TEST(NativeResponseDomainCapture,FailedAppendCannotBeRepairedByAnotherFrame)
{
    DomainCaptureFixture f;auto frame=f.frames[0];frame.effectiveModelRevision="changed";
    EXPECT_THROW(f.capture.Append(frame),std::invalid_argument);
    EXPECT_THROW(f.capture.Append(f.frames[0]),std::invalid_argument);
    EXPECT_THROW(f.capture.Close(f.Result(),f.domains),std::invalid_argument);
    EXPECT_FALSE(f.capture.Observation().complete);
}
TEST(NativeResponseDomainCapture,UnknownClosureDiagnosticCannotHideBehindInvalidFlag)
{
    DomainCaptureFixture f;f.AppendAll();auto r=f.Result();r.observation->valid=false;
    r.observation->reasons.push_back("unknown_integrity_failure");
    EXPECT_THROW(f.capture.Close(r,f.domains),std::invalid_argument);
    EXPECT_FALSE(f.capture.Observation().complete);
}
TEST(NativeResponseDomainCapture,ChangedSelectorOrBaseCannotCloseCapture)
{
    for(bool selector:{false,true}) {
        DomainCaptureFixture f;f.AppendAll();auto r=f.Result();
        if(selector)r.prepared->selectedInputIndex=0;else r.currentBaseRevision="effective";
        EXPECT_THROW(f.capture.Close(r,f.domains),std::invalid_argument);
    }
}
TEST(NativeResponseDomainCapture,ChangedEventOrCountCannotCloseCapture)
{
    for(bool event:{false,true}) {
        DomainCaptureFixture f;f.AppendAll();auto r=f.Result();
        if(event)r.observation->stimuli[0].time=.2;else --r.observation->sampleCount;
        EXPECT_THROW(f.capture.Close(r,f.domains),std::invalid_argument);
    }
}
TEST(NativeResponseDomainCapture,ReproducedLegacyAmbiguityDoesNotEraseCompleteWaveform)
{
    DomainCaptureFixture f;
    const double values[]{0.,2.,0.,3.,0.,0.};
    for(std::size_t i=0;i<f.frames.size();++i)f.frames[i].potentials[0]=values[i];
    f.AppendAll();auto r=f.Result();ASSERT_FALSE(r.observation->valid);ASSERT_TRUE(r.observation->complete);
    const auto diagnostic=f.capture.Close(r,f.domains);
    EXPECT_TRUE(f.capture.Observation().complete);EXPECT_FALSE(diagnostic.TrainingCertificateEligible());
}
TEST(NativeResponseDomainCapture,LostFrameAndCancelledClosureRemainIncomplete)
{
    DomainCaptureFixture f;f.capture.Append(f.frames[0]);
    EXPECT_THROW(f.capture.Append(f.frames[2]),std::invalid_argument);
    EXPECT_FALSE(f.capture.Observation().complete);
    DomainCaptureFixture g;g.AppendAll();auto r=g.Result();r.status=NativeProbeStatus::Cancelled;
    EXPECT_THROW(g.capture.Close(r,g.domains),std::invalid_argument);
    EXPECT_FALSE(g.capture.Observation().complete);
}
TEST(NativeResponseDomainCapture,ChangedMeasuredPeakCannotHideBehindSameValidityAndReasons)
{
    DomainCaptureFixture f;auto r=f.Result();f.frames[2].potentials[0]=3.;f.AppendAll();
    ASSERT_TRUE(r.observation->valid);ASSERT_TRUE(r.observation->reasons.empty());
    EXPECT_THROW(f.capture.Close(r,f.domains),std::invalid_argument);
    EXPECT_FALSE(f.capture.Observation().complete);
}
TEST(NativeResponseDomainCodec,RequiresClosedCaptureAndExactPrimaryBytes)
{
    DomainCaptureFixture f;EXPECT_THROW(EncodeNativeResponseDomainTrace(f.capture),std::invalid_argument);
    f.AppendAll();f.capture.Close(f.Result(),f.domains);auto csv=EncodeNativeResponseDomainTrace(f.capture);
    const auto packet=EncodeNativeResponseDomainEvidence(f.capture,f.domains,"trace.csv",csv);
    EXPECT_EQ(packet["kind"].toString(),"timelearner_native_response_domain_evidence");
    EXPECT_TRUE(packet["diagnostic_only"].toBool());EXPECT_FALSE(packet["training_certificate_eligible"].toBool());
    EXPECT_THROW(EncodeNativeResponseDomainEvidence(f.capture,f.domains,"trace.csv",csv+"0,0,0\n"),std::invalid_argument);
    EXPECT_THROW(EncodeNativeResponseDomainEvidence(f.capture,f.domains,"../trace.csv",csv),std::invalid_argument);
}
TEST(NativeResponseDomainCodec,UsesItsOwnImmutableClosureAndKeepsDiagnosticStatus)
{
    DomainCaptureFixture f;f.AppendAll();auto native=f.Result();f.capture.Close(native,f.domains);
    native.currentBaseRevision="unrelated_after_capture";
    const auto csv=EncodeNativeResponseDomainTrace(f.capture);
    const auto packet=EncodeNativeResponseDomainEvidence(f.capture,f.domains,"trace.csv",csv);
    EXPECT_EQ(packet["native_evidence"].toObject()["current_base_revision"].toString(),"base");
    EXPECT_EQ(packet["analysis"].toObject()["channels"].toArray().size(),1);
    EXPECT_EQ(packet["analysis"].toObject()["associations"].toArray().size(),1);
    EXPECT_TRUE(packet["scientific_verdict"].isNull());
}
}

TEST(NativeMatchedOmissionExecution,Classic2000) { ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,Branch2000) { ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,Classic20000) { ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,Branch20000) { ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,ClassicExternalStopBetweenControls) { ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::ExternalStop,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,BranchExternalStopBetweenControls) { ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::ExternalStop,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,ClassicPhysicalEditBetweenControls) { ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::TinyPhysicalCapacitance,2,3,false,false,false,{},false,false,false,true); }
TEST(NativeMatchedOmissionExecution,BranchPhysicalEditBetweenControls) { ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::TinyPhysicalCapacitance,2,3,false,false,false,{},false,false,false,true); }

namespace {
TEST(NativeMatchedOmissionCapture,CloseNativeVerifiesWaveformWithoutDomainHypothesis)
{
    DomainCaptureFixture fixture;fixture.AppendAll();const auto native=fixture.Result();
    fixture.capture.CloseNative(native);
    EXPECT_TRUE(fixture.capture.Observation().complete);
    EXPECT_EQ(fixture.capture.ClosedNativeEvidence().currentBaseRevision,native.currentBaseRevision);
    EXPECT_FALSE(EncodeNativeResponseDomainTrace(fixture.capture).isEmpty());
    EXPECT_THROW(fixture.capture.CloseNative(native),std::invalid_argument);
}
TEST(NativeMatchedOmissionCapture,CloseNativeRejectsTamperedObservation)
{
    DomainCaptureFixture fixture;fixture.AppendAll();auto native=fixture.Result();
    native.observation->sampleCount+=1;
    EXPECT_THROW(fixture.capture.CloseNative(native),std::invalid_argument);
    EXPECT_FALSE(fixture.capture.Observation().complete);
}
}

TEST(NativeMatchedOmissionExecution,ClassicSeparatedControl2000) { ExecuteProbeThroughLearner<NNeuronTimeLearner>(2000,Interference::None,2,3,false,false,false,{},false,false,false,true,true); }
TEST(NativeMatchedOmissionExecution,BranchSeparatedControl2000) { ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,false,false,{},false,false,false,true,true); }

namespace {
template<class Learner> void ExecuteDeclaredBasin(unsigned frequency,int input,
    Interference interference=Interference::None,bool merged=false) {
    ExecuteProbeThroughLearner<Learner>(frequency,interference,2,3,merged,false,false,{},false,false,false,true,false,true,input);
}
}
TEST(NativeDeclaredWindowBasinExecution,ClassicInput0At2000){ExecuteDeclaredBasin<NNeuronTimeLearner>(2000,0);}
TEST(NativeDeclaredWindowBasinExecution,ClassicInput1At2000){ExecuteDeclaredBasin<NNeuronTimeLearner>(2000,1);}
TEST(NativeDeclaredWindowBasinExecution,BranchInput0At2000){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(2000,0);}
TEST(NativeDeclaredWindowBasinExecution,BranchInput1At2000){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(2000,1);}
TEST(NativeDeclaredWindowBasinExecution,ClassicInput0At20000){ExecuteDeclaredBasin<NNeuronTimeLearner>(20000,0);}
TEST(NativeDeclaredWindowBasinExecution,ClassicInput1At20000){ExecuteDeclaredBasin<NNeuronTimeLearner>(20000,1);}
TEST(NativeDeclaredWindowBasinExecution,BranchInput0At20000){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(20000,0);}
TEST(NativeDeclaredWindowBasinExecution,BranchInput1At20000){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(20000,1);}
TEST(NativeDeclaredWindowBasinExecution,ClassicMergedInput0At2000){ExecuteDeclaredBasin<NNeuronTimeLearner>(2000,0,Interference::None,true);}
TEST(NativeDeclaredWindowBasinExecution,BranchMergedInput0At2000){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(2000,0,Interference::None,true);}
TEST(NativeDeclaredWindowBasinExecution,ClassicExternalStopBetweenControls){ExecuteDeclaredBasin<NNeuronTimeLearner>(2000,0,Interference::ExternalStop);}
TEST(NativeDeclaredWindowBasinExecution,BranchExternalStopBetweenControls){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(2000,0,Interference::ExternalStop);}
TEST(NativeDeclaredWindowBasinExecution,ClassicPhysicalEditBetweenControls){ExecuteDeclaredBasin<NNeuronTimeLearner>(2000,0,Interference::TinyPhysicalCapacitance);}
TEST(NativeDeclaredWindowBasinExecution,BranchPhysicalEditBetweenControls){ExecuteDeclaredBasin<NNeuronTimeLearnerBranch>(2000,0,Interference::TinyPhysicalCapacitance);}
