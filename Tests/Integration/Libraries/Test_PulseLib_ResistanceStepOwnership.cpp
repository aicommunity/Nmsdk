#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseLTZoneCommon.h"
#include "NPulseSynapse.h"
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelArchive.h"
#include "TimeLearner/NativeRecognitionState.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cstdlib>
#include <map>
#include <stdexcept>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
constexpr unsigned Frequency=2000;
constexpr const char* Implementation="resistance-step-ownership-fixture-v1";
void Require(bool condition,const char* reason)
{if(!condition)throw std::runtime_error(reason);}
struct Scope {
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UNet> model;
    Scope() {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        environment->DestroyModel();environment->SetUseIndTimeStepFlag(false);
        Require(environment->CreateModel("NModel"),"step_fixture_model");
        model=dynamic_pointer_cast<UNet>(environment->GetModel());Require(bool(model),"step_fixture_root");
        model->SetGlobalTimeStep(Frequency);
    }
    ~Scope(){if(model)model->BreakLinks();environment->DestroyModel();}
    template<class Owner> UEPtr<Owner> Take(const std::string& name) {
        auto owner=dynamic_pointer_cast<Owner>(storage->TakeObject(
            std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
        Require(bool(owner),"step_fixture_owner");owner->Name=name;
        owner->ControllerVersion=1;owner->CalculateMode=1;owner->StructureBuildMode=1;
        owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;
        owner->IsNeedToTrain=false;owner->SetGlobalTimeStep(Frequency);
        UEPtr<UContainer> component=owner;
        Require(model->AddComponent(component)!=ForbiddenId,"step_fixture_attach");return owner;
    }
};
template<class Owner> constexpr bool Branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
template<class Owner> std::string Label(int normalization,const char* suffix)
{return std::string(Branch<Owner>?"Branch":"Classic")+"_N"+std::to_string(normalization)+"_"+suffix;}
NativeModelSpec Specification(bool branch,int normalization,const std::string& neuronClass) {
    NativeModelSpec s;s.branch=branch;s.frequencyHz=Frequency;s.neuronClass=neuronClass;
    s.normalization=normalization?Normalization::TipResistance:Normalization::SynapseCount;
    s.editPolicy.normalization=s.normalization;s.editPolicy.maximumCableLength=8;
    s.initialIsi={.01,.03};s.inputs={{2,normalization?1:3,86e6},{branch?1:3,normalization?1:2,123e6}};
    return s;
}
using Resistances=std::map<std::string,double>;
Resistances AllResistances(UEPtr<NPulseNeuron> neuron) {
    Require(bool(neuron),"step_fixture_neuron");Resistances result;
    const auto visit=[&](auto&& self,UEPtr<UContainer> node,const std::string& path)->void {
        if(auto synapse=dynamic_pointer_cast<NPulseSynapseCommon>(node))
            Require(result.emplace(path,synapse->Resistance.GetData()).second,"step_fixture_duplicate_synapse");
        std::vector<NameT> names;node->GetComponentsList(names);
        for(const auto& name:names)self(self,node->GetComponent(name,true),path.empty()?name:path+"."+name);
    };
    visit(visit,neuron.Get(),"");Require(!result.empty(),"step_fixture_no_synapses");return result;
}
QJsonObject ResistanceJson(const Resistances& values) {
    QJsonObject result;for(const auto& [path,value]:values)result[QString::fromStdString(path)]=value;return result;
}
template<class Owner> QJsonObject Identity(UEPtr<Owner> owner) {
    auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto source=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    Require(bool(neuron) && bool(source),"step_fixture_native_graph");
    const auto identity=NmsdkTools::IdentifyModel(neuron,{{&source->Output,"burst"}});
    Require(identity["valid"].toBool(),"step_fixture_invalid_identity");return identity;
}
template<class Owner> QJsonObject NativeSnapshot(UEPtr<Owner> owner) {
    const auto identity=Identity(owner);return {{"identity",identity},
        {"individual_resistances",ResistanceJson(AllResistances(owner->template GetComponentL<NPulseNeuron>("Neuron",true)))},
        {"legacy_step",owner->SynapseResistanceStep.GetData()},
        {"probe_state",int(owner->NativeProbeState())},
        {"training_state",EncodeNativeTrainingState(owner->NativeTrainingController(),
            identity["sha256"].toString().toStdString(),owner->ReadNativeParameters())}};
}
void Write(const std::string& name,const QJsonObject& record) {
    if(const char* directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
        const auto folder=QString::fromLocal8Bit(directory);Require(QDir().mkpath(folder),"step_fixture_output_directory");
        QFile file(QDir(folder).filePath(QString::fromStdString(name)+".json"));
        Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"step_fixture_output_exists");
        const auto bytes=QJsonDocument(record).toJson();Require(file.write(bytes)==bytes.size() && file.flush(),"step_fixture_output_write");
    }
}
template<class Owner> void CheckGuard(UEPtr<Owner> owner,const char* phase,QJsonArray& phases) {
    const auto before=NativeSnapshot(owner);const double previous=owner->SynapseResistanceStep.GetData();
    const double changed=previous*1.25;
    // Both the public bool setter and ordinary UProperty assignment are covered.
    EXPECT_FALSE(owner->SetSynapseResistanceStep(changed));EXPECT_EQ(NativeSnapshot(owner),before);
    EXPECT_THROW(owner->SynapseResistanceStep.SetData(changed),UIProperty::EPropertySetterFail);
    EXPECT_EQ(NativeSnapshot(owner),before);EXPECT_DOUBLE_EQ(owner->SynapseResistanceStep.GetData(),previous);
    EXPECT_TRUE(owner->SetSynapseResistanceStep(previous));EXPECT_EQ(NativeSnapshot(owner),before);
    EXPECT_NO_THROW(owner->SynapseResistanceStep.SetData(previous));EXPECT_EQ(NativeSnapshot(owner),before);
    phases.append(QJsonObject{{"phase",phase},{"before",before},{"after",NativeSnapshot(owner)}});
}
template<class Owner> void CheckExtraBank(UEPtr<Owner> owner,const NativeModelSpec& spec) {
    auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    const auto values=AllResistances(neuron);
    for(std::size_t input=0;input<spec.inputs.size();++input)for(int k=1;k<=spec.inputs[input].synapses;++k) {
        const auto path="Dendrite"+std::to_string(Branch<Owner>?1:int(input+1))+"_"+
            std::to_string(spec.inputs[input].attachment)+".ExcSynapse"+std::to_string(k);
        // This finding concerns contacts actually handled by the legacy setter.
        ASSERT_TRUE(neuron->template GetComponentL<NPulseSynapse>(path,true))<<path;
        ASSERT_NE(values.find(path),values.end());EXPECT_DOUBLE_EQ(values.at(path),*spec.inputs[input].resistance);
        if(k>=2)EXPECT_NE(values.at(path),owner->SynapseResistanceStep.GetData());
    }
}
template<class Owner> UEPtr<Owner> ImportPhysicalModel(Scope& scope,UEPtr<Owner> source,const NativeModelSpec& spec) {
    auto neuron=source->template GetComponentL<NPulseNeuron>("Neuron",true);
    auto dataset=source->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
    Require(bool(neuron) && bool(dataset),"step_fixture_import_source");
    auto generator=dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Require(bool(generator),"step_fixture_import_generator");
    const auto datasetArchive=NmsdkTools::ExportDatasetSnapshot(dataset);
    std::vector<std::string> roots;for(const auto& value:datasetArchive["required_class_names"].toArray())
        roots.push_back(value.toString().toStdString());
    auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);
    Require(bool(zone),"step_fixture_import_ltzone");
    const QJsonObject metadata{{"implementation_id",Implementation},{"state_kind","model_spec"},
        {"training",QJsonObject{{"status","not_trained"}}},
        {"calibration",QJsonObject{{"status","fixed"},{"protocol","step-ownership-physical-import"},
            {"ltzone_path","$.LTZone"},{"threshold",zone->Threshold.GetData()}}},
        {"conversion",QJsonObject{{"mode","none"}}}};
    const auto archive=NmsdkTools::ExportModelArchive(neuron,metadata,{{&generator->Output,"burst"}},roots);
    NmsdkTools::PrepareModelArchive(archive,scope.storage,scope.environment,Implementation);
    auto importedDataset=dynamic_pointer_cast<NDatasetMatrix>(NmsdkTools::ImportDatasetSnapshot(
        datasetArchive,scope.storage,scope.environment));Require(bool(importedDataset),"step_fixture_import_dataset");
    auto importedSource=importedDataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Require(bool(importedSource),"step_fixture_import_source_missing");
    auto importedNeuron=dynamic_pointer_cast<NPulseNeuron>(NmsdkTools::ImportModelArchive(
        archive,scope.storage,scope.environment,Implementation,{{&importedSource->Output,"burst"}}));
    Require(bool(importedNeuron),"step_fixture_import_neuron");
    auto target=scope.Take<Owner>("ImportedLearner");
    const auto installed=target->InstallNativePreparedModel(spec,importedNeuron,importedDataset,source->ReadNativeParameters());
    Require(installed.status==NativeModelBuildStatus::Adopted,installed.reason.c_str());
    target->Build();target->Init();target->Reset();return target;
}
template<class Owner> void NativeOwnership(int normalization) {
    Scope scope;auto owner=scope.Take<Owner>("Learner");const auto name=Label<Owner>(normalization,"native_step_ownership");
    StorageProfileSpec profile;profile.name=name;profile.frequencyHz=Frequency;profile.neuronBaseClass="NSPNeuronGen";
    const auto registered=RegisterStorageProfile(scope.storage,scope.environment,profile);
    const auto spec=Specification(Branch<Owner>,normalization,registered.neuronClass);
    const double clock=scope.environment->GetTime().GetDoubleTime();
    const auto constructed=owner->ConstructNativeModel(spec);
    ASSERT_EQ(constructed.status,NativeModelBuildStatus::Constructed)<<constructed.reason;
    scope.model->Init();scope.model->Reset();CheckExtraBank(owner,spec);QJsonArray phases;
    const auto initial=Identity(owner);CheckGuard(owner,"constructed",phases);
    owner->Reset();EXPECT_EQ(Identity(owner),initial);CheckGuard(owner,"explicit_reset",phases);
    owner->Build();owner->Init();EXPECT_EQ(Identity(owner),initial);CheckGuard(owner,"explicit_build",phases);
    auto imported=ImportPhysicalModel(scope,owner,spec);
    EXPECT_EQ(Identity(imported),Identity(owner));CheckExtraBank(imported,spec);CheckGuard(imported,"prepared_archive_import",phases);
    imported->Reset();imported->Build();imported->Init();CheckGuard(imported,"import_reset_build",phases);
    // Default explicitly releases native ownership before legacy defaults/setters.
    owner->Default();EXPECT_TRUE(owner->SetSynapseResistanceStep(2.e9));
    EXPECT_NO_THROW(owner->SynapseResistanceStep.SetData(2.e9));EXPECT_DOUBLE_EQ(owner->SynapseResistanceStep.GetData(),2.e9);
    const auto rebuilt=owner->ConstructNativeModel(spec);ASSERT_EQ(rebuilt.status,NativeModelBuildStatus::Constructed)<<rebuilt.reason;
    owner->Build();owner->Init();owner->Reset();CheckExtraBank(owner,spec);CheckGuard(owner,"native_after_default",phases);
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(),clock);
    Write(name,{{"kind","native_resistance_step_ownership"},{"schema_version",1},{"phases",phases},
        {"normalization",normalization},{"topology",Branch<Owner>?"Branch":"Classic"},
        {"frequency_hz",int(Frequency)},{"clock_unchanged",true},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
}
template<class Owner> void LegacyOwnership(int normalization) {
    Scope scope;auto owner=scope.Take<Owner>("Learner");const auto name=Label<Owner>(normalization,"legacy_step_ownership");
    StorageProfileSpec profile;profile.name=name;profile.frequencyHz=Frequency;profile.neuronBaseClass="NSPNeuronGen";
    const auto registered=RegisterStorageProfile(scope.storage,scope.environment,profile);
    owner->NeuronClassName=registered.neuronClass;owner->NumInputDendrite=2;owner->NormalizationMode=normalization;
    owner->DendriteLength=std::vector<int>{2,Branch<Owner>?1:3};owner->NumSynapse=std::vector<int>{3,2};
    MDMatrix<double> pattern;pattern.Resize(2,1);pattern(0,0)=.01;pattern(1,0)=.03;owner->InputPattern=pattern;
    owner->IsNeedToTrain=true;scope.environment->ModelInit();scope.model->Reset();owner->IsNeedToTrain=false;
    auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);ASSERT_TRUE(neuron);
    const auto before=AllResistances(neuron);const double previous=owner->SynapseResistanceStep.GetData();
    const double changed=previous*1.25;EXPECT_NO_THROW(owner->SynapseResistanceStep.SetData(changed));
    EXPECT_DOUBLE_EQ(owner->SynapseResistanceStep.GetData(),changed);const auto after=AllResistances(neuron);
    ASSERT_EQ(before.size(),after.size());std::size_t modified=0;
    for(const auto& [path,resistance]:before) {
        ASSERT_NE(after.find(path),after.end());bool extra=false;
        if(!normalization)for(int input=0;input<2;++input)for(int k=2;k<=(input?2:3);++k) {
            const auto expected="Dendrite"+std::to_string(Branch<Owner>?1:input+1)+"_"+
                std::to_string(input?(Branch<Owner>?1:3):2)+".ExcSynapse"+std::to_string(k);
            if(path==expected){extra=true;ASSERT_TRUE(neuron->template GetComponentL<NPulseSynapse>(path,true));}
        }
        if(extra){EXPECT_DOUBLE_EQ(after.at(path),changed);if(after.at(path)!=resistance)++modified;}
        else EXPECT_DOUBLE_EQ(after.at(path),resistance)<<path;
    }
    EXPECT_EQ(modified,normalization?0u:3u);
    EXPECT_TRUE(owner->SetSynapseResistanceStep(changed));EXPECT_EQ(AllResistances(neuron),after);
    Write(name,{{"kind","legacy_resistance_step_control"},{"schema_version",1},
        {"normalization",normalization},{"topology",Branch<Owner>?"Branch":"Classic"},
        {"before",ResistanceJson(before)},{"after",ResistanceJson(after)},{"changed_contacts",double(modified)},
        {"legacy_step",owner->SynapseResistanceStep.GetData()},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
}
// An explicitly stopped, zero-packet boundary of the actual constructed graph.
// No measured peaks/references/certificate or successful Train are fabricated.
template<class Owner> QJsonObject ZeroPacketStoppedDiagnostic(Scope& scope,UEPtr<Owner> source,
    const NativeModelSpec& spec,const std::string& name) {
    auto generator=source->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
    Require(bool(generator),"step_fixture_stopped_source");
    ConfiguredNativeTraining c;c.model=spec;c.runId=name+"/zero-packet-stopped-boundary";
    c.protocolRevision="step-ownership-zero-packet-stopped-v1";
    c.stimulusProfile={generator->GetCompClassName(),generator->Amplitude.GetData(),generator->PulseLength.GetData(),
        double(generator->GetTimeStep()),generator->FrequencyDeviation.GetData(),generator->UseTransitSignal.GetData(),
        generator->UsePatternOutput.GetData()};
    c.duration=.15;c.maximumSampleGap=1./Frequency;c.maximumSamples=320;
    c.windows.assign(spec.inputs.size(),{0.,c.duration});c.maximumReferenceProbes=spec.inputs.size();
    c.maximumModelSeconds=1.;c.maximumWallSeconds=1.;c.peakSelection=PeakSelectionPolicy::AssignedBurstWave;
    c.search.normalization=spec.normalization;c.search.maximumProbes=4;c.search.maximumEdits=1;
    c.search.maximumCandidatesPerInput=1;c.search.maximumSweeps=1;c.search.resistanceSubdivisionDepth=0;
    for(const auto& p:source->ReadNativeParameters())
        c.search.bounds.push_back({p.length,p.length,p.synapses,p.synapses,p.resistance,p.resistance});
    const auto plan=MakeConfiguredNativeTrainingPlan(c);const auto revision=Identity(source)["sha256"].toString().toStdString();
    NativeTrainingService boundary;
    boundary.RestoreStoppedBoundary(plan,{},{},{},revision,0,1,revision,0,false,
        TrainingStatus::ExternalStop,"fixture_zero_packet_external_stop");
    Require(boundary.ReferencePackets().empty() && boundary.ObservedPackets().empty() && boundary.FinalPackets().empty() &&
        !boundary.References() && !boundary.Certificate(),"step_fixture_stopped_not_empty");
    const auto stopped=ExportNativeLearnedState(*source,spec,boundary,source->ReadNativeParameters(),
        source->ControllerVersion.GetData(),source->CalculateMode.GetData(),source->StructureBuildMode.GetData(),Implementation);
    Require(stopped["training_outcome"]==QJsonValue("external_stop") && stopped["certificate"].isNull() &&
        stopped["reference_complete"]==QJsonValue(false),"step_fixture_wrong_stopped_scope");
    return ConvertNativeStoppedToDiagnosticRecognition(stopped,{},scope.storage,scope.environment,Implementation);
}
template<class Owner> void ZeroPacketDiagnosticRecognitionOwnership(int normalization) {
    Scope scope;auto source=scope.Take<Owner>("SourceLearner");
    const auto name=Label<Owner>(normalization,"zero_packet_stopped_diagnostic_step_ownership");
    StorageProfileSpec profile;profile.name=name;profile.frequencyHz=Frequency;profile.neuronBaseClass="NSPNeuronGen";
    const auto registered=RegisterStorageProfile(scope.storage,scope.environment,profile);
    const auto spec=Specification(Branch<Owner>,normalization,registered.neuronClass);
    const auto constructed=source->ConstructNativeModel(spec);
    ASSERT_EQ(constructed.status,NativeModelBuildStatus::Constructed)<<constructed.reason;
    scope.model->Init();scope.model->Reset();CheckExtraBank(source,spec);
    const double clock=scope.environment->GetTime().GetDoubleTime();
    const auto package=ZeroPacketStoppedDiagnostic(scope,source,spec,name);
    ASSERT_EQ(package["kind"],QJsonValue("timelearner_diagnostic_recognition_state"));
    ASSERT_TRUE(package["recognition_certificate"].isNull());
    auto owner=scope.Take<Owner>("RecognitionLearner");
    const auto imported=owner->ImportNativeDiagnosticRecognitionState(package,Implementation);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    owner->Build();owner->Init();scope.model->Init();scope.model->Reset();ASSERT_TRUE(owner->HasNativeRecognitionState());
    CheckExtraBank(owner,spec);const auto before=owner->ExportNativeRecognitionState(Implementation);
    QJsonArray phases;CheckGuard(owner,"zero_packet_stopped_diagnostic_import",phases);
    owner->Reset();owner->Build();owner->Init();CheckGuard(owner,"diagnostic_recognition_reset_build",phases);
    EXPECT_EQ(owner->ExportNativeRecognitionState(Implementation),before);EXPECT_TRUE(owner->IsNativeRecognitionTrialIdle());
    EXPECT_DOUBLE_EQ(scope.environment->GetTime().GetDoubleTime(),clock);
    Write(name,{{"kind","zero_packet_stopped_diagnostic_recognition_step_ownership"},{"schema_version",1},
        {"normalization",normalization},{"source",package},{"phases",phases},
        {"package_after",owner->ExportNativeRecognitionState(Implementation)},
        {"successful_training_claimed",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
}
}
TEST(NativeResistanceStepOwnership,ClassicN0){NativeOwnership<NNeuronTimeLearner>(0);}
TEST(NativeResistanceStepOwnership,ClassicN1){NativeOwnership<NNeuronTimeLearner>(1);}
TEST(NativeResistanceStepOwnership,BranchN0){NativeOwnership<NNeuronTimeLearnerBranch>(0);}
TEST(NativeResistanceStepOwnership,BranchN1){NativeOwnership<NNeuronTimeLearnerBranch>(1);}
TEST(LegacyResistanceStep,ClassicN0){LegacyOwnership<NNeuronTimeLearner>(0);}
TEST(LegacyResistanceStep,ClassicN1){LegacyOwnership<NNeuronTimeLearner>(1);}
TEST(LegacyResistanceStep,BranchN0){LegacyOwnership<NNeuronTimeLearnerBranch>(0);}
TEST(LegacyResistanceStep,BranchN1){LegacyOwnership<NNeuronTimeLearnerBranch>(1);}
TEST(NativeResistanceStepOwnership,ClassicZeroPacketStoppedDiagnosticImport)
{for(int n:{0,1})ZeroPacketDiagnosticRecognitionOwnership<NNeuronTimeLearner>(n);}
TEST(NativeResistanceStepOwnership,BranchZeroPacketStoppedDiagnosticImport)
{for(int n:{0,1})ZeroPacketDiagnosticRecognitionOwnership<NNeuronTimeLearnerBranch>(n);}
