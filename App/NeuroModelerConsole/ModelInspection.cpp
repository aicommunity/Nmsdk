#include "ModelInspection.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseChannel.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseSynapse.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseNeuronCommon.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseMembraneCommon.h"

#include <QJsonArray>
#include <cmath>
#include <map>
#include <set>
#include <stdexcept>

namespace NmsdkTools {
namespace {
using namespace RDK;

struct Entry { UEPtr<UContainer> component; std::string path; };

void Collect(UEPtr<UContainer> component, const std::string& path,
             std::vector<Entry>& entries, std::set<const UContainer*>& seen)
{
    if(!component || !seen.insert(component.Get()).second)
        throw std::runtime_error("missing or repeated component in native graph");
    entries.push_back({component, path});
    std::vector<NameT> names;
    component->GetComponentsList(names);
    for(const auto& name : names)
        Collect(component->GetComponent(name, true), path + "." + name, entries, seen);
}

void Number(QJsonObject& destination, const char* name, double value,
            const std::string& path, QJsonArray& diagnostics)
{
    if(!std::isfinite(value))
    {
        destination[name] = QJsonValue(QJsonValue::Null);
        diagnostics.append(QString::fromStdString(path + ": nonfinite " + name));
    }
    else destination[name] = value;
}
}

QJsonObject InspectModel(RDK::UEPtr<RDK::UContainer> model)
{
    if(!model) throw std::runtime_error("no model to inspect");
    std::vector<Entry> entries;
    std::set<const UContainer*> seen;
    Collect(model, model->GetName(), entries, seen);
    std::map<const UContainer*, std::string> paths;
    std::map<const UIProperty*, std::string> propertyPaths;
    for(const auto& entry : entries)
    {
        paths[entry.component.Get()] = entry.path;
        for(const auto& property : entry.component->GetPropertiesList())
            propertyPaths[property.second.Property.Get()] = entry.path + ":" + property.first;
    }
    QJsonArray nodes, links, diagnostics;
    for(const auto& entry : entries)
    {
        auto component = entry.component;
        QJsonObject node;
        node["path"] = QString::fromStdString(entry.path);
        node["class"] = QString::fromStdString(component->GetCompClassName());
        node["active"] = component->GetActivity();
        node["initialized"] = component->IsInit();
        node["ready"] = component->IsReady();
        Number(node, "frequency_hz", double(component->GetTimeStep()), entry.path, diagnostics);
        QJsonObject properties;
        for(const auto& name : component->GetPropertiesOrder())
        {
            auto property = component->FindProperty(name);
            if(!property) throw std::runtime_error("registered property is missing: " + entry.path + ":" + name);
            QJsonObject value;
            value["mask"] = int(property->GetType());
            const QString normalizedName = QString::fromStdString(name).toLower();
            const bool sensitive = normalizedName == "password" || normalizedName == "apikey" ||
                normalizedName == "api_key" || normalizedName == "accesstoken" ||
                normalizedName == "access_token" || normalizedName == "secretkey" || normalizedName == "secret_key";
            // A property's textual value uses Rdk's serializer; no XML regex
            // or direct memory assignment is used to obtain the readback.
            try
            {
                std::string serialized;
                if(sensitive)
                {
                    value["redacted"] = true;
                    diagnostics.append(QString::fromStdString(entry.path + ":" + name + ": excluded credential property"));
                }
                else
                {
                    component->GetPropertyValue(name, serialized);
                    value["rdk_value"] = QString::fromStdString(serialized);
                }
            }
            catch(const std::exception& exception)
            {
                diagnostics.append(QString::fromStdString(entry.path + ":" + name + ": " + exception.what()));
                value["read_error"] = true;
            }
            if(auto input = dynamic_cast<UIPropertyInput*>(property.Get()))
            {
                value["connected"] = input->IsConnected() || input->UsesExternalDataSource();
                value["bindings_inspectable"] = input->CanInspectDataSources();
                const auto sources = input->GetDataSources();
                if((input->IsConnected() || input->UsesExternalDataSource()) &&
                   (!input->CanInspectDataSources() || sources.empty()))
                    diagnostics.append(QString::fromStdString(entry.path + ":" + name + ": connected property has no inspectable data source"));
                for(size_t i = 0; i < sources.size(); ++i)
                {
                    auto found = propertyPaths.find(sources[i]);
                    QJsonObject link;
                    link["target"] = QString::fromStdString(entry.path + ":" + name);
                    link["target_slot"] = int(i);
                    link["binding_kind"] = input->UsesExternalDataSource() ? "external_data_source" : "property_pointer";
                    if(found == propertyPaths.end())
                    {
                        link["source"] = QJsonValue(QJsonValue::Null);
                        link["resolved_in_scope"] = false;
                        diagnostics.append(QString::fromStdString(entry.path + ":" + name + ": null or out-of-scope data source"));
                    }
                    else
                    {
                        link["source"] = QString::fromStdString(found->second);
                        link["resolved_in_scope"] = true;
                    }
                    links.append(link);
                }
            }
            properties[QString::fromStdString(name)] = value;
        }
        node["properties"] = properties;
        QJsonObject physics;
        if(auto channel = dynamic_cast<NMSDK::NPulseChannel*>(component.Get()))
        {
            Number(physics, "capacity_f", channel->Capacity.GetData(), entry.path, diagnostics);
            Number(physics, "resistance_ohm", channel->Resistance.GetData(), entry.path, diagnostics);
            Number(physics, "resting_resistance_ohm", channel->RestingResistance.GetData(), entry.path, diagnostics);
            Number(physics, "time_constant_s", channel->TimeConstant.GetData(), entry.path, diagnostics);
        }
        if(auto synapse = dynamic_cast<NMSDK::NPulseSynapse*>(component.Get()))
        {
            Number(physics, "resistance_ohm", synapse->Resistance.GetData(), entry.path, diagnostics);
            Number(physics, "secretion_tc_s", synapse->SecretionTC.GetData(), entry.path, diagnostics);
            Number(physics, "dissociation_tc_s", synapse->DissociationTC.GetData(), entry.path, diagnostics);
            Number(physics, "typical_pulse_duration_s", synapse->TypicalPulseDuration.GetData(), entry.path, diagnostics);
            Number(physics, "inhibition_coefficient", synapse->InhibitionCoeff.GetData(), entry.path, diagnostics);
            physics["presynaptic_inhibition"] = synapse->UsePresynapticInhibition.GetData();
        }
        node["physics"] = physics;
        QJsonArray cachedMembranes, cachedChannels;
        auto cachePath = [&](const UContainer* pointer) {
            auto found = paths.find(pointer);
            if(found == paths.end())
            {
                diagnostics.append(QString::fromStdString(entry.path + ": cached component is outside the named graph"));
                return QJsonValue(QJsonValue::Null);
            }
            return QJsonValue(QString::fromStdString(found->second));
        };
        if(auto neuron = dynamic_cast<NMSDK::NPulseNeuronCommon*>(component.Get()))
        {
            for(auto membrane : neuron->Membranes) cachedMembranes.append(cachePath(membrane));
            node["cached_ltzone"] = neuron->GetLTZone() ? cachePath(neuron->GetLTZone()) : QJsonValue(QJsonValue::Null);
        }
        if(auto membrane = dynamic_cast<NMSDK::NPulseMembraneCommon*>(component.Get()))
            for(size_t i = 0; i < membrane->GetNumChannels(); ++i)
                cachedChannels.append(cachePath(membrane->GetChannel(i)));
        node["cached_membranes"] = cachedMembranes;
        node["cached_channels"] = cachedChannels;
        QJsonArray children;
        std::vector<NameT> names;
        component->GetComponentsList(names);
        for(const auto& name : names) children.append(QString::fromStdString(entry.path + "." + name));
        node["child_order"] = children;
        nodes.append(node);
    }
    QJsonObject result;
    result["schema_version"] = 1;
    result["kind"] = "effective_model_readback";
    result["lifecycle_mutated_by_inspector"] = false;
    result["nodes"] = nodes;
    result["links"] = links;
    result["diagnostics"] = diagnostics;
    result["valid"] = diagnostics.isEmpty();
    return result;
}
}
