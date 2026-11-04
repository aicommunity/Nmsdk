#include "TimeLearnerProbeJob.h"
#include "TimeLearnerProbeEvidenceWriter.h"
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "TimeLearner/NativeCalculationPolicy.h"
#include "TimeLearner/NumericChecks.h"
#include "TimeLearner/ModelArchive.h"
#include <chrono>
#include <iostream>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
using namespace NmsdkWorker;
struct Job {
    QJsonObject document;
    NativeModelSpec model;
    StimulusProfile stimulus;
    QJsonArray profiles;
    std::string ownerClass,runId,trialId,sampleId,protocolRevision;
    std::size_t input=0,maximumTicks=0,maximumSamples=0;
    double duration=0.,gap=0.,minimumAmplitude=0.,windowBegin=0.,windowEnd=0.,wallSeconds=0.;
    bool recordSpikes=false;
    PeakSelectionPolicy selection=PeakSelectionPolicy::IsolatedWindow;
};
bool Boolean(const QJsonValue& v){Require(v.isBool(),"probe_boolean_required");return v.toBool();}
Job Read(const QString& path)
{
    Job j;j.document=ReadDocument(path);const auto& d=j.document;
    Keys(d,{"kind","schema_version","owner_class","implementation_id","model","profile_archives",
        "stimulus_profile","probe","maximum_model_ticks","maximum_wall_seconds","sha256"});
    Require(d["kind"]==QJsonValue("timelearner_native_probe_job") && Count(d["schema_version"],1,1)==1,"unsupported_probe_job");
    Require(Signed(d)==d,"job_digest_mismatch");Text(d["implementation_id"]);
    j.model=DecodeNativeModelSpec(Object(d["model"]));ValidateNativeModelSpec(j.model);
    j.ownerClass=Text(d["owner_class"]);
    Require(j.ownerClass==(j.model.branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"),"probe_owner_mismatch");
    j.profiles=Array(d["profile_archives"]);Require(j.profiles.size()<=32,"probe_profile_budget_exceeded");
    for(const auto& p:j.profiles)Object(p);
    const auto source=Object(d["stimulus_profile"]);
    Keys(source,{"generator_class","amplitude","pulse_length","frequency_hz","frequency_deviation","use_transit_signal","use_pattern_output"});
    j.stimulus={Text(source["generator_class"]),Number(source["amplitude"]),Number(source["pulse_length"]),Number(source["frequency_hz"]),
        Number(source["frequency_deviation"]),Boolean(source["use_transit_signal"]),Boolean(source["use_pattern_output"])};
    const auto p=Object(d["probe"]);
    Keys(p,{"run_id","trial_id","sample_id","protocol_revision","input_index","duration","maximum_sample_gap",
        "minimum_amplitude","maximum_samples","record_spikes","peak_selection","window"});
    j.runId=Text(p["run_id"]);j.trialId=Text(p["trial_id"]);j.sampleId=Text(p["sample_id"]);j.protocolRevision=Text(p["protocol_revision"]);
    j.input=Count(p["input_index"],0,j.model.inputs.size()-1);j.duration=Number(p["duration"]);j.gap=Number(p["maximum_sample_gap"]);
    j.minimumAmplitude=Number(p["minimum_amplitude"]);j.maximumSamples=Count(p["maximum_samples"],1,100000000);
    j.recordSpikes=Boolean(p["record_spikes"]);
    Require(!j.recordSpikes,"native_probe_spike_capture_not_supported");
    const auto selection=Text(p["peak_selection"]);
    Require(selection=="isolated_window" || selection=="assigned_burst_wave","invalid_probe_selection");
    j.selection=selection=="isolated_window"?PeakSelectionPolicy::IsolatedWindow:PeakSelectionPolicy::AssignedBurstWave;
    const auto w=Object(p["window"]);Keys(w,{"begin","end"});j.windowBegin=Number(w["begin"]);j.windowEnd=Number(w["end"]);
    j.maximumTicks=Count(d["maximum_model_ticks"],1,1000000000);j.wallSeconds=Number(d["maximum_wall_seconds"]);
    Require(j.wallSeconds>0.,"invalid_probe_wall_budget");return j;
}
ConfiguredNativeTraining IdleConfiguration(const Job& j,const std::vector<InputParameters>& parameters)
{
    // The existing V2 owner uses its normal configuration/lifecycle path. No
    // search is started. Its internal fixed bounds cannot edit this model.
    ConfiguredNativeTraining c;c.model=j.model;c.stimulusProfile=j.stimulus;c.runId=j.runId;
    c.protocolRevision=j.protocolRevision;c.sampleId=j.sampleId;c.duration=j.duration;c.maximumSampleGap=j.gap;
    c.minimumAmplitude=j.minimumAmplitude;c.maximumSamples=j.maximumSamples;c.recordSpikes=j.recordSpikes;c.peakSelection=j.selection;
    c.maximumReferenceProbes=parameters.size();c.maximumModelSeconds=j.duration;c.maximumWallSeconds=j.wallSeconds;
    c.search.normalization=j.model.normalization;c.search.maximumProbes=1;c.search.maximumEdits=1;
    c.search.maximumCandidatesPerInput=1;c.search.maximumSweeps=1;c.search.resistanceSubdivisionDepth=0;
    for(std::size_t i=0;i<parameters.size();++i) {
        const auto& p=parameters[i];c.model.inputs[i].resistance=p.resistance;
        c.windows.emplace_back(i==j.input?j.windowBegin:0.,i==j.input?j.windowEnd:j.duration);
        c.search.bounds.push_back({p.length,p.length,p.synapses,p.synapses,p.resistance,p.resistance});
    }
    MakeConfiguredNativeTrainingPlan(c);return c;
}
QJsonArray Parameters(const std::vector<InputParameters>& values)
{QJsonArray a;for(const auto& p:values)a.append(QJsonObject{{"length",p.length},{"synapses",p.synapses},{"resistance",p.resistance}});return a;}
template<class Owner> int Execute(const Job& j,const QString& output)
{
    return WithFreshOwner<Owner>(j.ownerClass,j.model.frequencyHz,"ProbeOwner",[&](auto,auto environment,auto model,auto owner) {
        owner->ControllerVersion=2;owner->CalculateMode=1;
        owner->StructureBuildMode=j.model.editPolicy.preserveAllocatedCable?0:1;
        owner->SyncCapacitanceTrim=0;owner->EnablePostTrainTuning=false;owner->AutoCalibrateFixedLTZThreshold=false;owner->IsNeedToTrain=false;
        const auto built=owner->ConstructNativeModel(j.model);
        Require(built.status==NativeModelBuildStatus::Constructed,built.reason.c_str());
        Require(built.effective.size()==j.model.inputs.size(),"probe_initial_dimension_changed");
        const auto configuration=IdleConfiguration(j,built.effective);
        owner->ControllerConfiguration=QJsonDocument(EncodeConfiguredNativeTraining(configuration)).toJson(QJsonDocument::Compact).toStdString();
        owner->Build();owner->Init();model->Init();model->Reset();
        Require(owner->NativeModelEditFailure().empty(),owner->NativeModelEditFailure().c_str());
        Require(owner->ControllerVersion.GetData()==2 && owner->CalculateMode.GetData()==1 && owner->ConfiguredModelInitialized.GetData(),"probe_native_owner_not_initialized");
        RequireNativeCalculationSchedule(*owner);
        auto neuron=owner->template GetComponentL<NPulseNeuron>("Neuron",true);
        auto source=owner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        Require(bool(neuron) && bool(source),"probe_graph_missing");
        const NmsdkTools::ModelBoundarySources ports{{&source->Output,"burst"}};
        const auto initial=NmsdkTools::IdentifyModel(neuron,ports);
        Require(initial["valid"]==QJsonValue(true),"probe_invalid_initial_graph");
        const auto parameters=owner->ReadNativeParameters();
        Require(Parameters(parameters)==Parameters(built.effective),"probe_lifecycle_changed_parameters");
        const auto integration=AssessNativeIntegration(neuron,source->Amplitude.GetData());Require(integration.valid,integration.reason.c_str());
        const auto idle=[&]() {
            const auto& control=owner->NativeTrainingController();
            return control.State()==NativeTrainingState::Idle && control.IssuedReferenceProbes()==0 && control.ObservedPackets().empty() &&
                !control.Certificate() && !control.References() && !owner->IsNeedToTrain.GetData();
        };
        Require(idle() && environment->GetTime().GetDoubleTime()==0. && owner->NativeProbeState()==NativeProbeStatus::Idle,"probe_preparation_started_training");
        Require(QDir().mkdir(output),"job_output_exists_or_parent_missing");
        QJsonArray artifacts{Write(output,"job.json",j.document),Write(output,"owner-configuration.json",EncodeConfiguredNativeTraining(configuration))};
        artifacts.append(Write(output,"initial-state.json",Signed({{"kind","native_probe_initial_state"},{"schema_version",1},
            {"identity",initial},{"parameters",Parameters(parameters)},{"training_started",false},{"search_executed",false},{"dynamics_checkpoint",false}})));
        EvidenceWriter evidence(output,j.model.branch?1:parameters.size());
        auto request=MakeConfiguredNativeTrainingPlan(configuration).probe;
        request.activeInput=int(j.input);request.inputId="input"+std::to_string(j.input);request.baseModelRevision=initial["sha256"].toString().toStdString();
        request.specification.runId=j.runId;request.specification.trialId=j.trialId;
        request.specification.windows={MakeConfiguredNativeTrainingPlan(configuration).inputWindows[j.input]};
        NmsdkTools::ModelRevisionObserver observer;
        request.readModelRevision=[&](){return observer.Read(neuron,ports).toStdString();};
        request.readFullModelRevision=[&](){const auto identity=NmsdkTools::IdentifyModel(neuron,ports);
            Require(identity["valid"]==QJsonValue(true),"probe_invalid_live_graph");return identity["sha256"].toString().toStdString();};
        std::size_t ticks=0;double windowEnd=0.;std::string execution="completed";
        const auto start=std::chrono::steady_clock::now();
        request.onPrepared=[&](const auto& p,const auto& s){windowEnd=s.end;evidence.Prepared(p,s);};
        request.onSample=[&](const auto& s){
            evidence.Sample(s);
            if(QFileInfo::exists(QDir(output).filePath("cancel.request")))execution="cancelled";
            else if(std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count()>=j.wallSeconds)execution="timeout";
            else if(ticks>=j.maximumTicks && Detail::After(windowEnd,s.time))execution="model_tick_budget_exhausted";
            // The native executor catches a sink failure, retains the actual
            // partial recorder and restores routing. Never reset the learner
            // here or fabricate a complete observation at a budget boundary.
            if(execution!="completed")throw std::runtime_error(execution);
        };
        owner->QueueNativeProbe(std::move(request));std::optional<NativeProbeResult> result;
        while(!(result=owner->TakeNativeProbeResult())) {
            Require(ticks<j.maximumTicks,"probe_tick_budget_without_terminal_packet");
            ++ticks;model->Calculate();environment->IncreaseModelTimeByStep();
        }
        evidence.Observation(*result);
        for(const auto& record:evidence.FinalizeWithPrefix("probe_trial_"))artifacts.append(record);
        const auto final=NmsdkTools::IdentifyModel(neuron,ports);
        const bool unchanged=final==initial && Parameters(owner->ReadNativeParameters())==Parameters(parameters);
        const bool controllerIdle=idle();
        if(execution=="completed" && result->status!=NativeProbeStatus::Completed)execution="probe_rejected";
        if(!unchanged)execution="model_changed";
        if(!controllerIdle)execution="unexpected_training_activity";
        artifacts.append(Write(output,"final-state.json",Signed({{"kind","native_probe_final_state"},{"schema_version",1},
            {"identity",final},{"parameters",Parameters(owner->ReadNativeParameters())},{"model_unchanged",unchanged},{"controller_idle",controllerIdle}})));
        Write(output,"execution.json",Signed({{"kind","timelearner_native_probe_execution"},{"schema_version",1},
            {"execution",QString::fromStdString(execution)},{"job_sha256",j.document["sha256"]},{"model_revision",initial["sha256"]},
            {"frequency_hz",double(j.model.frequencyHz)},{"model_ticks",double(ticks)},{"model_time_begin",0.},
            {"model_time_end",environment->GetTime().GetDoubleTime()},{"training_started",false},{"search_executed",false},{"certificate_available",false},
            {"model_unchanged",unchanged},{"controller_idle",controllerIdle},{"probe_status",NativeProbeStatusName(result->status)},
            {"observation_valid",bool(result->observation && result->observation->valid)},
            {"observation_complete",bool(result->observation && result->observation->complete)},
            {"artifacts",artifacts},{"evaluation_verdict",QJsonValue(QJsonValue::Null)}}));
        return execution=="completed"?0:2;
    },[&](auto storage,auto environment) {
        for(const auto& p:j.profiles) {const auto profile=Object(p);
            NmsdkTools::PrepareModelArchive(profile,storage,environment,QString::fromStdString(Text(Object(profile["metadata"])["implementation_id"])));}
    });
}
}
int RunTimeLearnerProbeJob(const QString& input,const QString& output)
{
    try {const auto j=Read(input);Require(!output.isEmpty(),"job_output_required");
        return j.model.branch?Execute<NNeuronTimeLearnerBranch>(j,output):Execute<NNeuronTimeLearner>(j,output);}
    catch(const std::exception& error){std::cerr<<"TimeLearner probe job: "<<error.what()<<'\n';return 2;}
}
