#pragma once
#include "TimeLearnerJobSupport.h"
#include "TimeLearner/NativeCompositeTrainingEvidence.h"
#include "TimeLearner/CandidateWindowRecoveryLedger.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include <utility>

namespace NmsdkWorker {
// Portable groups are written from the exact production package. The embedded
// primary remains mandatory; external files are an independently hash-bound
// mirror, not regenerated traces or a substitute for missing native closure.
inline QJsonValue PublishNativeCompositeArchive(const QString& output,const QJsonObject& package,QJsonArray& artifacts) {
    const auto schema=package.value("schema_version");
    if(schema!=QJsonValue(5) && schema!=QJsonValue(6) && schema!=QJsonValue(7)) {
        Require(schema==QJsonValue(1) || schema==QJsonValue(2) || schema==QJsonValue(3) || schema==QJsonValue(4),
            "unsupported_composite_publication_package_schema");return QJsonValue(QJsonValue::Null);
    }
    const auto archive=Object(package["measurement_archive"]);const auto decoded=NMSDK::TimeLearner::DecodeNativeCompositeTrainingArchive(archive);
    Require(archive.value("schema_version")==QJsonValue(schema==QJsonValue(5)?1:2) &&
        decoded.Protocol().schemaVersion==(schema==QJsonValue(5)?4u:5u) &&
        NMSDK::TimeLearner::EncodeVerificationProtocol(decoded.Protocol())==Object(package["protocol"]),"composite_publication_version_binding");
    auto body=package;body.remove("sha256");Require(package.value("sha256")==QJsonValue(NmsdkTools::CanonicalModelDataSha256(body)),
        "composite_publication_package_digest");
    if(schema==QJsonValue(7)) {
        const auto ledger=Object(package["recovery_ledger"]);
        NMSDK::TimeLearner::DecodeCandidateWindowRecoveryLedger(ledger,decoded);
        Require(Object(Object(package["neuron"])["metadata"]).value("recovery_ledger_sha256")==ledger.value("sha256"),
            "recovery_publication_physical_archive_binding");
    }
    const auto blobs=Object(archive["primary_blobs"]);const auto records=Array(archive["records"]);
    Require(QDir().mkpath(QDir(output).filePath("composite-measurements")),"training_composite_directory_failed");
    for(int i=0;i<records.size();++i) {
        const auto record=Object(records[i]);
        artifacts.append(Write(output,QString("composite-measurements/group-%1.json").arg(i+1,6,10,QLatin1Char('0')),record));
        for(const auto& value:Array(record["raw_trials"])) {
            const auto ref=Object(Object(value)["primary_ref"]);const auto path=QString::fromStdString(Text(ref["relative_path"]));
            const auto slash=path.lastIndexOf('/');Require(slash>0 && QDir().mkpath(QDir(output).filePath(path.left(slash))),"training_composite_primary_directory_failed");
            const auto blob=Object(blobs[QString::fromStdString(Text(ref["sha256"]))]);
            const auto bytes=QByteArray::fromBase64(QString::fromStdString(Text(blob["base64"])).toLatin1());
            const auto actual=WriteBytes(output,path,bytes);Require(actual["bytes"]==ref["bytes"] && actual["sha256"]==ref["sha256"],"training_composite_primary_writeback_changed");
            artifacts.append(actual);
        }
    }
    const auto index=Write(output,"composite-measurements/index.json",archive);artifacts.append(index);return index;
}
inline QJsonObject WrapNativeCompositeExecution(bool composite,QJsonObject base,const QJsonObject& package,const QJsonValue& archive,
    const QJsonValue& actualModel,std::size_t rawTrials,std::size_t sampledFrames,bool preflight=false) {
    if(!composite)return Signed(base);
    // Preserve an owning value before insertion can shift a QJsonValueRef.
    const QJsonValue baseSchema=base.value("schema_version");
    base["base_schema_version"]=baseSchema;base["schema_version"]=3;
    base["measurement_method"]=NMSDK::TimeLearner::DeclaredWindowBasinResult::MethodId();base["measurement_archive"]=archive;
    base["model_semantic_hash"]=actualModel;base["source_origin"]=QJsonValue(QJsonValue::Null);
    QJsonValue attempt(QJsonValue::Null),history(QJsonValue::Null);
    if(!package.isEmpty()) {
        const auto source=Object(package["measurement_archive"]);base["source_origin"]=source["source_origin"];
        const auto counters=Object(source["counters"]);attempt=counters["attempt"];history=counters["archive"];
    } else if(preflight) {
        attempt=QJsonObject{{"logical_groups",0},{"native_probes",0},{"sampled_frames",0}};
        history=QJsonObject{{"groups",0},{"native_probes",0},{"sampled_frames",0},{"primary_bytes",0}};
    }
    base["composite_counters"]=QJsonObject{{"attempt",attempt},{"archive",history},
        {"execution",QJsonObject{{"native_trials",double(rawTrials)},{"sampled_frames",double(sampledFrames)}}}};
    return Signed(base);
}

// Explicit new wrapper. Old execution3 remains above with its original wire.
inline QJsonObject WrapNativeCandidateWindowFamilyExecution(QJsonObject base,const QJsonObject& package,const QJsonValue& archive,
    const QJsonValue& actualModel,std::size_t rawTrials,std::size_t sampledFrames,bool preflight,bool recovery) {
    Require(rawTrials<=9007199254740991ULL && sampledFrames<=9007199254740991ULL,"candidate_window_execution_inexact_counter");
    Require(!preflight || package.isEmpty(),"candidate_window_preflight_has_package");
    const QJsonValue baseSchema=base.value("schema_version");
    Require(baseSchema==QJsonValue(1) || baseSchema==QJsonValue(2),"candidate_window_execution_base_version");
    base["base_schema_version"]=baseSchema;base["schema_version"]=recovery?5:4;
    base["measurement_method"]=NMSDK::TimeLearner::DeclaredWindowBasinResult::MethodId();base["measurement_archive"]=archive;
    base["model_semantic_hash"]=actualModel;base["source_origin"]=QJsonValue(QJsonValue::Null);
    QJsonValue attempt(QJsonValue::Null),history(QJsonValue::Null);
    if(!package.isEmpty()) {
        Require(package.value("schema_version")==QJsonValue(recovery?7:6) && actualModel==package.value("model_revision"),"candidate_window_execution_package_binding");
        Require(archive.isObject(),"candidate_window_execution_missing_archive_descriptor");
        const auto descriptor=Object(archive);Keys(descriptor,{"path","bytes","sha256"});
        const double indexBytes=Number(descriptor.value("bytes"));
        Require(descriptor.value("path")==QJsonValue("composite-measurements/index.json") && indexBytes>=1. && indexBytes<=9007199254740991. && std::floor(indexBytes)==indexBytes &&
            !Text(descriptor.value("sha256")).empty(),"candidate_window_execution_archive_descriptor");
        const auto source=Object(package["measurement_archive"]);
        Require(source.value("schema_version")==QJsonValue(2) && Object(source["protocol"]).value("schema_version")==QJsonValue(5),
            "candidate_window_execution_archive_binding");
        base["source_origin"]=source["source_origin"];const auto counters=Object(source["counters"]);attempt=counters["attempt"];history=counters["archive"];
    } else if(preflight) {
        Require(rawTrials==0 && sampledFrames==0 && archive.isNull(),"candidate_window_preflight_has_execution");
        attempt=QJsonObject{{"logical_groups",0},{"native_probes",0},{"sampled_frames",0}};
        history=QJsonObject{{"groups",0},{"native_probes",0},{"sampled_frames",0},{"primary_bytes",0}};
    } else Require(archive.isNull(),"candidate_window_execution_archive_without_package");
    base["composite_counters"]=QJsonObject{{"attempt",attempt},{"archive",history},
        {"execution",QJsonObject{{"native_trials",double(rawTrials)},{"sampled_frames",double(sampledFrames)}}}};
    if(recovery) {
        base["recovery_ledger_sha256"]=QJsonValue(QJsonValue::Null);
        base["recovery_delivery_count"]=QJsonValue(QJsonValue::Null);
        if(!package.isEmpty()) {
            const auto ledger=Object(package["recovery_ledger"]);
            const auto decoded=NMSDK::TimeLearner::DecodeNativeCompositeTrainingArchive(Object(package["measurement_archive"]));
            const auto deliveries=NMSDK::TimeLearner::DecodeCandidateWindowRecoveryLedger(ledger,decoded);
            Require(Object(Object(package["neuron"])["metadata"]).value("recovery_ledger_sha256")==ledger.value("sha256"),
                "recovery_execution_physical_archive_binding");
            base["recovery_ledger_sha256"]=ledger.value("sha256");base["recovery_delivery_count"]=double(deliveries.size());
        }
    }
    return Signed(base);
}
inline QJsonObject WrapNativeCandidateWindowExecution(QJsonObject base,const QJsonObject& package,const QJsonValue& archive,
    const QJsonValue& actualModel,std::size_t rawTrials,std::size_t sampledFrames,bool preflight=false) {
    return WrapNativeCandidateWindowFamilyExecution(std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight,false);
}
inline QJsonObject WrapNativeRecoveryCandidateWindowExecution(QJsonObject base,const QJsonObject& package,const QJsonValue& archive,
    const QJsonValue& actualModel,std::size_t rawTrials,std::size_t sampledFrames,bool preflight=false) {
    return WrapNativeCandidateWindowFamilyExecution(std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight,true);
}
inline QJsonObject WrapConfiguredNativeExecution(const NMSDK::TimeLearner::ConfiguredNativeTraining& configuration,QJsonObject base,
    const QJsonObject& package,const QJsonValue& archive,const QJsonValue& actualModel,std::size_t rawTrials,std::size_t sampledFrames,bool preflight=false) {
    const auto schema=NMSDK::TimeLearner::EncodeConfiguredNativeTraining(configuration).value("schema_version");
    if(schema==QJsonValue(8))return WrapNativeRecoveryCandidateWindowExecution(std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight);
    if(schema==QJsonValue(7))return WrapNativeCandidateWindowExecution(std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight);
    if(schema==QJsonValue(6))return WrapNativeCompositeExecution(true,std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight);
    Require(schema==QJsonValue(1) || schema==QJsonValue(2) || schema==QJsonValue(3) || schema==QJsonValue(4) || schema==QJsonValue(5),
        "unknown_native_execution_configuration_version");
    return WrapNativeCompositeExecution(false,std::move(base),package,archive,actualModel,rawTrials,sampledFrames,preflight);
}

}
