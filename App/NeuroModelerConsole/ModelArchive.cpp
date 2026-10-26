#include "ModelArchive.h"
#include "../../../Rdk/Core/Engine/UClassImageRegistry.h"
#include "../../../Rdk/Core/Engine/UComponentFactory.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuron.h"
#include <QCryptographicHash>
#include <QJsonArray>
#include <QJsonDocument>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <functional>
#include <map>
#include <set>
#include <typeinfo>

namespace NmsdkTools {
namespace {
using namespace RDK;
const char* GraphRoot = "TimeLearnerNativeGraph";

[[noreturn]] void Fail(const char* code, const QString& detail)
{ throw ModelArchiveError(code, detail.toStdString()); }

QString RequiredString(const QJsonObject& object, const char* key)
{
    if(!object[key].isString() || object[key].toString().trimmed().isEmpty()) Fail("invalid_archive_field", key);
    return object[key].toString();
}

struct Lease
{
    UEPtr<UStorage> storage;
    UEPtr<UContainer> object;
    bool hasBoundary = false;
    ~Lease()
    {
        if(object)
        {
            // Rehearsal/failing-import instances must not remain listeners of
            // a caller-owned stimulus after being returned to the pool.
            if(hasBoundary)
                if(auto net = dynamic_pointer_cast<UNet>(object)) net->BreakLinks();
            storage->ReturnObject(object);
        }
    }
    UEPtr<UContainer> Release() { auto result = object; object = 0; return result; }
};

UEPtr<UNet> Take(UEPtr<UStorage> storage, UEPtr<UEnvironment> environment, const QString& name)
{
    if(!storage->CheckClass(name.toStdString())) Fail("missing_archive_class", name);
    auto object = dynamic_pointer_cast<UNet>(storage->TakeObject(name.toStdString()));
    if(!object) Fail("unsupported_archive_class", name);
    object->SetEnvironment(environment);
    return object;
}

QJsonObject Identity(UEPtr<UContainer> model, const ModelBoundarySources& boundarySources = {})
{
    auto identity = IdentifyModel(model, boundarySources);
    if(!identity["valid"].toBool()) Fail("invalid_model_identity", QString::fromStdString(model->GetName()) + ": " +
        QString::fromUtf8(QJsonDocument(identity["diagnostics"].toArray()).toJson(QJsonDocument::Compact)));
    return identity;
}

void RequireMatch(const QJsonObject& identity, UEPtr<UContainer> model,
                  const ModelBoundarySources& boundarySources = {})
{
    auto check = VerifyModelIdentity(identity, model, boundarySources);
    if(!check["valid"].toBool() || !check["match"].toBool())
        Fail("archive_model_mismatch", check["reason"].toString() + ": " + check["first_difference"].toString());
}

QString XmlDigest(const QString& xml)
{ return QString::fromLatin1(QCryptographicHash::hash(xml.toUtf8(), QCryptographicHash::Sha256).toHex()); }

QJsonObject Snapshot(UEPtr<UContainer> model, const ModelBoundarySources& boundarySources = {})
{
    auto net = dynamic_pointer_cast<UNet>(model);
    if(!net) Fail("unsupported_archive_graph", "UNet required");
    auto identity = Identity(model, boundarySources);
    USerStorageXML xml;
    if(!xml.Create(GraphRoot) || !net->SaveComponent(&xml, true, ptPubParameter | ptPubState | pgSystem))
        Fail("archive_serialization_failed", model->GetName().c_str());
    std::string bytes;
    if(!xml.Save(bytes)) Fail("archive_serialization_failed", "native XML Save");
    const auto text = QString::fromStdString(bytes);
    if(text.toUtf8().toStdString() != bytes) Fail("invalid_xml_encoding", "UTF8 required");
    QJsonObject snapshot;
    snapshot["component_name"] = QString::fromStdString(model->GetName());
    snapshot["component_class"] = QString::fromStdString(model->GetCompClassName());
    snapshot["native_xml"] = text; snapshot["native_xml_sha256"] = XmlDigest(text);
    snapshot["identity"] = identity;
    return snapshot;
}

std::set<QString> Classes(const QJsonObject& identity)
{
    std::set<QString> result;
    for(const auto& entry : identity["model"].toObject()["nodes"].toArray())
    {
        auto node = entry.toObject(); result.insert(RequiredString(node, "class"));
        auto parameters = node["parameters"].toObject();
        for(auto i = parameters.begin(); i != parameters.end(); ++i)
        {
            // Structural class selectors also govern future growth and need
            // definitions even when no instance of that class currently exists.
            if(!i.key().endsWith("ClassName")) continue;
            const auto data = i.value().toObject()["data"].toObject();
            if(data["type"].toString() == "utf8" && !data["value"].toString().isEmpty())
                result.insert(data["value"].toString());
        }
    }
    return result;
}

void ValidateMetadata(const QJsonObject& metadata, const QJsonObject& identity)
{
    QString rate;
    for(const auto& entry : identity["model"].toObject()["nodes"].toArray())
    {
        const auto node = entry.toObject(); const auto frequency = RequiredString(node,"frequency_hz");
        bool ok = false;
        if(frequency.toUInt(&ok) == 0 || !ok || (!rate.isEmpty() && rate != frequency))
            Fail("unsupported_multirate_archive", node["path"].toString());
        rate = frequency;
    }
    RequiredString(metadata, "implementation_id");
    const auto state = RequiredString(metadata, "state_kind");
    if(state != "model_spec" && state != "learned_solo" && state != "recognition") Fail("invalid_state_kind", state);
    if(!metadata["training"].isObject() || !metadata["calibration"].isObject() || !metadata["conversion"].isObject())
        Fail("incomplete_model_metadata", "training/calibration/conversion required");
    const auto training = metadata["training"].toObject();
    const auto status = RequiredString(training, "status");
    if(state == "model_spec")
    {
        if(status != "not_trained") Fail("invalid_training_metadata", "model_spec must not claim training");
    }
    else
    {
        const std::set<QString> statuses{"exact","quantized","best_effort","search_unresolved","budget_exhausted","external_stop"};
        if(!statuses.count(status)) Fail("invalid_training_metadata", status);
        RequiredString(training, "target_id");
        const auto trainer = RequiredString(training, "trainer"), normalization = RequiredString(training, "normalization");
        if((trainer != "Classic" && trainer != "Branch") || (normalization != "N0" && normalization != "N1"))
            Fail("invalid_training_metadata", "trainer/normalization");
        const auto target = training["target_pattern"].toArray(), references = training["captured_per_input"].toArray();
        if(target.isEmpty() || target.size() != references.size()) Fail("invalid_training_metadata", "target/reference dimension");
        for(const auto& value : target)
            if(!value.isDouble() || !std::isfinite(value.toDouble()) || value.toDouble() < 0.) Fail("invalid_training_metadata", "target value");
        for(const auto& value : references)
            if(!value.isDouble() || !std::isfinite(value.toDouble()) || value.toDouble() <= 0.) Fail("invalid_training_metadata", "reference value");
        const auto certificate = training["certificate"].toObject();
        if(certificate["state_identity"] != identity["sha256"] || certificate["status"] != training["status"])
            Fail("certificate_model_mismatch", "certificate does not identify the exported state");
    }
    const auto calibration = metadata["calibration"].toObject();
    const auto calibrationStatus = RequiredString(calibration, "status");
    const std::set<QString> calibrationStatuses{"fixed","calibrated","nonseparable","invalid"};
    if(!calibrationStatuses.count(calibrationStatus)) Fail("invalid_calibration_metadata", calibrationStatus);
    RequiredString(calibration, "protocol");
    if(!calibration["threshold"].isDouble() || !std::isfinite(calibration["threshold"].toDouble()))
        Fail("invalid_calibration_metadata", "threshold");
    const auto ltPath = RequiredString(calibration, "ltzone_path");
    bool actualLtZone = false, matchedThreshold = false;
    for(const auto& entry : identity["model"].toObject()["caches"].toArray())
        actualLtZone = actualLtZone || entry.toObject()["cached_ltzone"].toString() == ltPath;
    for(const auto& entry : identity["model"].toObject()["nodes"].toArray())
    {
        const auto node = entry.toObject();
        if(node["path"].toString() != ltPath) continue;
        const auto data = node["parameters"].toObject()["Threshold"].toObject()["data"].toObject();
        const auto text = data["value"].toString(); bool ok = false;
        const std::uint64_t bits = text.toULongLong(&ok,16); double threshold;
        std::memcpy(&threshold,&bits,sizeof(threshold));
        matchedThreshold = ok && text.size() == 16 && data["type"].toString() == "binary64" &&
            threshold == calibration["threshold"].toDouble();
    }
    if(!actualLtZone || !matchedThreshold) Fail("calibration_model_mismatch", ltPath);
    const auto conversion = metadata["conversion"].toObject();
    const auto mode = RequiredString(conversion, "mode");
    if(mode != "none" && mode != "parallel") Fail("invalid_conversion_metadata", mode);
    if(state != "recognition" && mode != "none") Fail("invalid_conversion_metadata", "solo/spec cannot be converted");
    if(mode == "parallel")
    {
        if(RequiredString(conversion, "source_solo_identity").size() != 64 || conversion["factors"].toArray().isEmpty())
            Fail("invalid_conversion_metadata", "origin and factors required");
        for(const auto& value : conversion["factors"].toArray())
            if(!value.isDouble() || !std::isfinite(value.toDouble()) || value.toDouble() <= 0.) Fail("invalid_conversion_metadata", "factor");
    }
}

void CheckXmlNode(USerStorageXML& xml, const QString& path, const std::map<QString,QJsonObject>& nodes)
{
    const auto found = nodes.find(path);
    if(found == nodes.end()) Fail("unexpected_archive_node", path);
    const auto expected = found->second;
    if(QString::fromStdString(xml.GetNodeAttribute("Class")) != expected["class"].toString())
        Fail("archive_node_class_mismatch", path);
    const auto parameters = expected["parameters"].toObject();
    for(auto i = parameters.begin(); i != parameters.end(); ++i)
    {
        bool present = false;
        for(const auto* section : {"Parameters", "State"})
        {
            if(xml.GetNumNodes(section) > 1) Fail("duplicate_archive_section", path);
            if(!xml.SelectNode(section)) continue;
            const auto count = xml.GetNumNodes(i.key().toStdString());
            if(count > 1) Fail("duplicate_archive_parameter", path + ":" + i.key());
            present = present || count == 1; xml.SelectUp();
        }
        if(!present) Fail("missing_archive_parameter", path + ":" + i.key());
    }
    if(xml.GetNumNodes("Components") != 1 || !xml.SelectNode("Components")) Fail("missing_archive_components", path);
    const auto children = expected["child_order"].toArray();
    if(xml.GetNumNodes() != children.size()) Fail("archive_child_count_mismatch", path);
    for(int i = 0; i < children.size(); ++i)
    {
        if(!xml.SelectNode(i)) Fail("missing_archive_child", path);
        const auto name = QString::fromStdString(xml.GetNodeName());
        if(name != children[i].toString()) Fail("archive_child_order_mismatch", path);
        CheckXmlNode(xml, path + "." + name, nodes); xml.SelectUp();
    }
    xml.SelectUp();
}

void CheckSnapshot(const QJsonObject& snapshot)
{
    const auto text = RequiredString(snapshot, "native_xml");
    if(snapshot["native_xml_sha256"].toString() != XmlDigest(text)) Fail("native_xml_digest_mismatch", "graph");
    const auto identity = snapshot["identity"].toObject();
    if(!identity["valid"].toBool() || (identity["schema_version"] != QJsonValue(1) && identity["schema_version"] != QJsonValue(2)) ||
       identity["model"].toObject()["schema_version"] != identity["schema_version"] ||
       identity["kind"].toString() != "semantic_model_identity" ||
       identity["canonical_encoding"].toString() != "length-framed-utf8-binary64-v1" ||
       !identity["diagnostics"].isArray() || !identity["diagnostics"].toArray().isEmpty() ||
       identity["sha256"].toString() != CanonicalModelDataSha256(identity["model"]))
        Fail("invalid_archive_identity", "graph");
    std::map<QString,QJsonObject> nodes;
    for(const auto& entry : identity["model"].toObject()["nodes"].toArray())
    {
        auto node = entry.toObject(); auto path = RequiredString(node, "path");
        if(!nodes.emplace(path,node).second) Fail("duplicate_archive_node", path);
    }
    if(!nodes.count("$") || nodes.at("$")["class"] != snapshot["component_class"])
        Fail("invalid_archive_root", "class");
    USerStorageXML xml;
    if(!xml.Load(text.toStdString(), GraphRoot) || xml.GetNumNodes() != 1 ||
       !xml.SelectNode(RequiredString(snapshot,"component_name").toStdString()))
        Fail("invalid_native_xml", "root");
    CheckXmlNode(xml, "$", nodes);
}

std::map<QString, UIPropertyOutput*> BoundaryOutputs(const QJsonObject& identity,
                                                    const ModelBoundarySources& sources)
{
    std::map<QString, UIPropertyOutput*> outputs;
    for(const auto& source : sources)
    {
        auto output = dynamic_cast<const UIPropertyOutput*>(source.first);
        if(!output || !(source.first->GetType() & ptOutput) ||
           !dynamic_cast<const UVBaseDataProperty<MDMatrix<double>>*>(source.first) ||
           source.second.trimmed().isEmpty() || !outputs.emplace(source.second,const_cast<UIPropertyOutput*>(output)).second)
            Fail("invalid_boundary_sources", "distinct matrix-double outputs required");
    }
    QJsonArray expected;
    for(const auto& output : outputs) expected.append(QJsonObject{{"id",output.first},{"type","matrix_binary64"}});
    const auto semantic = identity["model"].toObject();
    if((outputs.empty() && identity["schema_version"] != QJsonValue(1)) ||
       (!outputs.empty() && (identity["schema_version"] != QJsonValue(2) || semantic["stimulus_ports"] != QJsonValue(expected))))
        Fail("boundary_sources_mismatch", "archive ports must match supplied outputs exactly");
    return outputs;
}

UEPtr<UContainer> LoadSnapshot(const QJsonObject& snapshot, UEPtr<UStorage> storage, UEPtr<UEnvironment> environment,
                              const ModelBoundarySources& boundarySources = {})
{
    CheckSnapshot(snapshot);
    const auto outputs = BoundaryOutputs(snapshot["identity"].toObject(),boundarySources);
    auto object = Take(storage, environment, snapshot["component_class"].toString());
    Lease lease{storage, object,!boundarySources.empty()};
    object->UnInit();
    USerStorageXML xml;
    if(!xml.Load(snapshot["native_xml"].toString().toStdString(), GraphRoot) ||
       !xml.SelectNode(snapshot["component_name"].toString().toStdString())) Fail("invalid_native_xml", "load root");
    TProjectLoadDiagnostics diagnostics;
    if(!object->LoadComponent(&xml, true, &diagnostics) || !diagnostics.errors.empty() || !diagnostics.warnings.empty())
        Fail("native_model_load_failed", object->GetName().c_str());
    object->Init();
    const auto bindings = snapshot["identity"].toObject()["model"].toObject()["bindings"].toArray();
    for(const auto& entry : bindings)
    {
        const auto binding = entry.toObject();
        if(binding["kind"].toString() != "stimulus_port") continue;
        const auto target = binding["target"].toString(); const auto separator = target.lastIndexOf(':');
        const auto path = target.left(separator); const auto name = target.mid(separator+1).toStdString();
        bool ok = false; const int slot = binding["slot"].toString().toInt(&ok);
        auto source = outputs.find(binding["source"].toString());
        if(separator < 1 || (path != "$" && !path.startsWith("$.")) || !ok || slot < 0 ||
           slot >= bindings.size() || source == outputs.end()) Fail("invalid_boundary_binding", target);
        UEPtr<UContainer> owner = path == "$" ? static_pointer_cast<UContainer>(object) : object->GetComponentL(path.mid(2).toStdString(),true);
        auto property = owner ? owner->FindProperty(name) : UEPtr<UIProperty>();
        auto input = property ? dynamic_cast<UIPropertyInput*>(property.Get()) : nullptr;
        auto sourceItem = dynamic_cast<UItem*>(source->second->GetOwner());
        auto connector = dynamic_pointer_cast<UConnector>(owner);
        int actualSlot = slot;
        if(!input || !(property->GetType() & ptInput) || !sourceItem || !connector ||
           !sourceItem->IsReady() || !sourceItem->IsInit() ||
           !sourceItem->Connect(connector,source->second->GetName(),name,actualSlot,true) || actualSlot != slot)
            Fail("boundary_binding_failed", target);
    }
    RequireMatch(snapshot["identity"].toObject(), object,boundarySources);
    return lease.Release();
}

struct ImageSource { QString kind, base; UEPtr<UContainer> prototype; };
ImageSource Source(UEPtr<UStorage> storage, const QString& name)
{
    if(!storage->CheckClass(name.toStdString())) Fail("missing_archive_class", name);
    auto factory = storage->GetComponentFactory(name.toStdString());
    auto image = dynamic_pointer_cast<UVirtualMethodFactory>(factory);
    if(!image) return {"native_required", {}, {}};
    auto prototype = image->GetComponent();
    if(!prototype) Fail("invalid_image_factory", name);
    if(prototype->GetClass() == ForbiddenId || prototype->GetClass() == factory->GetClassId())
        return {"native_required", {}, {}};
    return {"derived_image", QString::fromStdString(storage->FindClassName(prototype->GetClass())), prototype};
}

QJsonObject ImageSnapshot(UEPtr<UStorage> storage, UEPtr<UEnvironment> environment,
                         const QString& name, const ImageSource& source)
{
    UEPtr<UContainer> object;
    if(source.kind == "native_required") object = Take(storage, environment, name);
    else object = source.prototype->Alloc(storage, false);
    Lease lease{storage, object};
    if(!object) Fail("image_copy_failed", name);
    object->SetEnvironment(environment); object->Init();
    return Snapshot(object);
}
}

QJsonObject ExportModelArchive(UEPtr<UContainer> model, const QJsonObject& metadata,
                               const ModelBoundarySources& boundarySources)
try
{
    if(!model || !model->GetStorage() || !model->GetEnvironment()) Fail("invalid_archive_context", "model/storage/environment");
    if(!dynamic_pointer_cast<NMSDK::NPulseNeuron>(model)) Fail("unsupported_archive_model", "NPulseNeuron graph required");
    auto storage = model->GetStorage(); auto environment = model->GetEnvironment();
    auto graph = Snapshot(model,boundarySources); CheckSnapshot(graph);
    ValidateMetadata(metadata, graph["identity"].toObject());
    // Prove the native serializer represents this graph, including direct links
    // regenerated by native Build, before emitting an apparently usable archive.
    Lease rehearsal{storage, LoadSnapshot(graph, storage, environment,boundarySources),!boundarySources.empty()};
    QJsonArray definitions; std::set<QString> done, visiting;
    std::function<void(const QString&)> capture = [&](const QString& name) {
        if(done.count(name)) return;
        if(!visiting.insert(name).second) Fail("image_dependency_cycle", name);
        auto source = Source(storage, name);
        auto snapshot = ImageSnapshot(storage, environment, name, source); CheckSnapshot(snapshot);
        auto dependencies = Classes(snapshot["identity"].toObject());
        dependencies.erase(name);
        if(!source.base.isEmpty()) dependencies.insert(source.base);
        for(const auto& dependency : dependencies) capture(dependency);
        QJsonObject definition;
        definition["name"] = name; definition["kind"] = source.kind; definition["base_class"] = source.base;
        definition["snapshot"] = snapshot;
        QJsonArray dependenciesJson; for(const auto& dependency : dependencies) dependenciesJson.append(dependency);
        definition["dependencies"] = dependenciesJson;
        definitions.append(definition); visiting.erase(name); done.insert(name);
    };
    for(const auto& name : Classes(graph["identity"].toObject())) capture(name);
    QJsonObject archive;
    archive["schema_version"] = boundarySources.empty() ? 1 : 2; archive["kind"] = "timelearner_model_archive";
    archive["encoding"] = boundarySources.empty() ? "native-xml-and-model-identity-v1" : "native-xml-and-model-identity-v2";
    archive["dynamic_checkpoint"] = false;
    archive["metadata"] = metadata; archive["graph"] = graph; archive["class_definitions"] = definitions;
    archive["sha256"] = CanonicalModelDataSha256(archive);
    return archive;
}
catch(const UException& error) { Fail("native_archive_export_failed",QString::fromStdString(std::string(typeid(error).name())+": "+error.what())); }

UEPtr<UContainer> ImportModelArchive(const QJsonObject& archive, UEPtr<UStorage> storage,
    UEPtr<UEnvironment> environment, const QString& implementationId, const ModelBoundarySources& boundarySources)
try
{
    if(!storage || !environment) Fail("invalid_archive_context", "storage/environment");
    const int version = boundarySources.empty() ? 1 : 2;
    if(archive["schema_version"] != QJsonValue(version) || archive["kind"].toString() != "timelearner_model_archive" ||
       archive["encoding"].toString() != QString("native-xml-and-model-identity-v%1").arg(version) || archive["dynamic_checkpoint"] != QJsonValue(false))
        Fail("unsupported_archive_schema", "header");
    auto payload = archive; payload.remove("sha256");
    if(archive["sha256"].toString() != CanonicalModelDataSha256(payload)) Fail("archive_digest_mismatch", "payload");
    const auto metadata = archive["metadata"].toObject();
    if(implementationId.isEmpty() || metadata["implementation_id"].toString() != implementationId)
        Fail("implementation_identity_mismatch", "runtime");
    const auto graph = archive["graph"].toObject(); CheckSnapshot(graph);
    BoundaryOutputs(graph["identity"].toObject(),boundarySources);
    ValidateMetadata(metadata, graph["identity"].toObject());
    if(!archive["class_definitions"].isArray()) Fail("missing_class_definitions", "array required");
    std::set<QString> declared;
    const auto definitions = archive["class_definitions"].toArray();
    // Validate every document and the complete ordered dependency closure before
    // registering the first image or constructing the imported learned model.
    for(const auto& entry : definitions)
    {
        const auto definition = entry.toObject(); const auto name = RequiredString(definition,"name");
        if(declared.count(name)) Fail("duplicate_class_definition", name);
        auto snapshot = definition["snapshot"].toObject(); CheckSnapshot(snapshot);
        if(snapshot["identity"].toObject()["schema_version"] != QJsonValue(1))
            Fail("image_has_boundary_ports", name);
        const auto kind = RequiredString(definition,"kind");
        auto dependencies = Classes(snapshot["identity"].toObject()); dependencies.erase(name);
        if(kind == "derived_image")
        {
            const auto base = RequiredString(definition,"base_class");
            if(base == name || snapshot["component_class"].toString() != base) Fail("invalid_image_base", name);
            dependencies.insert(base);
        }
        else if(kind != "native_required" || !definition["base_class"].toString().isEmpty() || snapshot["component_class"].toString() != name)
            Fail("invalid_image_definition", name);
        QJsonArray expected; for(const auto& dependency : dependencies) expected.append(dependency);
        if(definition["dependencies"] != QJsonValue(expected)) Fail("invalid_class_dependencies", name);
        for(const auto& dependency : dependencies)
            if(!declared.count(dependency)) Fail("missing_or_unordered_class_dependency", dependency);
        declared.insert(name);
    }
    for(const auto& name : Classes(graph["identity"].toObject()))
        if(!declared.count(name)) Fail("missing_class_definition", name);
    for(const auto& entry : definitions)
    {
        const auto definition = entry.toObject(); const auto name = definition["name"].toString();
        const auto snapshot = definition["snapshot"].toObject();
        if(definition["kind"].toString() == "native_required" || storage->CheckClass(name.toStdString()))
        {
            auto source = Source(storage, name);
            if(source.kind != definition["kind"].toString() || source.base != definition["base_class"].toString())
                Fail("image_factory_mismatch", name);
            auto actual = ImageSnapshot(storage, environment, name, source);
            if(actual["identity"] != snapshot["identity"]) Fail("image_definition_collision", name);
        }
        else
        {
            Lease candidate{storage, LoadSnapshot(snapshot, storage, environment)};
            RegisterClassImage(storage, name.toStdString(), candidate.object);
        }
    }
    Lease imported{storage,LoadSnapshot(graph, storage, environment,boundarySources),!boundarySources.empty()};
    if(!dynamic_pointer_cast<NMSDK::NPulseNeuron>(imported.object)) Fail("unsupported_archive_model", "NPulseNeuron graph required");
    return imported.Release();
}
catch(const UException& error) { Fail("native_archive_import_failed",QString::fromStdString(std::string(typeid(error).name())+": "+error.what())); }
}
