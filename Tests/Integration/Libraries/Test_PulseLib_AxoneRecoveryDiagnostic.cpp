#include <gtest/gtest.h>
#include "NAxoneSegment.h"
#include "NAperiodicLink.h"
#include "NDatasetMatrix.h"
#include "NPulseGenerator.h"
#include "NPulseLTZone.h"
#include "NPulseMembrane.h"
#include "NPulseChannel.h"
#include "TimeLearner/AxoneConductionObservation.h"
#include "TimeLearner/ModelIdentity.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <array>
#include <cmath>
#include <cstdlib>
#include <exception>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>

namespace {
using namespace RDK;using namespace NMSDK;using namespace NMSDK::TimeLearner;
void Need(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
double Scalar(const MDMatrix<double>& value){Need(value.GetSize()==1 && std::isfinite(value(0,0)),"recovery_nonfinite_or_nonscalar_signal");return value(0,0);}
QJsonArray Events(const std::vector<AxonePulseEvent>& values){QJsonArray result;
    for(const auto& event:values)result.append(QJsonObject{{"onset_tick",int(event.onsetTick)},{"end_tick",int(event.endTick)},
        {"peak",event.peak},{"right_censored",event.rightCensored}});return result;}
QJsonObject Association(const AxoneConductionAssignment& match,unsigned frequency){
    QJsonArray pairs,possibleInputs,possibleOutputs,inputUnmatched,outputUnmatched;
    for(const auto& pair:match.certainPairs)pairs.append(QJsonObject{{"input",int(pair.input)},{"output",int(pair.output)},{"lag_ticks",int(pair.lagTicks)}});
    for(const auto& candidates:match.possibleInputs){QJsonArray values;for(auto value:candidates)values.append(int(value));possibleInputs.append(values);}
    for(const auto& candidates:match.possibleOutputs){QJsonArray values;for(auto value:candidates)values.append(int(value));possibleOutputs.append(values);}
    for(bool value:match.inputCanBeUnmatched)inputUnmatched.append(value);for(bool value:match.outputCanBeUnmatched)outputUnmatched.append(value);
    return {{"complete_one_to_one",match.completeOneToOne},{"ambiguous",match.ambiguous},{"maximum_matched",int(match.maximumMatched)},
        {"certain_pairs",pairs},{"possible_inputs",possibleInputs},{"possible_outputs",possibleOutputs},
        {"input_can_be_unmatched",inputUnmatched},{"output_can_be_unmatched",outputUnmatched},
        {"minimum_lag_ticks",0},{"maximum_lag_ticks",int(frequency/5)}};
}
void Save(const std::string& name,const QByteArray& bytes){
    const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");if(!output)return;
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneRecoveryDiagnostic");
    Need(QDir().mkpath(folder),"recovery_output_directory");QFile file(QDir(folder).filePath(QString::fromStdString(name)));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"recovery_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(),"recovery_output_write");
}
struct Request{std::string id;unsigned frequency;int capacityIndex,tauIndex,gapMs;};
class AxoneRecoveryDiagnostic:public ::testing::Test,public ::testing::WithParamInterface<Request>{
protected:
    UEPtr<UStorage> storage;UEPtr<UEnvironment> environment;UEPtr<UNet> model;ULongTime originalTime=0;
    void SetUp()override{
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);ASSERT_TRUE(environment->CreateModel("NModel"));
        model=dynamic_pointer_cast<UNet>(environment->GetModel());ASSERT_TRUE(model);environment->GetTime().SetTime(0);
    }
    void TearDown()override{if(model)model->BreakLinks();if(environment){environment->DestroyModel();environment->GetTime().SetTime(originalTime);}}
    template<class T> UEPtr<T> Take(const char* image,const char* name){
        auto node=dynamic_pointer_cast<T>(storage->TakeObject(image));Need(bool(node),"recovery_factory");
        node->Name=name;node->SetEnvironment(environment);node->SetGlobalTimeStep(model->GetTimeStep());
        UEPtr<UContainer> base=node;Need(model->AddComponent(base)!=ForbiddenId,"recovery_attach");return node;
    }
};
TEST_P(AxoneRecoveryDiagnostic,CapturesMatchedPairAndOmissionControls){
    const auto& request=GetParam();model->SetGlobalTimeStep(request.frequency);
    const std::array<double,3> capacities{1e-9,2.5e-10,2.5e-11};
    const std::array<double,2> timeConstants{.00144,.00036};
    const double capacity=capacities.at(request.capacityIndex),tau=timeConstants.at(request.tauIndex),gap=request.gapMs/1000.;
    auto dataset=Take<NDatasetMatrix>("NDatasetMatrix","Source");
    dataset->NumSamples=1;dataset->NumFeatures=1;dataset->MaxSpikesPerFeature=2;dataset->PulseGeneratorClassName="NPulseGeneratorTransit";
    MDMatrix<double> pattern;pattern.Assign(2,1,0.);MDMatrix<int> labels;labels.Assign(1,1,1);
    dataset->MatrixData=pattern;dataset->MatrixClasses=labels;dataset->Iteration=0;dataset->StateGeneration=1;
    dataset->TimeGeneration=1.;dataset->Delay=2.;dataset->AdvanceSampleAfterBurst=false;dataset->LoopSamples=false;dataset->Build();
    auto source=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);Need(bool(source),"recovery_generator");
    source->Amplitude=1.;source->PulseLength=.001;source->FrequencyDeviation=0.;source->UseTransitSignal=false;source->UsePatternOutput=false;
    auto prototype=dynamic_pointer_cast<NPulseLTZone>(storage->TakeObject("NPLTZone"));Need(bool(prototype),"recovery_ltz_factory");
    prototype->SetEnvironment(environment);prototype->SetGlobalTimeStep(request.frequency);
    prototype->UseLTZIntegtation=true;prototype->UseSpikeStabilizer=true;prototype->TimeConstant=tau;
    prototype->Threshold=.02;prototype->ThresholdOff=0.;prototype->PulseAmplitude=1.;prototype->Init();prototype->Reset();
    const auto image="AxoneRecoveryStable_f"+std::to_string(request.frequency)+"_tau"+std::to_string(request.tauIndex);
    UEPtr<UContainer> prototypeBase=prototype;RegisterClassImage(storage,image,prototypeBase);storage->ReturnObject(prototype);
    auto axon=Take<NAxoneSegment>("NAxoneSegment","Axon");axon->LTZoneClassName=image;axon->Build();
    auto soma=axon->GetComponentL<NPulseMembrane>("Soma",true);
    auto zone=axon->GetComponentL<NPulseLTZone>("LTZone",true);auto inertial=axon->GetComponentL<NAperiodicLink>("Inertial",true);
    Need(soma && zone && inertial,"recovery_children");
    auto exc=dynamic_cast<NPulseChannel*>(soma->GetPosChannel(0));auto inh=dynamic_cast<NPulseChannel*>(soma->GetNegChannel(0));
    Need(exc && inh,"recovery_channel_types");exc->Capacity=capacity;inh->Capacity=capacity;
    Need(model->CreateLink("Source.Generator1","Output","Axon","Input"),"recovery_source_link");
    const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
    Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),"recovery_initialization");
    Need(exc->Capacity.GetData()==capacity && inh->Capacity.GetData()==capacity && zone->TimeConstant.GetData()==tau &&
         zone->UseLTZIntegtation.GetData() && zone->UseSpikeStabilizer.GetData() && zone->Threshold.GetData()==.02 &&
         zone->ThresholdOff.GetData()==0.,"recovery_effective_profile");
    const NmsdkTools::ModelBoundarySources ports{{&source->Output,"source"}};
    const auto identity=NmsdkTools::IdentifyModel(axon,ports);Need(identity["valid"].toBool(),"recovery_invalid_axon_identity");
    QJsonArray phases;
    for(const std::string phase:{"silent","first_only","second_only","pair"}){
        pattern.Assign(2,1,0.);if(phase=="first_only" || phase=="pair")pattern(0,0)=.01;
        if(phase=="second_only")pattern(0,0)=.01+gap;if(phase=="pair")pattern(1,0)=gap;
        dataset->MatrixData=pattern;dataset->Build();
        Need(source==dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true),"recovery_source_identity_replaced");
        environment->GetTime().SetTime(0);model->Reset();
        Need(source->Amplitude.GetData()==1. && source->PulseLength.GetData()==.001 && source->FrequencyDeviation.GetData()==0. &&
             !source->UseTransitSignal.GetData() && !source->UsePatternOutput.GetData(),"recovery_source_profile_changed");
        Need(NmsdkTools::IdentifyModel(axon,ports)==identity,"recovery_profile_changed_before_capture");
        const unsigned endTick=request.frequency/4;
        std::vector<double> inputs,outputs;std::ostringstream csv;csv.imbue(std::locale::classic());
        csv<<std::setprecision(17)<<"tick,time,source,inertial,exc_channel,inh_channel,soma_sum,lt_input,lt_pre,lt_potential,output,feedback,exc_tau,inh_tau\n";
        bool complete=false;std::string reason;std::exception_ptr failure;
        try{
            for(unsigned tick=0;tick<=endTick;++tick){
                model->Calculate();Need(!model->HasOperationFailureSince(marker),"recovery_calculate_failure");
                const double time=environment->GetTime().GetDoubleTime();Need(std::abs(time-double(tick)/request.frequency)<=1e-12,"recovery_clock_grid");
                const double input=Scalar(source->Output.GetData()),output=Scalar(axon->Output.GetData());
                const std::array<double,11> values{Scalar(inertial->Output.GetData()),Scalar(exc->Output.GetData()),Scalar(inh->Output.GetData()),
                    Scalar(soma->SumPotential.GetData()),zone->GetNeuralPotential(),zone->PrePotential.GetData(),zone->Potential.GetData(),
                    output,Scalar(soma->InputFeedbackSignal.GetData()),exc->TimeConstant.GetData(),inh->TimeConstant.GetData()};
                inputs.push_back(input);outputs.push_back(output);csv<<tick<<','<<time<<','<<input;
                for(double value:values){Need(std::isfinite(value),"recovery_nonfinite_state");csv<<','<<value;}csv<<'\n';
                environment->IncreaseModelTimeByStep();
            }
            complete=true;
        }catch(const std::exception& error){reason=error.what();failure=std::current_exception();}
        catch(...){reason="unknown_native_exception";failure=std::current_exception();}
        const auto sourceEvents=ExtractAxonePulseEvents(inputs,.5),outputEvents=ExtractAxonePulseEvents(outputs,.5);
        const auto after=NmsdkTools::IdentifyModel(axon,ports);
        // The shared assignment contract requires a real input event. A
        // silent control measures spontaneous output and has no input pairing.
        QJsonValue association(QJsonValue::Null);
        if(!sourceEvents.empty())association=Association(AssignAxoneConductionEvents(sourceEvents,outputEvents,0,request.frequency/5),request.frequency);
        const int expected=phase=="silent"?0:(phase=="pair"?2:1);
        const QJsonObject row{{"phase",QString::fromStdString(phase)},{"complete",complete},{"error",QString::fromStdString(reason)},
            {"expected_source_events",expected},{"source_events",Events(sourceEvents)},{"output_events",Events(outputEvents)},
            {"axon_identity_after",after},{"temporal_association",association},
            {"association_status",sourceEvents.empty()?"not_assessed_without_input_events":"assessed"}};
        phases.append(row);Save(request.id+"_"+phase+".csv",QByteArray::fromStdString(csv.str()));
        Save(request.id+"_"+phase+".json",QJsonDocument(row).toJson());
        EXPECT_TRUE(complete);EXPECT_EQ(after,identity);EXPECT_EQ(sourceEvents.size(),std::size_t(expected));
        if(!sourceEvents.empty()){
            const double nominal=phase=="second_only"?.01+gap:.01;
            EXPECT_LE(std::abs(double(sourceEvents.front().onsetTick)/request.frequency-nominal),2./request.frequency);
            if(phase=="pair" && sourceEvents.size()==2)
                EXPECT_LE(std::abs(double(sourceEvents[1].onsetTick-sourceEvents[0].onsetTick)/request.frequency-gap),2./request.frequency);
        }
        if(failure)std::rethrow_exception(failure);
    }
    const QJsonObject result{{"kind","axone_recovery_diagnostic"},{"schema_version",1},{"id",QString::fromStdString(request.id)},
        {"frequency_hz",int(request.frequency)},{"gap_ms",request.gapMs},{"capacity_f",capacity},{"lt_time_constant_s",tau},
        {"window_s",.25},{"axon_identity_before",identity},{"phases",phases},{"training",false},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    Save(request.id+".json",QJsonDocument(result).toJson());
}
std::vector<Request> Requests(){std::vector<Request> result;
    for(unsigned f:{20000u,40000u})for(int c:{0,1,2})for(int t:{0,1})for(int gap:{2,4,8,16,32,80})
        result.push_back({"f"+std::to_string(f)+"_c"+std::to_string(c)+"_t"+std::to_string(t)+"_gap"+std::to_string(gap),f,c,t,gap});return result;}
INSTANTIATE_TEST_SUITE_P(P1Recovery,AxoneRecoveryDiagnostic,::testing::ValuesIn(Requests()),
    [](const ::testing::TestParamInfo<Request>& value){return value.param.id;});
}
