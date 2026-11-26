#include <gtest/gtest.h>
#include "NPulseNeuron.h"
#include "NPulseChannel.h"
#include "NPulseMembraneCommon.h"
#include "NPulseSynapse.h"
#include "NPulseLTZoneCommon.h"
#include "NPulseGeneratorTransit.h"
#include "TimeLearner/NativeModelBuilder.h"
#include "TimeLearner/ModelInspection.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/StorageProfiles.h"
#include "../Support/ConsoleLikeInit.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;

struct Signal {
    std::string name;
    double tolerance;
    std::function<double()> read;
};

double Scalar(const MDMatrix<double>& value) {
    if(value.GetSize()!=1) throw std::runtime_error("frequency_probe_scalar_dimension");
    const double sample=value(0,0);
    if(!std::isfinite(sample)) throw std::runtime_error("frequency_probe_nonfinite_sample");
    return sample;
}

void Signals(UEPtr<UContainer> node,const std::string& path,std::vector<Signal>& result) {
    if(auto membrane=dynamic_pointer_cast<NPulseMembraneCommon>(node)) {
        result.push_back({path+".SumPotential",1e-12,[membrane]{return Scalar(membrane->SumPotential.GetData());}});
        result.push_back({path+".Feedback",1e-12,[membrane]{return membrane->Feedback.GetData();}});
    }
    if(auto channel=dynamic_pointer_cast<NPulseChannel>(node))
        result.push_back({path+".Output",1e-12,[channel]{return Scalar(channel->Output.GetData());}});
    if(auto synapse=dynamic_pointer_cast<NPulseSynapse>(node)) {
        result.push_back({path+".Output",1e-20,[synapse]{return Scalar(synapse->Output.GetData());}});
        result.push_back({path+".PreOutput",1e-12,[synapse]{return synapse->PreOutput.GetData();}});
    }
    if(auto zone=dynamic_pointer_cast<NLTZone>(node)) {
        result.push_back({path+".Potential",1e-12,[zone]{return zone->Potential.GetData();}});
        result.push_back({path+".Output",1e-15,[zone]{return Scalar(zone->Output.GetData());}});
    }
    std::vector<NameT> names;node->GetComponentsList(names);
    for(const auto& name:names) Signals(node->GetComponent(name,true),path+"."+name,result);
}

void CheckRate(UEPtr<UContainer> node,unsigned frequency) {
    ASSERT_TRUE(node);ASSERT_TRUE(node->IsInit());ASSERT_TRUE(node->IsReady());
    ASSERT_EQ(node->GetTimeStep(),frequency) << node->GetName();
    std::vector<NameT> names;node->GetComponentsList(names);
    for(const auto& name:names) CheckRate(node->GetComponent(name,true),frequency);
}

void Artifact(const std::string& name,const QByteArray& bytes) {
    if(const char* directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
        if(!QDir().mkpath(QString::fromLocal8Bit(directory)))
            throw std::runtime_error("frequency_probe_output_directory");
        QFile file(QString::fromLocal8Bit(directory)+"/"+QString::fromStdString(name));
        if(!file.open(QIODevice::WriteOnly|QIODevice::NewOnly) || file.write(bytes)!=bytes.size())
            throw std::runtime_error("frequency_probe_output_write");
    }
}

class FrequencyBoundary : public ::testing::Test {
protected:
    UEPtr<UStorage> storage;
    UEPtr<UEnvironment> environment;
    UEPtr<UContainer> model;
    UEPtr<UNet> fresh;bool freshAttached=false;
    ULongTime originalTime;
    void SetUp() override {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();storage=core.storage;environment=core.environment;
        originalTime=environment->GetTime().GetTime();environment->DestroyModel();
        environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(environment->CreateModel("NModel"));model=environment->GetModel();ASSERT_TRUE(model);
    }
    void TearDown() override {
        if(auto net=dynamic_pointer_cast<UNet>(model))net->BreakLinks();
        if(fresh && !freshAttached)storage->ReturnObject(fresh);
        environment->DestroyModel();environment->GetTime().SetTime(originalTime);
    }
    UEPtr<UNet> BuildOwner(const std::string& name,const NativeModelSpec& spec) {
        auto owner=dynamic_pointer_cast<UNet>(storage->TakeObject("NModel"));
        if(!owner)throw std::runtime_error("frequency_probe_owner_factory");
        owner->Name=name;owner->SetEnvironment(environment);owner->SetGlobalTimeStep(spec.frequencyHz);
        const auto result=ConstructNativeLearnerModel(*owner,spec);
        if(result.status!=NativeModelBuildStatus::Constructed) {
            storage->ReturnObject(owner);throw std::runtime_error("frequency_probe_construction:"+result.reason);
        }
        owner->Init();return owner;
    }
    void Exercise(bool branch,unsigned previousFrequency,unsigned targetFrequency,bool ltMembrane) {
        const std::string name=std::string(branch?"Branch":"Classic")+"_"+std::to_string(previousFrequency)+
            "_to_"+std::to_string(targetFrequency)+(ltMembrane?"_LtMembrane":"_DirectLtZone");
        StorageProfileSpec recipe;recipe.name="FrequencyBoundary_"+name;recipe.frequencyHz=targetFrequency;
        recipe.neuronBaseClass="NSPNeuronGen";recipe.initialThreshold=100.;
        // Uniform physics is a registered image recipe, never a per-tick overlay.
        recipe.body.excSynapse.dissociationTC=.005;recipe.body.inhSynapse.dissociationTC=.007;
        if(ltMembrane) {
            recipe.ltMembrane=recipe.body;
            recipe.ltMembrane->excChannel.capacity=.3e-9;
            recipe.ltMembrane->inhChannel.capacity=.6e-9;
        }
        const auto profile=RegisterStorageProfile(storage,environment,recipe);
        NativeModelSpec initial;initial.frequencyHz=previousFrequency;initial.branch=branch;
        initial.neuronClass=profile.neuronClass;initial.normalization=Normalization::SynapseCount;
        initial.editPolicy.normalization=initial.normalization;initial.editPolicy.maximumCableLength=8;
        initial.inputs={{4,2,86e6},{2,1,114e6}};initial.initialIsi={.01,.03};
        model->SetGlobalTimeStep(previousFrequency);
        auto warm=BuildOwner("Warm",initial);ASSERT_NE(model->AddComponent(warm),ForbiddenId);
        model->Init();environment->GetTime().SetTime(0);model->Reset();
        auto warmNeuron=warm->GetComponentL<NPulseNeuron>("Neuron",true);
        auto warmSource=warm->GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        ASSERT_TRUE(warmNeuron);ASSERT_TRUE(warmSource);
        EXPECT_EQ(bool(warmNeuron->GetComponent("LTMembrane",true)),ltMembrane);
        std::vector<Signal> a;Signals(warmNeuron,"$",a);ASSERT_GT(a.size(),10u);
        std::vector<double> warmLow(a.size()),warmHigh(a.size());
        for(std::size_t k=0;k<a.size();++k)warmLow[k]=warmHigh[k]=a[k].read();
        unsigned oldEdges=0;double oldInput=0.;
        std::ostringstream warming;warming.imbue(std::locale::classic());warming<<std::setprecision(17);
        warming<<"tick,time_s,actual_input";for(const auto& signal:a)warming<<','<<signal.name;warming<<'\n';
        for(unsigned tick=0;tick<previousFrequency/8;++tick) {
            model->Calculate();environment->IncreaseModelTimeByStep();
            const double input=Scalar(warmSource->Output.GetData());if(input>0. && oldInput<=0.)++oldEdges;oldInput=input;
            warming<<tick<<','<<double(tick)/previousFrequency<<','<<input;
            for(std::size_t k=0;k<a.size();++k) {
                const double value=a[k].read();ASSERT_TRUE(std::isfinite(value));
                warmLow[k]=std::min(warmLow[k],value);warmHigh[k]=std::max(warmHigh[k],value);warming<<','<<value;
            }
            warming<<'\n';
        }
        ASSERT_GE(oldEdges,2u);
        double warmPotentialRange=0.;
        for(std::size_t k=0;k<a.size();++k)if(a[k].name.find("SumPotential")!=std::string::npos)
            warmPotentialRange=std::max(warmPotentialRange,warmHigh[k]-warmLow[k]);
        ASSERT_GT(warmPotentialRange,1e-8) << "a flat warm model cannot test resetting real dynamics";
        Artifact(name+"_warm.csv",QByteArray::fromStdString(warming.str()));
        // Fresh target graph is built detached at f. It never calculates at f0.
        auto target=initial;target.frequencyHz=targetFrequency;fresh=BuildOwner("Fresh",target);
        model->SetGlobalTimeStep(targetFrequency);
        ASSERT_NE(model->AddComponent(fresh),ForbiddenId);freshAttached=true;
        ASSERT_TRUE(fresh->IsInit());ASSERT_TRUE(warm->IsInit());
        // This is the ordinary physical-model boundary. No learner Build,
        // parameter self-assignment or nested Calculate repairs the transition.
        environment->GetTime().SetTime(0);model->Reset();
        CheckRate(warm,targetFrequency);CheckRate(fresh,targetFrequency);ASSERT_FALSE(HasFatalFailure());
        auto freshNeuron=fresh->GetComponentL<NPulseNeuron>("Neuron",true);
        auto freshSource=fresh->GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        ASSERT_TRUE(freshNeuron);ASSERT_TRUE(freshSource);
        std::vector<Signal> b;Signals(freshNeuron,"$",b);ASSERT_EQ(a.size(),b.size());
        for(std::size_t k=0;k<a.size();++k)ASSERT_EQ(a[k].name,b[k].name);
        NmsdkTools::ModelBoundarySources warmPorts{{&warmSource->Output,"burst"}},freshPorts{{&freshSource->Output,"burst"}};
        const auto warmIdentity=NmsdkTools::IdentifyModel(warmNeuron.Get(),warmPorts);
        const auto freshIdentity=NmsdkTools::IdentifyModel(freshNeuron.Get(),freshPorts);
        ASSERT_TRUE(warmIdentity["valid"].toBool());ASSERT_TRUE(freshIdentity["valid"].toBool());
        EXPECT_EQ(warmIdentity["sha256"],freshIdentity["sha256"]);
        Artifact(name+"_warm_graph.json",QJsonDocument(NmsdkTools::InspectModel(warm)).toJson());
        Artifact(name+"_fresh_graph.json",QJsonDocument(NmsdkTools::InspectModel(fresh)).toJson());
        std::vector<double> difference(a.size(),0.),low(a.size()),high(a.size());
        for(std::size_t k=0;k<a.size();++k)low[k]=high[k]=a[k].read();
        std::ostringstream trace;trace.imbue(std::locale::classic());trace<<std::setprecision(17);
        trace<<"tick,time_s,warm_input,fresh_input";
        for(const auto& signal:a)trace<<",warm:"<<signal.name<<",fresh:"<<signal.name;trace<<'\n';
        unsigned edgesA=0,edgesB=0;double previousA=0.,previousB=0.;QJsonArray inputTicks;
        const unsigned ticks=targetFrequency/5;
        for(unsigned frame=0;frame<=ticks;++frame) {
            // Include the native Reset state, then all actual after-child samples.
            if(frame) {model->Calculate();environment->IncreaseModelTimeByStep();}
            const double inputA=Scalar(warmSource->Output.GetData()),inputB=Scalar(freshSource->Output.GetData());
            ASSERT_DOUBLE_EQ(inputA,inputB);
            if(inputA>0. && previousA<=0.){++edgesA;inputTicks.append(int(frame-1));}
            if(inputB>0. && previousB<=0.)++edgesB;
            previousA=inputA;previousB=inputB;
            trace<<int(frame)-1<<','<<(frame?double(frame-1)/targetFrequency:0.)<<','<<inputA<<','<<inputB;
            for(std::size_t k=0;k<a.size();++k) {
                const double av=a[k].read(),bv=b[k].read();ASSERT_TRUE(std::isfinite(av));ASSERT_TRUE(std::isfinite(bv));
                difference[k]=std::max(difference[k],std::abs(av-bv));
                low[k]=std::min(low[k],av);high[k]=std::max(high[k],av);trace<<','<<av<<','<<bv;
            }
            trace<<'\n';
        }
        ASSERT_GE(edgesA,2u);EXPECT_EQ(edgesA,edgesB);
        double potentialRange=0.;QJsonArray residuals;
        for(std::size_t k=0;k<a.size();++k) {
            EXPECT_LE(difference[k],a[k].tolerance)<<a[k].name;
            residuals.append(QJsonObject{{"signal",QString::fromStdString(a[k].name)},
                {"maximum_absolute_difference",difference[k]},{"absolute_tolerance",a[k].tolerance}});
            if(a[k].name.find("SumPotential")!=std::string::npos)potentialRange=std::max(potentialRange,high[k]-low[k]);
        }
        EXPECT_GT(potentialRange,1e-8);
        CheckRate(warm,targetFrequency);CheckRate(fresh,targetFrequency);
        Artifact(name+"_comparison.csv",QByteArray::fromStdString(trace.str()));
        Artifact(name+"_result.json",QJsonDocument(QJsonObject{{"kind","native_frequency_boundary_response_comparison"},
            {"schema_version",1},{"branch",branch},{"previous_frequency_hz",int(previousFrequency)},
            {"target_frequency_hz",int(targetFrequency)},{"lt_membrane",ltMembrane},
            {"warm_ticks",int(previousFrequency/8)},{"probe_ticks",int(ticks)},{"samples_including_reset",int(ticks+1)},
            {"actual_stimulus_onset_ticks",inputTicks},{"warm_potential_range",warmPotentialRange},
            {"probe_potential_range",potentialRange},{"signals",residuals},
            {"warm_model_identity",warmIdentity},{"fresh_model_identity",freshIdentity},
            {"new_training",false},{"live_learner_frequency_change_attested",false},
            {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    }
};
TEST_F(FrequencyBoundary,Classic2000To20000DirectLt) {Exercise(false,2000,20000,false);}
TEST_F(FrequencyBoundary,Classic20000To2000DirectLt) {Exercise(false,20000,2000,false);}
TEST_F(FrequencyBoundary,Branch2000To20000DirectLt) {Exercise(true,2000,20000,false);}
TEST_F(FrequencyBoundary,Branch20000To2000DirectLt) {Exercise(true,20000,2000,false);}
TEST_F(FrequencyBoundary,Classic2000To20000LtMembrane) {Exercise(false,2000,20000,true);}
TEST_F(FrequencyBoundary,Classic20000To2000LtMembrane) {Exercise(false,20000,2000,true);}
TEST_F(FrequencyBoundary,Branch2000To20000LtMembrane) {Exercise(true,2000,20000,true);}
TEST_F(FrequencyBoundary,Branch20000To2000LtMembrane) {Exercise(true,20000,2000,true);}
}
