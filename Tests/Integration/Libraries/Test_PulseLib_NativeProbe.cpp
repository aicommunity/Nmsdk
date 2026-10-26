#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/FinalVerification.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../App/NeuroModelerConsole/ModelIdentity.h"
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
        {"model_revision",QString::fromStdString(certificate.ModelRevision())},{"model_epoch",int(certificate.ModelEpoch())},
        {"reference_model_revision",QString::fromStdString(certificate.ReferenceModelRevision())},
        {"protocol_revision",QString::fromStdString(certificate.ProtocolRevision())},
        {"reference_trial_id",QString::fromStdString(reference.specification.trialId)},
        {"verification_trial_id",QString::fromStdString(residual.trialId)},
        {"target_raw_potential",residual.targetRawPotential},{"measured_raw_potential",residual.measuredRawPotential},
        {"amplitude_residual",residual.amplitudeResidual},{"amplitude_tolerance",residual.amplitudeTolerance},
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
}
