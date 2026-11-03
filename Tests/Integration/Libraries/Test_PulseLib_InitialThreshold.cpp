#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseNeuron.h"
#include "NPulseLTZoneCommon.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
void Require(bool ok,const char* why){if(!ok)throw std::runtime_error(why);}
struct Scope {
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UNet> model;
    explicit Scope(unsigned frequency) {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        environment->DestroyModel();environment->Reset();environment->SetUseIndTimeStepFlag(false);
        Require(environment->CreateModel("NModel"),"threshold_fixture_model");
        model=dynamic_pointer_cast<UNet>(environment->GetModel());Require(bool(model),"threshold_fixture_root");
        model->SetGlobalTimeStep(frequency);
    }
    ~Scope(){if(model)model->BreakLinks();environment->DestroyModel();}
    template<class Owner> UEPtr<Owner> OwnerNode(unsigned frequency) {
        auto owner=dynamic_pointer_cast<Owner>(storage->TakeObject(
            std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        Require(bool(owner),"threshold_fixture_owner");owner->Name="Learner";
        owner->CalculateMode=1;owner->StructureBuildMode=1;owner->IsNeedToTrain=false;
        owner->SetGlobalTimeStep(frequency);UEPtr<UContainer> node=owner;
        Require(model->AddComponent(node)!=ForbiddenId,"threshold_fixture_attach");return owner;
    }
    double StockThreshold() {
        auto neuron=dynamic_pointer_cast<NPulseNeuron>(storage->TakeObject("NSPNeuronGen"));
        Require(bool(neuron),"threshold_fixture_stock");
        const auto zone=neuron->GetComponentL<NPulseLTZoneCommon>("LTZone",true);
        Require(bool(zone),"threshold_fixture_stock_zone");const double value=zone->Threshold.GetData();
        storage->ReturnObject(neuron);return value;
    }
};
NativeModelSpec Spec(bool branch,unsigned frequency,std::optional<double> threshold) {
    NativeModelSpec s;s.branch=branch;s.frequencyHz=frequency;s.neuronClass="NSPNeuronGen";
    s.normalization=Normalization::TipResistance;s.editPolicy.normalization=s.normalization;
    s.editPolicy.maximumCableLength=100;s.initialIsi={.01,.08,.16,.24};
    s.inputs.assign(4,NativeInitialInput{1,1,86e6});s.allocatedCableLengths.assign(branch?1:4,1);
    if(threshold){s.schemaVersion=2;s.initialThreshold=threshold;}
    return s;
}
void Write(const std::string& name,const QJsonObject& data) {
    if(const char* directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
        Require(QDir().mkpath(QString::fromLocal8Bit(directory)),"threshold_fixture_artifact_directory");
        QFile file(QDir(QString::fromLocal8Bit(directory)).filePath(QString::fromStdString(name)));
        Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"threshold_fixture_artifact_exists");
        const auto bytes=QJsonDocument(data).toJson();Require(file.write(bytes)==bytes.size() && file.flush(),"threshold_fixture_write");
    }
}
template<class Owner> void Construct(unsigned frequency,bool explicitThreshold) {
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    Scope scope(frequency);const double stock=scope.StockThreshold();
    EXPECT_DOUBLE_EQ(stock,.0117);
    auto owner=scope.OwnerNode<Owner>(frequency);
    const auto s=Spec(branch,frequency,explicitThreshold?std::optional<double>(100.):std::nullopt);
    const double begin=scope.environment->GetTime().GetDoubleTime();
    const auto result=owner->ConstructNativeModel(s);
    ASSERT_EQ(result.status,NativeModelBuildStatus::Constructed)<<result.reason;
    scope.model->Init();scope.model->Reset();
    auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
    EXPECT_FALSE(neuron->GetComponent("LTMembrane",true));
    EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),explicitThreshold?100.:stock);
    const auto identity=InspectNativeLearnerModel(*owner,s,{1,1,1,1});
    ASSERT_EQ(identity.status,NativeModelBuildStatus::Adopted)<<identity.reason;
    for(int i=0;i<2;++i) {
        owner->Build();owner->Init();owner->Reset();
        EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),explicitThreshold?100.:stock);
        const auto again=InspectNativeLearnerModel(*owner,s,{1,1,1,1});
        ASSERT_EQ(again.status,NativeModelBuildStatus::Adopted)<<again.reason;
        EXPECT_EQ(again.modelRevision,identity.modelRevision);
    }
    EXPECT_DOUBLE_EQ(scope.StockThreshold(),stock);
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(),begin);
    EXPECT_EQ(EncodeNativeModelSpec(DecodeNativeModelSpec(EncodeNativeModelSpec(s))),EncodeNativeModelSpec(s));
    Write(std::string("initial_threshold_")+(branch?"Branch_":"Classic_")+std::to_string(frequency)+(explicitThreshold?"_v2.json":"_v1.json"),
        {{"model_spec",EncodeNativeModelSpec(s)},{"model_revision",QString::fromStdString(identity.modelRevision)},
         {"stock_threshold",stock},{"effective_threshold",zone->Threshold.GetData()},
         {"clock_unchanged",true},{"lt_membrane",false}});
}
}

TEST(NativeInitialThreshold,Classic2000){Construct<NNeuronTimeLearner>(2000,true);}
TEST(NativeInitialThreshold,Branch2000){Construct<NNeuronTimeLearnerBranch>(2000,true);}
TEST(NativeInitialThreshold,Classic20000){Construct<NNeuronTimeLearner>(20000,true);}
TEST(NativeInitialThreshold,Branch20000){Construct<NNeuronTimeLearnerBranch>(20000,true);}
TEST(NativeInitialThreshold,ClassicLegacyImage){Construct<NNeuronTimeLearner>(2000,false);}
TEST(NativeInitialThreshold,BranchLegacyImage){Construct<NNeuronTimeLearnerBranch>(2000,false);}
TEST(NativeInitialThreshold,StrictCodecAndExplicitSignedValues) {
    auto spec=Spec(false,2000,100.);const auto original=EncodeNativeModelSpec(spec);
    auto missing=original;missing.remove("initial_threshold");EXPECT_THROW(DecodeNativeModelSpec(missing),std::invalid_argument);
    auto boolean=original;boolean["initial_threshold"]=true;EXPECT_THROW(DecodeNativeModelSpec(boolean),std::invalid_argument);
    auto downgrade=original;downgrade["schema_version"]=1;EXPECT_THROW(DecodeNativeModelSpec(downgrade),std::invalid_argument);
    auto unknown=original;unknown["schema_version"]=3;EXPECT_THROW(DecodeNativeModelSpec(unknown),std::invalid_argument);
    spec.initialThreshold=std::numeric_limits<double>::infinity();EXPECT_THROW(ValidateNativeModelSpec(spec),std::invalid_argument);
    for(double value:{0.,-1.}) {
        spec.initialThreshold=value;
        EXPECT_EQ(DecodeNativeModelSpec(EncodeNativeModelSpec(spec)).initialThreshold,spec.initialThreshold);
    }
}
TEST(NativeInitialThreshold,UnsupportedZoneIsRejectedBeforeAttachment) {
    Scope scope(2000);auto owner=scope.OwnerNode<NNeuronTimeLearner>(2000);
    StorageProfileSpec p;p.name="InitialThresholdUnsupported";p.neuronBaseClass="NSPNeuronGen";p.ltZoneBaseClass="NPulseSimpleLTZone";
    const auto profile=RegisterStorageProfile(scope.storage,scope.environment,p);
    auto spec=Spec(false,2000,100.);spec.neuronClass=profile.neuronClass;
    const auto result=owner->ConstructNativeModel(spec);
    EXPECT_EQ(result.status,NativeModelBuildStatus::Rejected);
    EXPECT_EQ(result.reason,"native_scalar_spike_threshold_not_supported_by_ltzone");
    EXPECT_FALSE(owner->GetComponent("Neuron",true));EXPECT_FALSE(owner->GetComponent("DatasetMatrix",true));
}
TEST(NativeInitialThreshold,InspectionDoesNotReapplyConstructionValue) {
    Scope scope(2000);auto owner=scope.OwnerNode<NNeuronTimeLearner>(2000);auto spec=Spec(false,2000,100.);
    const auto constructed=owner->ConstructNativeModel(spec);ASSERT_EQ(constructed.status,NativeModelBuildStatus::Constructed)<<constructed.reason;
    scope.model->Init();scope.model->Reset();
    auto neuron=owner->GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    auto zone=neuron->GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
    // An explicit idle graph edit stands for a later threshold value. This is
    // not a calibrated package or a transferable training certificate.
    zone->Threshold=.02;zone->Init();
    const auto first=InspectNativeLearnerModel(*owner,spec,{1,1,1,1});ASSERT_EQ(first.status,NativeModelBuildStatus::Adopted)<<first.reason;
    const auto second=InspectNativeLearnerModel(*owner,spec,{1,1,1,1});
    EXPECT_EQ(first.modelRevision,second.modelRevision);EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),.02);
}
TEST(NativeInitialThreshold,ReturnTakeRestoresTheStorageImageThreshold) {
    for(bool explicitValue:{true,false}) {
        Scope scope(2000);auto owner=scope.OwnerNode<NNeuronTimeLearner>(2000);
        EXPECT_DOUBLE_EQ(scope.StockThreshold(),.0117);
        const auto s=Spec(false,2000,explicitValue?std::optional<double>(100.):std::nullopt);
        const auto result=owner->ConstructNativeModel(s);ASSERT_EQ(result.status,NativeModelBuildStatus::Constructed)<<result.reason;
        scope.model->Init();scope.model->Reset();
        auto neuron=owner->GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
        auto zone=neuron->GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
        EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),explicitValue?100.:.0117);
    }
}
