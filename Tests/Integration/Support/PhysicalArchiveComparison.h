#pragma once

#include "../../../Libraries/Nmsdk-PulseLib/Core/TimeLearner/ModelArchive.h"
#include <QJsonArray>
#include <stdexcept>

namespace NmsdkTests {

// Comparison views are test values only: never import, persist or reseal them.
// Validate the original content digest before separating artifact identity from
// model identity. Keep the entire live graph (including its native XML), metadata
// and every other field. Storage images use the existing production semantic
// fingerprint, as in TimeLearnerModelArchive's telemetry/transfer controls:
// parameter/structure/binding images are not dynamic checkpoints.
inline QJsonObject PhysicalArchiveComparisonView(QJsonObject archive)
{
    const auto digest = archive.take("sha256");
    if(!digest.isString() || digest.toString() != NmsdkTools::CanonicalModelDataSha256(archive))
        throw std::invalid_argument("physical_archive_comparison_digest");
    const int version = archive["schema_version"].toInt();
    if((version != 1 && version != 2) || archive["schema_version"] != QJsonValue(version) ||
       archive["kind"] != QJsonValue("timelearner_model_archive") ||
       archive["encoding"] != QJsonValue(QString("native-xml-and-model-identity-v%1").arg(version)) ||
       archive["dynamic_checkpoint"] != QJsonValue(false) ||
       !archive["graph"].isObject() || !archive["metadata"].isObject() ||
       !archive["class_definitions"].isArray())
        throw std::invalid_argument("physical_archive_comparison_schema");
    archive["class_definitions"] = NmsdkTools::ModelImageDefinitionsFingerprint(
        archive["class_definitions"].toArray());
    return archive;
}

// Controller state, certificates, references, dataset snapshots and provenance
// remain exact. Only the nested physical archive uses the image contract above;
// the package's original integrity digest is checked independently first.
inline QJsonObject LearnedStateComparisonView(QJsonObject package)
{
    const auto digest = package.take("sha256");
    if(!digest.isString() || digest.toString() != NmsdkTools::CanonicalModelDataSha256(package))
        throw std::invalid_argument("learned_state_comparison_digest");
    const int version = package["schema_version"].toInt();
    if((version != 5 && version != 6) || package["schema_version"] != QJsonValue(version) ||
       package["dynamic_checkpoint"] != QJsonValue(false) || !package["neuron"].isObject())
        throw std::invalid_argument("learned_state_comparison_schema");
    package["neuron"] = PhysicalArchiveComparisonView(package["neuron"].toObject());
    return package;
}

}
