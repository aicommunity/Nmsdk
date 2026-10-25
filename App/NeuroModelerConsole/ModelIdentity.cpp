#include "ModelIdentity.h"
#include "ModelInspection.h"
#include <QCryptographicHash>
#include <QJsonArray>
#include <cmath>
#include <cstring>
#include <cstdint>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>

namespace NmsdkTools {
namespace {
using namespace RDK;
struct Node { UEPtr<UContainer> component; QString path; };

QString F64(double value)
{
    static_assert(sizeof(double) == sizeof(std::uint64_t) && std::numeric_limits<double>::is_iec559,
                  "Model identity requires IEEE754 binary64");
    if(!std::isfinite(value)) throw std::runtime_error("nonfinite_parameter");
    if(value == 0.) value = 0.; // canonicalize negative zero
    std::uint64_t bits; std::memcpy(&bits, &value, sizeof(bits));
    return QString::number(static_cast<qulonglong>(bits), 16).rightJustified(16, QLatin1Char('0'));
}

template<class T> QJsonValue Scalar(T value) { return QString::fromStdString(std::to_string(value)); }
template<> QJsonValue Scalar<double>(double value) { return F64(value); }
template<> QJsonValue Scalar<bool>(bool value) { return value; }
template<> QJsonValue Scalar<std::string>(std::string value) { return QString::fromStdString(value); }

template<class T>
bool Simple(UIProperty* property, const char* kind, QJsonObject& result)
{
    auto typed = dynamic_cast<UVBaseDataProperty<T>*>(property);
    if(!typed) return false;
    result["type"] = kind; result["value"] = Scalar<T>(typed->GetData());
    return true;
}

template<class T>
bool Vector(UIProperty* property, const char* kind, QJsonObject& result)
{
    auto typed = dynamic_cast<UVBaseDataProperty<std::vector<T>>*>(property);
    if(!typed) return false;
    QJsonArray values;
    for(const auto& value : typed->GetData()) values.append(Scalar<T>(value));
    result["type"] = kind; result["value"] = values;
    return true;
}

template<class T>
bool Matrix(UIProperty* property, const char* kind, QJsonObject& result)
{
    auto typed = dynamic_cast<UVBaseDataProperty<MDMatrix<T>>*>(property);
    if(!typed) return false;
    const auto& matrix = typed->GetData();
    QJsonArray rows;
    for(int r = 0; r < matrix.GetRows(); ++r)
    {
        QJsonArray columns;
        for(int c = 0; c < matrix.GetCols(); ++c) columns.append(Scalar<T>(matrix(r,c)));
        rows.append(columns);
    }
    result["type"] = kind; result["rows"] = QString::number(matrix.GetRows());
    result["columns"] = QString::number(matrix.GetCols()); result["value"] = rows;
    return true;
}

QJsonObject Value(UIProperty* property)
{
    QJsonObject result;
    if(Simple<bool>(property, "boolean", result) || Simple<double>(property, "binary64", result) ||
       Simple<int>(property, "signed_integer", result) || Simple<long>(property, "signed_integer", result) ||
       Simple<long long>(property, "signed_integer", result) ||
       Simple<unsigned int>(property, "unsigned_integer", result) ||
       Simple<unsigned long>(property, "unsigned_integer", result) ||
       Simple<unsigned long long>(property, "unsigned_integer", result) ||
       Simple<std::string>(property, "utf8", result) ||
       Vector<double>(property, "binary64_vector", result) || Vector<int>(property, "integer_vector", result) ||
       Vector<std::string>(property, "utf8_vector", result) ||
       Matrix<double>(property, "binary64_matrix", result) || Matrix<int>(property, "integer_matrix", result))
        return result;
    throw std::runtime_error("unsupported_parameter_type");
}

void Collect(UEPtr<UContainer> component, const QString& path, std::vector<Node>& nodes,
             std::set<const UContainer*>& seen)
{
    if(!component || !seen.insert(component.Get()).second) throw std::runtime_error("invalid_graph");
    nodes.push_back({component, path});
    std::vector<NameT> children; component->GetComponentsList(children);
    for(const auto& child : children)
        Collect(component->GetComponent(child, true), path + "." + QString::fromStdString(child), nodes, seen);
}

// Length-framed UTF8 and explicit value tags avoid Qt5/Qt6 JSON number-format
// differences, locale dependence, compiler typeid names and ambiguous joins.
void Frame(QByteArray& destination, const QByteArray& bytes)
{
    destination += QByteArray::number(bytes.size()); destination += ':'; destination += bytes;
}

void Canonical(QByteArray& bytes, const QJsonValue& value)
{
    if(value.isObject())
    {
        bytes += 'o'; const auto object = value.toObject();
        Frame(bytes, QByteArray::number(object.size()));
        for(auto i = object.begin(); i != object.end(); ++i)
        { Frame(bytes, i.key().toUtf8()); Canonical(bytes, i.value()); }
    }
    else if(value.isArray())
    {
        bytes += 'a'; const auto array = value.toArray(); Frame(bytes, QByteArray::number(array.size()));
        for(const auto& element : array) Canonical(bytes, element);
    }
    else if(value.isString()) { bytes += 's'; Frame(bytes, value.toString().toUtf8()); }
    else if(value.isBool()) bytes += value.toBool() ? 't' : 'f';
    else if(value.isDouble()) { bytes += 'd'; Frame(bytes, F64(value.toDouble()).toLatin1()); }
    else if(value.isNull()) bytes += 'n';
    else throw std::runtime_error("undefined_identity_value");
}

bool Excluded(const std::string& name)
{
    // These UContainer properties affect identity/presentation/diagnostics,
    // not the numerical model. MaxCalculationDuration is intentionally included:
    // its budget can skip child calculation and changes the effective protocol.
    return name == "Name" || name == "Id" || name == "Coord" ||
           name == "DebugSysEventsMask" || name == "CalculationDurationThreshold";
}
}

QJsonObject IdentifyModel(UEPtr<UContainer> model)
{
    QJsonObject result; result["schema_version"] = 1; result["kind"] = "semantic_model_identity";
    result["canonical_encoding"] = "length-framed-utf8-binary64-v1";
    QJsonArray diagnostics, serializedNodes, bindings, caches;
    try
    {
        std::vector<Node> nodes; std::set<const UContainer*> seen;
        Collect(model, "$", nodes, seen);
        std::map<const UIProperty*, QString> propertyPaths;
        for(const auto& node : nodes)
            for(const auto& property : node.component->GetPropertiesList())
                propertyPaths[property.second.Property.Get()] = node.path + ":" + QString::fromStdString(property.first);
        for(const auto& node : nodes)
        {
            auto component = node.component;
            if(!component->IsReady() || !component->IsInit())
                diagnostics.append(node.path + ": model_not_ready_or_initialized");
            if(component->GetTimeStep() == 0) diagnostics.append(node.path + ": invalid_frequency");
            QJsonObject object, parameters;
            object["path"] = node.path;
            object["class"] = QString::fromStdString(component->GetCompClassName());
            object["frequency_hz"] = QString::number(component->GetTimeStep());
            for(const auto& name : component->GetPropertiesOrder())
            {
                auto property = component->FindProperty(name);
                if(!property) throw std::runtime_error("missing_registered_property");
                const QString path = node.path + ":" + QString::fromStdString(name);
                auto input = dynamic_cast<UIPropertyInput*>(property.Get());
                const bool connected = input && (input->IsConnected() || input->UsesExternalDataSource());
                if((property->GetType() & ptParameter) && !Excluded(name))
                {
                    try
                    {
                        // Bound parameters get their value from the source;
                        // sampling that source's dynamic value is not model identity.
                        QJsonObject parameter;
                        parameter["mask"] = QString::number(property->GetType());
                        parameter["binding"] = connected;
                        if(!connected) parameter["data"] = Value(property.Get());
                        parameters[QString::fromStdString(name)] = parameter;
                    }
                    catch(const std::exception& error) { diagnostics.append(path + ": " + error.what()); }
                }
                if(connected)
                {
                    const auto sources = input->GetDataSources();
                    if(!input->CanInspectDataSources() || sources.empty())
                        diagnostics.append(path + ": uninspectable_binding");
                    for(size_t i = 0; i < sources.size(); ++i)
                    {
                        const auto found = propertyPaths.find(sources[i]);
                        if(found == propertyPaths.end()) { diagnostics.append(path + ": external_or_null_binding"); continue; }
                        QJsonObject binding;
                        binding["target"] = path; binding["slot"] = QString::number(qulonglong(i));
                        binding["source"] = found->second;
                        binding["kind"] = input->UsesExternalDataSource() ? "external_data_source" : "property_pointer";
                        bindings.append(binding);
                    }
                }
            }
            object["parameters"] = parameters;
            QJsonArray children; std::vector<NameT> names; component->GetComponentsList(names);
            for(const auto& name : names) children.append(QString::fromStdString(name));
            object["child_order"] = children;
            QJsonArray aliases;
            if(auto net = dynamic_pointer_cast<UNet>(component))
                for(const auto& alias : net->GetPropertyAliases())
                {
                    QJsonObject entry;
                    entry["name"] = QString::fromStdString(alias.first);
                    entry["component"] = QString::fromStdString(alias.second.ComponentPath);
                    entry["property"] = QString::fromStdString(alias.second.PropertyName);
                    entry["type"] = QString::number(alias.second.PropertyType); aliases.append(entry);
                }
            object["aliases"] = aliases;
            serializedNodes.append(object);
        }
        // The inspector additionally checks cached neuron/membrane pointers.
        const auto readback = InspectModel(model);
        if(!readback["valid"].toBool())
            for(const auto& diagnostic : readback["diagnostics"].toArray()) diagnostics.append(diagnostic);
        const QString root = QString::fromStdString(model->GetName());
        const auto relative = [&root](const QJsonValue& value) -> QJsonValue {
            if(value.isNull()) return value;
            const auto path = value.toString();
            if(path != root && !path.startsWith(root + ".")) throw std::runtime_error("cache_outside_model");
            return "$" + path.mid(root.size());
        };
        for(const auto& entry : readback["nodes"].toArray())
        {
            const auto node = entry.toObject(); QJsonObject cache;
            cache["path"] = relative(node["path"]);
            for(const auto& key : {"cached_ltzone", "cached_positive_generator", "cached_negative_generator"})
                if(node.contains(key)) cache[key] = relative(node[key]);
            for(const auto& key : {"cached_membranes", "cached_channels"})
            {
                QJsonArray paths;
                for(const auto& path : node[key].toArray()) paths.append(relative(path));
                cache[key] = paths;
            }
            caches.append(cache);
        }
    }
    catch(const std::exception& error) { diagnostics.append(QString::fromUtf8(error.what())); }
    QJsonObject semantic;
    semantic["schema_version"] = 1; semantic["nodes"] = serializedNodes;
    semantic["bindings"] = bindings; semantic["caches"] = caches;
    result["model"] = semantic; result["diagnostics"] = diagnostics; result["valid"] = diagnostics.isEmpty();
    if(diagnostics.isEmpty())
    {
        QByteArray canonical; Canonical(canonical, semantic);
        result["sha256"] = QString::fromLatin1(QCryptographicHash::hash(canonical, QCryptographicHash::Sha256).toHex());
    }
    return result;
}
}
