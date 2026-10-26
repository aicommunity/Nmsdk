#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseGeneratorMulti.h"
#include "TimeLearner/ModelIdentity.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonDocument>
#include <QJsonArray>
#include <QDir>
#include <QFile>
#include <tuple>
#include <type_traits>
#include <sstream>
#include <iomanip>
#include <locale>
#include <cstdlib>
#include <algorithm>
#include <cmath>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
class NativeTimeLearnerProbe : public ::testing::TestWithParam<std::tuple<bool,unsigned,bool>> {};
QJsonValue ObservedNumber(const std::optional<double>& value)
{ return value?QJsonValue(*value):QJsonValue(QJsonValue::Null); }

template<class Learner> void NativeProbe(unsigned frequency,bool editDuringProbe,
    ProbeObservation* recorded=nullptr,unsigned inputCount=4,const std::string& artifactTag={},
    FinalVerificationSession* verification=nullptr,const VerificationRequest* request=nullptr)
{
    ASSERT_TRUE(inputCount==1 || inputCount==4);
    ASSERT_EQ(bool(verification),bool(request));
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+
        (inputCount==4?"":"_N1")+(editDuringProbe?"_edited":"_frozen");
    const std::string artifactName=name+artifactTag;
    StorageProfileSpec profile;profile.name="ProbeCharacterization_"+name;
    profile.frequencyHz=frequency;profile.neuronBaseClass="NSPNeuronGen";
    profile.initialThreshold=1.; // Explicit immutable subthreshold characterization profile.
    const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(learner);learner->Name="ProbeControl";
    learner->StructureBuildMode=1;learner->NumInputDendrite=inputCount;learner->NeuronClassName=registered.neuronClass;
    learner->CalculateMode=1;learner->NormalizationMode=1;learner->EnablePostTrainTuning=false;
    learner->AutoCalibrateFixedLTZThreshold=false;
    const double gaps[]{.01,.08,.16,.24};
    MDMatrix<double> pattern;pattern.Assign(inputCount,1,0.);
    for(unsigned i=0;i<inputCount;++i)pattern(i,0)=gaps[i];learner->InputPattern=pattern;
    UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();
    learner->ResetToUntrainedState=true;model->Reset();
    model->Calculate();core.environment->IncreaseModelTimeByStep();
    learner->IsNeedToTrain=false; // Frozen characterization, never a convergence claim.
    auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
    std::vector<UEPtr<NPulseMembrane>> somas;
    for(unsigned i=0;i<(branch?1u:inputCount);++i)
    {
        auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
        ASSERT_TRUE(soma);somas.push_back(soma);
    }
    NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);
    ASSERT_TRUE(before["valid"].toBool())<<QJsonDocument(before).toJson().constData();
    const auto initialRevision=before["sha256"].toString().toStdString();
    auto revision=initialRevision;
    if(request)
    {
        ASSERT_EQ(initialRevision,request->baseModelRevision);
        PreparedVerificationProbe prepared{request->routing,request->inputId,request->protocolRevision,
            request->baseModelRevision,initialRevision,request->epoch};
        verification->Arm(prepared);ASSERT_TRUE(verification->WaitingForObservation());
    }
    ProbeSpec spec;spec.runId=request?request->runId:"native_characterization";
    spec.trialId=request?request->trialId:artifactName;spec.sampleId="native_burst";
    QJsonArray configuredPattern;
    for(int i=0;i<learner->InputPattern.GetRows();++i)configuredPattern.append(learner->InputPattern(i,0));
    spec.patternHash=NmsdkTools::CanonicalModelDataSha256(configuredPattern).toStdString();
    spec.modelRevision=revision;spec.begin=core.environment->GetTime().GetDoubleTime();
    spec.end=inputCount==4?.56:.12;spec.maximumSampleGap=1./frequency;spec.maximumSamples=frequency;
    for(const auto& soma:somas)spec.baseline.push_back(soma->SumPotential(0,0));
    const double onsets[]{.01,.09,.25,.49};
    for(unsigned i=0;i<inputCount;++i)
    {
        const auto id="pulse"+std::to_string(i);spec.expectedStimulusIds.push_back(id);
        spec.windows.push_back({"input"+std::to_string(i),branch?0u:i,onsets[i]-.001,onsets[i]+.06,id});
    }
    ProbeRecorder recorder(spec);unsigned pulse=0;double previous=0.,last=spec.begin;
    bool edited=false;std::ostringstream trace;trace.imbue(std::locale::classic());
    trace<<std::setprecision(17)<<"native_tick_start_s,stimulus";
    for(unsigned i=0;i<somas.size();++i)trace<<",raw_soma_"<<i;trace<<'\n';
    while(last<spec.end)
    {
        last=core.environment->GetTime().GetDoubleTime();
        if(editDuringProbe && !edited && last>=.2)
        {
            // Deliberate illegal mid-probe learned-R edit: negative revision control.
            auto synapse=neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);
            ASSERT_TRUE(synapse);synapse->Resistance=synapse->Resistance.GetData()*1.1;
            const auto changed=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(changed["valid"].toBool());
            revision=changed["sha256"].toString().toStdString();edited=true;
        }
        model->Calculate();
        const double stimulus=generator->Output.GetData().GetSize()?generator->Output(0,0):0.;
        if(stimulus>0. && previous<=0.)recorder.RecordStimulus("pulse"+std::to_string(pulse++),last);
        previous=stimulus;
        std::vector<double> potentials;trace<<last<<','<<stimulus;
        // Read physical components. Branch diagnostic rows 1..N are cached peaks.
        for(const auto& soma:somas){potentials.push_back(soma->SumPotential(0,0));trace<<','<<potentials.back();}
        trace<<'\n';recorder.Observe(last,potentials,revision);
        core.environment->IncreaseModelTimeByStep();
    }
    const auto after=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(after["valid"].toBool());
    auto result=recorder.Close(last,after["sha256"].toString().toStdString(),"window_closed");
    EXPECT_TRUE(result.complete);EXPECT_EQ(pulse,inputCount);
    if(editDuringProbe)
    {
        EXPECT_TRUE(edited);EXPECT_FALSE(result.valid);
        EXPECT_NE(initialRevision,revision);
        EXPECT_NE(std::find(result.reasons.begin(),result.reasons.end(),"model_revision_changed"),result.reasons.end());
    }
    else
    {
        EXPECT_EQ(after["sha256"],before["sha256"]);EXPECT_TRUE(result.valid);
        for(const auto& peak:result.peaks)EXPECT_EQ(peak.validity,PeakValidity::Valid);
    }
    QJsonArray peaks,stimuli,reasons,baseline,windows;
    for(const auto& window:spec.windows)windows.append(QJsonObject{
        {"input_id",QString::fromStdString(window.inputId)}, {"stimulus_id",QString::fromStdString(window.stimulusId)},
        {"channel",int(window.channel)},{"begin",window.begin},{"end",window.end}});
    for(double v:spec.baseline)baseline.append(v);
    for(const auto& reason:result.reasons)reasons.append(QString::fromStdString(reason));
    for(const auto& event:result.stimuli)stimuli.append(QJsonObject{{"id",QString::fromStdString(event.id)},{"time",event.time}});
    for(const auto& peak:result.peaks)peaks.append(QJsonObject{{"input_id",QString::fromStdString(peak.inputId)},
        {"stimulus_id",QString::fromStdString(peak.stimulusId)},{"validity",PeakValidityName(peak.validity)},
        {"amplitude",ObservedNumber(peak.amplitude)},{"raw_potential",ObservedNumber(peak.rawPotential)},
        {"peak_time",ObservedNumber(peak.time)},{"plateau_end",ObservedNumber(peak.plateauEnd)},
        {"delay_from_actual_stimulus",ObservedNumber(peak.delayFromStimulus)},
        {"candidate_count",int(peak.candidateCount)}});
    QJsonObject observation{{"schema_version",1},{"kind","native_frozen_characterization_probe"},
        {"run_id",QString::fromStdString(spec.runId)},{"trial_id",QString::fromStdString(spec.trialId)},
        {"sample_id",QString::fromStdString(spec.sampleId)},{"configured_pattern_sha256",QString::fromStdString(spec.patternHash)},
        {"observed_stimulus_sha256",NmsdkTools::CanonicalModelDataSha256(stimuli)},
        {"model_before",before},{"model_after",after},{"frequency_hz",int(frequency)},
        {"window_begin",spec.begin},{"window_end",spec.end},{"maximum_sample_gap",spec.maximumSampleGap},
        {"minimum_amplitude",spec.minimumAmplitude},{"maximum_samples",int(spec.maximumSamples)},
        {"measurement_mode","signed_deviation_from_declared_baseline"},{"reset_policy","native_cold_then_frozen"},
        {"peak_windows",windows},{"end_reason",QString::fromStdString(result.endReason)},
        {"baseline",baseline},{"complete",result.complete},{"valid",result.valid},{"reasons",reasons},
        {"actual_stimuli",stimuli},{"peaks",peaks},{"sample_count",int(result.sampleCount)},
        {"spikes_observed",false},{"scientific_training_result",false}};
    if(verification)verification->Consume(result,after["sha256"].toString().toStdString());
    if(recorded)*recorded=result;
    std::cout<<artifactName<<" complete="<<result.complete<<" valid="<<result.valid
             <<" reasons="<<QJsonDocument(reasons).toJson(QJsonDocument::Compact).constData()<<std::endl;
    if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
    {
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile json(directory+"/"+QString::fromStdString(artifactName)+".json");ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(observation).toJson();ASSERT_EQ(json.write(bytes),bytes.size());
        QFile csv(directory+"/"+QString::fromStdString(artifactName)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto wave=QByteArray::fromStdString(trace.str());ASSERT_EQ(csv.write(wave),wave.size());
    }
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}

TEST_P(NativeTimeLearnerProbe, RawNativeSomaBurstAndModelRevision)
{
    const auto [branch,frequency,edit]=GetParam();
    if(branch)NativeProbe<NNeuronTimeLearnerBranch>(frequency,edit);
    else NativeProbe<NNeuronTimeLearner>(frequency,edit);
}
INSTANTIATE_TEST_SUITE_P(TopologiesRatesAndInvalidation,NativeTimeLearnerProbe,::testing::Values(
    std::make_tuple(false,2000u,false),std::make_tuple(true,2000u,false),
    std::make_tuple(false,20000u,false),std::make_tuple(true,20000u,false),
    std::make_tuple(false,2000u,true)));

class NativeFinalVerification : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
template<class Learner> void VerifyNativeSingleInput(unsigned frequency)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    ProbeObservation reference;
    NativeProbe<Learner>(frequency,false,&reference,1,"-reference");ASSERT_TRUE(reference.valid);
    VerificationProtocol protocol;protocol.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
    protocol.patternHash=reference.specification.patternHash;protocol.sampleId=reference.specification.sampleId;
    protocol.originStimulusId="pulse0";protocol.stimulusIds={"pulse0"};protocol.inputs={{"input0","pulse0"}};
    protocol.maximumSampleGap=1./frequency;
    protocol.revision=NmsdkTools::CanonicalModelDataSha256(QJsonObject{{"kind","native_single_input_burst"},
        {"routing",branch?"branch_solo_burst":"classic_burst"},{"frequency_hz",int(frequency)},
        {"pattern_sha256",QString::fromStdString(protocol.patternHash)},{"reset_policy","native_cold_then_frozen"}}).toStdString();
    const auto baseRevision=reference.specification.modelRevision;
    PreparedVerificationProbe initial{protocol.routing,"input0",protocol.revision,baseRevision,baseRevision,0};
    const auto references=CapturedReferences::Capture(protocol,{{initial,reference}});
    VerificationConfig configuration;configuration.runId=reference.specification.trialId+"-verification";
    configuration.currentModelRevision=baseRevision;configuration.maximumProbes=1;
    FinalVerificationSession session(references,configuration);
    const auto request=session.NextRequest();ASSERT_TRUE(request);ProbeObservation measured;
    // The helper arms only after constructing/resetting the actual native model,
    // and before its first stimulus. It performs a second physical probe.
    NativeProbe<Learner>(frequency,false,&measured,1,"-verification",&session,&*request);
    ASSERT_TRUE(measured.valid);ASSERT_EQ(session.Status(),VerificationStatus::Exact);
    ASSERT_TRUE(session.Certificate());const auto& certificate=*session.Certificate();
    EXPECT_TRUE(certificate.Exact());EXPECT_TRUE(certificate.Matches(baseRevision,references,configuration.tolerances,ModelStateKind::LearnedSolo,session.ModelEpoch()));
    EXPECT_FALSE(certificate.Matches(baseRevision,references,configuration.tolerances,ModelStateKind::Recognition,session.ModelEpoch()));
    ASSERT_EQ(certificate.Residuals().size(),1u);
    const auto& residual=certificate.Residuals()[0];
    QJsonObject document{{"schema_version",1},{"kind","native_solo_constraint_verification_certificate"},
        {"input_count",1},{"frequency_hz",int(frequency)},{"routing",branch?"branch_solo_burst":"classic_burst"},
        {"status",VerificationStatusName(session.Status())},{"exact",certificate.Exact()},
        {"model_state_kind","learned_solo"},{"amplitude_goal","captured_per_input_raw_potential"},
        {"model_revision",QString::fromStdString(certificate.ModelRevision())},{"model_epoch",int(certificate.ModelEpoch())},
        {"reference_model_revision",QString::fromStdString(certificate.ReferenceModelRevision())},
        {"reference_model_epoch",int(certificate.ReferenceModelEpoch())},
        {"protocol_revision",QString::fromStdString(certificate.ProtocolRevision())},
        {"reference_trial_id",QString::fromStdString(reference.specification.trialId)},
        {"verification_trial_id",QString::fromStdString(residual.trialId)},
        {"target_raw_potential",residual.targetRawPotential},{"measured_raw_potential",residual.measuredRawPotential},
        {"amplitude_residual",residual.amplitudeResidual},{"amplitude_tolerance",residual.amplitudeTolerance},
        {"amplitude_absolute_tolerance",certificate.Tolerances().amplitudeAbsolute},
        {"amplitude_relative_tolerance",certificate.Tolerances().amplitudeRelative},
        {"minimum_measurable_amplitude",protocol.minimumAmplitude},
        {"sync_tolerance",certificate.Tolerances().sync},{"timing_residual_low",residual.timingResidualLow},
        {"timing_residual_high",residual.timingResidualHigh},{"scientific_training_result",false},
        {"scope","N=1 frozen initial model; no claim of multi-input training or recognition"}};
    if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
    {
        QFile file(QString::fromLocal8Bit(output)+"/"+QString(branch?"Branch":"Classic")+"_"+QString::number(frequency)+"_N1_certificate.json");
        ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(document).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
    }
}
TEST_P(NativeFinalVerification, FreshSingleInputConstraintCertificate)
{
    if(GetParam().first)VerifyNativeSingleInput<NNeuronTimeLearnerBranch>(GetParam().second);
    else VerifyNativeSingleInput<NNeuronTimeLearner>(GetParam().second);
}
INSTANTIATE_TEST_SUITE_P(TopologiesAndRates,NativeFinalVerification,::testing::Values(
    std::make_pair(false,2000u),std::make_pair(true,2000u),
    std::make_pair(false,20000u),std::make_pair(true,20000u)));

class NativeProbeRestart : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
template<class Learner> void RepeatedNativeProbes(unsigned frequency)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+"_restart";
    StorageProfileSpec profile;profile.name="NativeRestart_"+name;profile.frequencyHz=frequency;
    profile.neuronBaseClass="NSPNeuronGen";profile.initialThreshold=1.;
    const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(learner);learner->Name="ProbeControl";learner->StructureBuildMode=1;
    learner->NumInputDendrite=4;learner->NeuronClassName=registered.neuronClass;
    learner->CalculateMode=1;learner->NormalizationMode=1;
    learner->EnablePostTrainTuning=false;learner->AutoCalibrateFixedLTZThreshold=false;
    MDMatrix<double> pattern;pattern.Assign(4,1,0.);
    const double gaps[]{.01,.08,.16,.24},onsets[]{.01,.09,.25,.49};
    for(unsigned i=0;i<4;++i)pattern(i,0)=gaps[i];learner->InputPattern=pattern;
    UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();
    learner->ResetToUntrainedState=true;model->Reset();
    model->Calculate();core.environment->IncreaseModelTimeByStep();learner->IsNeedToTrain=false;
    auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);ASSERT_TRUE(dataset);
    auto generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    const auto identity=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(identity["valid"].toBool());
    const auto revision=identity["sha256"].toString().toStdString();
    std::vector<UEPtr<NPulseMembrane>> somas;
    for(unsigned i=0;i<(branch?1u:4u);++i)
    {
        auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
        ASSERT_TRUE(soma);somas.push_back(soma);
    }
    QJsonArray trials,configuredPattern;std::vector<std::vector<double>> reference;
    for(double gap:gaps)configuredPattern.append(gap);
    const auto patternHash=NmsdkTools::CanonicalModelDataSha256(configuredPattern).toStdString();
    const auto phase=learner->TrainingPhase.GetData();
    // Different idle intervals; the same built graph is reused throughout.
    const double starts[]{.1,.9,2.};
    dataset->StateGeneration=0;
    for(unsigned trial=0;trial<3;++trial)
    {
        while(core.environment->GetTime().GetDoubleTime()+.25/frequency<starts[trial])
        { model->Calculate();core.environment->IncreaseModelTimeByStep(); }
        // Legal boundary: do not Build, reset the learner, or reset model time.
        neuron->Reset();dataset->Reset();dataset->StateGeneration=2;
        const double begin=core.environment->GetTime().GetDoubleTime();
        ProbeSpec spec;spec.runId=name;spec.trialId=name+"_"+std::to_string(trial);
        spec.sampleId="native_burst";spec.patternHash=patternHash;
        spec.modelRevision=revision;spec.begin=begin;spec.end=begin+.56;
        spec.maximumSampleGap=1./frequency;spec.maximumSamples=frequency;
        for(const auto& soma:somas)spec.baseline.push_back(soma->SumPotential(0,0));
        for(unsigned i=0;i<4;++i)
        {
            const auto id="pulse"+std::to_string(i);spec.expectedStimulusIds.push_back(id);
            spec.windows.push_back({"input"+std::to_string(i),branch?0u:i,begin+onsets[i]-.001,begin+onsets[i]+.06,id});
        }
        ProbeRecorder recorder(spec);unsigned count=0;double lastEmission=begin-1.;
        std::vector<std::vector<double>> waveform;QJsonArray stimuli;
        std::ostringstream trace;trace.imbue(std::locale::classic());
        trace<<std::setprecision(17)<<"native_tick_start_s,relative_time_s,stimulus";
        for(unsigned i=0;i<somas.size();++i)trace<<",raw_soma_"<<i;trace<<'\n';
        double now=begin;
        while(now<spec.end)
        {
            now=core.environment->GetTime().GetDoubleTime();model->Calculate();
            // Dataset resets the generator for every pulse. Read actual native
            // emission times, not PulseCounter or a rising edge of Output.
            for(int i=0;i<generator->OutputPulseTimes.GetCols();++i)
            {
                const double time=generator->OutputPulseTimes(0,i);
                if(time>=begin && time>lastEmission)
                {
                    recorder.RecordStimulus("pulse"+std::to_string(count++),time);
                    stimuli.append(time-begin);lastEmission=time;
                }
            }
            std::vector<double> values;
            trace<<now<<','<<now-begin<<','<<generator->Output(0,0);
            for(const auto& soma:somas){values.push_back(soma->SumPotential(0,0));trace<<','<<values.back();}
            trace<<'\n';
            waveform.push_back(values);recorder.Observe(now,values,revision);
            core.environment->IncreaseModelTimeByStep();
        }
        const auto actual=NmsdkTools::IdentifyModel(neuron,ports);ASSERT_TRUE(actual["valid"].toBool());
        const auto observation=recorder.Close(now,actual["sha256"].toString().toStdString(),"window_closed");
        ASSERT_TRUE(observation.complete);ASSERT_TRUE(observation.valid);ASSERT_EQ(count,4u);
        EXPECT_EQ(actual["sha256"],identity["sha256"]);EXPECT_FALSE(learner->IsNeedToTrain.GetData());
        EXPECT_EQ(learner->TrainingPhase.GetData(),phase);
        EXPECT_NEAR(dataset->GetSampleStartTime(),begin,1e-12);
        for(unsigned i=0;i<4;++i)EXPECT_NEAR(stimuli[int(i)].toDouble(),onsets[i],1./frequency+1e-12);
        double maximumDifference=0.;
        const auto compared=trial?std::min(reference.size(),waveform.size()):waveform.size();
        if(trial==0)reference=waveform;
        else
        {
            // Accumulated absolute-clock rounding can change the final sample
            // count by one; common relative samples still prove native response.
            ASSERT_GE(compared,static_cast<std::size_t>(.55*frequency));
            for(std::size_t i=0;i<compared;++i)for(unsigned c=0;c<somas.size();++c)
                maximumDifference=std::max(maximumDifference,std::abs(waveform[i][c]-reference[i][c]));
            EXPECT_LE(maximumDifference,1e-10)<<"trial="<<trial;
        }
        const auto csvName=spec.trialId+".csv";
        if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
        {
            const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
            QFile csv(directory+"/"+QString::fromStdString(csvName));ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QByteArray::fromStdString(trace.str());ASSERT_EQ(csv.write(bytes),bytes.size());
        }
        trials.append(QJsonObject{{"trial_id",QString::fromStdString(spec.trialId)},
            {"begin",begin},{"end",now},{"sample_count",int(observation.sampleCount)},
            {"complete",observation.complete},{"valid",observation.valid},{"actual_relative_stimuli",stimuli},
            {"configured_pattern_sha256",QString::fromStdString(patternHash)},
            {"waveform_file",QString::fromStdString(csvName)},{"compared_samples",int(compared)},
            {"maximum_raw_potential_difference",maximumDifference},{"comparison_tolerance",1e-10},
            {"model_before",identity},{"model_after",actual}});
        dataset->StateGeneration=0;
    }
    if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
    {
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile file(directory+"/"+QString::fromStdString(name)+".json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(QJsonObject{{"schema_version",1},{"kind","native_repeated_probe_control"},
            {"frequency_hz",int(frequency)},{"trials",trials},{"scientific_training_result",false}}).toJson();
        ASSERT_EQ(file.write(bytes),bytes.size());
    }
    dynamic_pointer_cast<UNet>(model)->BreakLinks();core.environment->DestroyModel();
}
TEST_P(NativeProbeRestart, DatasetAndPhysicalResetAtNonzeroModelTime)
{
    if(GetParam().first)RepeatedNativeProbes<NNeuronTimeLearnerBranch>(GetParam().second);
    else RepeatedNativeProbes<NNeuronTimeLearner>(GetParam().second);
}
INSTANTIATE_TEST_SUITE_P(TopologiesAndRates,NativeProbeRestart,::testing::Values(
    std::make_pair(false,2000u),std::make_pair(true,2000u),
    std::make_pair(false,20000u),std::make_pair(true,20000u)));

class NativeDatasetEvents : public ::testing::TestWithParam<unsigned> {};
TEST_P(NativeDatasetEvents, NoSyntheticZeroTimestampBeforeFirstEmission)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    auto dataset=dynamic_pointer_cast<NDatasetMatrix>(core.storage->TakeObject("NDatasetMatrix"));ASSERT_TRUE(dataset);
    dataset->Name="Dataset";dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=4;
    MDMatrix<double> pattern;pattern.Assign(4,1,.001);pattern(0,0)=.01;dataset->MatrixData=pattern;
    dataset->Delay=1.;dataset->StateGeneration=2;
    UEPtr<UContainer> component=dataset;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(GetParam());model->Init();model->Reset();
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    generator->PulseLength=.001;
    unsigned edges=0;double previous=0.,lastEmission=-1.;QJsonArray events;
    for(unsigned tick=0;tick<GetParam()/25;++tick)
    {
        model->Calculate();
        const auto output=generator->Output(0,0);if(output>0. && previous<=0.)++edges;previous=output;
        for(int i=0;i<generator->OutputPulseTimes.GetCols();++i)
        {
            const auto time=generator->OutputPulseTimes(0,i);
            if(time>lastEmission){events.append(time);lastEmission=time;}
        }
        core.environment->IncreaseModelTimeByStep();
    }
    EXPECT_EQ(events.size(),4);EXPECT_EQ(edges,4u);
    if(!events.isEmpty())EXPECT_GT(events[0].toDouble(),0.);
    std::cout<<"native_dataset_events frequency="<<GetParam()<<" edges="<<edges
             <<" events="<<QJsonDocument(events).toJson(QJsonDocument::Compact).constData()<<std::endl;
    for(int i=1;i<events.size();++i)EXPECT_GT(events[i].toDouble(),events[i-1].toDouble());
    if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
    {
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile file(directory+"/DatasetEvents_"+QString::number(GetParam())+".json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(QJsonObject{{"kind","native_dataset_stimulus_events"},
            {"frequency_hz",int(GetParam())},{"rising_edges",int(edges)},
            {"actual_stimuli",events},{"scientific_training_result",false}}).toJson();
        ASSERT_EQ(file.write(bytes),bytes.size());
    }
    core.environment->DestroyModel();
}
INSTANTIATE_TEST_SUITE_P(Rates,NativeDatasetEvents,::testing::Values(2000u,20000u));

class NativeGeneratorPulseTimes : public ::testing::TestWithParam<std::pair<bool,unsigned>> {};
template<class Generator> void ActualEmissionHistory(unsigned frequency,const std::string& className)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    auto generator=dynamic_pointer_cast<Generator>(core.storage->TakeObject(className));ASSERT_TRUE(generator);
    generator->Name="Generator";
    UEPtr<UContainer> component=generator;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();model->Reset();
    if constexpr(std::is_same<Generator,NPulseGeneratorMulti>::value)
    {
        std::cout<<"native_multi_after_init count="<<generator->PulseCount.GetData()
                 <<" delays="<<generator->Delays.GetCols()<<" counters="<<generator->PulseCounters->size()<<std::endl;
        EXPECT_EQ(generator->PulseCount.GetData(),1);
        EXPECT_EQ(generator->Delays.GetCols(),1);
        EXPECT_EQ(generator->PulseCounters->size(),1u);
    }
    EXPECT_EQ(generator->OutputPulseTimes.GetCols(),0);
    generator->Frequency=100.;model->Calculate();
    ASSERT_EQ(generator->OutputPulseTimes.GetCols(),1);
    EXPECT_EQ(generator->OutputPulseTimes(0,0),0.); // Real emission, not a sentinel.
    core.environment->IncreaseModelTimeByStep();
    generator->Frequency=0.;model->Calculate();
    EXPECT_EQ(generator->OutputPulseTimes.GetCols(),0);
    generator->Frequency=100.;generator->Reset();
    EXPECT_EQ(generator->OutputPulseTimes.GetCols(),0);
    model->Calculate();ASSERT_EQ(generator->OutputPulseTimes.GetCols(),1);
    EXPECT_EQ(generator->OutputPulseTimes(0,0),core.environment->GetTime().GetDoubleTime());
    if constexpr(std::is_same<Generator,NPulseGeneratorMulti>::value)
    {
        // Native setters own dimensions; no forced extra Build/Init sequence.
        MDMatrix<double> delays;delays.Assign(1,2,0.);delays(0,1)=.002;
        generator->Delays=delays;
        EXPECT_EQ(generator->PulseCount.GetData(),2);
        for(unsigned i=0;i<frequency/250;++i)
        { core.environment->IncreaseModelTimeByStep();model->Calculate(); }
        EXPECT_EQ(generator->PulseCounters->size(),2u);
        ASSERT_EQ(generator->OutputPulseTimes.GetCols(),2);
        EXPECT_NEAR(generator->OutputPulseTimes(0,1)-generator->OutputPulseTimes(0,0),.002,1./frequency+1e-12);
        generator->PulseCount=1;
        core.environment->IncreaseModelTimeByStep();model->Calculate();
        EXPECT_EQ(generator->Delays.GetCols(),1);
        EXPECT_EQ(generator->PulseCounters->size(),1u);
        ASSERT_EQ(generator->OutputPulseTimes.GetCols(),1);
    }
    core.environment->DestroyModel();
}
TEST_P(NativeGeneratorPulseTimes, EmptyHistoryAndActualZeroTimeAreDistinct)
{
    if(GetParam().first)ActualEmissionHistory<NPulseGeneratorMulti>(GetParam().second,"NPulseGeneratorMulti");
    else ActualEmissionHistory<NPulseGenerator>(GetParam().second,"NPGenerator");
}
INSTANTIATE_TEST_SUITE_P(VariantsAndRates,NativeGeneratorPulseTimes,::testing::Values(
    std::make_pair(false,2000u),std::make_pair(true,2000u),
    std::make_pair(false,20000u),std::make_pair(true,20000u)));
}
