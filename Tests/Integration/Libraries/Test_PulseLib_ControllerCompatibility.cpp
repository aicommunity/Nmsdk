#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearner.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NNeuronTimeLearnerBranch.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseGeneratorTransit.h"
#include "../Support/ConsoleLikeInit.h"
#include <QCryptographicHash>
#include <QJsonDocument>
#include <QJsonArray>
#include <QFile>
#include <QDir>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <cstdlib>

namespace {
using namespace RDK;
using namespace NMSDK;

template<class T> QJsonArray Array(const std::vector<T>& values)
{
    QJsonArray result;
    for(auto value : values) result.append(QJsonValue(value));
    return result;
}

template<class Learner> QJsonObject State(UEPtr<Learner> learner, unsigned tick)
{
    return {{"tick",int(tick)}, {"phase",learner->TrainingPhase.GetData()},
        {"need",learner->IsNeedToTrain.GetData()}, {"lengths",Array(learner->DendriteLength.GetData())},
        {"synapses",Array(learner->NumSynapse.GetData())},
        {"tip_rs",Array(learner->TipSynapseResistance.GetData())},
        {"references",Array(learner->InitialSomaPotential.GetData())},
        {"iteration",learner->StimulusIterTrace.GetSize() ? learner->StimulusIterTrace(0,0) : -1.},
        {"failure",learner->TrainingFailureReason.GetData()}};
}

void HashDouble(QCryptographicHash& hash, double value)
{
    std::uint64_t bits=0; std::memcpy(&bits,&value,sizeof(bits));
    char bytes[8];
    for(unsigned i=0;i<8;++i) bytes[i]=char((bits>>(8*i))&255);
    hash.addData(QByteArray(bytes,8));
}

struct Case { bool branch; int normalization; unsigned frequency; };
class NativeControllerCompatibility : public ::testing::TestWithParam<Case> {};

template<class Learner> void Run(const Case& spec, const QString& name)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();
    ASSERT_TRUE(core.environment->CreateModel("NModel"));
    auto model=core.environment->GetModel(); ASSERT_TRUE(model);
    core.environment->GetTime().SetTime(0);
    auto learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(spec.branch ? "NNeuronTimeLearnerBranch" : "NNeuronTimeLearner"));
    ASSERT_TRUE(learner); learner->SetEnvironment(core.environment);
    learner->Name="ControllerControl";
    learner->StructureBuildMode=1; learner->NumInputDendrite=2;
    learner->NeuronClassName="NSPNeuronGenAsymRmD001C1e9";
    learner->MaxDendriteLength=8; learner->NormalizationMode=spec.normalization;
    learner->CalculateMode=1; learner->ExperimentMode=false;
    learner->EnablePostTrainTuning=false; learner->AutoCalibrateFixedLTZThreshold=false;
    MDMatrix<double> pattern; pattern.Assign(2,1,0.); pattern(0,0)=.01; pattern(1,0)=.05;
    learner->InputPattern=pattern;
    UEPtr<UContainer> component=learner;
    ASSERT_NE(model->AddComponent(component),ForbiddenId);
    model->SetGlobalTimeStep(spec.frequency); model->Init();
    learner->ResetToUntrainedState=true; model->Reset();
    ASSERT_TRUE(model->IsReady()); ASSERT_TRUE(model->IsInit());
    ASSERT_TRUE(learner->IsReady()); ASSERT_TRUE(learner->IsInit());
    ASSERT_EQ(learner->NormalizationMode.GetData(),spec.normalization);
    auto generator=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    ASSERT_TRUE(generator);
    QJsonArray events; events.append(State(learner,0));
    QCryptographicHash waveform(QCryptographicHash::Sha256);
    const unsigned ticks=unsigned(2.25*spec.frequency);
    double low=0.,high=0.,previousIteration=-1.; bool decision=false;
    for(unsigned tick=0;tick<ticks;++tick)
    {
        model->Calculate(); core.environment->IncreaseModelTimeByStep();
        const auto& amplitudes=learner->SomaNeuronAmplitude.GetData();
        for(int i=0;i<amplitudes.GetSize();++i)
        {
            const double value=amplitudes.Data[i];
            ASSERT_TRUE(std::isfinite(value)); HashDouble(waveform,value);
            low=std::min(low,value); high=std::max(high,value);
        }
        const double iteration=learner->StimulusIterTrace.GetSize() ? learner->StimulusIterTrace(0,0) : -1.;
        if(iteration != previousIteration)
        {
            events.append(State(learner,tick)); previousIteration=iteration;
            for(auto length : learner->DendriteLength.GetData()) decision=decision || length!=1;
            for(auto count : learner->NumSynapse.GetData()) decision=decision || count!=1;
        }
    }
    events.append(State(learner,ticks));
    EXPECT_GE(generator->PulseCounter.GetData(),4);
    EXPECT_GT(high-low,1e-8);
    EXPECT_TRUE(decision) << "fixture must execute a real structural decision, not merely tick an idle model";
    QJsonObject result{{"schema_version",1},{"kind","native_legacy_controller_compatibility_control"},
        {"case",name},{"model_ticks",int(ticks)},{"frequency_hz",int(spec.frequency)},
        {"pulse_count",generator->PulseCounter.GetData()},{"events",events},
        {"waveform_sha256",QString::fromLatin1(waveform.result().toHex())},
        {"scientific_training_result",false}};
    if(const char* baseline=std::getenv("TIMELEARNER_COMPAT_BASELINE"))
    {
        QFile file(QString::fromLocal8Bit(baseline)+"/"+name+".json");
        ASSERT_TRUE(file.open(QIODevice::ReadOnly));
        QJsonParseError error; auto expected=QJsonDocument::fromJson(file.readAll(),&error);
        ASSERT_EQ(error.error,QJsonParseError::NoError);
        EXPECT_EQ(result,expected.object()) << "production observations/decisions differ from the native baseline";
    }
    const auto output=QString::fromLocal8Bit(std::getenv("TIMELEARNER_COMPAT_OUTPUT"));
    ASSERT_TRUE(QDir().mkpath(output));
    QFile file(output+"/"+name+".json"); ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
    const auto bytes=QJsonDocument(result).toJson(); ASSERT_EQ(file.write(bytes),bytes.size());
    dynamic_pointer_cast<UNet>(model)->BreakLinks();
    core.environment->DestroyModel();
}

TEST_P(NativeControllerCompatibility, NativeBurstObservationsAndDecisions)
{
    if(!std::getenv("TIMELEARNER_COMPAT_OUTPUT")) GTEST_SKIP() << "Explicit bounded native A/B run; not a convergence or scientific PASS";
    const auto spec=GetParam();
    const auto name=QString("%1-N%2-f%3").arg(spec.branch ? "Branch" : "Classic").arg(spec.normalization).arg(spec.frequency);
    if(spec.branch) Run<NNeuronTimeLearnerBranch>(spec,name);
    else Run<NNeuronTimeLearner>(spec,name);
}
INSTANTIATE_TEST_SUITE_P(TopologiesModesRates,NativeControllerCompatibility,::testing::Values(
    Case{false,0,2000},Case{false,1,2000},Case{true,0,2000},Case{true,1,2000},
    Case{false,0,20000},Case{false,1,20000},Case{true,0,20000},Case{true,1,20000}));
}
