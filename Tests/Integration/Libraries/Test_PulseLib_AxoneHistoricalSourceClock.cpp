#include <gtest/gtest.h>
#include "NDatasetMatrix.h"
#include "NPulseGenerator.h"
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
#include <limits>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
void Need(bool value,const char* reason) { if(!value)throw std::runtime_error(reason); }
double Scalar(const MDMatrix<double>& value) {
    Need(value.GetSize()==1 && std::isfinite(value(0,0)),"axone_source_clock_invalid_scalar");
    return value(0,0);
}
void Save(const std::string& id,const char* suffix,const QByteArray& bytes) {
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    if(!output)return;
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneHistoricalSourceClock");
    Need(QDir().mkpath(folder),"axone_source_clock_output_directory");
    QFile file(QDir(folder).filePath(QString::fromStdString(id)+suffix));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"axone_source_clock_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(),"axone_source_clock_output_write");
}
struct Request { std::string id; unsigned frequency; NmsdkTests::AxoneHistoricalTarget target; };
class AxoneHistoricalSourceClock:public ::testing::Test,public ::testing::WithParamInterface<Request> {
protected:
    UEPtr<UEnvironment> environment;
    UEPtr<UStorage> storage;
    UEPtr<UNet> model;
    ULongTime originalTime=0;
    void SetUp()override {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);
        originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));
        model=dynamic_pointer_cast<UNet>(environment->GetModel());ASSERT_TRUE(model);
        environment->GetTime().SetTime(ULongTime(0));
    }
    void TearDown()override {
        if(model)model->BreakLinks();
        if(environment){environment->DestroyModel();environment->GetTime().SetTime(originalTime);}
    }
};
TEST_P(AxoneHistoricalSourceClock,CapturesActualTargetEventsAndGridDelays)
{
    const auto& request=GetParam();
    model->SetGlobalTimeStep(request.frequency);
    auto dataset=dynamic_pointer_cast<NDatasetMatrix>(storage->TakeObject("NDatasetMatrix"));
    ASSERT_TRUE(dataset);
    dataset->Name="Source";
    dataset->SetEnvironment(environment);dataset->SetGlobalTimeStep(request.frequency);
    dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=4;
    dataset->PulseGeneratorClassName="NPulseGeneratorTransit";
    MDMatrix<double> pattern;pattern.Assign(4,1,0.);
    for(int index=0;index<4;++index)pattern(index,0)=request.target.isi[index];
    MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MatrixData=pattern;dataset->MatrixClasses=labels;dataset->Iteration=0;
    dataset->Delay=2.;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=false;
    dataset->StateGeneration=1;dataset->TimeGeneration=1.;
    UEPtr<UContainer> base=dataset;
    Need(model->AddComponent(base)!=ForbiddenId,"axone_source_clock_attach");
    const auto marker=model->OperationFailureSequence();
    model->Init();
    Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),
         "axone_source_clock_init");
    auto generator=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Need(bool(generator),"axone_source_clock_missing_generator");
    generator->Amplitude=1.;generator->PulseLength=.001;generator->FrequencyDeviation=0.;
    generator->UseTransitSignal=false;generator->UsePatternOutput=false;
    model->Reset();
    Need(!model->HasOperationFailureSince(marker) && dataset->MatrixData.GetData()==pattern &&
         generator->GetTimeStep()==request.frequency && dataset->GetTimeStep()==request.frequency,
         "axone_source_clock_effective_configuration");
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"tick,time,source\n";
    std::vector<unsigned> onsets;bool high=false,complete=false;
    std::exception_ptr failure;
    try {
        for(unsigned tick=0;tick<=request.frequency*11/10;++tick) {
            model->Calculate();
            Need(!model->HasOperationFailureSince(marker),"axone_source_clock_calculate");
            const double time=environment->GetTime().GetDoubleTime();
            Need(std::abs(time-double(tick)/request.frequency)<=1e-12,"axone_source_clock_grid");
            const double value=Scalar(generator->Output.GetData());
            if(value>.5 && !high)onsets.push_back(tick);
            high=value>.5;
            csv<<tick<<','<<time<<','<<value<<'\n';
            environment->IncreaseModelTimeByStep();
        }
        complete=true;
    }catch(...){failure=std::current_exception();}
    QJsonArray actual,isi,delays;
    for(auto tick:onsets)actual.append(QJsonObject{{"tick",int(tick)},{"time_s",double(tick)/request.frequency}});
    for(double value:request.target.isi)isi.append(value);
    if(complete && onsets.size()==4) {
        const unsigned target=onsets.back()+request.frequency/1000;
        for(auto tick:onsets) {
            const unsigned desired=target-tick;
            // An upward representable parameter avoids a one-tick truncation
            // when the exact rational tick duration rounds down in binary.
            const double seconds=std::nextafter(double(desired)/request.frequency,
                                                std::numeric_limits<double>::infinity());
            Need(desired>0 && std::isfinite(seconds) &&
                 std::floor(seconds*request.frequency)==desired,"axone_source_clock_delay_parameter");
            delays.append(QJsonObject{{"input_tick",int(tick)},{"target_tick",int(target)},
                {"desired_delay_ticks",int(desired)},{"configured_delay_s",seconds}});
        }
    }
    const QJsonObject record{{"kind","axone_historical_source_clock_observation"},{"schema_version",1},
        {"id",QString::fromStdString(request.id)},{"span_ms",request.target.spanMs},
        {"frequency_hz",int(request.frequency)},{"complete",complete},{"window_s",1.1},
        {"dataset_class",QString::fromStdString(dataset->GetCompClassName())},
        {"generator_class",QString::fromStdString(generator->GetCompClassName())},
        {"before_children_playback",dataset->WasPlaybackHandledBeforeChildren()},
        {"historical_recipe_canonical_lf_sha256",QString::fromStdString(request.target.recipeSha256)},
        {"initial_isi_s",isi},{"actual_source_events",actual},{"proposed_ideal_delays",delays},
        {"training",false},{"receiver_present",false},{"delays_physically_executed",false},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    Save(request.id,".csv",QByteArray::fromStdString(csv.str()));
    Save(request.id,".json",QJsonDocument(record).toJson(QJsonDocument::Indented));
    if(failure)std::rethrow_exception(failure);
    EXPECT_TRUE(complete);EXPECT_EQ(onsets.size(),4u);EXPECT_EQ(delays.size(),4);
    EXPECT_TRUE(dataset->WasPlaybackHandledBeforeChildren());
    EXPECT_EQ(dataset->MatrixData.GetData(),pattern);
}
std::vector<Request> Requests() {
    std::vector<Request> result;
    for(unsigned frequency:{2000u,20000u,40000u})
        for(const auto& target:NmsdkTests::AxoneHistoricalTargets())
            result.push_back({"span"+std::to_string(target.spanMs)+"_f"+std::to_string(frequency),frequency,target});
    return result;
}
INSTANTIATE_TEST_SUITE_P(P2Source,AxoneHistoricalSourceClock,::testing::ValuesIn(Requests()),
    [](const ::testing::TestParamInfo<Request>& value){return value.param.id;});
}
