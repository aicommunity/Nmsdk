#pragma once
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/ModelIdentity.h"
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonObject>
#include <QRegularExpression>
#include <cmath>
#include <set>
#include <stdexcept>

namespace NmsdkWorker {
// A transport indirection, not a smaller learned-state schema. The complete
// source object is restored before the ordinary signed job decoder sees it.
inline constexpr qint64 NativeJobMaximumBytes=256ll*1024*1024;
inline constexpr qint64 NativeJobSourceMaximumBytes=1024ll*1024*1024;
inline void JobSourceRequire(bool value,const char* reason)
{if(!value)throw std::invalid_argument(reason);}
inline void JobSourceKeys(const QJsonObject& object,const std::set<QString>& keys)
{
    JobSourceRequire(object.size()==int(keys.size()),"job_source_field_set");
    for(const auto& key:keys)JobSourceRequire(object.contains(key),"job_source_field_set");
}
inline QJsonObject ReadNativeJobDocument(const QString& path)
{
    QFile file(path);JobSourceRequire(file.open(QIODevice::ReadOnly),"job_input_unreadable");
    JobSourceRequire(file.size()>0 && file.size()<=NativeJobMaximumBytes,"job_input_size_out_of_range");
    auto document=NMSDK::TimeLearner::ParseStrictNativeJsonBytes(file.readAll(),NativeJobMaximumBytes);
    if(document["kind"]!=QJsonValue("timelearner_checked_file_source_job"))return document;
    JobSourceKeys(document,{"kind","schema_version","job","source","sha256"});
    JobSourceRequire(document["schema_version"]==QJsonValue(1) && document["job"].isObject() &&
        document["source"].isObject(),"job_source_transport_schema");
    const auto signature=document["sha256"];auto signedBody=document;signedBody.remove("sha256");
    JobSourceRequire(signature==QJsonValue(NmsdkTools::CanonicalModelDataSha256(signedBody)),"job_source_transport_digest");
    auto job=document["job"].toObject();const auto source=document["source"].toObject();
    JobSourceKeys(source,{"field","path","bytes","sha256","package_sha256"});
    const auto kind=job["kind"].toString();QString field;
    if(kind=="timelearner_native_diagnostic_evaluation_job")field="source_stopped";
    else if(kind=="timelearner_native_recognition_export_job")field="source_solo";
    else if(kind=="timelearner_native_evaluation_job")field="source_recognition";
    else throw std::invalid_argument("job_source_unsupported_operation");
    JobSourceRequire(source["field"]==QJsonValue(field) && !job.contains(field),"job_source_projection_changed");
    const auto relative=source["path"].toString();const auto parts=relative.split('/');
    JobSourceRequire(source["path"].isString() && !relative.isEmpty() && !QDir::isAbsolutePath(relative) &&
        !relative.contains('\\') && !relative.contains(':') && !parts.contains("..") && !parts.contains(".") &&
        !parts.contains("") && QDir::cleanPath(relative)==relative,"job_source_path_escape");
    JobSourceRequire(source["bytes"].isDouble(),"job_source_declared_size");
    const auto declared=source["bytes"].toDouble();
    JobSourceRequire(std::isfinite(declared) && declared>=1 && declared<=double(NativeJobSourceMaximumBytes) &&
        std::floor(declared)==declared,"job_source_declared_size");
    const QRegularExpression shaPattern("^[0-9a-f]{64}$");
    JobSourceRequire(source["sha256"].isString() && source["package_sha256"].isString() &&
        shaPattern.match(source["sha256"].toString()).hasMatch() &&
        shaPattern.match(source["package_sha256"].toString()).hasMatch(),"job_source_digest_schema");
    const auto parent=QFileInfo(path).absolutePath();
    JobSourceRequire(!QFileInfo(path).isSymLink() && !QFileInfo(parent).isSymLink(),"job_source_symlink");
    QString actual=parent;
    for(const auto& part:parts){actual=QDir(actual).filePath(part);JobSourceRequire(!QFileInfo(actual).isSymLink(),"job_source_symlink");}
    QFile input(actual);JobSourceRequire(input.open(QIODevice::ReadOnly),"job_source_unreadable");
    JobSourceRequire(input.size()==qint64(declared),"job_source_size_changed");
    const auto raw=input.readAll();
    JobSourceRequire(raw.size()==qint64(declared) && input.atEnd(),"job_source_size_changed");
    const auto digest=QString::fromLatin1(QCryptographicHash::hash(raw,QCryptographicHash::Sha256).toHex());
    JobSourceRequire(source["sha256"]==QJsonValue(digest),"job_source_bytes_changed");
    const auto package=NMSDK::TimeLearner::ParseStrictNativeJsonBytes(raw,std::size_t(declared));
    JobSourceRequire(package["sha256"]==source["package_sha256"],"job_source_package_changed");
    job[field]=package;
    const auto jobSignature=job["sha256"];auto jobBody=job;jobBody.remove("sha256");
    JobSourceRequire(jobSignature==QJsonValue(NmsdkTools::CanonicalModelDataSha256(jobBody)),"job_source_resolved_job_digest");
    return job;
}
}
