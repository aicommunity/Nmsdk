#include <gtest/gtest.h>
#include "NAxoneDelay.h"
#include "NDatasetMatrix.h"
#include "NPulseGenerator.h"
#include "TimeLearner/AxoneConductionObservation.h"
#include "TimeLearner/StrictNativeJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <array>
#include <cmath>
#include <cstdlib>
#include <exception>
#include <filesystem>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Need(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
unsigned Integer(const QJsonValue& value){
    Need(value.isDouble() && std::isfinite(value.toDouble()) && value.toDouble()>=0 &&
         value.toDouble()<=10000000 && std::floor(value.toDouble())==value.toDouble(),"manual_sync_integer");
    return unsigned(value.toDouble());
}
double Scalar(const MDMatrix<double>& value){
    Need(value.GetSize()==1 && std::isfinite(value(0,0)),"manual_sync_invalid_scalar");return value(0,0);
}
QJsonArray Events(const std::vector<AxonePulseEvent>& events){
    QJsonArray result;for(const auto& event:events)result.append(QJsonObject{{"onset_tick",int(event.onsetTick)},
        {"end_tick",int(event.endTick)},{"peak",event.peak},{"right_censored",event.rightCensored}});return result;
}
void Save(const std::string& id,const char* suffix,const QByteArray& bytes){
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");if(!output)return;
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneManualSynchronization");
    Need(QDir().mkpath(folder),"manual_sync_output_directory");
    QFile file(QDir(folder).filePath(QString::fromStdString(id)+suffix));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"manual_sync_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(),"manual_sync_output_write");
}
struct Request{std::string id;unsigned frequency;int span;};
class AxoneManualSynchronization:public ::testing::Test,public ::testing::WithParamInterface<Request>{
protected:
    UEPtr<UEnvironment> environment;UEPtr<UStorage> storage;UEPtr<UNet> model;ULongTime originalTime=0;
    void SetUp()override{
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));model=dynamic_pointer_cast<UNet>(environment->GetModel());
        ASSERT_TRUE(model);environment->GetTime().SetTime(ULongTime(0));
    }
    void TearDown()override{
        if(model)model->BreakLinks();if(environment){environment->DestroyModel();environment->GetTime().SetTime(originalTime);}
    }
    template<class T> UEPtr<T> Take(const std::string& image,const std::string& name){
        auto node=dynamic_pointer_cast<T>(storage->TakeObject(image));Need(bool(node),"manual_sync_factory");
        node->Name=name;node->SetEnvironment(environment);node->SetGlobalTimeStep(model->GetTimeStep());
        UEPtr<UContainer> base=node;Need(model->AddComponent(base)!=ForbiddenId,"manual_sync_attach");return node;
    }
};
TEST_P(AxoneManualSynchronization,PhysicallyShiftsEverySpikeAndAlignsSelectedEvents)
{
    const auto& request=GetParam();
    const auto root=std::filesystem::path(__FILE__).parent_path().parent_path().parent_path().parent_path();
    Need(root.is_absolute(),"manual_sync_absolute_compiled_source_required");
    const auto path=root/"Bin/Configs/SpikeSamples/StructTrain/AxoneTimeLearner/P2/manual-delay-calibrated-v1"/(request.id+".json");
    QFile file(QString::fromStdString(path.string()));Need(file.open(QIODevice::ReadOnly),"manual_sync_input_unavailable");
    const auto payload=file.readAll();const auto config=ParseStrictNativeJsonObject(payload.toStdString(),65536);
    Need(config["kind"]==QJsonValue("axone_manual_delay_condition") && Integer(config["schema_version"])==1 &&
         config["id"]==QJsonValue(QString::fromStdString(request.id)) && Integer(config["frequency_hz"])==request.frequency &&
         Integer(config["nominal_span_ms"])==unsigned(request.span) && config["carrier"]==QJsonValue("NAxoneDelay") &&
         config["training"]==QJsonValue(false) && config["receiver_present"]==QJsonValue(false) &&
         config["window_s"]==QJsonValue(1.1),"manual_sync_input_identity");
    const auto sourceConfig=config["source"].toObject();const auto isi=config["source_isi_s"].toArray();
    const auto expectedTicks=config["calibrated_source_ticks"].toArray();const auto settings=config["ideal_delay_paths"].toArray();
    const unsigned targetTick=Integer(config["selected_arrival_tick"]);
    Need(isi.size()==4 && expectedTicks.size()==4 && settings.size()==4 &&
         sourceConfig["dataset_class"]==QJsonValue("NDatasetMatrix") &&
         sourceConfig["generator_class"]==QJsonValue("NPulseGeneratorTransit") &&
         Integer(sourceConfig["NumSamples"])==1 && Integer(sourceConfig["NumFeatures"])==1 &&
         Integer(sourceConfig["MaxSpikesPerFeature"])==4 && Integer(sourceConfig["StateGeneration"])==1 &&
         sourceConfig["AdvanceSampleAfterBurst"]==QJsonValue(false) && sourceConfig["LoopSamples"]==QJsonValue(false),
         "manual_sync_source_contract");
    model->SetGlobalTimeStep(request.frequency);
    auto dataset=Take<NDatasetMatrix>("NDatasetMatrix","Source");
    dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=4;
    dataset->PulseGeneratorClassName="NPulseGeneratorTransit";
    MDMatrix<double> pattern;pattern.Assign(4,1,0.);for(int i=0;i<4;++i)pattern(i,0)=isi[i].toDouble();
    MDMatrix<int> labels;labels.Assign(1,1,1);dataset->MatrixData=pattern;dataset->MatrixClasses=labels;
    dataset->Iteration=0;dataset->Delay=sourceConfig["Delay_s"].toDouble();dataset->AdvanceSampleAfterBurst=false;
    dataset->LoopSamples=false;dataset->StateGeneration=1;dataset->TimeGeneration=sourceConfig["TimeGeneration_s"].toDouble();
    dataset->Build();
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);Need(bool(generator),"manual_sync_generator");
    generator->Amplitude=sourceConfig["amplitude"].toDouble();generator->PulseLength=sourceConfig["pulse_width_s"].toDouble();
    generator->FrequencyDeviation=sourceConfig["frequency_deviation"].toDouble();
    generator->UseTransitSignal=false;generator->UsePatternOutput=false;
    std::array<UEPtr<NAxoneDelay>,4> paths;std::array<unsigned,4> delayTicks{};
    for(int i=0;i<4;++i){
        const auto setting=settings[i].toObject();const auto name="Path"+std::to_string(i+1);
        delayTicks[i]=Integer(setting["desired_delay_ticks"]);const double parameter=setting["configured_delay_s"].toDouble();
        Need(delayTicks[i]>0 && std::isfinite(parameter) && std::floor(parameter*request.frequency)==delayTicks[i] &&
             Integer(setting["input_tick"])==Integer(expectedTicks[i]) && Integer(setting["target_tick"])==targetTick &&
             Integer(expectedTicks[i])+delayTicks[i]==targetTick,"manual_sync_delay_contract");
        paths[i]=Take<NAxoneDelay>("NAxoneDelay",name);paths[i]->DelayTime=parameter;
        Need(model->CreateLink("Source.Generator1","Output",name,"Input"),"manual_sync_source_link");
    }
    const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
    Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),"manual_sync_initialization");
    Need(generator==dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true),"manual_sync_generator_replaced");
    Need(generator->GetTimeStep()==request.frequency && dataset->GetTimeStep()==request.frequency &&
         generator->Amplitude.GetData()==sourceConfig["amplitude"].toDouble() &&
         generator->PulseLength.GetData()==sourceConfig["pulse_width_s"].toDouble() &&
         generator->FrequencyDeviation.GetData()==sourceConfig["frequency_deviation"].toDouble() &&
         !generator->UseTransitSignal.GetData() && !generator->UsePatternOutput.GetData(),"manual_sync_effective_source");
    std::vector<double> input;std::array<std::vector<double>,4> outputs;
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"tick,time,source,path1,path2,path3,path4\n";
    bool complete=false;std::exception_ptr failure;
    try{
        for(unsigned tick=0;tick<=request.frequency*11/10;++tick){
            model->Calculate();Need(!model->HasOperationFailureSince(marker),"manual_sync_calculate");
            const double time=environment->GetTime().GetDoubleTime();
            Need(std::abs(time-double(tick)/request.frequency)<=1e-12,"manual_sync_clock_grid");
            const double value=Scalar(generator->Output.GetData());input.push_back(value);csv<<tick<<','<<time<<','<<value;
            for(int i=0;i<4;++i){const double output=Scalar(paths[i]->Output.GetData());outputs[i].push_back(output);csv<<','<<output;}
            csv<<'\n';environment->IncreaseModelTimeByStep();
        }
        complete=true;
    }catch(...){failure=std::current_exception();}
    const auto inputEvents=ExtractAxonePulseEvents(input,.5);QJsonArray pathRecords;
    for(int i=0;i<4;++i){const auto events=ExtractAxonePulseEvents(outputs[i],.5);
        pathRecords.append(QJsonObject{{"path",i+1},{"delay_ticks",int(delayTicks[i])},
            {"effective_delay_s",paths[i]->DelayTime.GetData()},{"frequency_hz",int(paths[i]->GetTimeStep())},
            {"events",Events(events)}});
        EXPECT_EQ(events.size(),4u);EXPECT_EQ(paths[i]->GetTimeStep(),request.frequency);
        EXPECT_DOUBLE_EQ(paths[i]->DelayTime.GetData(),settings[i].toObject()["configured_delay_s"].toDouble());
        if(inputEvents.size()==4 && events.size()==4)for(int j=0;j<4;++j){
            EXPECT_EQ(events[j].onsetTick,inputEvents[j].onsetTick+delayTicks[i]);
            EXPECT_EQ(events[j].endTick,inputEvents[j].endTick+delayTicks[i]);
            EXPECT_FALSE(events[j].rightCensored);
        }
        if(events.size()==4)EXPECT_EQ(events[i].onsetTick,targetTick);
    }
    const QJsonObject record{{"kind","axone_manual_synchronization_observation"},{"schema_version",1},
        {"id",QString::fromStdString(request.id)},{"frequency_hz",int(request.frequency)},{"complete",complete},
        {"window_s",1.1},{"config_sha256",QString::fromLatin1(QCryptographicHash::hash(payload,QCryptographicHash::Sha256).toHex())},
        {"source_config",config},{"source_events",Events(inputEvents)},{"paths",pathRecords},
        {"selected_target_tick",int(targetTick)},{"training",false},{"receiver_present",false},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    Save(request.id,".csv",QByteArray::fromStdString(csv.str()));Save(request.id,".json",QJsonDocument(record).toJson());
    if(failure)std::rethrow_exception(failure);
    EXPECT_TRUE(complete);ASSERT_EQ(inputEvents.size(),4u);
    for(int i=0;i<4;++i)EXPECT_EQ(inputEvents[i].onsetTick,Integer(expectedTicks[i]));
    EXPECT_TRUE(dataset->WasPlaybackHandledBeforeChildren());EXPECT_EQ(dataset->MatrixData.GetData(),pattern);
}
std::vector<Request> Requests(){std::vector<Request> result;
    for(unsigned frequency:{2000u,20000u,40000u})for(int span:{25,50,100,200,480})
        result.push_back({"span"+std::to_string(span)+"_f"+std::to_string(frequency),frequency,span});return result;}
INSTANTIATE_TEST_SUITE_P(P2Manual,AxoneManualSynchronization,::testing::ValuesIn(Requests()),
    [](const ::testing::TestParamInfo<Request>& value){return value.param.id;});
}
