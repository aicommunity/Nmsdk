#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseNeuron.h"
#include "NPulseLTZoneCommon.h"
#include "NPulseMembrane.h"
#include "NPulseGeneratorTransit.h"
#include "NDatasetMatrix.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelArchive.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <type_traits>
#include <algorithm>
#include <cmath>

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
    template<class Owner> UEPtr<Owner> OwnerNode(unsigned frequency,const std::string& name="Learner") {
        auto owner=dynamic_pointer_cast<Owner>(storage->TakeObject(
            std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        Require(bool(owner),"threshold_fixture_owner");owner->Name=name;
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

template<class Owner> void PostConstructionArchive(unsigned frequency) {
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    constexpr double laterThreshold=.005;
    const std::string implementation="initial-threshold-archive-roundtrip-v1";
    Scope scope(frequency);auto source=scope.OwnerNode<Owner>(frequency);
    const auto spec=Spec(branch,frequency,100.);
    const auto cold=source->ConstructNativeModel(spec);
    ASSERT_EQ(cold.status,NativeModelBuildStatus::Constructed)<<cold.reason;
    scope.model->Init();scope.model->Reset();
    auto neuron=source->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto dataset=source->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    ASSERT_TRUE(neuron);ASSERT_TRUE(dataset);
    auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
    ASSERT_FALSE(neuron->GetComponent("LTMembrane",true));
    ASSERT_DOUBLE_EQ(zone->Threshold.GetData(),100.);
    // Explicit idle instance edit; no calibration data, trained state or
    // successful certificate is invented by this physical-graph fixture.
    zone->Threshold=laterThreshold;zone->Init();
    const auto adopted=source->AdoptNativeModel(spec);
    ASSERT_EQ(adopted.status,NativeModelBuildStatus::Adopted)<<adopted.reason;
    EXPECT_NE(adopted.modelRevision,cold.modelRevision);
    ASSERT_DOUBLE_EQ(zone->Threshold.GetData(),laterThreshold);
    dataset->Delay=0.;dataset->LoopSamples=false;dataset->AdvanceSampleAfterBurst=false;
    auto generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(generator);
    NmsdkTools::ModelBoundarySources sourcePorts{{&generator->Output,"burst"}};
    const auto datasetArchive=NmsdkTools::ExportDatasetSnapshot(dataset);
    std::vector<std::string> imageRoots;
    for(const auto& value:datasetArchive["required_class_names"].toArray())imageRoots.push_back(value.toString().toStdString());
    const QJsonObject metadata{{"implementation_id",QString::fromStdString(implementation)},
        {"state_kind","model_spec"},{"training",QJsonObject{{"status","not_trained"}}},
        {"calibration",QJsonObject{{"status","fixed"},{"protocol","explicit-idle-instance-edit"},
            {"ltzone_path","$.LTZone"},{"threshold",laterThreshold}}},
        {"conversion",QJsonObject{{"mode","none"}}}};
    const auto archive=NmsdkTools::ExportModelArchive(neuron,metadata,sourcePorts,imageRoots);
    const auto artifactPrefix=std::string("initial_threshold_archive_")+(branch?"Branch_":"Classic_")+std::to_string(frequency);
    Write(artifactPrefix+"_source.json",{{"model_spec",EncodeNativeModelSpec(spec)},
        {"archive",archive},{"dataset",datasetArchive},{"training_completed",false}});
    auto target=scope.OwnerNode<Owner>(frequency,"ImportedLearner");
    const auto targetCold=target->ConstructNativeModel(spec);
    ASSERT_EQ(targetCold.status,NativeModelBuildStatus::Constructed)<<targetCold.reason;
    target->Init();target->Reset();
    ASSERT_DOUBLE_EQ(target->template GetComponentL<NPulseNeuron>("Neuron",true)->template
        GetComponentL<NPulseLTZoneCommon>("LTZone",true)->Threshold.GetData(),100.);
    const double clock=scope.environment->GetTime().GetDoubleTime();
    NmsdkTools::PrepareModelArchive(archive,scope.storage,scope.environment,QString::fromStdString(implementation));
    auto importedDataset=dynamic_pointer_cast<NDatasetMatrix>(NmsdkTools::ImportDatasetSnapshot(
        datasetArchive,scope.storage,scope.environment));ASSERT_TRUE(importedDataset);
    auto importedGenerator=importedDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    ASSERT_TRUE(importedGenerator);
    NmsdkTools::ModelBoundarySources targetPorts{{&importedGenerator->Output,"burst"}};
    auto importedNeuron=dynamic_pointer_cast<NPulseNeuron>(NmsdkTools::ImportModelArchive(
        archive,scope.storage,scope.environment,QString::fromStdString(implementation),targetPorts));
    ASSERT_TRUE(importedNeuron);
    const auto installed=CommitNativeLearnerChildren(*target,spec,adopted.effective,importedNeuron,importedDataset);
    ASSERT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
    // Public adoption refreshes cached child aliases after the native commit.
    // It must inspect the imported graph rather than replay constructor100.
    const auto current=target->AdoptNativeModel(spec);
    ASSERT_EQ(current.status,NativeModelBuildStatus::Adopted)<<current.reason;
    ASSERT_EQ(current.modelRevision,adopted.modelRevision);
    target->Build();target->Init();target->Reset();
    importedNeuron=target->template GetComponentL<NPulseNeuron>("Neuron",true);
    importedDataset=target->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    ASSERT_TRUE(importedNeuron);ASSERT_TRUE(importedDataset);
    importedGenerator=importedDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);ASSERT_TRUE(importedGenerator);
    targetPorts={{&importedGenerator->Output,"burst"}};
    auto importedZone=importedNeuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(importedZone);
    ASSERT_DOUBLE_EQ(importedZone->Threshold.GetData(),laterThreshold);
    ASSERT_EQ(NmsdkTools::IdentifyModel(importedNeuron,targetPorts),NmsdkTools::IdentifyModel(neuron,sourcePorts));
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(),clock);
    scope.model->Init();scope.model->Reset();
    // Lifecycle operations may legitimately rebuild children. Resolve actual
    // named objects and boundary ports; pointer identity is not the contract.
    neuron=source->template GetComponentL<NPulseNeuron>("Neuron",true);
    dataset=source->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    importedNeuron=target->template GetComponentL<NPulseNeuron>("Neuron",true);
    importedDataset=target->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    ASSERT_TRUE(neuron);ASSERT_TRUE(dataset);ASSERT_TRUE(importedNeuron);ASSERT_TRUE(importedDataset);
    generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    importedGenerator=importedDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    ASSERT_TRUE(generator);ASSERT_TRUE(importedGenerator);
    zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);
    importedZone=importedNeuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);
    ASSERT_TRUE(zone);ASSERT_TRUE(importedZone);
    sourcePorts={{&generator->Output,"burst"}};targetPorts={{&importedGenerator->Output,"burst"}};
    ASSERT_DOUBLE_EQ(zone->Threshold.GetData(),laterThreshold);
    ASSERT_DOUBLE_EQ(importedZone->Threshold.GetData(),laterThreshold);
    dataset->StateGeneration=1;importedDataset->StateGeneration=1;
    QJsonArray frames,columns{"time","stimulus_source","stimulus_imported","spike_source","spike_imported"};
    const std::size_t somas=branch?1u:spec.inputs.size();
    for(std::size_t i=0;i<somas;++i) {
        columns.append(QString::fromStdString("soma_source"+std::to_string(i)));
        columns.append(QString::fromStdString("soma_imported"+std::to_string(i)));
    }
    bool emitted=false;double minimum=std::numeric_limits<double>::infinity(),maximum=-minimum;
    const std::size_t count=std::size_t(std::llround(.06*frequency))+1;
    for(std::size_t tick=0;tick<count;++tick) {
        scope.model->Calculate();
        const double a=generator->Output(0,0),b=importedGenerator->Output(0,0);
        ASSERT_TRUE(std::isfinite(a));ASSERT_TRUE(std::isfinite(b));ASSERT_DOUBLE_EQ(a,b)<<tick;emitted=emitted || a>0.;
        const double spike=zone->Output(0,0),otherSpike=importedZone->Output(0,0);
        ASSERT_TRUE(std::isfinite(spike));ASSERT_TRUE(std::isfinite(otherSpike));ASSERT_DOUBLE_EQ(spike,otherSpike)<<tick;
        QJsonArray frame{scope.environment->GetTime().GetDoubleTime(),a,b,spike,otherSpike};
        for(std::size_t i=0;i<somas;++i) {
            const auto path="Soma"+std::to_string(i+1);
            auto left=neuron->template GetComponentL<NPulseMembrane>(path,true);
            auto right=importedNeuron->template GetComponentL<NPulseMembrane>(path,true);ASSERT_TRUE(left);ASSERT_TRUE(right);
            const double va=left->SumPotential(0,0),vb=right->SumPotential(0,0);
            ASSERT_TRUE(std::isfinite(va));ASSERT_TRUE(std::isfinite(vb));ASSERT_DOUBLE_EQ(va,vb)<<tick<<":"<<path;
            minimum=std::min(minimum,va);maximum=std::max(maximum,va);frame.append(va);frame.append(vb);
        }
        frames.append(frame);scope.environment->IncreaseModelTimeByStep();
    }
    EXPECT_TRUE(emitted);EXPECT_GT(maximum-minimum,1e-6);
    EXPECT_DOUBLE_EQ(zone->Threshold.GetData(),laterThreshold);
    EXPECT_DOUBLE_EQ(importedZone->Threshold.GetData(),laterThreshold);
    EXPECT_FALSE(source->NativeTrainingController().Certificate());EXPECT_FALSE(target->NativeTrainingController().Certificate());
    EXPECT_DOUBLE_EQ(scope.StockThreshold(),.0117);
    const auto after=NmsdkTools::IdentifyModel(importedNeuron,targetPorts);
    EXPECT_EQ(after,archive["graph"].toObject()["identity"].toObject());
    Write(artifactPrefix+".json",
        {{"kind","initial_threshold_postconstruction_graph_roundtrip"},{"schema_version",1},
         {"model_spec",EncodeNativeModelSpec(spec)},{"archive",archive},{"dataset",datasetArchive},
         {"imported_identity",after},{"constructor_threshold",100.},{"effective_threshold",laterThreshold},
         {"frequency_hz",int(frequency)},{"lt_membrane",false},{"training_completed",false},
         {"measurement","paired_native_first-pulse_prefix_not_training"},{"columns",columns},{"samples",frames}});
}
}

TEST(NativeInitialThreshold,Classic2000){Construct<NNeuronTimeLearner>(2000,true);}
TEST(NativeInitialThreshold,Branch2000){Construct<NNeuronTimeLearnerBranch>(2000,true);}
TEST(NativeInitialThreshold,Classic20000){Construct<NNeuronTimeLearner>(20000,true);}
TEST(NativeInitialThreshold,Branch20000){Construct<NNeuronTimeLearnerBranch>(20000,true);}
TEST(NativeInitialThreshold,ClassicLegacyImage){Construct<NNeuronTimeLearner>(2000,false);}
TEST(NativeInitialThreshold,BranchLegacyImage){Construct<NNeuronTimeLearnerBranch>(2000,false);}
TEST(NativeInitialThreshold,ClassicArchive2000){PostConstructionArchive<NNeuronTimeLearner>(2000);}
TEST(NativeInitialThreshold,BranchArchive2000){PostConstructionArchive<NNeuronTimeLearnerBranch>(2000);}
TEST(NativeInitialThreshold,ClassicArchive20000){PostConstructionArchive<NNeuronTimeLearner>(20000);}
TEST(NativeInitialThreshold,BranchArchive20000){PostConstructionArchive<NNeuronTimeLearnerBranch>(20000);}
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
    // TakeObject may return a fully built learner image. Rejection must retain
    // its live graph, rather than manufacture empty slots by deleting children.
    const auto baseline=Spec(false,2000,std::nullopt);
    const auto constructed=owner->ConstructNativeModel(baseline);
    ASSERT_EQ(constructed.status,NativeModelBuildStatus::Constructed)<<constructed.reason;
    scope.model->Init();scope.model->Reset();
    const auto before=InspectNativeLearnerModel(*owner,baseline,{1,1,1,1});
    ASSERT_EQ(before.status,NativeModelBuildStatus::Adopted)<<before.reason;
    const auto oldNeuron=owner->GetComponent("Neuron",true),oldDataset=owner->GetComponent("DatasetMatrix",true);
    ASSERT_TRUE(oldNeuron);ASSERT_TRUE(oldDataset);
    const auto datasetBefore=NmsdkTools::IdentifyModel(oldDataset);
    ASSERT_TRUE(datasetBefore["valid"].toBool())<<QJsonDocument(datasetBefore).toJson().toStdString();
    std::vector<NameT> orderBefore;owner->GetComponentsList(orderBefore);
    scope.environment->GetTime().SetTime(1000000);
    const double clock=scope.environment->GetTime().GetDoubleTime();
    // Storage image names differ from C++ implementation names; exercise the
    // real registered simple-zone image, not a missing-template exception.
    ASSERT_TRUE(scope.storage->CheckClass("NPSimpleLTZone"));
    StorageProfileSpec p;p.name="InitialThresholdUnsupported";p.neuronBaseClass="NSPNeuronGen";p.ltZoneBaseClass="NPSimpleLTZone";
    const auto profile=RegisterStorageProfile(scope.storage,scope.environment,p);
    auto spec=Spec(false,2000,100.);spec.neuronClass=profile.neuronClass;
    const auto result=owner->ConstructNativeModel(spec);
    EXPECT_EQ(result.status,NativeModelBuildStatus::Rejected);
    EXPECT_EQ(result.reason,"native_scalar_spike_threshold_not_supported_by_ltzone");
    EXPECT_FALSE(result.modelMayHaveChanged);
    EXPECT_EQ(owner->GetComponent("Neuron",true).Get(),oldNeuron.Get());
    EXPECT_EQ(owner->GetComponent("DatasetMatrix",true).Get(),oldDataset.Get());
    std::vector<NameT> orderAfter;owner->GetComponentsList(orderAfter);EXPECT_EQ(orderBefore,orderAfter);
    const auto after=InspectNativeLearnerModel(*owner,baseline,{1,1,1,1});
    ASSERT_EQ(after.status,NativeModelBuildStatus::Adopted)<<after.reason;
    EXPECT_EQ(after.modelRevision,before.modelRevision);EXPECT_EQ(after.effective,before.effective);
    EXPECT_EQ(NmsdkTools::IdentifyModel(oldDataset),datasetBefore);
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(),clock);
    Write("initial_threshold_rejection_unchanged.json",{{"reason",QString::fromStdString(result.reason)},
        {"before",QString::fromStdString(before.modelRevision)},{"after",QString::fromStdString(after.modelRevision)},
        {"dataset_before",datasetBefore},{"dataset_after",NmsdkTools::IdentifyModel(oldDataset)},
        {"clock_before",clock},{"clock_after",scope.environment->GetTime().GetDoubleTime()},
        {"children_retained",owner->GetComponent("Neuron",true).Get()==oldNeuron.Get() &&
                             owner->GetComponent("DatasetMatrix",true).Get()==oldDataset.Get()},
        {"order_retained",orderBefore==orderAfter}});
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
