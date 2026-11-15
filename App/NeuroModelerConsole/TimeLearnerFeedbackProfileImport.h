#pragma once
#include "TimeLearnerJobSupport.h"
#include "TimeLearner/NativeLearnedState.h"
#include "TimeLearner/StorageProfiles.h"
#include "NPulseLTZoneCommon.h"
#include "NPulseSynapse.h"
#include <QRegularExpression>

namespace NmsdkWorker {
struct FeedbackProfileIntervention {
    std::string imagePrefix;
    double gain=0.;
    bool baseline=false;
};
inline FeedbackProfileIntervention ReadFeedbackProfileIntervention(const QJsonObject& value)
{
    Keys(value,{"kind","image_prefix","feedback_gain","baseline_reconstruction"});
    Require(value["kind"]==QJsonValue("uniform_feedback_storage_profile"),"unsupported_feedback_profile_intervention");
    FeedbackProfileIntervention result;result.imagePrefix=Text(value["image_prefix"]);result.gain=Number(value["feedback_gain"]);
    Require(result.gain>=0. && value["baseline_reconstruction"].isBool(),"invalid_feedback_profile_intervention");
    result.baseline=value["baseline_reconstruction"].toBool();
    Require(QRegularExpression("\\A[A-Za-z][A-Za-z0-9_]{0,95}\\z").match(QString::fromStdString(result.imagePrefix)).hasMatch(),
        "invalid_feedback_profile_image_prefix");
    return result;
}
struct PreparedFeedbackProbe {
    NMSDK::TimeLearner::NativeModelBuildResult built;
    NMSDK::TimeLearner::NativeModelSpec declaration;
    QJsonObject record,identity;
};
struct UnownedProbeGraph {
    RDK::UEPtr<RDK::UStorage> storage;
    RDK::UEPtr<RDK::UContainer> node;
    ~UnownedProbeGraph(){if(node && !node->GetOwner()){if(auto net=RDK::dynamic_pointer_cast<RDK::UNet>(node))net->BreakLinks();storage->ReturnObject(node);}}
};
template<class Owner> PreparedFeedbackProbe InstallFeedbackProfileProbe(Owner& owner,
    const QJsonObject& source,const std::string& implementation,const FeedbackProfileIntervention& intervention)
{
    using namespace RDK;using namespace NMSDK;using namespace NMSDK::TimeLearner;
    auto storage=owner.GetStorage();auto environment=owner.GetEnvironment();
    auto original=PrepareNativeLearnedState(source,storage,environment,implementation);
    Require(original->neuron && original->dataset,"feedback_probe_source_children_missing");
    auto generator=original->dataset->template GetComponentL<NPulseGeneratorTransit>("Generator1",true);
    Require(bool(generator),"feedback_probe_source_generator_missing");
    const NmsdkTools::ModelBoundarySources ports{{&generator->Output,"burst"}};
    const auto snapshot=NmsdkTools::ExportPhysicalGraphForEdit(original->neuron,ports);
    const auto originalDataset=NmsdkTools::ExportDatasetSnapshot(original->dataset)["identity"].toObject();
    Require(snapshot["identity"]==Object(Object(source["neuron"])["graph"])["identity"],"feedback_probe_source_identity_changed");
    FeedbackStorageProfileSpec recipe;recipe.name=intervention.imagePrefix;recipe.frequencyHz=owner.GetTimeStep();
    recipe.neuronBaseClass=original->neuron->GetCompClassName();recipe.bodyFeedbackGain=intervention.gain;
    const auto body=original->neuron->MembraneClassName.GetData(),lt=original->neuron->LTMembraneClassName.GetData();
    if(!lt.empty())recipe.ltFeedbackGain=intervention.gain;
    const auto images=RegisterFeedbackStorageProfile(storage,environment,recipe);
    std::map<std::string,std::string> names{{recipe.neuronBaseClass,images.neuronClass},{body,images.bodyMembraneClass}};
    if(!lt.empty() && lt!=body)names.emplace(lt,images.ltMembraneClass);
    const auto gain=intervention.baseline?std::optional<double>{}:std::optional<double>{intervention.gain};
    auto candidate=NmsdkTools::ImportFeedbackProfileGraphForEdit(snapshot,storage,environment,names,gain,ports);
    UnownedProbeGraph lease{storage,candidate};auto neuron=dynamic_pointer_cast<NPulseNeuron>(candidate);
    Require(bool(neuron),"feedback_probe_candidate_neuron_missing");
    PreparedFeedbackProbe result;result.identity=NmsdkTools::IdentifyModel(candidate,ports);
    auto& declaration=result.declaration;declaration=original->configuration.model;
    declaration.neuronClass=neuron->GetCompClassName();declaration.neuronStructureMode=neuron->StructureBuildMode.GetData();
    Require(declaration.neuronStructureMode==1 || declaration.neuronStructureMode==2,"feedback_probe_structure_mode_not_supported");
    declaration.inputs.clear();
    for(const auto& p:original->parameters)declaration.inputs.push_back({p.length,p.synapses,p.resistance});
    if(declaration.neuronStructureMode==2)declaration.allocatedCableLengths=neuron->NumDendriteMembranePartsVec.GetData();
    else declaration.allocatedCableLengths.assign(declaration.branch?1:declaration.inputs.size(),neuron->NumDendriteMembraneParts.GetData());
    declaration.allowMutedInputBaseline=declaration.branch;
    // Derive inhibition bank values from actual imported components, not an
    // initial-parameter formula which could discard a trained correction.
    for(auto& rule:declaration.editPolicy.inhibition)
    {
        const auto& p=original->parameters.at(rule.inputIndex);
        const auto path="Dendrite"+std::to_string(declaration.branch?1:rule.inputIndex+1)+"_"+
            std::to_string(p.length+rule.offset)+".InhSynapse1";
        auto synapse=neuron->template GetComponentL<NPulseSynapseCommon>(path,true);
        Require(bool(synapse),"feedback_probe_inhibition_bank_missing");rule.resistance=synapse->Resistance.GetData();
    }
    auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);
    Require(bool(zone),"feedback_probe_threshold_zone_missing");
    declaration.schemaVersion=2;declaration.initialThreshold=zone->Threshold.GetData();
    ValidateNativeModelSpec(declaration);
    result.built=owner.InstallNativePreparedModel(declaration,neuron,original->dataset,original->parameters);
    Require(result.built.status==NativeModelBuildStatus::Adopted,result.built.reason.c_str());
    Require(NmsdkTools::IdentifyModel(neuron,ports)==result.identity,"feedback_probe_attachment_changed_model");
    Require(NmsdkTools::ExportDatasetSnapshot(original->dataset)["identity"]==QJsonValue(originalDataset),"feedback_probe_dataset_changed");
    QJsonObject renames;for(const auto& entry:names)renames[QString::fromStdString(entry.first)]=QString::fromStdString(entry.second);
    const auto definitions=NmsdkTools::CaptureModelImageDefinitions(neuron,ports);
    result.record=Signed({{"kind","native_feedback_profile_import"},{"schema_version",1},
        {"source_stopped_sha256",source["sha256"]},{"source_identity",snapshot["identity"]},{"candidate_identity",result.identity},
        {"dataset_identity",originalDataset},{"class_renames",renames},{"image_prefix",QString::fromStdString(intervention.imagePrefix)},
        {"feedback_gain",intervention.gain},{"baseline_reconstruction",intervention.baseline},
        {"image_definitions",definitions},{"image_definitions_fingerprint",NmsdkTools::ModelImageDefinitionsFingerprint(definitions)},
        {"physical_dynamics_reset",true},{"controller_history_copied",false},{"certificate_copied",false},{"training_started",false}});
    return result;
}
}
