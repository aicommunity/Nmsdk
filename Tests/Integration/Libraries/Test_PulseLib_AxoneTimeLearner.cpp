#include <gtest/gtest.h>
#include "NNeuronAxoneTimeLearner.h"
#include "NAxoneTreeChain.h"
#include "NAxoneDelay.h"
#include "NPulseLTZone.h"
#include "NPulseNeuron.h"
#include "NPulseSynapseCommon.h"
#include "NPulseGenerator.h"
#include "NDatasetMatrix.h"
#include "TimeLearner/NativeModelBuilder.h"
#include "TimeLearner/StorageProfiles.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Need(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
void Save(const std::string& name,const QByteArray& bytes){
    const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");if(!output)return;
    const auto* info=::testing::UnitTest::GetInstance()->current_test_info();
    const auto folder=QDir(QString::fromLocal8Bit(output)).filePath("AxoneTimeLearner/"+QString::fromLatin1(info->name()));
    Need(QDir().mkpath(folder),"axon_trainer_output_directory");
    QFile file(QDir(folder).filePath(QString::fromStdString(name)));
    Need(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"axon_trainer_output_exists");
    Need(file.write(bytes)==bytes.size() && file.flush(),"axon_trainer_output_write");
}
class AxoneTimeLearner:public ::testing::Test {
protected:
    UEPtr<UEnvironment> environment;UEPtr<UStorage> storage;UEPtr<UNet> model;
    UEPtr<NPulseNeuron> neuron;UEPtr<NDatasetMatrix> dataset;UEPtr<NPulseGeneratorTransit> source;
    UEPtr<NAxoneTreeChain> tree;UEPtr<NNeuronAxoneTimeLearner> trainer;
    ULongTime originalTime=0;
    void SetUp()override{
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        ASSERT_TRUE(storage);ASSERT_TRUE(environment);originalTime=environment->GetTime().GetTime();
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));model=dynamic_pointer_cast<UNet>(environment->GetModel());
        ASSERT_TRUE(model);model->SetGlobalTimeStep(2000);environment->GetTime().SetTime(0);
    }
    void TearDown()override{
        if(trainer)trainer->CancelSession("fixture_teardown");
        if(model)model->BreakLinks();if(environment){environment->DestroyModel();environment->GetTime().SetTime(originalTime);}
    }
    template<class T> UEPtr<T> Take(const char* image,const char* name){
        auto result=dynamic_pointer_cast<T>(storage->TakeObject(image));Need(bool(result),"axon_trainer_factory");
        result->Name=name;result->SetEnvironment(environment);result->SetGlobalTimeStep(2000);
        UEPtr<UContainer> base=result;Need(model->AddComponent(base)!=ForbiddenId,"axon_trainer_attach");return result;
    }
    void Physical(){
        const auto* info=::testing::UnitTest::GetInstance()->current_test_info();const std::string suffix=info->name();
        StorageProfileSpec profile;profile.name="AxonDiagnostic_"+suffix;profile.neuronBaseClass="NSPNeuronGen";
        profile.frequencyHz=2000;profile.initialThreshold=.0117;
        const auto images=RegisterStorageProfile(storage,environment,profile);
        NativeModelSpec specification;specification.frequencyHz=2000;specification.neuronClass=images.neuronClass;
        specification.inputs={{1,1,{}},{1,1,{}}};specification.initialIsi={.01,.08};
        specification.allocatedCableLengths={1,1};specification.editPolicy.maximumCableLength=1;
        const auto built=ConstructNativeLearnerModel(*model,specification);
        Need(built.status==NativeModelBuildStatus::Constructed,built.reason.c_str());
        neuron=model->GetComponentL<NPulseNeuron>("Neuron",true);dataset=model->GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        source=dataset->GetComponentL<NPulseGeneratorTransit>("Generator1",true);Need(neuron && dataset && source,"axon_trainer_physics");
        dataset->StateGeneration=1;dataset->TimeGeneration=1.;dataset->Delay=2.;dataset->LoopSamples=false;
        source->Amplitude=1.;source->PulseLength=.001;source->FrequencyDeviation=0.;
        source->UseTransitSignal=false;source->UsePatternOutput=false;
        auto prototype=dynamic_pointer_cast<NPulseLTZone>(storage->TakeObject("NPLTZone"));Need(bool(prototype),"axon_trainer_ltzone");
        prototype->SetEnvironment(environment);prototype->SetGlobalTimeStep(2000);
        prototype->Threshold=.02;prototype->ThresholdOff=0.;prototype->UseSpikeStabilizer=true;
        prototype->UseLTZIntegtation=true;prototype->TimeConstant=.00144;prototype->PulseAmplitude=1.;prototype->Init();prototype->Reset();
        const auto image="AxonDiagnosticStable_"+suffix;UEPtr<UContainer> base=prototype;
        RegisterClassImage(storage,image,base);storage->ReturnObject(prototype);
        tree=Take<NAxoneTreeChain>("NAxoneTreeChain","Axon");
        tree->Topology=R"({"schema_version":1,"sections":[{"id":"Stem","parent":"","attach_segment":0,"carrier":"NAxoneChain","segments":1},{"id":"First","parent":"Stem","attach_segment":1,"carrier":"NAxoneChainAndDelay","segments":3,"internode_delay_s":0.002},{"id":"Last","parent":"Stem","attach_segment":1,"carrier":"NAxoneChainAndDelay","segments":3,"internode_delay_s":0.002}],"ports":{"first":"First","last":"Last"},"output_port":"last"})";
        tree->Build();
        auto stem=tree->GetComponentL<NAxoneChain>("Stem",true);Need(bool(stem),"axon_trainer_stem");
        stem->LTZoneClassName=image;stem->Build();
        for(const auto& port:{"first","last"}){
            auto path=dynamic_pointer_cast<NAxoneChainAndDelay>(tree->GetPortComponent(port));Need(bool(path),"axon_trainer_terminal");
            path->LTZoneClassName=image;path->Build();
        }
        Need(model->CreateLink("DatasetMatrix.Generator1","Output","Axon","Input"),"axon_trainer_input_link");
        for(int i=0;i<2;++i){
            auto synapse=neuron->GetComponentL<NPulseSynapseCommon>("Dendrite"+std::to_string(i+1)+"_1.ExcSynapse1",true);
            Need(bool(synapse),"axon_trainer_synapse");
            source->Disconnect(synapse,"Output","Input",0);
            Need(model->CreateLink("Axon",i?"last":"first","Neuron.Dendrite"+std::to_string(i+1)+"_1.ExcSynapse1","Input"),"axon_trainer_terminal_link");
        }
        trainer=Take<NNeuronAxoneTimeLearner>("NNeuronAxoneTimeLearner","Trainer");
        trainer->PathBindings=R"({"schema_version":1,"paths":[{"port":"first","membrane":"Dendrite1_1","internode":1},{"port":"last","membrane":"Dendrite2_1","internode":1}]})";
        Need(model->SetComponentPosition("DatasetMatrix",0) && model->SetComponentPosition("Axon",1) &&
             model->SetComponentPosition("Neuron",2) && model->SetComponentPosition("Trainer",3),"axon_trainer_scheduler_order");
        const auto marker=model->OperationFailureSequence();model->Init();model->Reset();
        Need(model->IsReady() && model->IsInit() && !model->HasOperationFailureSince(marker),"axon_trainer_initialization");
    }
    void ResetPhysical(){environment->GetTime().SetTime(0);model->Reset();}
    QJsonObject Presentation(unsigned index,bool verification=false){
        ResetPhysical();trainer->BeginPresentation({20,180},600,verification);
        Need(trainer->State.GetData()=="Observing","axon_trainer_presentation_not_started");
        const auto marker=model->OperationFailureSequence();
        for(unsigned tick=0;tick<=600;++tick){model->Calculate();
            Need(!model->HasOperationFailureSince(marker),"axon_trainer_calculate_failure");
            Need(trainer->State.GetData()=="Observing","axon_trainer_invalid_observation");environment->IncreaseModelTimeByStep();}
        const auto result=trainer->FinishPresentation();
        Save("presentation"+std::to_string(index)+".json",QJsonDocument(result).toJson());return result;
    }
    QJsonObject CapturePresentation(unsigned index,bool verification=false){
        std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"tick,time,source,first,last,soma1,soma2,lt_input\n";
        trainer->SetSampleSink([&](const AxoneLearnerSample& sample){
            Need(sample.terminalOutputs.size()==2 && sample.somaPotentials.size()==2,"axon_trainer_sample_dimension");
            csv<<sample.tick<<','<<sample.time<<','<<sample.source;
            for(double value:sample.terminalOutputs)csv<<','<<value;
            for(double value:sample.somaPotentials)csv<<','<<value;csv<<','<<sample.receiverDecisionPotential<<'\n';
        });
        try{const auto result=Presentation(index,verification);trainer->SetSampleSink({});
            Save("presentation"+std::to_string(index)+".csv",QByteArray::fromStdString(csv.str()));return result;}
        catch(...){Save("presentation"+std::to_string(index)+".partial.csv",QByteArray::fromStdString(csv.str()));
            Save("presentation"+std::to_string(index)+".failure.json",QJsonDocument(trainer->LastPresentation()).toJson());throw;}
    }
};

TEST_F(AxoneTimeLearner,FactoryHasNoPhysicalChildrenAndRejectsMissingBindings){
    trainer=Take<NNeuronAxoneTimeLearner>("NNeuronAxoneTimeLearner","Trainer");trainer->Init();
    EXPECT_EQ(trainer->GetNumComponents(),0);EXPECT_FALSE(trainer->IsTrained());
    EXPECT_THROW(trainer->BeginSession("missing"),std::invalid_argument);EXPECT_EQ(trainer->State.GetData(),"InvalidBinding");
}
TEST_F(AxoneTimeLearner,ManagedTerminalAlignmentRequiresFreshVerification){
    Physical();const auto sourceOwner=source->GetOwner();const auto treeOwner=tree->GetOwner();
    const NmsdkTools::ModelBoundarySources terminals{{&tree->GetPortComponent("first")->Output,"axon_first"},{&tree->GetPortComponent("last")->Output,"axon_last"}};
    const auto receiverBefore=NmsdkTools::IdentifyModel(neuron,terminals);
    trainer->BeginSession("native_managed_terminal_diagnostic_v1");
    const auto initial=CapturePresentation(0);EXPECT_FALSE(initial["terminal_alignment_within_tolerance"].toBool());
    EXPECT_TRUE(trainer->CommitProposedDelays());EXPECT_FALSE(trainer->HasVerifiedTerminalAlignment());
    const auto aligned=CapturePresentation(1);ASSERT_TRUE(aligned["terminal_alignment_within_tolerance"].toBool());
    EXPECT_FALSE(trainer->HasVerifiedTerminalAlignment());EXPECT_FALSE(trainer->IsTrained());
    const auto verified=CapturePresentation(2,true);EXPECT_TRUE(verified["joint_verification"].toBool());
    EXPECT_TRUE(trainer->HasVerifiedTerminalAlignment());EXPECT_EQ(trainer->State.GetData(),"TerminalVerified");
    EXPECT_EQ(trainer->RequestedPresentations.GetData(),3);EXPECT_EQ(trainer->ActualPresentations.GetData(),3);
    EXPECT_EQ(trainer->CompletedObservations.GetData(),3);EXPECT_FALSE(trainer->IsTrained());
    EXPECT_EQ(trainer->GetNumComponents(),0);EXPECT_EQ(source->GetOwner(),sourceOwner);EXPECT_EQ(tree->GetOwner(),treeOwner);
    EXPECT_EQ(NmsdkTools::IdentifyModel(neuron,terminals),receiverBefore);
    EXPECT_DOUBLE_EQ(source->Amplitude.GetData(),1.);EXPECT_DOUBLE_EQ(source->PulseLength.GetData(),.001);
}
TEST_F(AxoneTimeLearner,RejectsForeignTerminalConsumer){
    Physical();auto listener=Take<NAxoneDelay>("NAxoneDelay","OtherReceiver");listener->Init();
    Need(model->CreateLink("Axon","first","OtherReceiver","Input"),"axon_trainer_foreign_listener");
    EXPECT_THROW(trainer->BeginSession("foreign_consumer"),std::invalid_argument);
    EXPECT_EQ(trainer->State.GetData(),"InvalidBinding");EXPECT_FALSE(trainer->IsTrained());
}
TEST_F(AxoneTimeLearner,TerminalDelayLeaseIsExclusiveAndReleasedByCancellation){
    Physical();auto second=Take<NNeuronAxoneTimeLearner>("NNeuronAxoneTimeLearner","SecondTrainer");
    second->PathBindings=trainer->PathBindings.GetData();second->Init();trainer->BeginSession("first_owner");
    EXPECT_THROW(second->BeginSession("conflicting_owner"),std::invalid_argument);
    trainer->CancelSession("handoff_private_terminal");EXPECT_NO_THROW(second->BeginSession("second_owner"));
    second->CancelSession("test_complete");EXPECT_EQ(tree->GetOwner(),model);EXPECT_EQ(neuron->GetOwner(),model);
}
TEST_F(AxoneTimeLearner,RequiresExternalResetAndRejectsResetInsideObservation){
    Physical();trainer->BeginSession("reset_contract");
    EXPECT_THROW(trainer->BeginPresentation({20,180},600),std::invalid_argument);
    ResetPhysical();trainer->BeginPresentation({20,180},600);model->Calculate();model->Reset();
    EXPECT_EQ(trainer->State.GetData(),"InvalidObservation");EXPECT_FALSE(trainer->HasVerifiedTerminalAlignment());
}
TEST_F(AxoneTimeLearner,RejectsSourceProfileMutationDuringObservation){
    Physical();trainer->BeginSession("source_profile");ResetPhysical();trainer->BeginPresentation({20,180},600);
    source->PulseLength=.002;model->Calculate();
    EXPECT_EQ(trainer->State.GetData(),"InvalidObservation");EXPECT_FALSE(trainer->IsTrained());
    EXPECT_NE(trainer->FailureReason.GetData().find("source_profile_changed"),std::string::npos);
}
TEST_F(AxoneTimeLearner,PresentationBudgetTerminatesBeforeAnotherPhysicalRun){
    Physical();trainer->MaximumPresentations=1;trainer->BeginSession("finite_budget");
    CapturePresentation(0);trainer->CommitProposedDelays();ResetPhysical();trainer->BeginPresentation({20,180},600);
    EXPECT_EQ(trainer->State.GetData(),"BudgetExhausted");EXPECT_EQ(trainer->RequestedPresentations.GetData(),1);
    EXPECT_EQ(trainer->ActualPresentations.GetData(),1);EXPECT_FALSE(trainer->IsTrained());
}
TEST_F(AxoneTimeLearner,RejectsUnsupportedVersionAndSubTickDelayLimit){
    Physical();trainer->ControllerVersion=99;EXPECT_THROW(trainer->BeginSession("unknown_version"),std::invalid_argument);
    trainer->ControllerVersion=1;trainer->MaximumInternodeDelay=.0001;
    EXPECT_THROW(trainer->BeginSession("sub_tick_limit"),std::invalid_argument);
}
}
