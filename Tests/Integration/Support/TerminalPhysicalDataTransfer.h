#pragma once
#include "TimeLearner/NativePhysicalModelData.h"
#include "TimeLearner/NativeRecognitionState.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <algorithm>
#include <cmath>
#include <functional>
#include <optional>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <vector>

namespace NmsdkTests {
// Consume genuine completed/restored terminal fixtures. Physical DATA must
// retain their actual graph and response while the destination controller stays
// idle: a reference to a source8 certificate is not that certificate.
template<class Owner,class Fixture,class Plan>
void CheckTerminalPhysicalDataTransfer(Fixture& f,const Plan& plan,const QJsonObject& source,
    const std::function<void(const QJsonObject&)>& save)
{
    using namespace RDK;using namespace NMSDK;using namespace NMSDK::TimeLearner;
    ASSERT_EQ(source["schema_version"],QJsonValue(8));
    const auto revision=f.Revision();const auto clock=f.Time();
    const auto implementation=source["implementation_id"].toString().toStdString();
    const auto data=ExportNativePhysicalModelData(source,f.storage,f.environment,implementation);
    EXPECT_EQ(data["source_boundary"].toObject()["sha256"],source["sha256"]);
    EXPECT_EQ(data["source_boundary"].toObject()["schema_version"],QJsonValue(8));
    EXPECT_TRUE(data["certificate"].isNull());EXPECT_TRUE(data["data_only"].toBool());
    EXPECT_FALSE(data["dynamic_checkpoint"].toBool());
    for(const auto* key:{"historical_state","measurement_archive","search_history","terminal_journal","source_solo"})
        EXPECT_FALSE(data.contains(key));
    const auto prepared=PrepareNativePhysicalModelData(data,f.storage,f.environment,implementation);
    EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(data,f.storage,f.environment,implementation),std::invalid_argument);
    EXPECT_EQ(prepared->modelRevision,revision);EXPECT_EQ(prepared->parameters,f.owner->ReadNativeParameters());
    EXPECT_EQ(data["neuron"].toObject()["graph"].toObject()["identity"],source["neuron"].toObject()["graph"].toObject()["identity"]);
    EXPECT_EQ(f.Time(),clock);EXPECT_EQ(f.Revision(),revision);
    auto unknown=data;auto boundary=unknown["source_boundary"].toObject();boundary["schema_version"]=9;
    unknown["source_boundary"]=boundary;unknown.remove("sha256");unknown["sha256"]=NmsdkTools::CanonicalModelDataSha256(unknown);
    EXPECT_THROW(PrepareNativePhysicalModelData(unknown,f.storage,f.environment,implementation),std::invalid_argument);
    const auto recognition=source["kind"]==QJsonValue("timelearner_completed_state")?
        ConvertNativeSoloToRecognition(source,NativeRecognitionSpec{},f.storage,f.environment,implementation):
        ConvertNativeStoppedToDiagnosticRecognition(source,NativeRecognitionSpec{},f.storage,f.environment,implementation);
    const auto frozenData=ExportNativePhysicalModelData(recognition,f.storage,f.environment,implementation);
    const auto frozen=PrepareNativeFrozenPhysicalModelData(frozenData,f.storage,f.environment,implementation);
    EXPECT_EQ(frozen->modelRevision,recognition["model_revision"].toString().toStdString());
    EXPECT_EQ(frozenData["source_solo_revision"],source["model_revision"]);
    EXPECT_EQ(frozenData["source_boundary"].toObject()["sha256"],recognition["sha256"]);
    EXPECT_TRUE(frozenData["certificate"].isNull());
    auto unknownRecognition=frozenData;auto recognitionBoundary=unknownRecognition["source_boundary"].toObject();
    recognitionBoundary["schema_version"]=8;unknownRecognition["source_boundary"]=recognitionBoundary;
    unknownRecognition.remove("sha256");unknownRecognition["sha256"]=NmsdkTools::CanonicalModelDataSha256(unknownRecognition);
    EXPECT_THROW(PrepareNativeFrozenPhysicalModelData(unknownRecognition,f.storage,f.environment,implementation),std::invalid_argument);
    EXPECT_EQ(f.Time(),clock);EXPECT_EQ(f.Revision(),revision);

    auto destination=dynamic_pointer_cast<Owner>(f.storage->TakeObject(
        std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(destination);destination->Name="TerminalPhysicalData";
    destination->SetEnvironment(f.environment);destination->SetGlobalTimeStep(f.frequency);
    destination->ControllerVersion=prepared->controllerVersion;destination->CalculateMode=prepared->calculateMode;
    destination->StructureBuildMode=prepared->structureBuildMode;destination->IsNeedToTrain=false;
    destination->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(prepared->configuration)).toJson(QJsonDocument::Compact).toStdString();
    UEPtr<UContainer> component=destination;ASSERT_NE(f.model->AddComponent(component),ForbiddenId);
    // Solo DATA uses the ordinary prepared-graph installer. The public frozen
    // DATA importer must continue to reject an implicit solo conversion.
    const auto imported=destination->InstallNativePreparedModel(prepared->configuration.model,
        prepared->neuron,prepared->dataset,prepared->parameters);
    ASSERT_EQ(imported.status,NativeModelBuildStatus::Adopted)<<imported.reason;
    destination->Init();ASSERT_TRUE(destination->IsReady() && destination->IsInit());
    EXPECT_DOUBLE_EQ(f.Time(),clock);
    EXPECT_FALSE(destination->HasNativePhysicalModelData());EXPECT_FALSE(destination->IsNeedToTrain.GetData());
    EXPECT_EQ(destination->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(destination->NativeTrainingController().Search());
    EXPECT_FALSE(destination->NativeTrainingController().Certificate());
    EXPECT_EQ(destination->NativeTrainingController().ModelEpoch(),0u);
    auto frozenDestination=dynamic_pointer_cast<Owner>(f.storage->TakeObject(
        std::is_same_v<Owner,NNeuronTimeLearnerBranch>?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));
    ASSERT_TRUE(frozenDestination);frozenDestination->Name="TerminalFrozenPhysicalData";
    frozenDestination->SetEnvironment(f.environment);frozenDestination->SetGlobalTimeStep(f.frequency);
    UEPtr<UContainer> frozenComponent=frozenDestination;ASSERT_NE(f.model->AddComponent(frozenComponent),ForbiddenId);
    const auto frozenImported=frozenDestination->ImportNativePhysicalModelData(frozenData,implementation);
    ASSERT_EQ(frozenImported.status,NativeModelBuildStatus::Adopted)<<frozenImported.reason;
    frozenDestination->Init();ASSERT_TRUE(frozenDestination->IsReady() && frozenDestination->IsInit());
    EXPECT_TRUE(frozenDestination->HasNativePhysicalModelData());EXPECT_FALSE(frozenDestination->IsNeedToTrain.GetData());
    EXPECT_EQ(frozenDestination->NativeTrainingController().State(),NativeTrainingState::Idle);
    EXPECT_FALSE(frozenDestination->NativeTrainingController().Certificate());
    EXPECT_EQ(frozenDestination->ExportNativePhysicalModelData(implementation),frozenData);
    EXPECT_DOUBLE_EQ(f.Time(),clock);

    std::vector<NativeProbeSample> originalTrace,dataTrace;
    const auto request=[&](auto owner,const char* id,std::vector<NativeProbeSample>& trace) {
        auto probe=plan.probe;probe.routing=plan.protocol.routing;probe.activeInput=0;
        probe.inputId=plan.protocol.inputs.front().id;probe.protocolRevision=plan.protocol.revision;
        probe.baseModelRevision=revision;probe.modelEpoch=owner->NativeTrainingController().ModelEpoch();
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto generator=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        probe.readModelRevision=[neuron,generator] {
            return NmsdkTools::IdentifyModel(UEPtr<UContainer>(neuron.Get()),{{&generator->Output,"burst"}})["sha256"].toString().toStdString();
        };
        probe.readFullModelRevision=probe.readModelRevision;
        probe.onSample=[&trace](const NativeProbeSample& sample){trace.push_back(sample);};
        auto& spec=probe.specification;spec.schemaVersion=6;spec.runId="terminal-physical-transfer";spec.trialId=spec.runId+"/"+id;
        spec.windows.clear();spec.characterization.reset();spec.waveAssignment=WaveAssignmentPolicy::WindowOnly;
        spec.peakSelection=PeakSelectionPolicy::IsolatedWindow;spec.expectedStimulusIds=plan.protocol.stimulusIds;
        StimulusSubsetCharacterization subset{plan.protocol.patternHash,plan.protocol.inputs.size(),{}};
        for(std::size_t i=0;i<subset.physicalInputCount;++i)subset.sourceOrdinals.push_back(i);
        spec.stimulusSubset=std::move(subset);return probe;
    };
    f.owner->IsNeedToTrain=false;f.owner->QueueNativeProbe(request(f.owner,"original",originalTrace));
    destination->QueueNativeProbe(request(destination,"data",dataTrace));
    std::optional<NativeProbeResult> originalResult,dataResult;
    for(unsigned tick=0;tick<4*f.frequency && (!originalResult || !dataResult);++tick) {
        f.model->Calculate();f.environment->IncreaseModelTimeByStep();
        if(!originalResult)originalResult=f.owner->TakeNativeProbeResult();
        if(!dataResult)dataResult=destination->TakeNativeProbeResult();
    }
    ASSERT_TRUE(originalResult);ASSERT_TRUE(dataResult);
    ASSERT_EQ(originalResult->status,NativeProbeStatus::Completed);ASSERT_EQ(dataResult->status,NativeProbeStatus::Completed);
    ASSERT_TRUE(originalResult->observation && originalResult->observation->complete);
    ASSERT_TRUE(dataResult->observation && dataResult->observation->complete);
    ASSERT_FALSE(originalTrace.empty());ASSERT_EQ(originalTrace.size(),dataTrace.size());
    double largestDifference=0.,excursion=0.;QJsonArray rows;
    for(std::size_t i=0;i<originalTrace.size();++i) {
        EXPECT_DOUBLE_EQ(originalTrace[i].time,dataTrace[i].time);EXPECT_DOUBLE_EQ(originalTrace[i].stimulus,dataTrace[i].stimulus);
        ASSERT_EQ(originalTrace[i].potentials.size(),dataTrace[i].potentials.size());
        ASSERT_EQ(originalTrace[i].potentials.size(),originalTrace.front().potentials.size());
        for(std::size_t j=0;j<originalTrace[i].potentials.size();++j) {
            ASSERT_TRUE(std::isfinite(originalTrace[i].potentials[j]));ASSERT_TRUE(std::isfinite(dataTrace[i].potentials[j]));
            largestDifference=std::max(largestDifference,std::abs(originalTrace[i].potentials[j]-dataTrace[i].potentials[j]));
            excursion=std::max(excursion,std::abs(originalTrace[i].potentials[j]-originalTrace.front().potentials[j]));
        }
        QJsonArray sourceValues,dataValues;
        for(double value:originalTrace[i].potentials)sourceValues.append(value);
        for(double value:dataTrace[i].potentials)dataValues.append(value);
        rows.append(QJsonArray{originalTrace[i].time,originalTrace[i].stimulus,sourceValues,dataValues});
    }
    EXPECT_LE(largestDifference,1e-12);EXPECT_GT(excursion,1e-6);
    EXPECT_EQ(destination->ReadNativeParameters(),prepared->parameters);
    EXPECT_EQ(frozenDestination->ExportNativePhysicalModelData(implementation),frozenData);
    EXPECT_EQ(f.Revision(),revision);EXPECT_EQ(f.owner->NativeTrainingController().State(),NativeTrainingState::Finished);
    EXPECT_EQ(bool(f.owner->NativeTrainingController().Certificate()),!source["certificate"].isNull());
    save({{"kind","timelearner_terminal_physical_data_fixture"},{"schema_version",1},{"source_sha256",source["sha256"]},
        {"physical_model_data",data},{"source_probe",EncodeNativeProbeEvidence(*originalResult)},
        {"data_probe",EncodeNativeProbeEvidence(*dataResult)},{"maximum_sample_difference",largestDifference},
        {"response_columns",QJsonArray{"native_absolute_time","actual_input","source_potentials","data_potentials"}},
        {"response_rows",rows},{"recognition_source",recognition},{"recognition_model_data",frozenData},
        {"source_response_excursion",excursion},
        {"destination_controller_epoch",double(destination->NativeTrainingController().ModelEpoch())},
        {"destination_controller_state",NativeTrainingStateName(destination->NativeTrainingController().State())},
        {"frozen_destination_controller_state",NativeTrainingStateName(frozenDestination->NativeTrainingController().State())},
        {"frozen_destination_has_data",frozenDestination->HasNativePhysicalModelData()},
        {"frozen_destination_certificate_present",bool(frozenDestination->NativeTrainingController().Certificate())},
        {"training_certificate_transferred",bool(destination->NativeTrainingController().Certificate())},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}});
}
}
