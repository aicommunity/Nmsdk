#include <gtest/gtest.h>
#include "NAxoneChain.h"
#include "NAxoneChainAndDelay.h"
#include "NDatasetMatrix.h"
#include "NPulseGenerator.h"
#include "NPulseLTZone.h"
#include "TimeLearner/AxoneConductionObservation.h"
#include "TimeLearner/ModelIdentity.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "AxoneHistoricalTargets.inc"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <cmath>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Need(bool value,const char* reason) { if(!value)throw std::runtime_error(reason); }
double Scalar(const MDMatrix<double>& value) {
    Need(value.GetSize()==1 && std::isfinite(value(0,0)),"axone_burst_invalid_scalar");return value(0,0);
}
void CheckRates(UEPtr<UContainer> node,unsigned frequency) {
    Need(node && node->IsReady() && node->IsInit() && node->GetTimeStep()==frequency,
         "axone_burst_effective_child_clock");
    for(int index=0;index<node->GetNumComponents();++index)CheckRates(node->GetComponentByIndex(index),frequency);
}
void Save(const std::string& id,const char* suffix,const QByteArray& bytes) {
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");if(!output)return;
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneBurstDiagnostic");
    Need(QDir().mkpath(folder),"axone_burst_output_directory");
    QFile file(QDir(folder).filePath(QString::fromStdString(id)+suffix));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"axone_burst_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(),"axone_burst_output_write");
}
QJsonArray Events(const std::vector<AxonePulseEvent>& events) {
    QJsonArray result;
    for(const auto& event:events)result.append(QJsonObject{{"onset_tick",int(event.onsetTick)},
        {"end_tick",int(event.endTick)},{"peak",event.peak},{"right_censored",event.rightCensored}});
    return result;
}
QJsonObject Assignment(const std::vector<AxonePulseEvent>& input,const std::vector<AxonePulseEvent>& output,
                       unsigned frequency) {
    const auto match=AssignAxoneConductionEvents(input,output,0,frequency/5);
    QJsonArray pairs,possibleInputs,possibleOutputs,unmatchedInput,unmatchedOutput;
    for(const auto& pair:match.certainPairs)pairs.append(QJsonObject{{"input",int(pair.input)},
        {"output",int(pair.output)},{"lag_ticks",int(pair.lagTicks)}});
    for(const auto& row:match.possibleInputs){QJsonArray item;for(auto value:row)item.append(int(value));possibleInputs.append(item);}
    for(const auto& row:match.possibleOutputs){QJsonArray item;for(auto value:row)item.append(int(value));possibleOutputs.append(item);}
    for(bool value:match.inputCanBeUnmatched)unmatchedInput.append(value);
    for(bool value:match.outputCanBeUnmatched)unmatchedOutput.append(value);
    return {{"maximum_matched",int(match.maximumMatched)},{"ambiguous",match.ambiguous},
        {"complete_one_to_one",match.completeOneToOne},{"certain_pairs",pairs},
        {"possible_inputs",possibleInputs},{"possible_outputs",possibleOutputs},
        {"input_can_be_unmatched",unmatchedInput},{"output_can_be_unmatched",unmatchedOutput},
        {"minimum_lag_ticks",0},{"maximum_lag_ticks",int(frequency/5)},
        {"claim_scope","Temporal association, not causal identification."}};
}
struct Request { std::string id,carrier,pattern;unsigned frequency;int segments;std::vector<double> isi; };
class AxoneBurstDiagnostic:public ::testing::Test,public ::testing::WithParamInterface<Request> {
protected:
    UEPtr<UEnvironment> environment;UEPtr<UStorage> storage;UEPtr<UNet> model;ULongTime originalTime=0;
    void SetUp()override {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));model=dynamic_pointer_cast<UNet>(environment->GetModel());
        ASSERT_TRUE(model);environment->GetTime().SetTime(ULongTime(0));
    }
    void TearDown()override {
        if(model)model->BreakLinks();
        if(environment){environment->DestroyModel();environment->GetTime().SetTime(originalTime);}
    }
    template<class T> UEPtr<T> Take(const std::string& image,const std::string& name) {
        auto node=dynamic_pointer_cast<T>(storage->TakeObject(image));Need(bool(node),"axone_burst_factory");
        node->Name=name;node->SetEnvironment(environment);node->SetGlobalTimeStep(model->GetTimeStep());
        UEPtr<UContainer> base=node;Need(model->AddComponent(base)!=ForbiddenId,"axone_burst_attach");return node;
    }
};
TEST_P(AxoneBurstDiagnostic,CapturesDeclaredBurstAndLengthCondition)
{
    const auto& request=GetParam();
    Need(1000000u%request.frequency==0,"axone_burst_unsupported_global_clock_grid");
    model->SetGlobalTimeStep(request.frequency);
    auto dataset=Take<NDatasetMatrix>("NDatasetMatrix","Source");
    dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=int(request.isi.size());
    dataset->PulseGeneratorClassName="NPulseGeneratorTransit";
    MDMatrix<double> pattern;pattern.Assign(int(request.isi.size()),1,0.);
    for(std::size_t i=0;i<request.isi.size();++i)pattern(int(i),0)=request.isi[i];
    MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MatrixData=pattern;dataset->MatrixClasses=labels;dataset->Iteration=0;
    dataset->Delay=2.;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=false;
    dataset->StateGeneration=1;dataset->TimeGeneration=1.;dataset->Build();
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Need(bool(generator),"axone_burst_missing_generator");
    generator->Amplitude=1.;generator->PulseLength=.001;generator->FrequencyDeviation=0.;
    generator->UseTransitSignal=false;generator->UsePatternOutput=false;
    auto prototype=dynamic_pointer_cast<NPulseLTZone>(storage->TakeObject("NPLTZone"));
    Need(bool(prototype),"axone_burst_ltz_factory");
    prototype->SetEnvironment(environment);prototype->SetGlobalTimeStep(request.frequency);
    prototype->UseSpikeStabilizer=true;prototype->UseLTZIntegtation=true;prototype->TimeConstant=.00144;
    prototype->Threshold=.02;prototype->ThresholdOff=0.;prototype->PulseAmplitude=1.;
    const auto prototypeMarker=prototype->OperationFailureSequence();prototype->Init();prototype->Reset();
    Need(prototype->IsReady() && prototype->IsInit() && !prototype->HasOperationFailureSince(prototypeMarker),
         "axone_burst_ltz_initialization");
    const std::string image="AxoneP1BurstStable20_f"+std::to_string(request.frequency);
    UEPtr<UContainer> prototypeBase=prototype;RegisterClassImage(storage,image,prototypeBase);storage->ReturnObject(prototype);
    auto axon=Take<NAxoneCommon>(request.carrier,"Axon");
    if(auto chain=dynamic_pointer_cast<NAxoneChain>(axon)){chain->NumSegments=request.segments;chain->LTZoneClassName=image;}
    if(auto chain=dynamic_pointer_cast<NAxoneChainAndDelay>(axon)){
        chain->NumNodes=request.segments;chain->InternodeDelayTime=.002;chain->LTZoneClassName=image;
    }
    Need(model->CreateLink("Source.Generator1","Output","Axon","Input"),"axone_burst_source_link");
    const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
    Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),"axone_burst_initialization");
    Need(generator==dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true) &&
         generator->Amplitude.GetData()==1. && generator->PulseLength.GetData()==.001 &&
         generator->FrequencyDeviation.GetData()==0. && !generator->UseTransitSignal.GetData() &&
         !generator->UsePatternOutput.GetData(),"axone_burst_effective_generator_changed");
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"source"}};
    CheckRates(axon,request.frequency);CheckRates(dataset,request.frequency);
    const auto before=NmsdkTools::IdentifyModel(axon,ports);
    EXPECT_TRUE(before["valid"].toBool()) << QJsonDocument(before).toJson(QJsonDocument::Compact).toStdString();
    std::vector<UEPtr<NAxoneSegment>> segments;
    for(int i=1;i<=request.segments;++i){
        auto segment=axon->GetComponentL<NAxoneSegment>("Segment"+std::to_string(i),true);
        Need(bool(segment) && segment->GetTimeStep()==request.frequency,"axone_burst_segment_binding");segments.push_back(segment);
    }
    const unsigned endTick=request.frequency*(request.pattern=="span480"?3:1)/4;
    std::vector<double> sourceWave,axonWave;std::vector<std::vector<double>> segmentWaves(segments.size());
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"tick,time,source,axon";
    for(std::size_t i=0;i<segments.size();++i)csv<<",segment"<<i+1;csv<<'\n';
    bool complete=false;std::string error;std::exception_ptr failure;
    try {
        for(unsigned tick=0;tick<=endTick;++tick){
            model->Calculate();Need(!model->HasOperationFailureSince(marker),"axone_burst_calculate");
            const double time=environment->GetTime().GetDoubleTime();
            Need(std::abs(time-double(tick)/request.frequency)<=1e-12,"axone_burst_clock_grid");
            const double input=Scalar(generator->Output.GetData()),output=Scalar(axon->Output.GetData());
            sourceWave.push_back(input);axonWave.push_back(output);csv<<tick<<','<<time<<','<<input<<','<<output;
            for(std::size_t i=0;i<segments.size();++i){const double value=Scalar(segments[i]->Output.GetData());
                segmentWaves[i].push_back(value);csv<<','<<value;}
            csv<<'\n';environment->IncreaseModelTimeByStep();
        }
        complete=true;
    } catch(const std::exception& e){error=e.what();failure=std::current_exception();}
      catch(...){error="unknown native exception";failure=std::current_exception();}
    QJsonObject after;
    try {
        after=NmsdkTools::IdentifyModel(axon,ports);
        EXPECT_TRUE(after["valid"].toBool()) << QJsonDocument(after).toJson(QJsonDocument::Compact).toStdString();
        CheckRates(axon,request.frequency);CheckRates(dataset,request.frequency);
    } catch(const std::exception& e){error+="; readback: "+std::string(e.what());if(!failure)failure=std::current_exception();}
      catch(...){error+="; unknown readback exception";if(!failure)failure=std::current_exception();}
    const auto sourceEvents=ExtractAxonePulseEvents(sourceWave,.5),axonEvents=ExtractAxonePulseEvents(axonWave,.5);
    QJsonArray sourceIsi,nodeEvents;
    for(double value:request.isi)sourceIsi.append(value);
    for(std::size_t i=0;i<segments.size();++i){const auto events=ExtractAxonePulseEvents(segmentWaves[i],.5);
        nodeEvents.append(QJsonObject{{"segment",int(i+1)},{"events",Events(events)},
            {"assignment",Assignment(sourceEvents,events,request.frequency)}});}
    QJsonObject record{{"kind","axone_burst_diagnostic"},{"schema_version",1},{"id",QString::fromStdString(request.id)},
        {"carrier",QString::fromStdString(request.carrier)},{"frequency_hz",int(request.frequency)},
        {"segments",request.segments},{"pattern",QString::fromStdString(request.pattern)},{"source_isi_s",sourceIsi},
        {"expected_source_events",int(request.isi.size())},{"complete",complete},{"error",QString::fromStdString(error)},
        {"window_s",double(endTick)/request.frequency},{"source_events",Events(sourceEvents)},
        {"axon_events",Events(axonEvents)},{"segment_events",nodeEvents},
        {"assignment",Assignment(sourceEvents,axonEvents,request.frequency)},
        {"axon_identity_before",before},{"axon_identity_after",after},
        {"before_children_playback",dataset->WasPlaybackHandledBeforeChildren()},
        {"training",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)},
        {"assertion_scope","Complete finite capture, effective parameters and source; output conduction is measured."}};
    Save(request.id,".csv",QByteArray::fromStdString(csv.str()));Save(request.id,".json",QJsonDocument(record).toJson());
    if(failure)std::rethrow_exception(failure);
    EXPECT_TRUE(complete);EXPECT_EQ(sourceEvents.size(),request.isi.size());EXPECT_EQ(before,after);
    EXPECT_EQ(dataset->MatrixData.GetData(),pattern);EXPECT_TRUE(dataset->WasPlaybackHandledBeforeChildren());
}
std::vector<Request> Requests(){
    std::vector<Request> result;
    for(unsigned frequency:{20000u,40000u,100000u})for(const std::string carrier:{"NAxoneChain","NAxoneChainAndDelay"}){
        const auto add=[&](int length,const std::string& pattern,const std::vector<double>& isi){
            result.push_back({carrier+"_f"+std::to_string(frequency)+"_n"+std::to_string(length)+"_"+pattern,
                              carrier,pattern,frequency,length,isi});};
        for(int length:{1,3,7,15,31})add(length,"single",{.01});
        for(const auto& target:NmsdkTests::AxoneHistoricalTargets())if(target.spanMs==25 || target.spanMs==480)
            add(3,"span"+std::to_string(target.spanMs),std::vector<double>(target.isi.begin(),target.isi.end()));
        for(const auto& [count,interval]:std::vector<std::pair<int,double>>{{4,.002},{4,.005},{16,.002}}){
            std::vector<double> isi(count,interval);isi.front()=.01;
            add(3,"m"+std::to_string(count)+"_isi"+std::to_string(int(std::lround(interval*1000)))+"ms",isi);
        }
    }
    return result;
}
INSTANTIATE_TEST_SUITE_P(P1Stable,AxoneBurstDiagnostic,::testing::ValuesIn(Requests()),
    [](const ::testing::TestParamInfo<Request>& value){return value.param.id;});
}
