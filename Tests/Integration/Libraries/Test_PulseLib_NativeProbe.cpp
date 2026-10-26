#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.h"
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

template<class Learner> void NativeProbe(unsigned frequency,bool editDuringProbe)
{
    const bool branch=std::is_same<Learner,NNeuronTimeLearnerBranch>::value;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel();ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(frequency)+(editDuringProbe?"_edited":"_frozen");
    StorageProfileSpec profile;profile.name="ProbeCharacterization_"+name;
    profile.frequencyHz=frequency;profile.neuronBaseClass="NSPNeuronGen";
    profile.initialThreshold=1.; // Explicit immutable subthreshold characterization profile.
    const auto registered=RegisterStorageProfile(core.storage,core.environment,profile);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(learner);learner->Name="ProbeControl";
    learner->StructureBuildMode=1;learner->NumInputDendrite=4;learner->NeuronClassName=registered.neuronClass;
    learner->CalculateMode=1;learner->NormalizationMode=1;learner->EnablePostTrainTuning=false;
    learner->AutoCalibrateFixedLTZThreshold=false;
    MDMatrix<double> pattern;pattern.Assign(4,1,0.);
    pattern(0,0)=.01;pattern(1,0)=.08;pattern(2,0)=.16;pattern(3,0)=.24;learner->InputPattern=pattern;
    UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(frequency);model->Init();
    learner->ResetToUntrainedState=true;model->Reset();
    model->Calculate();core.environment->IncreaseModelTimeByStep();
    learner->IsNeedToTrain=false; // Frozen characterization, never a convergence claim.
    auto neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);ASSERT_TRUE(generator);
    std::vector<UEPtr<NPulseMembrane>> somas;
    for(unsigned i=0;i<(branch?1u:4u);++i)
    {
        auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
        ASSERT_TRUE(soma);somas.push_back(soma);
    }
    NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);
    ASSERT_TRUE(before["valid"].toBool())<<QJsonDocument(before).toJson().constData();
    const auto initialRevision=before["sha256"].toString().toStdString();
    auto revision=initialRevision;
    ProbeSpec spec;spec.runId="native_characterization";spec.trialId=name;spec.sampleId="native_burst";
    spec.patternHash=NmsdkTools::CanonicalModelDataSha256(QJsonArray{.01,.08,.16,.24}).toStdString();
    spec.modelRevision=revision;spec.begin=core.environment->GetTime().GetDoubleTime();
    spec.end=.56;spec.maximumSampleGap=1./frequency;spec.maximumSamples=frequency;
    for(const auto& soma:somas)spec.baseline.push_back(soma->SumPotential(0,0));
    const double onsets[]{.01,.09,.25,.49};
    for(unsigned i=0;i<4;++i)
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
    EXPECT_TRUE(result.complete);EXPECT_EQ(pulse,4u);
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
    QJsonArray peaks,stimuli,reasons,baseline;
    for(double v:spec.baseline)baseline.append(v);
    for(const auto& reason:result.reasons)reasons.append(QString::fromStdString(reason));
    for(const auto& event:result.stimuli)stimuli.append(QJsonObject{{"id",QString::fromStdString(event.id)},{"time",event.time}});
    for(const auto& peak:result.peaks)peaks.append(QJsonObject{{"input_id",QString::fromStdString(peak.inputId)},
        {"stimulus_id",QString::fromStdString(peak.stimulusId)},{"validity",PeakValidityName(peak.validity)},
        {"amplitude",peak.amplitude},{"raw_potential",peak.rawPotential},{"peak_time",peak.time},
        {"plateau_end",peak.plateauEnd},{"delay_from_actual_stimulus",peak.delayFromStimulus},
        {"candidate_count",int(peak.candidateCount)}});
    QJsonObject observation{{"schema_version",1},{"kind","native_frozen_characterization_probe"},
        {"run_id",QString::fromStdString(spec.runId)},{"trial_id",QString::fromStdString(spec.trialId)},
        {"sample_id",QString::fromStdString(spec.sampleId)},{"pattern_sha256",QString::fromStdString(spec.patternHash)},
        {"model_before",before},{"model_after",after},{"frequency_hz",int(frequency)},
        {"window_begin",spec.begin},{"window_end",spec.end},{"maximum_sample_gap",spec.maximumSampleGap},
        {"baseline",baseline},{"complete",result.complete},{"valid",result.valid},{"reasons",reasons},
        {"actual_stimuli",stimuli},{"peaks",peaks},{"sample_count",int(result.sampleCount)},
        {"spikes_observed",false},{"scientific_training_result",false}};
    std::cout<<name<<" complete="<<result.complete<<" valid="<<result.valid
             <<" reasons="<<QJsonDocument(reasons).toJson(QJsonDocument::Compact).constData()<<std::endl;
    if(const char* output=std::getenv("TIMELEARNER_PROBE_OUTPUT"))
    {
        const auto directory=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(directory));
        QFile json(directory+"/"+QString::fromStdString(name)+".json");ASSERT_TRUE(json.open(QIODevice::WriteOnly|QIODevice::NewOnly));
        const auto bytes=QJsonDocument(observation).toJson();ASSERT_EQ(json.write(bytes),bytes.size());
        QFile csv(directory+"/"+QString::fromStdString(name)+".csv");ASSERT_TRUE(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly));
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
}
