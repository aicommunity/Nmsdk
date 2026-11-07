#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseLTZoneCommon.h"
#include <cmath>
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NumericChecks.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QDir>
#include <QFile>
#include <cstdlib>
#include <type_traits>

namespace {
using namespace RDK;
using namespace NMSDK;
using namespace NMSDK::TimeLearner;
enum class Fault { None, Prepared, Sample, FinalSample };
template<class Learner> class SinglePulseFixture {
public:
    UEPtr<UContainer> model;
    UEPtr<Learner> learner;
    UEPtr<NPulseNeuron> neuron;
    UEPtr<NDatasetMatrix> dataset;
    UEPtr<NPulseGeneratorTransit> source;
    std::vector<double> isi;
    QJsonArray original;
    NmsdkTools::ModelRevisionObserver observer;
    unsigned frequency=0,count=0,index=0,serial=0;
    bool branch=std::is_same_v<Learner,NNeuronTimeLearnerBranch>;
    double duration=0.;
    std::string base,artifactFlavor;
    bool captureFeedback=false;
    std::vector<std::vector<double>> feedbackSamples;
    std::vector<double> ltSpikeTimes;
    ~SinglePulseFixture() {
        if(model)dynamic_pointer_cast<UNet>(model)->BreakLinks();
        NmsdkTests::InitEngineForPulseLibTests().environment->DestroyModel();
    }
    void Make(unsigned f,unsigned n,std::optional<double> feedback={},double threshold=1.) {
        frequency=f;count=n;index=n>2?2:n-1;
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        core.environment->DestroyModel();core.environment->SetUseIndTimeStepFlag(false);
        ASSERT_TRUE(core.environment->CreateModel("NModel"));model=core.environment->GetModel();ASSERT_TRUE(model);
        core.environment->GetTime().SetTime(0);
        StorageProfileSpec p;p.name=std::string("SinglePulse_")+(branch?"Branch":"Classic")+std::to_string(f)+"_"+std::to_string(n);
        p.neuronBaseClass="NSPNeuronGen";p.frequencyHz=f;p.initialThreshold=threshold;p.body.feedbackGain=feedback;
        if(feedback || threshold!=1.) {
            artifactFlavor="_feedback_"+(feedback?std::to_string(*feedback):"inherited")+"_threshold_"+std::to_string(threshold);
            p.name+=artifactFlavor;
        }
        auto profile=RegisterStorageProfile(core.storage,core.environment,p);
        learner=dynamic_pointer_cast<Learner>(core.storage->TakeObject(branch?"NNeuronTimeLearnerBranch":"NNeuronTimeLearner"));ASSERT_TRUE(learner);
        learner->Name="Learner";learner->StructureBuildMode=1;learner->NumInputDendrite=n;
        learner->NeuronClassName=profile.neuronClass;learner->CalculateMode=1;learner->NormalizationMode=1;
        learner->EnablePostTrainTuning=false;learner->AutoCalibrateFixedLTZThreshold=false;
        if(threshold!=1.) {
            // Legacy Reset legitimately reapplies the learner-owned threshold.
            // Declare both modes before construction; never repair LT per tick.
            learner->TrainingLTZThreshold=threshold;learner->FixedLTZThreshold=threshold;learner->LTZThreshold=threshold;
        }
        std::vector<int> lengths;for(unsigned i=0;i<n;++i)lengths.push_back(n-i);learner->DendriteLength=lengths;
        MDMatrix<double> pattern;pattern.Assign(n,1,0.);double last=0.;
        for(unsigned i=0;i<n;++i){const double v=i?.08:.01;pattern(i,0)=v;isi.push_back(v);original.append(v);last+=v;}
        duration=last+.08;learner->InputPattern=pattern;
        UEPtr<UContainer> component=learner;ASSERT_NE(model->AddComponent(component),ForbiddenId);
        model->SetGlobalTimeStep(f);model->Init();model->Reset();
        model->Calculate();core.environment->IncreaseModelTimeByStep();
        neuron=learner->template GetComponentL<NPulseNeuron>("Neuron",true);
        dataset=learner->template GetComponentL<NDatasetMatrix>("DatasetMatrix",true);
        source=learner->template GetComponentL<NPulseGeneratorTransit>("DatasetMatrix.Generator1",true);
        ASSERT_TRUE(neuron);ASSERT_TRUE(dataset);ASSERT_TRUE(source);base=Revision();
    }
    std::string Revision() {
        return observer.Read(neuron,{{&source->Output,"burst"}}).toStdString();
    }
    void CheckRestored() {
        ASSERT_TRUE(dataset->IsReady());ASSERT_TRUE(dataset->IsInit());
        EXPECT_EQ(dataset->MaxSpikesPerFeature.GetData(),int(count));
        ASSERT_EQ(dataset->MatrixData.GetRows(),int(count));ASSERT_EQ(dataset->MatrixData.GetCols(),1);
        ASSERT_EQ(learner->InputPattern.GetRows(),int(count));
        for(unsigned i=0;i<count;++i){EXPECT_EQ(dataset->MatrixData(i,0),isi[i]);EXPECT_EQ(learner->InputPattern(i,0),isi[i]);}
        EXPECT_EQ(dataset->StateGeneration.GetData(),0);EXPECT_EQ(source->Frequency.GetData(),0.);
        EXPECT_EQ(Revision(),base);
    }
    void Run(bool single,Fault fault,NativeProbeResult& result,std::vector<std::vector<double>>& samples) {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        NativeProbeRequest r;r.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        r.activeInput=int(index);r.inputId="input"+std::to_string(index);r.protocolRevision="single-pulse-diagnostic-test";
        r.baseModelRevision=base;r.expectedInputIsi=isi;r.readModelRevision=[&](){return Revision();};
        auto& s=r.specification;s.schemaVersion=single?4:2;
        s.runId="single-pulse-native";s.trialId="trial"+std::to_string(++serial);s.sampleId="sample";
        s.patternHash=NmsdkTools::CanonicalModelDataSha256(single?QJsonArray{isi.front()}:original).toStdString();
        s.end=single?.12:duration;s.maximumSampleGap=1./frequency;s.maximumSamples=(duration+.15)*frequency;
        if(single)s.characterization=SinglePulseCharacterization{NmsdkTools::CanonicalModelDataSha256(original).toStdString(),count,index};
        for(unsigned i=0;i<(single?1u:count);++i)s.expectedStimulusIds.push_back("pulse"+std::to_string(i));
        const double onset=single?.01:.01+.08*index;
        s.windows={{r.inputId,branch?0u:index,onset-.001,onset+.06,single?"pulse0":"pulse"+std::to_string(index)}};
        double begin=0.,end=0.;
        std::vector<UEPtr<NPulseMembrane>> feedbackMembranes;
        if(captureFeedback)for(unsigned i=0;i<(branch?1u:count);++i) {
            auto soma=neuron->template GetComponentL<NPulseMembrane>("Soma"+std::to_string(i+1),true);
            ASSERT_TRUE(soma);feedbackMembranes.push_back(soma);
        }
        r.onPrepared=[&](const auto& prepared,const auto& spec) {
            begin=spec.begin;end=spec.end;
            EXPECT_EQ(spec.baseline.size(),branch?1u:count);
            EXPECT_EQ(dataset->MaxSpikesPerFeature.GetData(),single?1:int(count));
            if(single && branch)EXPECT_EQ(prepared.selectedInputIndex,std::optional<std::size_t>(index));
            if(fault==Fault::Prepared)throw std::runtime_error("single_pulse_prepared_fault");
        };
        r.onSample=[&](const auto& sample) {
            std::vector<double> row{sample.time-begin,sample.stimulus};
            row.insert(row.end(),sample.potentials.begin(),sample.potentials.end());samples.push_back(row);
            if(captureFeedback) {
                std::vector<double> feedback;
                for(const auto& soma:feedbackMembranes)feedback.push_back(soma->Feedback.GetData());
                feedbackSamples.push_back(std::move(feedback));
            }
            if((fault==Fault::Sample && samples.size()==4) ||
                (fault==Fault::FinalSample && !Detail::After(end,sample.time)))throw std::runtime_error("single_pulse_sample_fault");
        };
        learner->QueueNativeProbe(std::move(r));unsigned ticks=0;
        while(learner->NativeProbeState()==NativeProbeStatus::Queued || learner->NativeProbeState()==NativeProbeStatus::Running) {
            ASSERT_LT(ticks++,unsigned((duration+.2)*frequency));
            model->Calculate();core.environment->IncreaseModelTimeByStep();
        }
        auto actual=learner->TakeNativeProbeResult();ASSERT_TRUE(actual);result=*actual;
        if(captureFeedback) {
            auto zone=neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
            for(int i=0;i<zone->OutputPulseTimes.GetCols();++i)ltSpikeTimes.push_back(zone->OutputPulseTimes(0,i));
        }
        for(const auto& reason:result.reasons)std::cout<<"single pulse reason="<<reason<<std::endl;
        CheckRestored();
        EXPECT_TRUE(learner->IsNativeProbeAtEditBoundary());
        const auto encoded=EncodeNativeProbeEvidence(result);
        EXPECT_EQ(EncodeNativeProbeEvidence(DecodeNativeProbeEvidence(encoded)),encoded);
        if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
            const QString dir=QString::fromLocal8Bit(output);ASSERT_TRUE(QDir().mkpath(dir));
            const auto test=::testing::UnitTest::GetInstance()->current_test_info();
            const QString name=QString("single-pulse-%1-%2-%3-%4-%5").arg(QString::fromUtf8(test->name()))
                .arg(branch?"Branch":"Classic").arg(frequency).arg(count).arg(serial)+QString::fromStdString(artifactFlavor);
            QFile file(dir+"/"+name+".json");ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto bytes=QJsonDocument(encoded).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
            QJsonArray rows;for(const auto& row:samples){QJsonArray values;for(double v:row)values.append(v);rows.append(values);}
            QFile raw(dir+"/"+name+"-samples.json");ASSERT_TRUE(raw.open(QIODevice::WriteOnly|QIODevice::NewOnly));
            const auto data=QJsonDocument(rows).toJson(QJsonDocument::Compact);ASSERT_EQ(raw.write(data),data.size());
            if(captureFeedback) {
                QJsonArray feedback,spikes;
                for(const auto& row:feedbackSamples){QJsonArray values;for(double v:row)values.append(v);feedback.append(values);}
                for(double v:ltSpikeTimes)spikes.append(v);
                QFile control(dir+"/feedback-control-"+name+".json");ASSERT_TRUE(control.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                const auto bytes=QJsonDocument(QJsonObject{{"feedback",feedback},{"actual_lt_spike_times",spikes},
                    {"engineering_threshold",1e-6},{"native_probe_training_started",false},{"classification_evaluated",false}}).toJson();
                ASSERT_EQ(control.write(bytes),bytes.size());
            }
        }
    }
};
template<class Learner> void Matrix(unsigned frequency) {
    for(unsigned n:{1u,2u,4u,6u}) {
        SinglePulseFixture<Learner> f;f.Make(frequency,n);ASSERT_TRUE(f.learner);
        NativeProbeResult r;std::vector<std::vector<double>> samples;f.Run(true,Fault::None,r,samples);
        ASSERT_EQ(r.status,NativeProbeStatus::Completed);ASSERT_TRUE(r.observation);EXPECT_TRUE(r.observation->complete);
        ASSERT_EQ(r.observation->stimuli.size(),1u);EXPECT_EQ(r.observation->stimuli[0].id,"pulse0");
        ASSERT_TRUE(r.prepared);EXPECT_EQ(r.observation->specification.characterization->selectedInputIndex,f.index);
        VerificationProtocol forbidden;forbidden.schemaVersion=4;
        EXPECT_THROW(ValidateVerificationProtocol(forbidden),std::invalid_argument);
        EXPECT_THROW(CapturedReferences::Capture(forbidden,{{*r.prepared,*r.observation}}),std::invalid_argument);
        // Even relabelling the outer/schema fields cannot launder a diagnostic
        // into a valid legacy training observation while its purpose is retained.
        auto relabelled=*r.observation;relabelled.schemaVersion=2;relabelled.specification.schemaVersion=2;
        relabelled.valid=true;relabelled.reasons.clear();
        VerificationProtocol legacy;legacy.schemaVersion=2;legacy.routing=r.prepared->routing;
        legacy.revision=r.prepared->protocolRevision;legacy.sampleId=relabelled.specification.sampleId;
        legacy.patternHash=relabelled.specification.patternHash;legacy.originStimulusId="pulse0";
        legacy.inputs={{r.prepared->inputId,"pulse0"}};legacy.stimulusIds={"pulse0"};
        legacy.maximumSampleGap=relabelled.specification.maximumSampleGap;
        legacy.stimulusProfile=relabelled.specification.stimulusProfile;
        try {
            ValidateProbeMeasurement(legacy,0,*r.prepared,relabelled);
            FAIL()<<"diagnostic accepted as training measurement";
        } catch(const std::invalid_argument& error) {
            EXPECT_STREQ(error.what(),"diagnostic_probe_cannot_certify_training");
        }
    }
}
template<class Learner> void Roundtrip(Fault fault) {
    SinglePulseFixture<Learner> f;f.Make(2000,2);ASSERT_TRUE(f.learner);
    NativeProbeResult before,diagnostic,after;std::vector<std::vector<double>> a,d,b;
    f.Run(false,Fault::None,before,a);ASSERT_EQ(before.status,NativeProbeStatus::Completed);
    f.Run(true,fault,diagnostic,d);
    EXPECT_EQ(diagnostic.status,fault==Fault::None?NativeProbeStatus::Completed:NativeProbeStatus::Rejected);
    f.Run(false,Fault::None,after,b);ASSERT_EQ(after.status,NativeProbeStatus::Completed);
    ASSERT_EQ(a.size(),b.size());ASSERT_FALSE(a.empty());
    for(std::size_t i=0;i<a.size();++i) {
        ASSERT_EQ(a[i].size(),b[i].size());EXPECT_NEAR(a[i][0],b[i][0],1e-12);
        for(std::size_t j=1;j<a[i].size();++j)EXPECT_EQ(a[i][j],b[i][j]);
    }
}
TEST(SinglePulseCharacterization,ClassicPhysicalSizesAt2000Hz){Matrix<NNeuronTimeLearner>(2000);}
TEST(SinglePulseCharacterization,BranchPhysicalSizesAt2000Hz){Matrix<NNeuronTimeLearnerBranch>(2000);}
TEST(SinglePulseCharacterization,ClassicPhysicalSizesAt20000Hz){Matrix<NNeuronTimeLearner>(20000);}
TEST(SinglePulseCharacterization,BranchPhysicalSizesAt20000Hz){Matrix<NNeuronTimeLearnerBranch>(20000);}
TEST(SinglePulseCharacterization,ClassicRestoresBurstResponse){Roundtrip<NNeuronTimeLearner>(Fault::None);}
TEST(SinglePulseCharacterization,BranchRestoresBurstResponse){Roundtrip<NNeuronTimeLearnerBranch>(Fault::None);}
TEST(SinglePulseCharacterization,PreparedFaultRestoresBothTopologies){Roundtrip<NNeuronTimeLearner>(Fault::Prepared);Roundtrip<NNeuronTimeLearnerBranch>(Fault::Prepared);}
TEST(SinglePulseCharacterization,SampleFaultRestoresBothTopologies){Roundtrip<NNeuronTimeLearner>(Fault::Sample);Roundtrip<NNeuronTimeLearnerBranch>(Fault::Sample);}
TEST(SinglePulseCharacterization,FinalSampleFaultRestoresBothTopologies){Roundtrip<NNeuronTimeLearner>(Fault::FinalSample);Roundtrip<NNeuronTimeLearnerBranch>(Fault::FinalSample);}
template<class Learner> void FeedbackDynamics() {
    for(unsigned frequency:{2000u,20000u}) {
        std::vector<std::vector<double>> inherited,explicitTwo,zero;
        std::vector<double> inheritedSpikes,explicitSpikes;
        for(std::optional<double> gain:{std::optional<double>{},std::optional<double>{2.},std::optional<double>{0.}}) {
            SinglePulseFixture<Learner> f;f.Make(frequency,2,gain,1e-6);ASSERT_TRUE(f.learner);
            auto zone=f.neuron->template GetComponentL<NPulseLTZoneCommon>("LTZone",true);ASSERT_TRUE(zone);
            ASSERT_DOUBLE_EQ(zone->Threshold.GetData(),1e-6);
            std::vector<NameT> names;f.neuron->GetComponentsList(names);
            for(const auto& name:names)if(auto membrane=f.neuron->template GetComponentL<NPulseMembrane>(name,true))
                EXPECT_DOUBLE_EQ(membrane->FeedbackGain.GetData(),gain.value_or(2.));
            f.captureFeedback=true;NativeProbeResult result;std::vector<std::vector<double>> samples;
            f.Run(true,Fault::None,result,samples);ASSERT_EQ(result.status,NativeProbeStatus::Completed);
            ASSERT_TRUE(result.observation);ASSERT_TRUE(result.observation->complete);ASSERT_FALSE(f.ltSpikeTimes.empty());
            ASSERT_EQ(f.feedbackSamples.size(),samples.size());bool nonzero=false;
            for(const auto& row:f.feedbackSamples)for(double value:row) {
                ASSERT_TRUE(std::isfinite(value));nonzero=nonzero || value!=0.;
                if(gain && *gain==0.)EXPECT_EQ(value,0.);
            }
            if(!gain || *gain==2.)EXPECT_TRUE(nonzero);
            if(!gain){inherited=samples;inheritedSpikes=f.ltSpikeTimes;}
            else if(*gain==2.){explicitTwo=samples;explicitSpikes=f.ltSpikeTimes;}
            else zero=samples;
        }
        EXPECT_EQ(inherited,explicitTwo);EXPECT_EQ(inheritedSpikes,explicitSpikes);
        ASSERT_EQ(inherited.size(),zero.size());bool changed=false;
        for(std::size_t i=0;i<inherited.size();++i) {
            ASSERT_EQ(inherited[i].size(),zero[i].size());
            EXPECT_EQ(inherited[i][0],zero[i][0]);EXPECT_EQ(inherited[i][1],zero[i][1]);
            for(std::size_t j=2;j<inherited[i].size();++j)changed=changed || inherited[i][j]!=zero[i][j];
        }
        EXPECT_TRUE(changed); // Actual physical response changes, not only the property value.
    }
}
TEST(StorageFeedbackProfiles,ClassicNativeFeedbackDynamics){FeedbackDynamics<NNeuronTimeLearner>();}
TEST(StorageFeedbackProfiles,BranchNativeFeedbackDynamics){FeedbackDynamics<NNeuronTimeLearnerBranch>();}

}
