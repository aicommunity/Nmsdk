#pragma once
#include "TimeLearnerJobSupport.h"
#include "TimeLearner/NumericChecks.h"
#include "NPulseNeuron.h"
#include "NPulseMembrane.h"
#include "NPulseChannelCommon.h"
#include "NPulseLTZoneCommon.h"
#include <optional>
#include <limits>

namespace NmsdkWorker {
// A read-only observer at the existing native onSample boundary. It owns no
// component, changes no property and never calls Build/Reset/Calculate.
class ProbeChannelDiagnostics {
    using Membrane=RDK::UEPtr<NMSDK::NPulseMembrane>;
    using Channel=RDK::UEPtr<NMSDK::NPulseChannelCommon>;
    struct Soma { Membrane membrane;Channel exc,inh; };
    std::vector<Soma> somas;
    RDK::UEPtr<NMSDK::NPulseLTZoneCommon> zone;
    QJsonArray descriptors,rows;
    std::optional<double> lastSpike;
    std::size_t maximumSamples;
    std::string trial,revision;
    template<class Matrix> static double Scalar(const Matrix& value) {
        Require(value.GetRows()==1 && value.GetCols()==1,"probe_diagnostic_scalar_shape_changed");
        const double result=value(0,0);
        Require(std::isfinite(result),"probe_diagnostic_nonfinite_signal");return result;
    }
    void Descriptor(const QString& path,const QString& property,const std::string& className) {
        descriptors.append(QJsonObject{{"path",path+"."+property},{"component_class",QString::fromStdString(className)},
            {"units","model_units_SI_unverified"}});
    }
public:
    ProbeChannelDiagnostics(RDK::UEPtr<NMSDK::NPulseNeuron> neuron,std::size_t count,
        std::size_t maximum,const std::string& trialId,const std::string& modelRevision)
        :maximumSamples(maximum),trial(trialId),revision(modelRevision) {
        zone=neuron->GetComponentL<NMSDK::NPulseLTZoneCommon>("LTZone",true);
        Require(bool(zone),"probe_diagnostic_ltzone_missing");
        Descriptor("$.LTZone","Potential",zone->GetCompClassName());
        Descriptor("$.LTZone","Output",zone->GetCompClassName());
        for(std::size_t i=0;i<count;++i) {
            const std::string path="Soma"+std::to_string(i+1);
            Soma s;s.membrane=neuron->GetComponentL<NMSDK::NPulseMembrane>(path,true);
            Require(bool(s.membrane),"probe_diagnostic_soma_missing");
            s.exc=s.membrane->GetComponentL<NMSDK::NPulseChannelCommon>("ExcChannel",true);
            s.inh=s.membrane->GetComponentL<NMSDK::NPulseChannelCommon>("InhChannel",true);
            Require(bool(s.exc) && bool(s.inh),"probe_diagnostic_channel_missing");
            const QString p="$."+QString::fromStdString(path);
            Descriptor(p,"SumPotential",s.membrane->GetCompClassName());
            Descriptor(p,"Feedback",s.membrane->GetCompClassName());
            for(const auto& c:std::vector<std::pair<QString,Channel>>{{"ExcChannel",s.exc},{"InhChannel",s.inh}})
                for(const auto& property:{QString("Output"),QString("SumChannelInput")})
                    Descriptor(p+"."+c.first,property,c.second->GetCompClassName());
            somas.push_back(s);
        }
    }
    void Sample(double time) {
        Require(std::isfinite(time) && std::size_t(rows.size())<maximumSamples,"probe_diagnostic_sample_budget_or_time");
        Require(bool(zone),"probe_diagnostic_ltzone_destroyed");
        Require(std::isfinite(zone->Potential.GetData()),"probe_diagnostic_nonfinite_signal");
        QJsonArray values{zone->Potential.GetData(),Scalar(zone->Output.GetData())};
        for(const auto& s:somas) {
            Require(bool(s.membrane) && bool(s.exc) && bool(s.inh),"probe_diagnostic_channel_destroyed");
            Require(std::isfinite(s.membrane->Feedback.GetData()),"probe_diagnostic_nonfinite_signal");
            values.append(Scalar(s.membrane->SumPotential.GetData()));values.append(s.membrane->Feedback.GetData());
            for(const auto& channel:{s.exc,s.inh}) {
                values.append(Scalar(channel->Output.GetData()));
                values.append(Scalar(channel->SumChannelInput.GetData()));
            }
        }
        QJsonArray spikes;
        Require(zone->OutputPulseTimes.GetRows()==1 || zone->OutputPulseTimes.GetSize()==0,
            "probe_diagnostic_spike_shape_changed");
        double previous=-std::numeric_limits<double>::infinity();
        for(int i=0;i<zone->OutputPulseTimes.GetCols();++i) {
            const double event=zone->OutputPulseTimes(0,i);
            Require(std::isfinite(event) && event>previous && !NMSDK::TimeLearner::Detail::After(event,time),
                "probe_diagnostic_invalid_spike_time");
            if(!lastSpike || event>*lastSpike){spikes.append(event);lastSpike=event;}
            previous=event;
        }
        rows.append(QJsonObject{{"time",time},{"values",values},{"new_lt_spike_times",spikes}});
    }
    QJsonObject Finish(bool closed) const {
        return {{"kind","native_probe_channel_diagnostics"},{"schema_version",1},
            {"sample_phase","native_after_children"},{"trial_id",QString::fromStdString(trial)},
            {"base_model_revision",QString::fromStdString(revision)},
            {"descriptors",descriptors},{"samples",rows},{"complete",closed},
            {"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    }
};
}
