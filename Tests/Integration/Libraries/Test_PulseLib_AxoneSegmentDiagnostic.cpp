#include <gtest/gtest.h>
#include "NAxoneSegment.h"
#include "NAxoneChain.h"
#include "NAxoneChainAndDelay.h"
#include "NPulseGenerator.h"
#include "NPulseChannel.h"
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
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;

void Need(bool condition, const char* reason)
{ if(!condition) throw std::runtime_error(reason); }

double Scalar(const MDMatrix<double>& value)
{
    Need(value.GetSize()==1 && std::isfinite(value(0,0)), "axone_diagnostic_invalid_scalar");
    return value(0,0);
}

void Save(const std::string& stem, const char* suffix, const QByteArray& bytes)
{
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    if(!output) return;
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneSegmentDiagnostic");
    Need(QDir().mkpath(folder), "axone_diagnostic_output_directory");
    QFile file(QDir(folder).filePath(QString::fromStdString(stem)+suffix));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly), "axone_diagnostic_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(), "axone_diagnostic_output_write");
}

QJsonArray ChildOrder(const UEPtr<UContainer>& node)
{
    QJsonArray result;
    for(int index=0;index<node->GetNumComponents();++index) {
        auto child=node->GetComponentByIndex(index);
        result.append(QJsonObject{{"name",QString::fromStdString(child->GetName())},
            {"class",QString::fromStdString(child->GetCompClassName())},
            {"frequency_hz",int(child->GetTimeStep())},{"ready",child->IsReady()},
            {"initialized",child->IsInit()},{"children",ChildOrder(child)}});
    }
    return result;
}

struct Segment {
    UEPtr<NAxoneSegment> segment;
    UEPtr<NAperiodicLink> inertial;
    UEPtr<NPulseMembrane> soma;
    UEPtr<NLTZone> zone;
};

QJsonObject Channel(NPulseChannelCommon* value)
{
    Need(value!=nullptr, "axone_diagnostic_missing_channel");
    QJsonObject record{{"class",QString::fromStdString(value->GetCompClassName())},
        {"type",value->Type.GetData()},{"average_potential",value->UseAveragePotential.GetData()},
        {"average_synapses",value->UseAverageSynapsis.GetData()}};
    if(auto channel=dynamic_cast<NPulseChannel*>(value)) {
        record.insert("capacity",channel->Capacity.GetData());
        record.insert("resistance",channel->Resistance.GetData());
        record.insert("feedback_resistance",channel->FBResistance.GetData());
        record.insert("resting_resistance",channel->RestingResistance.GetData());
    }
    return record;
}

QJsonObject Parameters(const Segment& value)
{
    QJsonObject record{{"segment_class",QString::fromStdString(value.segment->GetCompClassName())},
        {"membrane_class",QString::fromStdString(value.soma->GetCompClassName())},
        {"ltzone_class",QString::fromStdString(value.zone->GetCompClassName())},
        {"threshold",value.zone->Threshold.GetData()},{"threshold_off",value.zone->ThresholdOff.GetData()},
        {"inertial_tau",value.inertial->Tau.GetData()},{"inertial_bias",value.inertial->Bias.GetData()},
        {"reset_available",value.soma->ResetAvailable.GetData()},{"feedback_gain",value.soma->FeedbackGain.GetData()},
        {"average_soma_potential",value.soma->UseAveragePotential.GetData()},
        {"exc_channel",Channel(value.soma->GetPosChannel(0))},
        {"inh_channel",Channel(value.soma->GetNegChannel(0))}};
    if(auto zone=dynamic_pointer_cast<NPulseLTZoneCommon>(value.zone)) {
        record.insert("ltzone_channels_in_group",zone->NumChannelsInGroup.GetData());
        record.insert("output_amplitude",zone->PulseAmplitude.GetData());
        record.insert("output_pulse_length",zone->PulseLength.GetData());
    }
    return record;
}

struct Request { std::string id,carrier; unsigned frequency; };

class AxoneSegmentDiagnostic: public ::testing::Test,
                              public ::testing::WithParamInterface<Request> {
protected:
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UNet> model;
    ULongTime originalTime=0;
    void SetUp() override {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);
        originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));
        model=dynamic_pointer_cast<UNet>(environment->GetModel());
        ASSERT_TRUE(model);
        environment->GetTime().SetTime(ULongTime(0));
    }
    void TearDown() override {
        if(model) model->BreakLinks();
        if(environment) {
            environment->DestroyModel();
            environment->GetTime().SetTime(originalTime);
        }
    }
    template<class T> UEPtr<T> Take(const std::string& image,const std::string& name) {
        auto node=dynamic_pointer_cast<T>(storage->TakeObject(image));
        Need(bool(node),"axone_diagnostic_factory");
        node->Name=name;node->SetEnvironment(environment);node->SetGlobalTimeStep(model->GetTimeStep());
        UEPtr<UContainer> base=node;
        Need(model->AddComponent(base)!=ForbiddenId,"axone_diagnostic_attach");
        return node;
    }
};

TEST_P(AxoneSegmentDiagnostic, CapturesUnchangedFactorySegmentDynamics)
{
    const auto& request=GetParam();
    model->SetGlobalTimeStep(request.frequency);
    auto source=Take<NPulseGenerator>("NPGenerator","Source");
    source->Frequency=10.;source->PulseLength=.001;source->Amplitude=1.;
    source->Delay=.01;source->FrequencyDeviation=0.;source->AvgInterval=1.;
    auto axon=Take<NAxoneCommon>(request.carrier,"Axon");
    if(auto chain=dynamic_pointer_cast<NAxoneChain>(axon)) chain->NumSegments=3;
    if(auto chain=dynamic_pointer_cast<NAxoneChainAndDelay>(axon)) {
        chain->NumNodes=3;chain->InternodeDelayTime=.002;
    }
    Need(model->CreateLink("Source","Output","Axon","Input"),"axone_diagnostic_source_link");
    const auto marker=model->OperationFailureSequence();
    model->Init();model->Reset();
    Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),
         "axone_diagnostic_init");
    std::vector<Segment> segments;
    const int count=request.carrier=="NAxoneSegment"?1:3;
    QJsonArray before;
    for(int index=0;index<count;++index) {
        auto segment=request.carrier=="NAxoneSegment"?dynamic_pointer_cast<NAxoneSegment>(axon):
            axon->GetComponentL<NAxoneSegment>("Segment"+std::to_string(index+1),true);
        Need(bool(segment),"axone_diagnostic_segment");
        Segment value{segment,segment->GetComponentL<NAperiodicLink>("Inertial",true),
            segment->GetComponentL<NPulseMembrane>("Soma",true),segment->GetComponentL<NLTZone>("LTZone",true)};
        Need(bool(value.inertial) && bool(value.soma) && bool(value.zone),"axone_diagnostic_children");
        before.append(Parameters(value));segments.push_back(value);
    }
    UEPtr<UContainer> modelBase=model;
    const auto order=ChildOrder(modelBase);
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17);
    csv<<"tick,time,source,axon";
    for(int index=0;index<count;++index)
        for(const char* field:{"input","inertial","exc_input","exc_output","inh_input","inh_output",
                              "soma","ltz_potential","ltz_output","segment_output","feedback"})
            csv<<",s"<<index+1<<"_"<<field;
    csv<<'\n';
    bool complete=false;
    std::exception_ptr failure;
    try {
        for(unsigned tick=0;tick<=request.frequency*8/100;++tick) {
            model->Calculate();
            Need(!model->HasOperationFailureSince(marker),"axone_diagnostic_calculate");
            const double time=environment->GetTime().GetDoubleTime();
            Need(std::abs(time-double(tick)/request.frequency)<=1e-12,"axone_diagnostic_grid");
            csv<<tick<<','<<time<<','<<Scalar(source->Output.GetData())<<','<<Scalar(axon->Output.GetData());
            for(const auto& value:segments) {
                auto* exc=value.soma->GetPosChannel(0);auto* inh=value.soma->GetNegChannel(0);
                csv<<','<<Scalar(value.segment->Input.GetData())<<','<<Scalar(value.inertial->Output.GetData())
                   <<','<<Scalar(exc->SumChannelInput.GetData())<<','<<Scalar(exc->Output.GetData())
                   <<','<<Scalar(inh->SumChannelInput.GetData())<<','<<Scalar(inh->Output.GetData())
                   <<','<<Scalar(value.soma->SumPotential.GetData())<<','<<value.zone->Potential.GetData()
                   <<','<<Scalar(value.zone->Output.GetData())<<','<<Scalar(value.segment->Output.GetData())
                   <<','<<Scalar(value.soma->InputFeedbackSignal.GetData());
                Need(std::isfinite(value.zone->Potential.GetData()),"axone_diagnostic_nonfinite_ltz");
            }
            csv<<'\n';environment->IncreaseModelTimeByStep();
        }
        complete=true;
    } catch(...) { failure=std::current_exception(); }
    QJsonArray after;
    for(const auto& value:segments) after.append(Parameters(value));
    QJsonArray emissions;
    const auto& emissionTimes=source->OutputPulseTimes.GetData();
    for(int index=0;index<emissionTimes.GetCols();++index) emissions.append(emissionTimes(0,index));
    const QJsonObject record{{"kind","axone_factory_segment_diagnostic"},{"schema_version",1},
        {"id",QString::fromStdString(request.id)},{"carrier",QString::fromStdString(request.carrier)},
        {"frequency_hz",int(request.frequency)},{"complete",complete},{"window_s",.08},
        {"source",QJsonObject{{"image","NPGenerator"},{"frequency_hz",10.},{"amplitude",1.},
                              {"pulse_length_s",.001},{"delay_s",.01},{"frequency_deviation",0.}}},
        {"parameters_before",before},{"parameters_after",after},{"native_child_order",order},
        {"actual_source_emission_times",emissions},
        {"training",false},{"parameter_intervention",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)},
        {"assertion_scope","Complete finite capture and unchanged parameters; output conduction is measured, not required."}};
    Save(request.id,".csv",QByteArray::fromStdString(csv.str()));
    Save(request.id,".json",QJsonDocument(record).toJson(QJsonDocument::Indented));
    if(failure) std::rethrow_exception(failure);
    EXPECT_TRUE(complete);
    EXPECT_EQ(before,after);
    EXPECT_EQ(emissions.size(),1);
}

std::vector<Request> Requests()
{
    std::vector<Request> result;
    for(unsigned frequency:{2000u,20000u,40000u})
        for(const std::string carrier:{"NAxoneSegment","NAxoneChain","NAxoneChainAndDelay"})
            result.push_back({carrier+"_f"+std::to_string(frequency),carrier,frequency});
    return result;
}
INSTANTIATE_TEST_SUITE_P(P1Diagnostic,AxoneSegmentDiagnostic,::testing::ValuesIn(Requests()),
    [](const ::testing::TestParamInfo<Request>& value){return value.param.id;});
} // namespace
