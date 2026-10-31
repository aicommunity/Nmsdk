#pragma once
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/ModelIdentity.h"
#include "../../../Rdk/Deploy/Include/rdk_cpp_init.h"
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <set>

namespace NmsdkWorker {
inline void Require(bool value,const char* why){if(!value)throw std::invalid_argument(why);}
inline QJsonObject Object(const QJsonValue& value)
{Require(value.isObject(),"job_object_required");return value.toObject();}
inline QJsonArray Array(const QJsonValue& value)
{Require(value.isArray(),"job_array_required");return value.toArray();}
inline std::string Text(const QJsonValue& value)
{Require(value.isString() && !value.toString().trimmed().isEmpty(),"job_text_required");return value.toString().toStdString();}
inline double Number(const QJsonValue& value)
{Require(value.isDouble() && std::isfinite(value.toDouble()),"job_finite_number_required");return value.toDouble();}
inline std::size_t Count(const QJsonValue& value,std::size_t minimum,std::size_t maximum)
{
    const double n=Number(value);
    Require(n>=double(minimum) && n<=double(maximum) && std::floor(n)==n,"job_count_out_of_range");return std::size_t(n);
}
inline QJsonObject Signed(QJsonObject value)
{value.remove("sha256");value["sha256"]=NmsdkTools::CanonicalModelDataSha256(value);return value;}
inline QJsonObject WriteBytes(const QString& directory,const QString& name,const QByteArray& bytes)
{
    QFile file(QDir(directory).filePath(name));
    Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"job_artifact_exists_or_unwritable");
    Require(file.write(bytes)==bytes.size() && file.flush(),"job_artifact_write_failed");file.close();
    return {{"path",name},{"bytes",double(bytes.size())},
        {"sha256",QString::fromLatin1(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())}};
}
inline QJsonObject Write(const QString& directory,const QString& name,const QJsonObject& value)
{return WriteBytes(directory,name,QJsonDocument(value).toJson());}
inline QJsonObject ReadDocument(const QString& path)
{
    QFile file(path);Require(file.open(QIODevice::ReadOnly),"job_input_unreadable");
    Require(file.size()>0 && file.size()<=256*1024*1024,"job_input_size_out_of_range");
    return NMSDK::TimeLearner::ParseStrictNativeJsonObject(file.readAll().toStdString(),256*1024*1024);
}
inline void Keys(const QJsonObject& object,const std::set<QString>& keys)
{Require(object.size()==int(keys.size()),"job_field_set_mismatch");for(const auto& key:keys)Require(object.contains(key),"job_missing_field");}
struct ModelScope {
    RDK::UEPtr<RDK::UEnvironment> environment;
    ~ModelScope(){if(auto net=RDK::dynamic_pointer_cast<RDK::UNet>(environment->GetModel()))net->BreakLinks();environment->DestroyModel();}
};
}
