#pragma once
#include "TimeLearnerJobSupport.h"
#include "TimeLearner/NativeCompositeTrainingEvidence.h"

namespace NmsdkWorker {
// Portable groups are written from the exact production package. The embedded
// primary remains mandatory; external files are an independently hash-bound
// mirror, not regenerated traces or a substitute for missing native closure.
inline QJsonValue PublishNativeCompositeArchive(const QString& output,const QJsonObject& package,QJsonArray& artifacts) {
    if(package["schema_version"]!=QJsonValue(5))return QJsonValue(QJsonValue::Null);
    const auto archive=Object(package["measurement_archive"]);NMSDK::TimeLearner::DecodeNativeCompositeTrainingArchive(archive);
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
    base["base_schema_version"]=base["schema_version"];base["schema_version"]=3;
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

}
