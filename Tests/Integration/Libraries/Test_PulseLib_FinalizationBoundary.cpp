#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NNeuronPostTrainTune.h"
#include "TimeLearner/NativeFinalizationBoundary.h"
#include "TimeLearner/NativeFinalizationControlPolicy.h"
#include "TimeLearner/NativeTrainingBindings.h"
#include "TimeLearner/NativeLiveFinalization.h"
#include "TimeLearner/ModelArchive.h"
#include "../Support/ConsoleLikeInit.h"
#include "../../../App/NeuroModelerConsole/TimeLearnerJobSupport.h"
#include <cstdlib>
#include <optional>
#include <type_traits>
#include <fstream>
#include <iomanip>
#include <locale>
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
        const auto capturedSummary=frozen->TrainingSummary();
        EXPECT_EQ(capturedSummary,EncodeNativeTrainingState(owner->NativeTrainingController(),
            frozen->Solo()["model_revision"].toString().toStdString(),owner->ReadNativeParameters()));
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
        EXPECT_EQ(frozen->TrainingSummary(),capturedSummary); // Original solo metadata survives import/reset as immutable DATA.
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
    const auto ownerResult=NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "FinalizationBoundaryOwner",[&](auto storage,auto environment,auto model,auto owner) {
            exercise(storage,environment,model,owner);return ::testing::Test::HasFatalFailure()?2:0;
        });
    EXPECT_EQ(ownerResult,0);
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
template<class Owner> void ManagedFinalization(int calculateMode,bool owned=false,bool connected=true,bool interrupted=false,bool clockGap=false)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original native source/model primaries";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const auto name=std::string(branch?"Branch":"Classic")+"_managed_finalization_"+std::to_string(calculateMode)+(owned?(connected?"_owned_connected":"_owned_local"):"")+(interrupted?"_reset":"")+(clockGap?"_clock_gap":"");
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
    const auto ownerResult=NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "ManagedFinalizationOwner",[&](auto storage,auto environment,auto model,auto owner) {
        model->Init();model->Reset();
        EXPECT_EQ(owner->ImportNativeLearnedState(original["source_solo"].toObject(),implementation).status,NativeModelBuildStatus::Adopted);
        owner->Build();owner->Init();owner->CalculateMode=calculateMode;
        UEPtr<ExternalFinalizationFlag> flag=new ExternalFinalizationFlag;
        flag->SetStorage(storage);flag->SetEnvironment(environment);flag->Default();flag->Name="ManagedRequest";
        flag->Activity=true;flag->SetGlobalTimeStep(2000);UEPtr<UContainer> node=flag;
        EXPECT_NE(model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
        if(connected)EXPECT_TRUE(owner->IsNeedToTrain.SetPointer(0,&flag->Value));
        else {
            // This fixture restores administrative request state around an
            // imported finished Solo snapshot. The public false -> true setter
            // intentionally starts new training and invalidates that boundary.
            owner->IsNeedToTrain.SetDataDirect(true);
        }
        owner->EnablePostTrainTuning=true;owner->AutoCalibrateFixedLTZThreshold=true;
        owner->EnablePostTrainMidThreshold=false;owner->PostTrainTipResistanceMode=PostTrainTune::kPostTipKeepDone;
        const auto boundary=CaptureNativeFinalizationBoundary(*owner,implementation);
        const auto repeated=clockGap?CaptureNativeFinalizationBoundary(*owner,implementation).Document():QJsonObject{};
        const double capturedTime=environment->GetTime().GetDoubleTime();
        if(clockGap)environment->IncreaseModelTimeByStep(); // no Calculate or structural edit
        const double entryTime=environment->GetTime().GetDoubleTime();
        if(clockGap) {
            EXPECT_NEAR(entryTime-capturedTime,1./2000.,1e-12);
            const auto afterClock=CaptureNativeFinalizationBoundary(*owner,implementation).Document();
            if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"-projection.json",
                    {{"initial",boundary.Document()},{"repeat_without_clock",repeated},{"after_clock",afterClock}});
            }
            EXPECT_TRUE(afterClock==repeated)<<"Boundary changed after clock-only advance";
        }
        auto unsupported=boundary.Document();auto controls=unsupported["controls"].toObject();
        auto parameters=controls["parameters"].toObject();parameters["SyncCapacitanceTrim"]=1;
        controls["parameters"]=parameters;unsupported["controls"]=controls;
        try{CheckNativeFinalizationControls(*owner,unsupported);ADD_FAILURE()<<"Unsupported C-trim was accepted";}
        catch(const std::logic_error& error){EXPECT_EQ(std::string(error.what()),"native_finalization_c_trim_not_yet_supported");}
        EXPECT_EQ(ReadNativeFinalizationControls(*owner),boundary.Controls());
        const auto source=ConvertNativeSoloToRecognition(boundary.Solo(),DecodeNativeRecognitionSpec(original["conversion_spec"].toObject()),
            storage,environment,implementation);
        // Ordinary frozen import owns local mirrors and may deliberately clear
        // them. Only a live connected provider must reject that transition.
        if(connected)EXPECT_EQ(owner->ImportNativeRecognitionState(source,implementation).status,NativeModelBuildStatus::Rejected);
        const auto installed=owner->ImportNativeFinalizationState(source,implementation,boundary);
        EXPECT_EQ(installed.status,NativeModelBuildStatus::Adopted)<<installed.reason;
        if(installed.status!=NativeModelBuildStatus::Adopted)return 2;
        owner->Build();owner->Init();
        EXPECT_EQ(owner->NativeFinalizationIntent(),boundary.Document());
        if(clockGap) {
            EXPECT_TRUE(owner->IsNativeRecognitionTrialIdle());
            EXPECT_TRUE(flag->Value.GetData());
            const auto effective=owner->ExportNativeRecognitionState(implementation);
            EXPECT_EQ(effective,source);
            if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",
                    {{"kind","native_finalization_clock_handoff"},{"schema_version",1},
                     {"boundary",boundary.Document()},{"recognition_package",effective},
                     {"calculate_mode",calculateMode},{"capture_time",capturedTime},{"entry_time",entryTime},
                     {"clock_only_advance",true},{"live_train_handoff_implemented",false},
                     {"scientific_verdict",QJsonValue(QJsonValue::Null)}});
            }
            return ::testing::Test::HasFailure()?2:0;
        }
        if(owned) {
            owner->BeginNativePostTunePhase(specification,implementation);
            EXPECT_THROW(owner->BeginNativePostTunePhase(specification,implementation),std::logic_error);
            EXPECT_THROW(owner->TakeNativeRecognitionTrialResult(),std::logic_error);
            EXPECT_EQ(owner->ReplaceNativeRecognitionState(source,implementation).reason,"native_owned_post_tune_owns_model");
            std::size_t ticks=0;
            const auto maximum=std::size_t(job["maximum_model_ticks"].toDouble());
            while(!owner->NativePostTunePhaseDone() && ticks<maximum) {
                model->Calculate();environment->IncreaseModelTimeByStep();++ticks;
                if(interrupted && ticks==3)owner->Reset();
                EXPECT_TRUE(flag->Value.GetData());
                EXPECT_TRUE(owner->EnablePostTrainTuning.GetData());
                EXPECT_TRUE(owner->AutoCalibrateFixedLTZThreshold.GetData());
                EXPECT_EQ(owner->CalculateMode.GetData(),calculateMode);
            }
            EXPECT_TRUE(owner->NativePostTunePhaseDone());
            const auto report=owner->NativePostTunePhaseReport();
            const auto execution=owner->NativePostTunePhaseExecution();
            EXPECT_EQ(execution["advance_phase"],QJsonValue("owner_before_children"));
            const auto times=execution["advance_times"].toArray();
            EXPECT_EQ(times.size(),int(ticks));
            for(int i=1;i<times.size();++i)EXPECT_NEAR(times[i].toDouble()-times[i-1].toDouble(),1./2000.,1e-12);
            QJsonObject selected;
            if(interrupted) {
                EXPECT_EQ(report["status"],QJsonValue("recovery_required"));
                EXPECT_EQ(report["reason"],QJsonValue("learner_reset"));
            } else {
                EXPECT_EQ(report["status"],QJsonValue("weights_selected"));
                EXPECT_FALSE(execution["internal_lifecycle"].toObject().isEmpty());
                EXPECT_EQ(owner->IsNeedToTrain.GetData(),connected || calculateMode!=0);
                EXPECT_EQ(owner->NativeFinalizationIntent(),boundary.Document());
                selected=owner->ExportNativeRecognitionState(implementation);
                EXPECT_THROW(owner->BeginNativePostTunePhase(specification,implementation),std::logic_error);
                // Closing the administrative request never writes the real provider.
                if(connected)flag->Value=false;else owner->IsNeedToTrain=false;
                model->Calculate();environment->IncreaseModelTimeByStep();
                EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),selected);
            }
            if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",
                    {{"kind","native_owned_post_tune_control"},{"schema_version",1},{"boundary",boundary.Document()},
                     {"transaction",report},{"execution",execution},{"selected_package",selected},
                     {"calculate_mode",calculateMode},{"connected",connected},{"interrupted",interrupted},
                     {"configured_phase_dispatch_implemented",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
            }
            return ::testing::Test::HasFailure()?2:0;
        }
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
    });
    EXPECT_EQ(ownerResult,0);
}
}
TEST(NativeFinalizationOwnership,ClassicAutomatic){ManagedFinalization<NNeuronTimeLearner>(0);}
TEST(NativeFinalizationOwnership,ClassicExternal){ManagedFinalization<NNeuronTimeLearner>(1);}
TEST(NativeFinalizationOwnership,BranchAutomatic){ManagedFinalization<NNeuronTimeLearnerBranch>(0);}
TEST(NativeFinalizationOwnership,BranchExternal){ManagedFinalization<NNeuronTimeLearnerBranch>(1);}

TEST(NativeOwnedPostTune,ClassicAutomaticConnected){ManagedFinalization<NNeuronTimeLearner>(0,true,true);}

TEST(NativeOwnedPostTune,ClassicAutomaticLocal){ManagedFinalization<NNeuronTimeLearner>(0,true,false);}

TEST(NativeOwnedPostTune,ClassicExternalConnected){ManagedFinalization<NNeuronTimeLearner>(1,true,true);}

TEST(NativeOwnedPostTune,ClassicExternalLocal){ManagedFinalization<NNeuronTimeLearner>(1,true,false);}

TEST(NativeOwnedPostTune,ClassicResetInterrupt){ManagedFinalization<NNeuronTimeLearner>(0,true,true,true);}

TEST(NativeOwnedPostTune,BranchAutomaticConnected){ManagedFinalization<NNeuronTimeLearnerBranch>(0,true,true);}

TEST(NativeOwnedPostTune,BranchAutomaticLocal){ManagedFinalization<NNeuronTimeLearnerBranch>(0,true,false);}

TEST(NativeOwnedPostTune,BranchExternalConnected){ManagedFinalization<NNeuronTimeLearnerBranch>(1,true,true);}

TEST(NativeOwnedPostTune,BranchExternalLocal){ManagedFinalization<NNeuronTimeLearnerBranch>(1,true,false);}

TEST(NativeOwnedPostTune,BranchResetInterrupt){ManagedFinalization<NNeuronTimeLearnerBranch>(0,true,true,true);}

TEST(NativeFinalizationClockHandoff,ClassicAutomatic){ManagedFinalization<NNeuronTimeLearner>(0,false,true,false,true);}
TEST(NativeFinalizationClockHandoff,ClassicExternal){ManagedFinalization<NNeuronTimeLearner>(1,false,true,false,true);}
TEST(NativeFinalizationClockHandoff,BranchAutomatic){ManagedFinalization<NNeuronTimeLearnerBranch>(0,false,true,false,true);}
TEST(NativeFinalizationClockHandoff,BranchExternal){ManagedFinalization<NNeuronTimeLearnerBranch>(1,false,true,false,true);}

namespace {
enum class LiveScenario { Fixed, Calibrate, Stopped, ControlDrift, ResetQueued, StopQueued, InvalidDesign, Multirate, CancelArmed, CancelTraining, CancelQueued, CancelPostTune };
template<class Owner> void LiveFinalization(int mode,bool connected,LiveScenario scenario)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    const auto coldDirectory=std::getenv("TIMELEARNER_LIVE_COLD_SOURCE");
    const auto calibrationDirectory=std::getenv("TIMELEARNER_LIVE_CALIBRATION_SOURCE");
    if(!directory || !coldDirectory || !calibrationDirectory)
        GTEST_SKIP()<<"Requires separate saved-state, cold-training and calibration declarations";
    constexpr bool branch=std::is_same_v<Owner,NNeuronTimeLearnerBranch>;
    const std::string name=std::string(branch?"Branch":"Classic")+"_live_finalization_"+
        std::to_string(mode)+(connected?"_connected":"_local")+"_"+std::to_string(int(scenario));
    const QDir root(QString::fromLocal8Bit(directory));
    const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
    const auto implementation=job["implementation_id"].toString().toStdString();
    const QString coldName=branch?"Branch-v1":"Classic-v1";
    const QDir coldRoot(QString::fromLocal8Bit(coldDirectory));
    const auto coldJob=NmsdkWorker::ReadDocument(coldRoot.filePath(coldName+"-train/input/job.json"));
    const auto evaluationJob=NmsdkWorker::ReadDocument(coldRoot.filePath(coldName+"-frozen/input/job.json"));
    const auto calibrationJob=NmsdkWorker::ReadDocument(QDir(QString::fromLocal8Bit(calibrationDirectory)).filePath(
        coldName+"/measured-grid-job.json"));
    for(const auto& declaration:{coldJob,evaluationJob,calibrationJob}) {
        NmsdkWorker::Require(NmsdkWorker::Signed(declaration)==declaration,"live_fixture_job_digest_mismatch");
        NmsdkWorker::Require(declaration["implementation_id"]==job["implementation_id"],"live_fixture_implementation_mismatch");
    }
    NmsdkWorker::Require(coldJob["kind"]==QJsonValue("timelearner_native_training_job") &&
        coldJob["schema_version"]==QJsonValue(1),"live_fixture_requires_cold_training_declaration");
    auto configuration=DecodeConfiguredNativeTraining(coldJob["configuration"].toObject());
    configuration.runId=name;
    if(scenario==LiveScenario::Stopped)configuration.maximumModelSeconds=1./2000.;
    NativeThresholdGridSpec grid;grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    grid.confirmation.attemptId=name+"/post_tune";
    for(const auto& value:evaluationJob["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(value.toObject()));
    if(scenario==LiveScenario::InvalidDesign) {
        EXPECT_GE(grid.trials.size(),2u);
        for(std::size_t i=1;i<grid.trials.size();++i) {
            grid.trials[i]=grid.trials.front();
            grid.trials[i].trialId+="/additional-target/"+std::to_string(i);
        }
    }
    if(scenario==LiveScenario::Calibrate) {
        for(const auto& value:calibrationJob["thresholds"].toArray())grid.thresholds.push_back(value.toDouble());
        grid.maximumCandidates=std::size_t(calibrationJob["maximum_candidates"].toDouble());
    }
    auto spec=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
    spec.mode=NativePostTuneControllerMode::KeepDone;spec.canonicalFloor=spec.canonicalLast=0.;spec.resistanceBounds.clear();
    spec.finalization=scenario==LiveScenario::Calibrate?NativePostTuneFinalization::Calibrate:NativePostTuneFinalization::KeepFixedThreshold;
    spec.weightProbeThreshold=2.;
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    const auto ownerResult=NmsdkWorker::WithFreshOwner<Owner>(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner",2000,
        "LiveFinalizationOwner",[&](auto storage,auto environment,auto model,auto owner) {
        owner->ControllerVersion=2;owner->CalculateMode=mode;owner->StructureBuildMode=1;
        owner->EnablePostTrainTuning=true;owner->AutoCalibrateFixedLTZThreshold=false;owner->SyncCapacitanceTrim=0;
        owner->EnablePostTrainMidThreshold=scenario==LiveScenario::Calibrate;
        owner->PostTrainTipResistanceMode=PostTrainTune::kPostTipKeepDone;owner->PostTrainMidMetric=int(spec.metric);
        owner->PostTrainSilentThreshold=2.;owner->UseCandidateMidOnNonSeparableTest=false;
        owner->ConfigureNativeFinalization({DecodeNativeRecognitionSpec(job["source_recognition"].toObject()["conversion_spec"].toObject()),spec,implementation});
        owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact).toStdString();
        owner->IsNeedToTrain=false;owner->Build();owner->Init();model->Init();model->Reset();
        EXPECT_TRUE(owner->NativeModelEditFailure().empty())<<owner->NativeModelEditFailure();
        if(!owner->NativeModelEditFailure().empty())return 2;
        EXPECT_FALSE(owner->HasNativeRecognitionState());
        EXPECT_EQ(owner->NativeTrainingController().State(),NativeTrainingState::Idle);
        const auto initial=owner->ReadNativeParameters();
        for(std::size_t i=0;i<initial.size();++i) {
            EXPECT_EQ(initial[i].length,configuration.model.inputs[i].attachment);
            EXPECT_EQ(initial[i].synapses,configuration.model.inputs[i].synapses);
        }
        UEPtr<ExternalFinalizationFlag> flag;
        if(connected) {
            flag=new ExternalFinalizationFlag;flag->SetStorage(storage);flag->SetEnvironment(environment);flag->Default();
            flag->Name="LiveRequest";flag->Activity=true;flag->SetGlobalTimeStep(2000);
            UEPtr<UContainer> node=flag;EXPECT_NE(model->AddComponent(node),ForbiddenId);flag->Init();flag->Value=true;
            EXPECT_TRUE(owner->IsNeedToTrain.SetPointer(0,&flag->Value));
        }
        const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
        if(output) {
            EXPECT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
            NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_source_declarations.json",
                {{"kind","native_live_fixture_declarations"},{"schema_version",1},
                 {"training_job_sha256",coldJob["sha256"]},{"evaluation_job_sha256",evaluationJob["sha256"]},
                 {"calibration_job_sha256",calibrationJob["sha256"]},{"post_tune_controls_job_sha256",job["sha256"]},
                 {"cold_training",true},{"saved_model_installed",false}});
        }
        std::vector<NativeProbeSample> samples;std::size_t trial=0;
        owner->SetConfiguredNativeEvidenceSinks({[&](const auto&,const auto&){samples.clear();},
            [&](const auto& sample){samples.push_back(sample);},[&](const auto& result) {
                ++trial;if(!output)return;
                const auto stem=name+((scenario==LiveScenario::Stopped || scenario==LiveScenario::CancelTraining)?"_stopped_trial_":"_state_trial_")+std::to_string(trial);
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(stem)+".json",EncodeNativeProbeEvidence(result));
                const auto path=QDir(QString::fromLocal8Bit(output)).filePath(QString::fromStdString(stem)+".csv");
                std::ofstream stream(path.toStdString());stream.imbue(std::locale::classic());stream<<std::setprecision(17);
                stream<<"time,stimulus";for(std::size_t i=0;i<(branch?1:initial.size());++i)stream<<",soma"<<i;stream<<'\n';
                for(const auto& sample:samples) {
                    stream<<sample.time<<','<<sample.stimulus;for(double v:sample.potentials)stream<<','<<v;stream<<'\n';
                }
                EXPECT_TRUE(stream.good());
            }});
        if(scenario==LiveScenario::Multirate)
            owner->template GetComponentL<NPulseNeuron>("Neuron",true)->SetGlobalTimeStep(1000);
        if(!connected)owner->IsNeedToTrain=true;
        if(scenario==LiveScenario::CancelArmed)owner->CancelNativeLiveFinalization("fixture_cancel");
        bool queued=false,intervention=false;QJsonObject summary;
        std::size_t ticks=0;const std::size_t maximum=200000;
        while(!owner->NativeLiveFinalizationDone() && ticks<maximum) {
            model->Calculate();environment->IncreaseModelTimeByStep();++ticks;
            if(scenario==LiveScenario::CancelTraining && ticks==2) {
                const double time=environment->GetTime().GetDoubleTime();
                owner->CancelNativeLiveFinalization("fixture_cancel");intervention=true;
                EXPECT_EQ(environment->GetTime().GetDoubleTime(),time);
            }
            const auto live=owner->NativeLiveFinalizationReport();
            if(live["status"]==QJsonValue("queued") && !queued) {
                queued=true;EXPECT_FALSE(owner->HasNativeRecognitionState());
                EXPECT_TRUE(owner->IsNeedToTrain.GetData());
                const auto solo=live["boundary"].toObject()["source_solo"].toObject();
                EXPECT_EQ(solo["kind"],QJsonValue("timelearner_completed_state"));
                summary=EncodeNativeTrainingState(owner->NativeTrainingController(),solo["model_revision"].toString().toStdString(),owner->ReadNativeParameters());
                if(output) {
                    NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_learned_state.json",solo);
                    NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_learned_summary.json",summary);
                }
                if(scenario==LiveScenario::CancelQueued){owner->CancelNativeLiveFinalization("fixture_cancel");intervention=true;}
                if(scenario==LiveScenario::ControlDrift){owner->PostTrainMidMetric=(int(spec.metric)+1)%3;intervention=true;}
                if(scenario==LiveScenario::ResetQueued){owner->Reset();intervention=true;}
                if(scenario==LiveScenario::StopQueued){if(connected)flag->Value=false;else owner->IsNeedToTrain=false;intervention=true;}
            }
            if(scenario==LiveScenario::CancelPostTune && live["status"]==QJsonValue("post_tune")) {
                const double time=environment->GetTime().GetDoubleTime();
                owner->CancelNativeLiveFinalization("fixture_cancel");intervention=true;
                EXPECT_EQ(environment->GetTime().GetDoubleTime(),time);
            }
            if(connected && scenario!=LiveScenario::StopQueued)EXPECT_TRUE(flag->Value.GetData());
        }
        EXPECT_TRUE(owner->NativeLiveFinalizationDone())<<owner->NativeLiveFinalizationReport()["reason"].toString().toStdString();
        const auto live=owner->NativeLiveFinalizationReport();QJsonObject final;NativeCalibrationMatrix frozen;
        if(scenario==LiveScenario::CancelArmed || scenario==LiveScenario::CancelQueued) {
            EXPECT_EQ(queued,scenario==LiveScenario::CancelQueued);
            EXPECT_FALSE(owner->HasNativeRecognitionState());
            EXPECT_EQ(live["status"],QJsonValue("cancelled"));EXPECT_EQ(live["reason"],QJsonValue("fixture_cancel"));
            if(scenario==LiveScenario::CancelArmed) {
                EXPECT_EQ(trial,0u);EXPECT_TRUE(live["boundary"].isNull());EXPECT_TRUE(live["training_request"].toObject().isEmpty());
                EXPECT_EQ(owner->NativeTrainingController().State(),NativeTrainingState::Idle);
            } else EXPECT_TRUE(intervention);
        } else if(scenario==LiveScenario::CancelTraining) {
            EXPECT_TRUE(intervention);EXPECT_FALSE(queued);EXPECT_FALSE(owner->HasNativeRecognitionState());
            EXPECT_EQ(live["status"],QJsonValue("stopped_diagnostic"));
            EXPECT_EQ(owner->NativeTrainingController().Outcome(),TrainingStatus::ExternalStop);
            EXPECT_FALSE(owner->NativeTrainingController().Certificate().has_value());
            EXPECT_GT(trial,0u);EXPECT_FALSE(owner->NativeTrainingController().ObservedPackets().empty());
            EXPECT_TRUE(live["boundary"].toObject()["diagnostic_only"].toBool());
            EXPECT_TRUE(live["entry_model_time"].isNull());
            const auto stopped=live["boundary"].toObject()["source_solo"].toObject();
            summary=EncodeNativeTrainingState(owner->NativeTrainingController(),stopped["model_revision"].toString().toStdString(),owner->ReadNativeParameters());
            if(output) {
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_stopped_state.json",stopped);
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_stopped_summary.json",summary);
            }
        } else if(scenario==LiveScenario::CancelPostTune) {
            EXPECT_TRUE(intervention);EXPECT_TRUE(queued);EXPECT_TRUE(owner->HasNativeRecognitionState());
            EXPECT_EQ(live["status"],QJsonValue("completed"));
            const auto phase=live["post_tune"].toObject();
            EXPECT_EQ(phase["status"],QJsonValue("cancelled"));EXPECT_TRUE(phase["source_restored"].toBool());
            EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),phase["source_recognition"].toObject());
            EXPECT_TRUE(live["post_tune_execution"].toObject()["done"].toBool());
        } else if(scenario==LiveScenario::InvalidDesign || scenario==LiveScenario::Multirate) {
            EXPECT_FALSE(queued);EXPECT_FALSE(owner->HasNativeRecognitionState());EXPECT_EQ(trial,0u);
            EXPECT_EQ(live["status"],QJsonValue("failed"));
            EXPECT_EQ(live["reason"],QJsonValue(scenario==LiveScenario::InvalidDesign?
                "unbalanced_live_finalization_design":"native_owned_post_tune_requires_uniform_frequency_tree"));
        } else if(scenario==LiveScenario::Stopped) {
            EXPECT_FALSE(queued);EXPECT_FALSE(owner->HasNativeRecognitionState());
            EXPECT_EQ(live["status"],QJsonValue("stopped_diagnostic"));
            EXPECT_TRUE(live["boundary"].toObject()["diagnostic_only"].toBool());
            const auto stopped=live["boundary"].toObject()["source_solo"].toObject();
            summary=EncodeNativeTrainingState(owner->NativeTrainingController(),stopped["model_revision"].toString().toStdString(),owner->ReadNativeParameters());
            if(output) {
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_stopped_state.json",stopped);
                NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+"_stopped_summary.json",summary);
            }
        } else if(scenario==LiveScenario::ControlDrift || scenario==LiveScenario::StopQueued || scenario==LiveScenario::ResetQueued) {
            EXPECT_TRUE(queued);EXPECT_TRUE(intervention);EXPECT_FALSE(owner->HasNativeRecognitionState());
            EXPECT_EQ(live["status"],QJsonValue(scenario==LiveScenario::ResetQueued?"interrupted":"failed"));
        } else {
            EXPECT_TRUE(queued);EXPECT_EQ(live["status"],QJsonValue("completed"));
            EXPECT_TRUE(owner->HasNativeRecognitionState());
            EXPECT_FALSE(live["post_tune_execution"].toObject()["advance_times"].toArray().isEmpty());
            EXPECT_EQ(owner->IsNeedToTrain.GetData(),connected || mode!=0);
            final=owner->ExportNativeRecognitionState(implementation);
            for(auto q:grid.trials) {
                q.runId=name+"/frozen-replay";q.trialId+="/frozen-replay";
                owner->QueueNativeRecognitionTrial(q);std::optional<NativeRecognitionTrialObservation> observed;
                for(std::size_t i=0;i<5000 && !observed;++i) {
                    model->Calculate();environment->IncreaseModelTimeByStep();observed=owner->TakeNativeRecognitionTrialResult();
                }
                EXPECT_TRUE(observed.has_value());if(!observed)return 2;
                EXPECT_TRUE(observed->complete);EXPECT_TRUE(observed->valid);
                EXPECT_EQ(owner->ExportNativeRecognitionState(implementation),final);
                frozen.requests.push_back(q);frozen.observations.push_back(std::move(*observed));
            }
        }
        if(int(scenario)>=int(LiveScenario::CancelArmed)) {
            // Cancel is idempotent, does not tick, never writes a connected flag,
            // and an unchanged true provider cannot restart the cancelled plan.
            const auto terminal=owner->NativeLiveFinalizationReport();
            const double time=environment->GetTime().GetDoubleTime();
            const auto trialCount=trial;owner->CancelNativeLiveFinalization("duplicate_cancel");
            EXPECT_EQ(environment->GetTime().GetDoubleTime(),time);
            EXPECT_EQ(owner->NativeLiveFinalizationReport(),terminal);
            for(int i=0;i<2;++i){model->Calculate();environment->IncreaseModelTimeByStep();}
            EXPECT_EQ(owner->NativeLiveFinalizationReport(),terminal);EXPECT_EQ(trial,trialCount);
            if(connected)EXPECT_TRUE(flag->Value.GetData());
            if(mode==0 && !connected)EXPECT_FALSE(owner->IsNeedToTrain.GetData());
        }
        if(output)NmsdkWorker::Write(QString::fromLocal8Bit(output),QString::fromStdString(name)+".json",
            {{"kind","native_live_finalization_control"},{"schema_version",1},{"scenario",int(scenario)},
             {"calculate_mode",mode},{"connected",connected},{"cold_training",true},{"live",live},
             {"training_summary",summary},{"final_package",final},{"frozen_replay",EncodeNativeCalibrationMatrix(frozen)},
             {"scientific_verdict",QJsonValue(QJsonValue::Null)}});
        return ::testing::Test::HasFailure()?2:0;
    },[&](auto storage,auto environment) {
        // The same cold-job storage registration as the production Console.
        // No saved learned graph, parameters or controller is installed.
        for(const auto& value:coldJob["profile_archives"].toArray()) {
            const auto profile=NmsdkWorker::Object(value);
            const auto imageImplementation=NmsdkWorker::Text(NmsdkWorker::Object(profile["metadata"])["implementation_id"]);
            NmsdkTools::PrepareModelArchive(profile,storage,environment,QString::fromStdString(imageImplementation));
        }
    });
    EXPECT_EQ(ownerResult,0);
}
}
TEST(NativeLiveFinalization,ClassicAutomaticFixed){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::Fixed);}
TEST(NativeLiveFinalization,BranchAutomaticFixed){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::Fixed);}
TEST(NativeLiveFinalization,ClassicConnectedCalibrate){LiveFinalization<NNeuronTimeLearner>(1,true,LiveScenario::Calibrate);}
TEST(NativeLiveFinalization,BranchConnectedCalibrate){LiveFinalization<NNeuronTimeLearnerBranch>(1,true,LiveScenario::Calibrate);}
TEST(NativeLiveFinalization,ClassicStopped){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::Stopped);}
TEST(NativeLiveFinalization,BranchStopped){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::Stopped);}
TEST(NativeLiveFinalization,ClassicQueuedControlDrift){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::ControlDrift);}
TEST(NativeLiveFinalization,BranchQueuedControlDrift){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::ControlDrift);}
TEST(NativeLiveFinalization,ClassicQueuedReset){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::ResetQueued);}
TEST(NativeLiveFinalization,BranchQueuedReset){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::ResetQueued);}
TEST(NativeLiveFinalization,ClassicQueuedStop){LiveFinalization<NNeuronTimeLearner>(1,true,LiveScenario::StopQueued);}
TEST(NativeLiveFinalization,BranchQueuedStop){LiveFinalization<NNeuronTimeLearnerBranch>(1,true,LiveScenario::StopQueued);}
TEST(NativeLiveFinalization,ClassicInvalidDesign){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::InvalidDesign);}
TEST(NativeLiveFinalization,BranchInvalidDesign){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::InvalidDesign);}
TEST(NativeLiveFinalization,ClassicMultirate){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::Multirate);}
TEST(NativeLiveFinalization,BranchMultirate){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::Multirate);}

TEST(NativeLiveFinalization,ClassicCancelArmed){LiveFinalization<NNeuronTimeLearner>(1,true,LiveScenario::CancelArmed);}

TEST(NativeLiveFinalization,BranchCancelArmed){LiveFinalization<NNeuronTimeLearnerBranch>(1,true,LiveScenario::CancelArmed);}

TEST(NativeLiveFinalization,ClassicCancelTraining){LiveFinalization<NNeuronTimeLearner>(0,false,LiveScenario::CancelTraining);}

TEST(NativeLiveFinalization,BranchCancelTraining){LiveFinalization<NNeuronTimeLearnerBranch>(0,false,LiveScenario::CancelTraining);}

TEST(NativeLiveFinalization,ClassicCancelQueued){LiveFinalization<NNeuronTimeLearner>(1,true,LiveScenario::CancelQueued);}

TEST(NativeLiveFinalization,BranchCancelQueued){LiveFinalization<NNeuronTimeLearnerBranch>(1,true,LiveScenario::CancelQueued);}

TEST(NativeLiveFinalization,ClassicCancelPostTune){LiveFinalization<NNeuronTimeLearner>(1,true,LiveScenario::CancelPostTune);}

TEST(NativeLiveFinalization,BranchCancelPostTune){LiveFinalization<NNeuronTimeLearnerBranch>(1,true,LiveScenario::CancelPostTune);}

TEST(NativeLiveFinalizationPlanCodec,ActualDesignRoundtripAndMalformedDeclarations)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_FIXED_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires actual persisted PostTune designs";
    const QDir root(QString::fromLocal8Bit(directory));QJsonArray plans;int rejected=0;
    for(bool branch:{false,true})for(bool calibrate:{false,true}) {
        const auto job=NmsdkWorker::ReadDocument(root.filePath(branch?"Branch-synthetic/input/job.json":"Classic-auto_metric/input/job.json"));
        NativeThresholdGridSpec grid;
        grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
        for(const auto& q:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(q.toObject()));
        if(calibrate) {
            for(const auto& t:job["thresholds"].toArray())grid.thresholds.push_back(t.toDouble());
            grid.maximumCandidates=std::size_t(job["maximum_candidates"].toDouble());
        } else grid.maximumCandidates=0;
        auto post=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
        post.mode=NativePostTuneControllerMode::KeepDone;post.canonicalFloor=post.canonicalLast=0.;post.resistanceBounds.clear();
        post.finalization=calibrate?NativePostTuneFinalization::Calibrate:NativePostTuneFinalization::KeepFixedThreshold;
        post.weightProbeThreshold=2.;
        NativeLiveFinalizationSpec spec{DecodeNativeRecognitionSpec(job["source_recognition"].toObject()["conversion_spec"].toObject()),
            post,job["implementation_id"].toString().toStdString()};
        const auto plan=EncodeNativeLiveFinalizationSpec(spec);
        const auto persisted=QJsonDocument::fromJson(QJsonDocument(plan).toJson(QJsonDocument::Compact)).object();
        EXPECT_EQ(EncodeNativeLiveFinalizationSpec(DecodeNativeLiveFinalizationSpec(persisted)),plan);
        plans.append(plan);
        const auto resign=[](QJsonObject value) {value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;};
        for(int mutation=0;mutation<8;++mutation) {
            auto bad=plan;
            switch(mutation) {
            case 0:bad["unknown_field"]=true;break;
            case 1:bad["maximum_calibration_candidates"]=1.5;break;
            case 2:bad["maximum_calibration_candidates"]=9007199254740992.;break;
            case 3:bad["thresholds"]=QJsonArray{"NaN"};break;
            case 4:bad["schema_version"]=true;break;
            case 5:bad["trials"]=QJsonArray{QJsonObject{}};break;
            case 6:bad["implementation_id"]="";break;
            case 7:bad["sha256"]="invalid_digest";break;
            }
            if(mutation!=7)bad=resign(bad);
            EXPECT_THROW(DecodeNativeLiveFinalizationSpec(bad),std::invalid_argument)<<"mutation="<<mutation;
            ++rejected;
        }
    }
    EXPECT_EQ(plans.size(),4);EXPECT_EQ(rejected,32);
    if(const auto output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
        ASSERT_TRUE(QDir().mkpath(QString::fromLocal8Bit(output)));
        NmsdkWorker::Write(QString::fromLocal8Bit(output),"live-finalization-plan-codec.json",
            {{"kind","native_live_finalization_plan_codec_control"},{"schema_version",1},{"plans",plans},
             {"malformed_controls",rejected},{"rdk_objects_constructed",false},{"scientific_verdict",QJsonValue(QJsonValue::Null)}});
    }
}
