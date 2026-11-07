#include <gtest/gtest.h>
#include "NNeuronTimeLearner.h"
#include "NNeuronTimeLearnerBranch.h"
#include "NPulseLTZoneCommon.h"
#include <cmath>
#include "TimeLearner/StorageProfiles.h"
#include "TimeLearner/ModelIdentity.h"
#include "TimeLearner/ModelArchive.h"
#include "NPulseChannel.h"
#include "NPulseSynapse.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include "TimeLearner/NumericChecks.h"
#include "../Support/ConsoleLikeInit.h"
#include <QJsonArray>
#include <QJsonDocument>
#include <QDir>
#include <QFile>
#include <QCryptographicHash>
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
    void Make(unsigned f,unsigned n,std::optional<double> feedback={},double threshold=1.,bool inheritedPhysics=false) {
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
        RegisteredStorageProfile profile;
        if(inheritedPhysics) {
            artifactFlavor+="_stock_images";p.name+="_stock_images";
            if(feedback) {
                FeedbackStorageProfileSpec inherited;
                inherited.name=p.name;inherited.frequencyHz=f;inherited.neuronBaseClass=p.neuronBaseClass;
                inherited.bodyFeedbackGain=feedback;
                profile=RegisterFeedbackStorageProfile(core.storage,core.environment,inherited);
            } else profile.neuronClass=p.neuronBaseClass;
        } else profile=RegisterStorageProfile(core.storage,core.environment,p);
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
    void Run(bool single,Fault fault,NativeProbeResult& result,std::vector<std::vector<double>>& samples,
             bool largest=false,bool wholeWindow=false) {
        const auto& core=NmsdkTests::InitEngineForPulseLibTests();
        NativeProbeRequest r;r.routing=branch?ProbeRouting::BranchSoloBurst:ProbeRouting::ClassicBurst;
        r.activeInput=int(index);r.inputId="input"+std::to_string(index);r.protocolRevision="single-pulse-diagnostic-test";
        r.baseModelRevision=base;r.expectedInputIsi=isi;r.readModelRevision=[&](){return Revision();};
        auto& s=r.specification;s.schemaVersion=single?(largest?5:4):2;
        if(largest)s.peakSelection=PeakSelectionPolicy::SingleImpulseMaximum;
        s.runId="single-pulse-native";s.trialId="trial"+std::to_string(++serial);s.sampleId="sample";
        s.patternHash=NmsdkTools::CanonicalModelDataSha256(single?QJsonArray{isi.front()}:original).toStdString();
        s.end=single?.12:duration;s.maximumSampleGap=1./frequency;s.maximumSamples=(duration+.15)*frequency;
        if(single)s.characterization=SinglePulseCharacterization{NmsdkTools::CanonicalModelDataSha256(original).toStdString(),count,index};
        for(unsigned i=0;i<(single?1u:count);++i)s.expectedStimulusIds.push_back("pulse"+std::to_string(i));
        const double onset=single?.01:.01+.08*index;
        s.windows={{r.inputId,branch?0u:index,onset-.001,onset+.06,single?"pulse0":"pulse"+std::to_string(index)}};
        if(wholeWindow){s.windows[0].begin=0.;s.windows[0].end=s.end;}
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
                    {"actual_model_identity",NmsdkTools::IdentifyModel(neuron,{{&source->Output,"burst"}})},
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
template<class Learner> void Roundtrip(Fault fault,bool largest=false) {
    SinglePulseFixture<Learner> f;f.Make(2000,2);ASSERT_TRUE(f.learner);
    if(largest)f.artifactFlavor+="_maximum_fault_"+std::to_string(static_cast<int>(fault));
    NativeProbeResult before,diagnostic,after;std::vector<std::vector<double>> a,d,b;
    f.Run(false,Fault::None,before,a);ASSERT_EQ(before.status,NativeProbeStatus::Completed);
    f.Run(true,fault,diagnostic,d,largest,largest);
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
template<class Learner> void FeedbackDynamics(bool inheritedPhysics=false) {
    for(unsigned frequency:{2000u,20000u}) {
        std::vector<std::vector<double>> inherited,explicitTwo,zero;
        std::vector<double> inheritedSpikes,explicitSpikes;
        for(std::optional<double> gain:{std::optional<double>{},std::optional<double>{2.},std::optional<double>{0.}}) {
            SinglePulseFixture<Learner> f;f.Make(frequency,2,gain,1e-6,inheritedPhysics);ASSERT_TRUE(f.learner);
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
TEST(FeedbackProfileImages,ClassicNativeInheritedPhysics){FeedbackDynamics<NNeuronTimeLearner>(true);}
TEST(FeedbackProfileImages,BranchNativeInheritedPhysics){FeedbackDynamics<NNeuronTimeLearnerBranch>(true);}

struct ProfileImportLease {
    UEPtr<UStorage> storage;UEPtr<UContainer> node;
    ~ProfileImportLease(){if(node){if(auto net=dynamic_pointer_cast<UNet>(node))net->BreakLinks();storage->ReturnObject(node);}}
};
template<class Learner> void FullProfileGraphImport() {
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    for(unsigned frequency:{2000u,20000u}) {
        SinglePulseFixture<Learner> f;f.Make(frequency,4,{},.0117,true);ASSERT_TRUE(f.learner);
        NativeProbeResult result;std::vector<std::vector<double>> samples;
        f.Run(true,Fault::None,result,samples);ASSERT_EQ(result.status,NativeProbeStatus::Completed);
        // Explicit private fixture state at a consumed probe boundary. These
        // heterogeneous individual parameters are not uniform image settings
        // and are not claimed as the result of a Train.
        auto channel=f.neuron->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);
        auto tip=f.neuron->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);
        ASSERT_TRUE(channel);ASSERT_TRUE(tip);channel->Capacity=1.3e-9;tip->Resistance=93e6;
        f.neuron->Build();f.neuron->Reset();f.base=f.Revision();
        const NmsdkTools::ModelBoundarySources ports{{&f.source->Output,"burst"}};
        const auto original=NmsdkTools::ExportPhysicalGraphForEdit(f.neuron,ports);
        EXPECT_THROW(NmsdkTools::ImportFeedbackProfileGraphForEdit(original,core.storage,core.environment,{},0.,ports),
                     NmsdkTools::ModelArchiveError);
        for(double gain:{2.,0.}) {
            FeedbackStorageProfileSpec spec;spec.frequencyHz=frequency;spec.bodyFeedbackGain=gain;
            spec.name=std::string("FullProfileImport_")+(f.branch?"Branch":"Classic")+std::to_string(frequency)+"_"+std::to_string(int(gain));
            const auto profile=RegisterFeedbackStorageProfile(core.storage,core.environment,spec);
            const std::map<std::string,std::string> names{{"NSPNeuronGen",profile.neuronClass},{"NPMembraneBio",profile.bodyMembraneClass}};
            const std::optional<double> factor=gain==2.?std::optional<double>{}:std::optional<double>{gain};
            ProfileImportLease imported{core.storage,NmsdkTools::ImportFeedbackProfileGraphForEdit(original,core.storage,core.environment,names,factor,ports)};
            ASSERT_TRUE(imported.node);
            const auto actual=NmsdkTools::IdentifyModel(imported.node,ports);ASSERT_TRUE(actual["valid"].toBool());
            auto actualChannel=imported.node->template GetComponentL<NPulseChannel>("Soma1.ExcChannel",true);
            auto actualTip=imported.node->template GetComponentL<NPulseSynapse>("Dendrite1_1.ExcSynapse1",true);
            ASSERT_TRUE(actualChannel);ASSERT_TRUE(actualTip);
            EXPECT_EQ(actualChannel->Capacity.GetData(),1.3e-9);EXPECT_EQ(actualTip->Resistance.GetData(),93e6);
            EXPECT_EQ(NmsdkTools::IdentifyModel(f.neuron,ports),original["identity"].toObject());
            const auto exported=NmsdkTools::ExportPhysicalGraphForEdit(imported.node,ports);
            ProfileImportLease roundtrip{core.storage,NmsdkTools::ImportPhysicalGraphForEdit(exported,core.storage,core.environment,ports)};
            ASSERT_TRUE(roundtrip.node);EXPECT_EQ(NmsdkTools::IdentifyModel(roundtrip.node,ports),actual);
            EXPECT_THROW(NmsdkTools::ImportFeedbackProfileGraphForEdit(original,core.storage,core.environment,names,.25,ports),
                         NmsdkTools::ModelArchiveError);
            auto corrupt=original;USerStorageXML xml;
            ASSERT_TRUE(xml.Load(original["native_xml"].toString().toStdString(),"TimeLearnerNativeGraph"));
            ASSERT_TRUE(xml.SelectNode("Neuron"));ASSERT_TRUE(xml.SelectNode("Components"));
            ASSERT_TRUE(xml.SelectNode("Soma1"));ASSERT_TRUE(xml.SelectNode("Parameters"));
            ASSERT_TRUE(xml.SelectNode("FeedbackGain"));ASSERT_TRUE(xml.SetNodeText("3"));xml.SelectRoot();
            std::string broken;ASSERT_TRUE(xml.Save(broken));const auto brokenText=QString::fromStdString(broken);
            corrupt["native_xml"]=brokenText;
            corrupt["native_xml_sha256"]=QString::fromLatin1(QCryptographicHash::hash(brokenText.toUtf8(),QCryptographicHash::Sha256).toHex());
            try {
                auto invalid=NmsdkTools::ImportFeedbackProfileGraphForEdit(corrupt,core.storage,core.environment,names,factor,ports);
                ProfileImportLease unexpected{core.storage,invalid};FAIL()<<"contradictory source gain hidden by substitution";
            } catch(const NmsdkTools::ModelArchiveError& error) {EXPECT_EQ(error.code,"archive_model_mismatch");}
            // The internal inheritance exception must never weaken ordinary
            // source/archive completeness checks.
            ASSERT_TRUE(xml.SelectNode("Neuron"));ASSERT_TRUE(xml.SelectNode("Components"));
            ASSERT_TRUE(xml.SelectNode("Soma1"));ASSERT_TRUE(xml.SelectNode("Parameters"));
            ASSERT_TRUE(xml.SelectNode("FeedbackGain"));xml.DelNode();xml.SelectRoot();
            ASSERT_TRUE(xml.Save(broken));const auto incompleteText=QString::fromStdString(broken);
            auto incomplete=original;incomplete["native_xml"]=incompleteText;
            incomplete["native_xml_sha256"]=QString::fromLatin1(QCryptographicHash::hash(incompleteText.toUtf8(),QCryptographicHash::Sha256).toHex());
            try {
                auto invalid=NmsdkTools::ImportPhysicalGraphForEdit(incomplete,core.storage,core.environment,ports);
                ProfileImportLease unexpected{core.storage,invalid};FAIL()<<"incomplete ordinary snapshot accepted";
            } catch(const NmsdkTools::ModelArchiveError& error) {EXPECT_EQ(error.code,"missing_archive_parameter");}
            try {
                auto invalid=NmsdkTools::ImportFeedbackProfileGraphForEdit(incomplete,core.storage,core.environment,names,factor,ports);
                ProfileImportLease unexpected{core.storage,invalid};FAIL()<<"incomplete source snapshot accepted";
            } catch(const NmsdkTools::ModelArchiveError& error) {EXPECT_EQ(error.code,"missing_archive_parameter");}
            if(const char* output=std::getenv("TIMELEARNER_EXECUTION_OUTPUT")) {
                QJsonObject renames;for(const auto& entry:names)renames[QString::fromStdString(entry.first)]=QString::fromStdString(entry.second);
                const auto record=QJsonObject{{"source_identity",original["identity"]},{"candidate_identity",actual},
                    {"roundtrip_identity",NmsdkTools::IdentifyModel(roundtrip.node,ports)},{"class_renames",renames},
                    {"feedback_gain",factor?QJsonValue(*factor):QJsonValue(QJsonValue::Null)},
                    {"individual_fixture_state",true},{"candidate_waveform_evaluated",false},{"training_started",false}};
                const QString name=QString("profile-import-%1-%2-%3.json").arg(f.branch?"Branch":"Classic").arg(frequency).arg(int(gain));
                QFile file(QString::fromLocal8Bit(output)+"/"+name);ASSERT_TRUE(file.open(QIODevice::WriteOnly|QIODevice::NewOnly));
                const auto bytes=QJsonDocument(record).toJson();ASSERT_EQ(file.write(bytes),bytes.size());
            }
        }
    }
}
TEST(FeedbackProfileImport,ClassicFullIndividualStateAndRoundtrip){FullProfileGraphImport<NNeuronTimeLearner>();}
TEST(FeedbackProfileImport,BranchFullIndividualStateAndRoundtrip){FullProfileGraphImport<NNeuronTimeLearnerBranch>();}

template<class Learner> void MaximumNative(unsigned frequency,unsigned count=2) {
    // A declared high-threshold control isolates the measurement policy A/B.
    // Archived stock multi-peak responses require a separate Console replay.
    SinglePulseFixture<Learner> f;f.Make(frequency,count,{},100.);ASSERT_TRUE(f.learner);
    NativeProbeResult old,current;std::vector<std::vector<double>> before,after;
    f.Run(true,Fault::None,old,before,false,true);
    f.Run(true,Fault::None,current,after,true,true);
    ASSERT_EQ(old.status,NativeProbeStatus::Completed);ASSERT_EQ(current.status,NativeProbeStatus::Completed);
    ASSERT_TRUE(current.observation);ASSERT_TRUE(current.observation->valid);ASSERT_TRUE(current.prepared);
    ASSERT_EQ(before.size(),after.size());ASSERT_FALSE(after.empty());
    for(std::size_t i=0;i<before.size();++i) {
        ASSERT_EQ(before[i].size(),after[i].size());EXPECT_NEAR(before[i][0],after[i][0],1e-12);
        for(std::size_t j=1;j<before[i].size();++j)EXPECT_EQ(before[i][j],after[i][j]);
    }
    const auto& o=*current.observation;ASSERT_EQ(o.stimuli.size(),1u);ASSERT_EQ(o.peaks.size(),1u);
    EXPECT_EQ(o.specification.baseline.size(),f.branch?1u:count);
    ASSERT_TRUE(o.specification.characterization);
    EXPECT_EQ(o.specification.characterization->physicalInputCount,count);
    EXPECT_EQ(o.specification.characterization->selectedInputIndex,f.index);
    const auto& p=o.peaks[0];ASSERT_TRUE(p.rawPotential);ASSERT_TRUE(p.time);
    const auto channel=f.branch?0u:f.index;
    double largest=after.front()[channel+2];std::size_t maximum=0;
    for(std::size_t i=1;i<after.size();++i)if(after[i][channel+2]>largest){largest=after[i][channel+2];maximum=i;}
    EXPECT_EQ(*p.rawPotential,largest);EXPECT_NEAR(*p.time-o.specification.begin,after[maximum][0],1e-12);
    EXPECT_EQ(old.observation->peaks[0].candidateCount,p.candidateCount);
    if(p.candidateCount>1)EXPECT_FALSE(old.observation->valid);
    VerificationProtocol forbidden;forbidden.schemaVersion=5;
    EXPECT_THROW(ValidateVerificationProtocol(forbidden),std::invalid_argument);
    EXPECT_THROW(CapturedReferences::Capture(forbidden,{{*current.prepared,o}}),std::invalid_argument);
}
TEST(SingleImpulseMaximumNative,Classic2000){MaximumNative<NNeuronTimeLearner>(2000);}
TEST(SingleImpulseMaximumNative,Branch2000){MaximumNative<NNeuronTimeLearnerBranch>(2000);}
TEST(SingleImpulseMaximumNative,Classic20000){MaximumNative<NNeuronTimeLearner>(20000);}
TEST(SingleImpulseMaximumNative,Branch20000){MaximumNative<NNeuronTimeLearnerBranch>(20000);}
// N=2 is retained in the four original cases. These independent native cases
// add the remaining required dimensions without changing their old inventory.
template<class Learner> void MaximumPhysicalMatrix(unsigned frequency) {
    for(unsigned count:{1u,4u,6u}) {
        SCOPED_TRACE(::testing::Message()<<"physical N="<<count);
        MaximumNative<Learner>(frequency,count);
    }
}
TEST(SingleImpulseMaximumNative,ClassicPhysicalMatrix2000){MaximumPhysicalMatrix<NNeuronTimeLearner>(2000);}
TEST(SingleImpulseMaximumNative,BranchPhysicalMatrix2000){MaximumPhysicalMatrix<NNeuronTimeLearnerBranch>(2000);}
TEST(SingleImpulseMaximumNative,ClassicPhysicalMatrix20000){MaximumPhysicalMatrix<NNeuronTimeLearner>(20000);}
TEST(SingleImpulseMaximumNative,BranchPhysicalMatrix20000){MaximumPhysicalMatrix<NNeuronTimeLearnerBranch>(20000);}
TEST(SingleImpulseMaximumNative,FaultsRestoreBothTopologies) {
    for(auto fault:{Fault::Prepared,Fault::Sample,Fault::FinalSample}) {
        Roundtrip<NNeuronTimeLearner>(fault,true);Roundtrip<NNeuronTimeLearnerBranch>(fault,true);
    }
}

}
