#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/BoundedTraining.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QDir>
#include <QFile>
#include <type_traits>
#include <cstdlib>
#include <sstream>
#include <iomanip>
#include <locale>
#include <cmath>
#include <algorithm>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
class NativeLearnerExecution : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
enum class Interference { None,PhysicalReset,SourceAmplitude,SourceFrequency,Pattern,DeleteSynapse,ExternalStop,OwnerBuild,NoopOwnerBuild,PrepareFailure,SampleFailure,RevisionFailure,OwnerUnInit,TinySourceAmplitude,WrongObservationChannel,WrongSoloSelector };

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

template<class Learner> void ExecuteProbeThroughLearner(unsigned frequency,Interference interference=Interference::None,unsigned inputCount=2,unsigned observationSchema=2,bool mergedBurst=false,bool boundedTraining=false)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    ASSERT_GE(inputCount,1u);ASSERT_LE(inputCount,6u);
    const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+"_N"+std::to_string(inputCount)+"_native_executor"+
        (interference==Interference::None?"":"_fault"+std::to_string(int(interference)))+
        (observationSchema==3?"_whole_burst":"")+(mergedBurst?"_merged_burst":"")+(boundedTraining?"_bounded":"");
    StorageProfileSpec profile;profile.name=name;profile.frequencyHz=frequency;
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
    int active=0;
    if(branch && inputCount>1)
    {
        auto point0=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_"+std::to_string(inputCount)+".ExcSynapse1",true);
        auto point1=neuron->template GetComponentL<NPulseSynapseCommon>("Dendrite1_"+std::to_string(inputCount-1)+".ExcSynapse1",true);
        ASSERT_TRUE(point0);ASSERT_TRUE(point1);
        if(point0->Input.IsConnected() && !point1->Input.IsConnected())active=1;
    }
    const auto phase=learner->TrainingPhase.GetData();const auto need=learner->IsNeedToTrain.GetData();
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    std::size_t revisionReads=0;bool revisionFailure=false;
    const auto readRevision=[&]() {
        ++revisionReads;if(revisionFailure)throw std::runtime_error("injected_revision_failure");
        const auto identity=NmsdkTools::IdentifyModel(neuron,ports);
        if(!identity["valid"].toBool())throw std::runtime_error("invalid_native_identity");
        return identity["sha256"].toString().toStdString();
    };
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(before["valid"].toBool());
    const auto base=readRevision();bool armed=false;
    std::ostringstream trace;trace.imbue(std::locale::classic());
    trace<<std::setprecision(17)<<"native_tick_start_s,stimulus";
    for(unsigned i=0;i<(branch?1u:inputCount);++i)trace<<",raw_soma_"<<i;trace<<'\n';
    unsigned sampled=0,sourceEvents=0;
    NativeProbeRequest request;request.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
    request.activeInput=active;request.inputId="input"+std::to_string(active);request.protocolRevision="native_burst_N"+std::to_string(inputCount)+"_v1";
    if(observationSchema==3)request.protocolRevision="native_ordered_burst_N"+std::to_string(inputCount)+"_v2";
    request.baseModelRevision=base;request.expectedInputIsi=isi;request.readModelRevision=readRevision;
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
    if(interference==Interference::WrongObservationChannel)spec.windows[0].channel=1;
    if(interference==Interference::WrongSoloSelector)request.activeInput=1-active;
    request.onPrepared=[&](const PreparedVerificationProbe& declaration,const ProbeSpec& actual) {
        if(interference==Interference::PrepareFailure)throw std::runtime_error("injected_prepare_failure");
        armed=true;EXPECT_EQ(declaration.baseModelRevision,base);
        EXPECT_EQ(actual.modelRevision,declaration.effectiveModelRevision);
        EXPECT_GE(actual.begin,1./frequency);
        EXPECT_EQ(actual.baseline.size(),branch?1u:inputCount);
        if(observationSchema==3)
        {
            if(branch)EXPECT_EQ(declaration.selectedInputIndex,std::optional<std::size_t>(active));
            else EXPECT_FALSE(declaration.selectedInputIndex);
        }
        if(branch)
        {
            if(inputCount>1)EXPECT_NE(declaration.effectiveModelRevision,base);
            for(unsigned input=0;input<inputCount;++input)
            {
                auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(
                    "Dendrite1_"+std::to_string(inputCount-input)+".ExcSynapse1",true);
                ASSERT_TRUE(synapse);EXPECT_EQ(synapse->Input.IsConnected(),int(input)==active);
            }
        }
    };
    request.onSample=[&](const NativeProbeSample& sample) {
        if(interference==Interference::SampleFailure && sampled==10)throw std::runtime_error("injected_sample_failure");
        ++sampled;sourceEvents+=unsigned(sample.newStimuli.size());
        trace<<sample.time<<','<<sample.stimulus;
        for(const auto value:sample.potentials)trace<<','<<value;trace<<'\n';
    };
    const auto prototype=request;
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
        QFile csv(directory+"/"+QString::fromStdString(name)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto wave=QByteArray::fromStdString(trace.str());ASSERT_EQ(csv.write(wave),wave.size());
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
        if(interference==Interference::DeleteSynapse)EXPECT_TRUE(result->currentBaseRevision.empty());
        dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();return;
    }
    ASSERT_EQ(result->status,NativeProbeStatus::Completed);
    ASSERT_TRUE(result->observation);const auto& observed=*result->observation;
    for(const auto& reason:observed.reasons)std::cout<<name<<" observation_reason="<<reason<<std::endl;
    if(mergedBurst)
    {
        ASSERT_TRUE(observed.complete);ASSERT_EQ(observed.stimuli.size(),2u);
        EXPECT_EQ(result->currentBaseRevision,base);EXPECT_EQ(readRevision(),base);
        if(observationSchema==2)
        {
            // Two real emissions have merged into one physical response wave.
            // WindowOnly labels that same response independently for each input.
            EXPECT_TRUE(observed.valid);EXPECT_TRUE(observed.burstAssignments.empty());
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
TEST(NativeBoundedTraining, Branch2000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(2000,Interference::None,2,3,false,true);}
TEST(NativeBoundedTraining, Classic20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearner>(20000,Interference::None,2,3,false,true);}
TEST(NativeBoundedTraining, Branch20000)
{ExecuteProbeThroughLearner<NNeuronTimeLearnerBranch>(20000,Interference::None,2,3,false,true);}
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
}
