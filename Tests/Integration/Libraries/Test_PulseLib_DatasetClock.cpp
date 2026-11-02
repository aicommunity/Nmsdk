#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NDatasetMatrix.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ModelIdentity.h"
#include "../Support/ConsoleLikeInit.h"
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Require(bool ok,const char* reason) { if(!ok)throw std::runtime_error(reason); }
void Write(const std::string& name,const QByteArray& bytes)
{
    if(const char* directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        std::filesystem::create_directories(directory);
        QFile file(QString::fromStdString((std::filesystem::path(directory)/name).string()));
        Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"clock fixture artifact exists/unavailable");
        Require(file.write(bytes)==bytes.size() && file.flush(),"clock fixture artifact write failed");
    }
}
struct Frame { double time,stimulus,soma; };
struct Playback { std::vector<Frame> frames;QJsonObject record; };

Playback Play(unsigned frequency,int mode,double delay,double origin,const std::string& stem)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    core.environment->DestroyModel();
    Require(core.environment->CreateModel("NModel"),"clock fixture model unavailable");
    auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());Require(bool(model),"clock fixture root unavailable");
    model->SetEnvironment(core.environment);model->SetGlobalTimeStep(frequency);
    StorageProfileSpec profile;profile.name="DatasetClockProfile_"+std::to_string(frequency);profile.frequencyHz=frequency;
    const auto images=RegisterStorageProfile(core.storage,core.environment,profile);
    auto neuron=dynamic_pointer_cast<NPulseNeuron>(core.storage->TakeObject(images.neuronClass));
    auto dataset=dynamic_pointer_cast<NDatasetMatrix>(core.storage->TakeObject("NDatasetMatrix"));
    Require(bool(neuron) && bool(dataset),"clock fixture native components unavailable");
    neuron->Name="Neuron";dataset->Name="Dataset";
    neuron->SetEnvironment(core.environment);dataset->SetEnvironment(core.environment);
    neuron->SetGlobalTimeStep(frequency);dataset->SetGlobalTimeStep(frequency);
    neuron->NumSomaMembraneParts=1;neuron->StructureBuildMode=2;
    neuron->NumDendriteMembranePartsVec=std::vector<int>{1};
    dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=2;
    MDMatrix<double> pattern;pattern.Assign(2,1,0.);pattern(0,0)=.01;pattern(1,0)=.04;
    MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MatrixData=pattern;dataset->MatrixClasses=labels;
    dataset->Delay=delay;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=true;
    dataset->TimeGeneration=.18;dataset->StateGeneration=mode;
    UEPtr<UContainer> dataNode=dataset,neuronNode=neuron;
    Require(model->AddComponent(dataNode)!=ForbiddenId && model->AddComponent(neuronNode)!=ForbiddenId,"clock fixture attach failed");
    const auto marker=model->OperationFailureSequence();model->Init();
    Require(!model->HasOperationFailureSince(marker) && model->IsReady() && model->IsInit(),"clock fixture native Init failed");
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    auto synapse=neuron->GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);
    auto soma=neuron->GetComponentL<NPulseMembrane>("Soma1",true);
    Require(bool(generator) && bool(synapse) && bool(soma),"clock fixture effective graph incomplete");
    generator->PulseLength=.001;generator->FrequencyDeviation=0.;
    int slot=0;Require(generator->Connect(dynamic_pointer_cast<UConnector>(synapse),"Output","Input",slot),"clock fixture stimulus binding failed");
    // UTimeControl::SetTime takes integer microseconds, not seconds.
    core.environment->GetTime().SetTime(static_cast<ULongTime>(std::llround(origin*1e6)));model->Reset();
    Require(core.environment->GetTime().GetDoubleTime()==origin,"clock fixture origin not applied");
    Require(!model->HasOperationFailureSince(marker),"clock fixture native Reset failed");
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"dataset_generator"}};
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);Require(before["valid"].toBool(),"clock fixture identity invalid");
    Playback result;QJsonArray edges;std::ostringstream csv;csv.imbue(std::locale::classic());
    csv<<std::setprecision(17)<<"time,stimulus,soma0\n";
    bool wasHigh=false;double peak=0.;
    for(unsigned tick=0;tick<=frequency/4;++tick)
    {
        model->Calculate();
        Require(!model->HasOperationFailureSince(marker),"clock fixture caught native Calculate failure");
        const double time=core.environment->GetTime().GetDoubleTime();
        Require(std::abs((time-origin)-double(tick)/frequency)<1e-12,"clock fixture native sample grid differs");
        Require(generator->Output.GetRows()==1 && generator->Output.GetCols()==1 && soma->SumPotential.GetRows()==1 && soma->SumPotential.GetCols()==1,"clock fixture invalid readout dimensions");
        const double input=generator->Output(0,0),potential=soma->SumPotential(0,0);
        Require(std::isfinite(time) && std::isfinite(input) && std::isfinite(potential),"clock fixture nonfinite measurement");
        Require(synapse->Input(0,0)==input,"clock fixture actual synapse input differs");
        if(input>0. && !wasHigh)edges.append(QJsonObject{{"tick",double(tick)},{"time",time}});
        wasHigh=input>0.;peak=std::max(peak,std::abs(potential));
        result.frames.push_back({time,input,potential});csv<<time<<','<<input<<','<<potential<<'\n';
        core.environment->IncreaseModelTimeByStep();
    }
    const auto after=NmsdkTools::IdentifyModel(neuron,ports);
    Require(after["valid"].toBool() && after["sha256"]==before["sha256"],"clock fixture physical model changed");
    Require(edges.size()>=4 && peak>1e-6,"clock fixture must show repeated real pulses and soma response");
    result.record=QJsonObject{{"kind","native_dataset_clock_observation"},{"schema_version",1},
        {"frequency_hz",int(frequency)},{"mode",mode},{"delay",delay},{"origin",origin},
        {"complete",true},{"window_duration",.25},{"sample_count",double(result.frames.size())},
        {"scheduled_isi",QJsonArray{.01,.04}},{"pulse_length",.001},{"time_generation",.18},
        {"rising_edges",edges},{"model",before},{"after_model",after},{"peak_abs_soma",peak},
        {"trace",QString::fromStdString(stem+".csv")},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    Write(stem+".csv",QByteArray::fromStdString(csv.str()));Write(stem+".json",QJsonDocument(result.record).toJson());
    const auto attached=model->GetNumComponents();
    neuron->BreakLinks();
    model->DelComponent("Neuron",false);model->DelComponent("Dataset",false);
    Require(model->GetNumComponents()==attached-2,"clock fixture detach failed");
    // Native Free recursively releases children, breaks ownership and returns
    // a non-static storage object itself. Do not ReturnObject a second time.
    neuron->Free();dataset->Free();core.environment->DestroyModel();
    return result;
}
void OriginInvariant(unsigned frequency,int mode,double delay)
{
    const auto stem="dataset_clock_"+std::to_string(frequency)+"_mode"+std::to_string(mode)+"_gap"+std::to_string(int(delay*1000));
    try
    {
        std::vector<Playback> runs;
        for(unsigned index=0;index<3;++index)runs.push_back(Play(frequency,mode,delay,index==0?0.:index==1?.1:1.,stem+"_origin"+std::to_string(index)));
        for(unsigned index=1;index<runs.size();++index)
        {
            ASSERT_EQ(runs[index].frames.size(),runs[0].frames.size());
            EXPECT_EQ(runs[index].record["model"].toObject()["sha256"],runs[0].record["model"].toObject()["sha256"]);
            unsigned changedInput=0,changedSoma=0;double maximum=0.;
            for(std::size_t tick=0;tick<runs[0].frames.size();++tick)
            {
                const auto& a=runs[0].frames[tick];const auto& b=runs[index].frames[tick];
                changedInput+=a.stimulus!=b.stimulus;changedSoma+=a.soma!=b.soma;maximum=std::max(maximum,std::abs(a.soma-b.soma));
            }
            EXPECT_EQ(changedInput,0u)<<"origin="<<index<<" real pulse samples must be invariant";
            EXPECT_EQ(changedSoma,0u)<<"origin="<<index<<" maximum soma difference="<<std::setprecision(17)<<maximum;
        }
    }
    catch(const RDK::UException& e) { FAIL()<<e.what(); }
    catch(const std::exception& e) { FAIL()<<e.what(); }
}
TEST(DatasetClockOrigin,ContinuousNoGapAt2000){OriginInvariant(2000,2,0.);}
TEST(DatasetClockOrigin,ContinuousFiveMsAt2000){OriginInvariant(2000,2,.005);}
TEST(DatasetClockOrigin,ContinuousThirtyMsAt2000){OriginInvariant(2000,2,.03);}
TEST(DatasetClockOrigin,TimedNoGapAt2000){OriginInvariant(2000,1,0.);}
TEST(DatasetClockOrigin,TimedFiveMsAt2000){OriginInvariant(2000,1,.005);}
TEST(DatasetClockOrigin,TimedThirtyMsAt2000){OriginInvariant(2000,1,.03);}
TEST(DatasetClockOrigin,ContinuousNoGapAt20000){OriginInvariant(20000,2,0.);}
TEST(DatasetClockOrigin,ContinuousFiveMsAt20000){OriginInvariant(20000,2,.005);}
TEST(DatasetClockOrigin,ContinuousThirtyMsAt20000){OriginInvariant(20000,2,.03);}
TEST(DatasetClockOrigin,TimedNoGapAt20000){OriginInvariant(20000,1,0.);}
TEST(DatasetClockOrigin,TimedFiveMsAt20000){OriginInvariant(20000,1,.005);}
TEST(DatasetClockOrigin,TimedThirtyMsAt20000){OriginInvariant(20000,1,.03);}
}
