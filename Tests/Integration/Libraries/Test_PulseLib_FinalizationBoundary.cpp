#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NNeuronPostTrainTune.h"
#include "TimeLearner/NativeFinalizationBoundary.h"
#include "TimeLearner/NativeTrainingBindings.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <cstdlib>
#include <optional>
#include <type_traits>
#include <QCryptographicHash>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
class ExternalFinalizationFlag : public UNet {
public:
    UProperty<bool,ExternalFinalizationFlag,ptOutput | ptPubState> Value;
    ExternalFinalizationFlag():Value("Value",this){}
    ExternalFinalizationFlag* New(void) override {return new ExternalFinalizationFlag;}
};
enum class Scenario { Snapshot, Connected, QueuedProbe, Stopped };

QJsonObject SemanticSolo(QJsonObject package)
{
    // Repeated native image allocation can initialize this one unconnected
    // feedback cache. Do not discard other XML: it can contain physics that
    // an incomplete semantic identity would otherwise fail to protect.
    const auto snapshot=[](QJsonObject value) {
        const auto xml=value["native_xml"].toString();
        const auto digest=[](const QString& text) {
            return QString::fromLatin1(QCryptographicHash::hash(text.toUtf8(),QCryptographicHash::Sha256).toHex());
        };
        EXPECT_EQ(value["native_xml_sha256"].toString(),digest(xml));
        if(value["component_class"]!=QJsonValue("NPMembraneBio"))return value;
        const QString empty="<InputFeedbackSignal Type=\"MDMatrix&lt;d&gt;\" Rows=\"0\" Cols=\"0\" PType=\"266\" IoType=\"17\"></InputFeedbackSignal>";
        const QString zero="<InputFeedbackSignal Type=\"MDMatrix&lt;d&gt;\" Rows=\"1\" Cols=\"1\" PType=\"266\" IoType=\"17\">0</InputFeedbackSignal>";
        auto normalized=xml;normalized.replace(empty,zero);
        value["native_xml"]=normalized;value["native_xml_sha256"]=digest(normalized);return value;
    };
    package.remove("sha256");auto neuron=package["neuron"].toObject();neuron.remove("sha256");
    neuron["graph"]=snapshot(neuron["graph"].toObject());
    auto definitions=neuron["class_definitions"].toArray();
    for(int i=0;i<definitions.size();++i)
    {auto value=definitions[i].toObject();value["snapshot"]=snapshot(value["snapshot"].toObject());definitions[i]=value;}
    neuron["class_definitions"]=definitions;package["neuron"]=neuron;
    package["dataset"]=snapshot(package["dataset"].toObject());return package;
}

template<class Owner> void Boundary(Scenario scenario)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires portable original native source/model primaries";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const std::string name=std::string(branch?"Branch":"Classic")+"_finalization_boundary_"+std::to_string(int(scenario));
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto recognition=job["source_recognition"].toObject(),solo=recognition["source_solo"].toObject();
    const auto implementation=job["implementation_id"].toString().toStdString();
    std::optional<NativeFinalizationBoundary> frozen;QJsonObject saved;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    const auto exercise=[&](auto storage,auto environment,auto model,auto owner) {
        EXPECT_THROW(CaptureNativeFinalizationBoundary(*owner,implementation),std::logic_error);
        // Initialize/reset the cold parent before restoring a completed learner.
        // A later explicit parent Reset would correctly reset its controller.
        model->Init();model->Reset();
        ASSERT_EQ(owner->ImportNativeLearnedState(solo,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();
        ASSERT_EQ(owner->NativeTrainingController().State(),NativeTrainingState::Finished);
        ASSERT_TRUE(owner->IsNativeProbeAtEditBoundary());
        if(scenario==Scenario::QueuedProbe)
        {
            auto q=owner->NativeTrainingController().Plan().probe;
            q.specification.runId=name;q.specification.trialId="reserved-not-yet-presented";
            owner->QueueNativeProbe(std::move(q));ASSERT_FALSE(owner->IsNativeProbeAtEditBoundary());
            const auto lifecycle=owner->ObserveLifecycle();
            EXPECT_THROW(CaptureNativeFinalizationBoundary(*owner,implementation),std::logic_error);
            EXPECT_TRUE(lifecycle.IsCurrent());EXPECT_EQ(owner->NativeProbeState(),NativeProbeStatus::Queued);
            return;
        }
        if(scenario==Scenario::Stopped)
        {
            auto plan=owner->NativeTrainingController().Plan();
            owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;
            owner->BeginNativeTraining(std::move(plan));
            ASSERT_TRUE(NativeTrainingIsActive(owner->NativeTrainingController()));
            owner->IsNeedToTrain=false;
            ASSERT_EQ(owner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
            ASSERT_TRUE(owner->IsNativeProbeAtEditBoundary());
            EXPECT_THROW(CaptureNativeFinalizationBoundary(*owner,implementation),std::logic_error);
            frozen.emplace(CaptureNativeFinalizationBoundary(*owner,implementation,true));
            EXPECT_TRUE(frozen->DiagnosticOnly());EXPECT_EQ(frozen->Solo()["kind"],QJsonValue("timelearner_stopped_state"));
            EXPECT_TRUE(frozen->Solo()["certificate"].isNull());
            EXPECT_EQ(frozen->Document()["training_outcome"],QJsonValue("external_stop"));
            saved=frozen->Document();return;
        }
        UEPtr<ExternalFinalizationFlag> flag;
        if(scenario==Scenario::Connected)
        {
            flag=new ExternalFinalizationFlag;flag->SetStorage(storage);flag->SetEnvironment(environment);flag->Default();
            flag->Name="ExternalFinalizationRequest";flag->Activity=true;flag->SetGlobalTimeStep(2000);
            UEPtr<UContainer> node=flag;ASSERT_NE(model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
            ASSERT_TRUE(owner->IsNeedToTrain.SetPointer(0,&flag->Value));
        }
        owner->EnablePostTrainTuning=true;owner->EnablePostTrainMidThreshold=false;
        owner->AutoCalibrateFixedLTZThreshold=true;owner->PostTrainTipResistanceMode=PostTrainTune::kPostTipKeepDone;
        owner->PostTrainSilentThreshold=2.;owner->PostTrainSyntheticFoilCount=3;owner->PostTrainTipSearchIters=7;
        const auto before=owner->ExportNativeLearnedState(implementation),controls=ReadNativeFinalizationControls(*owner);
        const auto lifecycle=owner->ObserveLifecycle();const double clock=environment->GetTime().GetDoubleTime();
        frozen.emplace(CaptureNativeFinalizationBoundary(*owner,implementation));saved=frozen->Document();
        const auto afterCapture=owner->ExportNativeLearnedState(implementation);
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_capture-comparison.json",
                {{"kind","native_finalization_capture_comparison"},{"schema_version",1},{"before",before},{"captured",frozen->Solo()},
                 {"after",afterCapture},{"semantic_equal",SemanticSolo(before)==SemanticSolo(frozen->Solo()) && SemanticSolo(before)==SemanticSolo(afterCapture)}});
        }
        EXPECT_FALSE(frozen->DiagnosticOnly());EXPECT_EQ(SemanticSolo(frozen->Solo()),SemanticSolo(before));EXPECT_EQ(frozen->Controls(),controls);
        EXPECT_TRUE(lifecycle.IsCurrent());EXPECT_DOUBLE_EQ(environment->GetTime().GetDoubleTime(),clock);
        EXPECT_EQ(SemanticSolo(afterCapture),SemanticSolo(before));
        EXPECT_EQ(ReadNativeFinalizationControls(*owner),controls);
        auto copy=frozen->Controls();copy["parameters"]=QJsonObject{};EXPECT_EQ(frozen->Controls(),controls);
        const auto parameters=frozen->Controls()["parameters"].toObject();
        EXPECT_EQ(parameters["IsNeedToTrain"].toBool(),bool(flag));EXPECT_TRUE(parameters["EnablePostTrainTuning"].toBool());
        EXPECT_FALSE(parameters["EnablePostTrainMidThreshold"].toBool());EXPECT_TRUE(parameters["AutoCalibrateFixedLTZThreshold"].toBool());
        if(flag)
        {
            EXPECT_TRUE(flag->Value.GetData());
            const auto binding=frozen->Controls()["bindings"].toObject()["IsNeedToTrain"].toObject();
            EXPECT_TRUE(binding["connected"].toBool());ASSERT_EQ(binding["sources"].toArray().size(),1);
            EXPECT_EQ(binding["sources"].toArray()[0].toObject()["property"],QJsonValue("Value"));
            EXPECT_EQ(binding["sources"].toArray()[0].toObject()["owner_path"],QJsonValue(QString::fromStdString(flag->GetFullName())));
            EXPECT_EQ(owner->ImportNativeRecognitionState(recognition,implementation).status,NativeModelBuildStatus::Rejected);
            EXPECT_TRUE(flag->Value.GetData());EXPECT_EQ(SemanticSolo(owner->ExportNativeLearnedState(implementation)),SemanticSolo(before));
            flag->Value=false; // External request changes, never a write by capture/import.
        }
        ASSERT_EQ(owner->ImportNativeRecognitionState(recognition,implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();owner->Reset();
        EXPECT_EQ(owner->NativeTrainingController().State(),NativeTrainingState::Idle);
        EXPECT_FALSE(owner->AutoCalibrateFixedLTZThreshold.GetData());EXPECT_FALSE(owner->EnablePostTrainTuning.GetData());
        EXPECT_FALSE(owner->IsNeedToTrain.GetData());EXPECT_EQ(frozen->Document(),saved);
        EXPECT_THROW(CaptureNativeFinalizationBoundary(*owner,implementation),std::logic_error);
        QJsonArray observations;
        for(const auto& value:job["trials"].toArray())
        {
            auto q=DecodeNativeCalibrationRequest(value.toObject());q.runId=name;
            owner->QueueNativeRecognitionTrial(q);std::optional<NativeRecognitionTrialObservation> result;
            const auto maximum=std::size_t(std::ceil(q.duration*2000))+5;
            for(std::size_t tick=0;!result && tick<maximum;++tick)
            {model->Calculate();environment->IncreaseModelTimeByStep();result=owner->TakeNativeRecognitionTrialResult();}
            ASSERT_TRUE(result);ASSERT_TRUE(result->complete);ASSERT_TRUE(result->valid)<<result->reason;
            EXPECT_EQ(result->modelBefore,recognition["model_revision"].toString().toStdString());
            EXPECT_EQ(result->modelAfter,result->modelBefore);observations.append(NativeRecognitionTrialJson(*result));
        }
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),recognition);EXPECT_EQ(frozen->Document(),saved);
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_replay.json",
                {{"kind","native_finalization_boundary_replay"},{"schema_version",1},{"boundary",saved},
                 {"recognition",recognition},{"observations",observations},{"recognition_success",QJsonValue(QJsonValue::Null)}});
        }
        owner->Default();EXPECT_EQ(frozen->Document(),saved);
    };
    EXPECT_EQ(NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "FinalizationBoundaryOwner",[&](auto storage,auto environment,auto model,auto owner) {
            exercise(storage,environment,model,owner);return ::testing::Test::HasFatalFailure()?2:0;
        }),0);
    if(frozen)
    {
        EXPECT_EQ(frozen->Document(),saved); // Survives real model teardown; owns no Rdk pointers.
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
        {
            ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",saved);
        }
    }
}
}
TEST(NativeFinalizationBoundary,ClassicSnapshot){Boundary<NNeuronTimeLearner>(Scenario::Snapshot);}
TEST(NativeFinalizationBoundary,BranchSnapshot){Boundary<NNeuronTimeLearnerBranch>(Scenario::Snapshot);}
TEST(NativeFinalizationBoundary,ClassicConnectedRequest){Boundary<NNeuronTimeLearner>(Scenario::Connected);}
TEST(NativeFinalizationBoundary,BranchConnectedRequest){Boundary<NNeuronTimeLearnerBranch>(Scenario::Connected);}
TEST(NativeFinalizationBoundary,ClassicPendingProbeRejects){Boundary<NNeuronTimeLearner>(Scenario::QueuedProbe);}
TEST(NativeFinalizationBoundary,BranchPendingProbeRejects){Boundary<NNeuronTimeLearnerBranch>(Scenario::QueuedProbe);}
TEST(NativeFinalizationBoundary,ClassicStoppedIsDiagnostic){Boundary<NNeuronTimeLearner>(Scenario::Stopped);}
TEST(NativeFinalizationBoundary,BranchStoppedIsDiagnostic){Boundary<NNeuronTimeLearnerBranch>(Scenario::Stopped);}
TEST(NativeFinalizationBoundary,PublicEnumsUseExplicitMapping)
{
    EXPECT_EQ(NativePostTuneModeFromPublic(PostTrainTune::kPostTipOff),NativePostTuneControllerMode::Off);
    EXPECT_EQ(NativePostTuneModeFromPublic(PostTrainTune::kPostTipCanonRmin),NativePostTuneControllerMode::CanonRmin);
    EXPECT_EQ(NativePostTuneModeFromPublic(PostTrainTune::kPostTipFlatLastR),NativePostTuneControllerMode::FlatLastR);
    EXPECT_EQ(NativePostTuneModeFromPublic(PostTrainTune::kPostTipKeepDone),NativePostTuneControllerMode::KeepDone);
    EXPECT_EQ(NativePostTuneModeFromPublic(PostTrainTune::kPostTipSearchSynthetic),NativePostTuneControllerMode::SearchSynthetic);
    EXPECT_EQ(NativePostTuneMetricFromPublic(PostTrainTune::kMidMetricLtz),NativePostTuneMetric::LTZone);
    EXPECT_EQ(NativePostTuneMetricFromPublic(PostTrainTune::kMidMetricSoma),NativePostTuneMetric::SomaSum);
    EXPECT_THROW(NativePostTuneModeFromPublic(77),std::invalid_argument);
    EXPECT_THROW(NativePostTuneMetricFromPublic(77),std::invalid_argument);
}

namespace {
template<class Owner> void ManagedFinalization(int calculateMode)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original native source/model primaries";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const auto name=std::string(branch?"Branch":"Classic")+"_managed_finalization_"+std::to_string(calculateMode);
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto original=job["source_recognition"].toObject();
    const auto implementation=job["implementation_id"].toString().toStdString();
    NativeThresholdGridSpec grid;grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    for(const auto& q:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(q.toObject()));
    auto specification=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
    specification.mode=NativePostTuneControllerMode::KeepDone;
    specification.canonicalFloor=specification.canonicalLast=0.;specification.resistanceBounds.clear();
    specification.finalization=NativePostTuneFinalization::KeepFixedThreshold;specification.weightProbeThreshold=2.;
    specification.calibration.maximumCandidates=0;specification.calibration.thresholds.clear();
    specification.calibration.confirmation.attemptId+="/"+name;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    EXPECT_EQ(NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "ManagedFinalizationOwner",[&](auto storage,auto environment,auto model,auto owner) {
        model->Init();model->Reset();
        EXPECT_EQ(owner->ImportNativeLearnedState(original["source_solo"].toObject(),implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();owner->CalculateMode=calculateMode;
        UEPtr<ExternalFinalizationFlag> flag=new ExternalFinalizationFlag;
        flag->SetStorage(storage);flag->SetEnvironment(environment);flag->Default();flag->Name="ManagedRequest";
        flag->Activity=true;flag->SetGlobalTimeStep(2000);UEPtr<UContainer> node=flag;
        EXPECT_NE(model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
        EXPECT_TRUE(owner->IsNeedToTrain.SetPointer(0,&flag->Value));
        owner->EnablePostTrainTuning=true;owner->AutoCalibrateFixedLTZThreshold=true;
        owner->EnablePostTrainMidThreshold=false;owner->PostTrainTipResistanceMode=PostTrainTune::kPostTipKeepDone;
        const auto boundary=CaptureNativeFinalizationBoundary(*owner,implementation);
        auto unsupported=boundary.Document();auto controls=unsupported["controls"].toObject();
        auto parameters=controls["parameters"].toObject();parameters["SyncCapacitanceTrim"]=1;
        controls["parameters"]=parameters;unsupported["controls"]=controls;
        try{CheckNativeFinalizationControls(*owner,unsupported);ADD_FAILURE()<<"Unsupported C-trim was accepted";}
        catch(const std::logic_error& error){EXPECT_EQ(std::string(error.what()),"native_finalization_c_trim_not_yet_supported");}
        EXPECT_EQ(ReadNativeFinalizationControls(*owner),boundary.Controls());
        const auto source=ConvertNativeSoloToRecognition(boundary.Solo(),DecodeNativeRecognitionSpec(original["conversion_spec"].toObject()),
            storage,environment,implementation);
        EXPECT_EQ(owner->ImportNativeRecognitionState(source,implementation).status,NativeModelBuildStatus::Rejected);
        const auto installed=owner->ImportNativeFinalizationState(source,implementation,boundary);
        EXPECT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
        if(installed.status!=NativeModelBuildStatus::Adopted)return 2;
        owner->Build();owner->Init();
        EXPECT_EQ(owner->NativeFinalizationIntent(),boundary.Document());
        NativePostTuneTransaction<Owner> transaction(*owner,specification,implementation);
        struct Detach {NativePostTuneTransaction<Owner>& t;~Detach(){t.InterruptOwnerLifecycle("fixture_exit");}} detach{transaction};
        transaction.Advance();std::size_t ticks=0;
        const auto maximum=std::size_t(job["maximum_model_ticks"].toDouble());
        while(!transaction.Done() && ticks<maximum) {
            model->Calculate();environment->IncreaseModelTimeByStep();++ticks;transaction.Advance();
            EXPECT_TRUE(flag->Value.GetData());EXPECT_TRUE(owner->IsNeedToTrain.GetData());
            EXPECT_TRUE(owner->EnablePostTrainTuning.GetData());EXPECT_TRUE(owner->AutoCalibrateFixedLTZThreshold.GetData());
            EXPECT_EQ(owner->CalculateMode.GetData(),calculateMode);
        }
        EXPECT_EQ(transaction.Status(),NativePostTuneTransactionStatus::WeightsSelected)<<transaction.Reason();
        if(transaction.Status()!=NativePostTuneTransactionStatus::WeightsSelected)return 2;
        EXPECT_EQ(owner->NativeFinalizationIntent(),boundary.Document());
        const auto final=owner->ExportNativeRecognitionState(implementation);
        EXPECT_EQ(owner->ReplaceNativeRecognitionState(original,implementation).status,NativeModelBuildStatus::Rejected);
        EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),final);
        flag->Value=false; // Only the real external provider clears the request.
        model->Calculate();environment->IncreaseModelTimeByStep();
        EXPECT_FALSE(flag->Value.GetData());EXPECT_FALSE(owner->IsNeedToTrain.GetData());
        EXPECT_THROW(owner->ExportNativeRecognitionState(implementation),std::logic_error);
        const auto stopped=owner->ReplaceNativeRecognitionState(final,implementation);
        EXPECT_EQ(stopped.status,NativeModelBuildStatus::Rejected);
        EXPECT_EQ(stopped.reason,"native_finalization_external_stop");
        // Explicit transition to frozen evaluation, never automatic success.
        const auto frozen=owner->ImportNativeRecognitionState(final,implementation);
        EXPECT_EQ(frozen.status,NativeModelBuildStatus::Adopted)<<frozen.reason;
        EXPECT_TRUE(owner->NativeFinalizationIntent().isEmpty());EXPECT_FALSE(flag->Value.GetData());
        if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
            EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",
                {{"kind","native_managed_finalization_control"},{"schema_version",1},{"boundary",boundary.Document()},
                 {"transaction",transaction.Report()},{"selected_package",final},{"external_stop_reason",QString::fromStdString(stopped.reason)},
                 {"calculate_mode",calculateMode},{"provider_after_stop",flag->Value.GetData()},
                 {"configured_phase_dispatch_implemented",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
        }
        return ::testing::Test::HasFailure()?2:0;
    }),0);
}
}
TEST(NativeFinalizationOwnership,ClassicAutomatic){ManagedFinalization<NNeuronTimeLearner>(0);}
TEST(NativeFinalizationOwnership,ClassicExternal){ManagedFinalization<NNeuronTimeLearner>(1);}
TEST(NativeFinalizationOwnership,BranchAutomatic){ManagedFinalization<NNeuronTimeLearnerBranch>(0);}
TEST(NativeFinalizationOwnership,BranchExternal){ManagedFinalization<NNeuronTimeLearnerBranch>(1);}
