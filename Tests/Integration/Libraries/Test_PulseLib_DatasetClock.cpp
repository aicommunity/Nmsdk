#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NDatasetMatrix.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NDataset.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembrane.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/StorageProfiles.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ModelIdentity.h"
#include "../Support/ConsoleLikeInit.h"
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QTemporaryDir>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <locale>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <vector>

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
struct Protocol {
    double firstIsi=.01,secondIsi=.04,timeGeneration=.18;
    int minimumEdges=4;
    bool nearGrid=false;
    std::string tag;
};

Playback Play(unsigned frequency,int mode,double delay,double origin,const std::string& stem,const Protocol& protocol)
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
    MDMatrix<double> pattern;pattern.Assign(2,1,0.);pattern(0,0)=protocol.firstIsi;pattern(1,0)=protocol.secondIsi;
    MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MatrixData=pattern;dataset->MatrixClasses=labels;
    dataset->Delay=delay;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=true;
    dataset->TimeGeneration=protocol.timeGeneration;dataset->StateGeneration=mode;
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
    Require(generator->PulseLength.GetData()==.001 && generator->FrequencyDeviation.GetData()==0. &&
            !generator->UseTransitSignal.GetData() && !generator->UsePatternOutput.GetData() &&
            generator->TimeStep.GetData()==frequency && dataset->Delay.GetData()==delay &&
            dataset->StateGeneration.GetData()==mode && dataset->TimeGeneration.GetData()==protocol.timeGeneration &&
            dataset->MatrixData.GetData()==pattern,"clock fixture effective source configuration differs");
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"dataset_generator"}};
    const auto before=NmsdkTools::IdentifyModel(neuron,ports);Require(before["valid"].toBool(),"clock fixture identity invalid");
    for(const auto& value:before["model"].toObject()["nodes"].toArray())
        Require(value.toObject()["frequency_hz"]==QJsonValue(QString::number(frequency)),"clock fixture physical child frequency differs");
    Playback result;QJsonArray edges;std::ostringstream csv;csv.imbue(std::locale::classic());
    csv<<std::setprecision(17)<<"time,stimulus,soma0\n";
    bool wasHigh=false;double peak=0.,low=std::numeric_limits<double>::infinity(),high=-low;
    for(unsigned tick=0;tick<=frequency/4;++tick)
    {
        model->Calculate();
        Require(!model->HasOperationFailureSince(marker),"clock fixture caught native Calculate failure");
        const double time=core.environment->GetTime().GetDoubleTime();
        const auto clockRoundoff=32.*std::numeric_limits<double>::epsilon()*std::max({1.,std::abs(time),std::abs(origin)});
        Require(std::abs((time-origin)-double(tick)/frequency)<=std::max(1e-12,clockRoundoff),"clock fixture native sample grid differs");
        Require(generator->Output.GetRows()==1 && generator->Output.GetCols()==1 && soma->SumPotential.GetRows()==1 && soma->SumPotential.GetCols()==1,"clock fixture invalid readout dimensions");
        const double input=generator->Output(0,0),potential=soma->SumPotential(0,0);
        Require(std::isfinite(time) && std::isfinite(input) && std::isfinite(potential),"clock fixture nonfinite measurement");
        Require(synapse->Input(0,0)==input,"clock fixture actual synapse input differs");
        if(input>0. && !wasHigh)edges.append(QJsonObject{{"tick",double(tick)},{"time",time}});
        wasHigh=input>0.;peak=std::max(peak,std::abs(potential));
        low=std::min(low,potential);high=std::max(high,potential);
        result.frames.push_back({time,input,potential});csv<<time<<','<<input<<','<<potential<<'\n';
        core.environment->IncreaseModelTimeByStep();
    }
    const auto after=NmsdkTools::IdentifyModel(neuron,ports);
    Require(after["valid"].toBool() && after["sha256"]==before["sha256"],"clock fixture physical model changed");
    Require(edges.size()>=protocol.minimumEdges && high-low>1e-6,"clock fixture must show declared real pulses and soma response");
    result.record=QJsonObject{{"kind","native_dataset_clock_observation"},{"schema_version",2},
        {"assertion_contract","origin_and_pulse_program_v1"},
        {"playback_phase",dataset->WasPlaybackHandledBeforeChildren()?"before_children":"after_children_compatibility"},
        {"frequency_hz",int(frequency)},{"mode",mode},{"delay",delay},{"origin",origin},
        {"complete",true},{"window_duration",.25},{"sample_count",double(result.frames.size())},
        {"scheduled_isi",QJsonArray{protocol.firstIsi,protocol.secondIsi}},{"pulse_length",.001},{"time_generation",protocol.timeGeneration},
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
void OriginInvariant(unsigned frequency,int mode,double delay,Protocol protocol={},bool extended=false)
{
    const auto stem="dataset_clock_"+std::to_string(frequency)+"_mode"+std::to_string(mode)+"_gap"+std::to_string(int(delay*1000))+protocol.tag;
    try
    {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        struct RestoreClock {
            UEPtr<UEnvironment> environment;ULongTime prior;
            ~RestoreClock() { environment->DestroyModel();environment->GetTime().SetTime(prior); }
        } restore{core.environment,core.environment->GetTime().GetTime()};
        std::vector<Playback> runs;
        const std::vector<double> origins=extended?std::vector<double>{0.,.1,1.,86400.,1e9}:std::vector<double>{0.,.1,1.};
        for(unsigned index=0;index<origins.size();++index)
        {
            runs.push_back(Play(frequency,mode,delay,origins[index],stem+"_origin"+std::to_string(index),protocol));
            EXPECT_EQ(runs.back().record["rising_edges"].toArray()[0].toObject()["tick"].toInt(),
                      int(frequency/100)+(protocol.nearGrid?1:0))<<"first actual pulse must occur at the declared native tick";
            const auto period=frequency*51/1000+unsigned(std::llround(delay*frequency));
            const auto first=frequency/100+unsigned(protocol.nearGrid),last=frequency/20,width=frequency/1000;
            const auto cutoff=unsigned(std::llround(protocol.timeGeneration*frequency));
            unsigned wrongPulseSamples=0;
            for(unsigned tick=0;tick<runs.back().frames.size();++tick)
            {
                const auto phase=tick%period;
                const bool expected=(mode!=1 || tick<=cutoff) &&
                    ((phase>=first && phase<first+width) || (phase>=last && phase<last+width));
                wrongPulseSamples+=(runs.back().frames[tick].stimulus>0.)!=expected;
            }
            EXPECT_EQ(wrongPulseSamples,0u)<<"entire native pulse program must retain declared width, repeat and timed cutoff";
        }
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
Protocol Extended(const std::string& tag,bool nearGrid=false,bool cutoff=false)
{
    Protocol p;p.tag="_"+tag;p.nearGrid=nearGrid;
    if(nearGrid){p.firstIsi=.01000001;p.secondIsi=.03999999;}
    if(cutoff){p.timeGeneration=.01;p.minimumEdges=1;}
    return p;
}
TEST(DatasetClockExtended,ContinuousAt2000){OriginInvariant(2000,2,0.,Extended("long"),true);}
TEST(DatasetClockExtended,TimedAt2000){OriginInvariant(2000,1,0.,Extended("long"),true);}
TEST(DatasetClockExtended,ContinuousAt20000){OriginInvariant(20000,2,0.,Extended("long"),true);}
TEST(DatasetClockExtended,TimedAt20000){OriginInvariant(20000,1,0.,Extended("long"),true);}
TEST(DatasetClockExtended,NearGridAt2000){OriginInvariant(2000,2,0.,Extended("near",true),true);}
TEST(DatasetClockExtended,NearGridAt20000){OriginInvariant(20000,2,0.,Extended("near",true),true);}
TEST(DatasetClockExtended,TimedFirstOnsetCutoffAt2000){OriginInvariant(2000,1,0.,Extended("cutoff",false,true),true);}
TEST(DatasetClockExtended,TimedFirstOnsetCutoffAt20000){OriginInvariant(20000,1,0.,Extended("cutoff",false,true),true);}

// Exercise the production file owner, including children added to an already
// initialized tree. Matrix-only probes cannot establish this lifecycle contract.
void FileReload(unsigned frequency)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    struct Cleanup {
        UEPtr<UEnvironment> environment;ULongTime prior;
        ~Cleanup(){environment->DestroyModel();environment->GetTime().SetTime(prior);}
    } cleanup{core.environment,core.environment->GetTime().GetTime()};
    core.environment->DestroyModel();
    Require(core.environment->CreateModel("NModel"),"file fixture model unavailable");
    auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());Require(bool(model),"file fixture root unavailable");
    model->SetEnvironment(core.environment);model->SetGlobalTimeStep(frequency);
    auto dataset=dynamic_pointer_cast<NDataset>(core.storage->TakeObject("NDataset"));
    Require(bool(dataset),"file fixture storage image unavailable");
    QTemporaryDir directory;Require(directory.isValid(),"file fixture temporary directory unavailable");
    const auto path=directory.filePath("patterns.txt");
    dataset->Name="Dataset";dataset->SetEnvironment(core.environment);dataset->SetGlobalTimeStep(frequency);
    dataset->UseRelativePathFromConfig=false;dataset->UseRelativePathFromWorkDir=false;
    dataset->FileName=path.toStdString();dataset->StateGeneration=2;dataset->Delay=.005;
    UEPtr<UContainer> child=dataset;
    Require(model->AddComponent(child)!=ForbiddenId,"file fixture attach failed");
    const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
    Require(!model->HasOperationFailureSince(marker) && model->IsInit() && model->IsReady(),"file fixture native initialization failed");
    core.environment->GetTime().SetTime(1000000);
    model->Calculate();
    Require(dataset->ReloadDataset.GetData() && dataset->GetNumComponents()==0 &&
            !model->HasOperationFailureSince(marker),"missing file must remain retryable and idle");
    core.environment->IncreaseModelTimeByStep();
    auto replaceFile=[&](const QByteArray& text) {
        QFile file(path);Require(file.open(QIODevice::WriteOnly|QIODevice::Truncate),"file fixture write unavailable");
        Require(file.write(text)==text.size() && file.flush(),"file fixture write failed");
    };
    replaceFile("# NDataset MaxSpikes=2\nclass;f1;f2\n7;0.01;0.015\n;0.04;0.03\n");
    QJsonArray observations;
    for(int phase=0;phase<2;++phase)
    {
        if(phase==1)
        {
            replaceFile("# NDataset MaxSpikes=2\nclass;f1\n9;0.02\n;0.02\n");
            dataset->ReloadDataset=true;
        }
        std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"time,input1,input2\n";
        std::vector<unsigned> firstEdges(phase==0?2:1,std::numeric_limits<unsigned>::max());
        std::vector<bool> previous(firstEdges.size(),false);
        unsigned wrong=0;
        for(unsigned tick=0;tick<=frequency*8/100;++tick)
        {
            model->Calculate();
            Require(!model->HasOperationFailureSince(marker),"file fixture caught native failure");
            Require(!dataset->ReloadDataset.GetData() && dataset->WasPlaybackHandledBeforeChildren(),"file playback did not prepare before children");
            Require(dataset->GetNumComponents()==int(firstEdges.size()) && dataset->NumFeatures.GetData()==int(firstEdges.size()) &&
                    dataset->MaxSpikesPerFeature.GetData()==2 && dataset->GetSampleClass(0)==(phase==0?7:9),"file reload effective graph/data differ");
            csv<<core.environment->GetTime().GetDoubleTime();
            const unsigned period=frequency*(phase==0?56:46)/1000;
            for(unsigned index=0;index<firstEdges.size();++index)
            {
                auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator"+std::to_string(index+1),true);
                Require(bool(generator) && generator->IsInit() && generator->IsReady() && generator->TimeStep.GetData()==frequency,
                        "hot-created generator is not natively initialized at the declared frequency");
                Require(generator->Output.GetRows()==1 && generator->Output.GetCols()==1,"file fixture output shape differs");
                const double output=generator->Output(0,0);Require(std::isfinite(output),"file fixture nonfinite output");
                const bool high=output>0.;if(high && !previous[index] && firstEdges[index]==std::numeric_limits<unsigned>::max())firstEdges[index]=tick;
                previous[index]=high;
                const unsigned first=frequency*(phase==1?20:index==0?10:15)/1000;
                const unsigned last=frequency*(phase==1?40:index==0?50:45)/1000;
                const unsigned position=tick%period,width=frequency/1000;
                const bool expected=(position>=first && position<first+width)||(position>=last && position<last+width);
                wrong+=high!=expected;csv<<','<<output;
            }
            if(phase==1)csv<<",0";
            csv<<'\n';core.environment->IncreaseModelTimeByStep();
        }
        EXPECT_EQ(wrong,0u)<<"hot reload must preserve every actual pulse sample";
        for(unsigned index=0;index<firstEdges.size();++index)
            EXPECT_EQ(firstEdges[index],frequency*(phase==1?20:index==0?10:15)/1000);
        const auto stem="dataset_file_reload_"+std::to_string(frequency)+"_phase"+std::to_string(phase);
        Write(stem+".csv",QByteArray::fromStdString(csv.str()));
        observations.append(QJsonObject{{"phase",phase},{"features",int(firstEdges.size())},{"wrong_pulse_samples",int(wrong)},
            {"trace",QString::fromStdString(stem+".csv")},{"complete",true}});
    }
    Write("dataset_file_reload_"+std::to_string(frequency)+".json",QJsonDocument(QJsonObject{
        {"kind","native_dataset_file_reload"},{"schema_version",1},{"frequency_hz",int(frequency)},
        {"observations",observations},{"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
}
TEST(DatasetFileLifecycle,MissingThenGrowThenShrinkAt2000)
{try{FileReload(2000);}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
TEST(DatasetFileLifecycle,MissingThenGrowThenShrinkAt20000)
{try{FileReload(20000);}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}

class ObservedDataset: public NDatasetMatrix {
public:
    unsigned beforeCalls=0,calculateCalls=0,prepareCalls=0;
protected:
    bool ABeforeCalculate() override {++beforeCalls;return NDatasetMatrix::ABeforeCalculate();}
    bool ACalculate() override {++calculateCalls;return NDatasetMatrix::ACalculate();}
    void PreparePlaybackData() override {++prepareCalls;NDatasetMatrix::PreparePlaybackData();}
};
// Instrument only native callbacks; all playback and child calculations remain
// production implementations. This establishes dispatch, not multirate physics.
void Scheduling(unsigned sourceFrequency)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    struct Cleanup {
        UEPtr<UEnvironment> environment;ULongTime prior;
        ~Cleanup(){environment->DestroyModel();environment->GetTime().SetTime(prior);}
    } cleanup{core.environment,core.environment->GetTime().GetTime()};
    core.environment->DestroyModel();Require(core.environment->CreateModel("NModel"),"dispatch root unavailable");
    auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());Require(bool(model),"dispatch root type differs");
    model->SetEnvironment(core.environment);model->SetGlobalTimeStep(2000);
    UEPtr<ObservedDataset> dataset(new ObservedDataset);
    dataset->SetStorage(core.storage);dataset->SetEnvironment(core.environment);dataset->Default();dataset->Name="Dataset";
    dataset->Activity=true;
    MDMatrix<double> values;values.Assign(2,1,0.);values(0,0)=.01;values(1,0)=.04;
    MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MaxSpikesPerFeature=2;dataset->MatrixData=values;dataset->MatrixClasses=labels;
    dataset->Delay=.005;dataset->StateGeneration=2;
    UEPtr<UContainer> child=dataset;Require(model->AddComponent(child)!=ForbiddenId,"dispatch attach failed");
    const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
    Require(!model->HasOperationFailureSince(marker) && model->IsInit() && model->Activity.GetData() &&
            dataset->IsInit() && dataset->Activity.GetData(),"dispatch native Init/activity precondition failed");
    // Explicit multirate intervention after native construction. Never update
    // frequency or repair the graph inside the calculation loop.
    dataset->SetGlobalTimeStep(sourceFrequency);
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Require(bool(generator) && generator->TimeStep.GetData()==sourceFrequency && model->TimeStep.GetData()==2000,
            "dispatch frequency intervention not applied");
    core.environment->GetTime().SetTime(1000000);
    dataset->beforeCalls=dataset->calculateCalls=dataset->prepareCalls=0;
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"time,stimulus,before_calls,calculate_calls,prepare_calls\n";
    unsigned highSamples=0;
    constexpr unsigned count=160;
    for(unsigned tick=0;tick<count;++tick)
    {
        model->Calculate();Require(!model->HasOperationFailureSince(marker),"dispatch native Calculate failed");
        EXPECT_EQ(dataset->WasPlaybackHandledBeforeChildren(),sourceFrequency==2000);
        Require(generator->Output.GetRows()==1 && generator->Output.GetCols()==1,"dispatch output unavailable");
        const double output=generator->Output(0,0);Require(std::isfinite(output),"dispatch nonfinite output");highSamples+=output>0.;
        csv<<core.environment->GetTime().GetDoubleTime()<<','<<output<<','<<dataset->beforeCalls<<','<<dataset->calculateCalls<<','<<dataset->prepareCalls<<'\n';
        core.environment->IncreaseModelTimeByStep();
    }
    EXPECT_EQ(dataset->beforeCalls,count);
    // Preserve the actual Rdk higher-frequency loop (ratio+1), without silently
    // replacing it by the scientifically desired ratio in a learner controller.
    const unsigned expected=sourceFrequency==1000?count/2:sourceFrequency==2000?count:count*3;
    EXPECT_EQ(dataset->calculateCalls,expected);EXPECT_EQ(dataset->prepareCalls,expected);
    EXPECT_GT(highSamples,0u);
    const auto stem="dataset_dispatch_"+std::to_string(sourceFrequency);
    Write(stem+".csv",QByteArray::fromStdString(csv.str()));
    Write(stem+".json",QJsonDocument(QJsonObject{{"kind","native_dataset_dispatch"},{"schema_version",1},
        {"root_frequency_hz",2000},{"source_frequency_hz",int(sourceFrequency)},{"native_ticks",int(count)},
        {"before_calls",int(dataset->beforeCalls)},{"calculate_calls",int(dataset->calculateCalls)},
        {"prepare_calls",int(dataset->prepareCalls)},{"expected_calculate_calls",int(expected)},
        {"high_samples",int(highSamples)},{"trace",QString::fromStdString(stem+".csv")},
        {"scope","native dispatch only; no multirate physical-support certificate"}}).toJson());
}
TEST(DatasetScheduling,UniformSourceAt2000)
{try{Scheduling(2000);}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
TEST(DatasetScheduling,SlowerSourceAt1000)
{try{Scheduling(1000);}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
TEST(DatasetScheduling,FasterSourceAt4000)
{try{Scheduling(4000);}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
}
