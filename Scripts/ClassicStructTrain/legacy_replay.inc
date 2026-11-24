// Saved-state inference adapter. It attaches runtime caches to existing native
// objects; it does not invoke BuildStructure or replace a training algorithm.
void legacyBind(const json& job) {
 const auto d=job.at("dendrites").get<std::vector<int>>();
 const auto s=job.at("synapses").get<std::vector<int>>();
 auto subject=learner ? static_cast<UNet*>(learner.Get()) : static_cast<UNet*>(trainer.Get());
 auto n=subject->GetComponentL<NPulseNeuron>("Neuron",true);
 if(!n) throw std::runtime_error("Saved neuron is absent");
 std::vector<UEPtr<NPulseGeneratorTransit>> sources;
 for(int i=1;i<=5;++i) {
  auto source=subject->GetComponentL<NPulseGeneratorTransit>("Source"+std::to_string(i),true);
  if(!source) throw std::runtime_error("Saved generator is absent");
  sources.push_back(source);
 }
 if(learner) { LearnerAccess::bind(*learner,n,sources); learner->DendriteLength.SetDataDirect(d); learner->NumSynapse.SetDataDirect(s); }
 else { TrainerAccess::bind(*trainer,n,sources); TrainerAccess::structure(*trainer,d,s); }
 SavedNeuronAccess::bind(*n);
 if(job.value("preserve_native_order",false)) return;
 // This is the native variable-length dendrite computation order. Mode zero
// intentionally prevents NPulseNeuron::BuildStructure and needs explicit order.
 int position=0;
 for(int i=0;i<5;++i) for(int j=d[i];j>=1;--j)
  n->SetComponentPosition("Dendrite"+std::to_string(i+1)+"_"+std::to_string(j),position++);
 for(int i=1;i<=5;++i) n->SetComponentPosition("Soma"+std::to_string(i),position++);
 n->SetComponentPosition("LTZone",position++);
 for(int i=1;i<=5;++i) subject->SetComponentPosition("Source"+std::to_string(i),i-1);
 subject->SetComponentPosition("Neuron",5);
}

void legacyLoad(const json& job, const fs::path& config) {
 learner=nullptr; trainer=nullptr; model=nullptr; env=nullptr;
 kind=job.at("kind").get<std::string>();
 if(!app->OpenProject(config.string())) throw std::runtime_error("Saved project OpenProject failed");
 Core_SelectChannel(0); env=RDK::GetEnvironment(); model=env ? env->GetModel() : UEPtr<UContainer>();
 if(!env || !model) throw std::runtime_error("Saved project model is absent");
 env->SetMinInterstepsInterval(0); env->SetMaxCalcTime(0);
 env->SetCurrentDataDir((out/"native").string()); fs::create_directories(out/"native");
 const auto subjectPath=job.value("subject_path",std::string("Subject"));
 learner=model->GetComponentL<NNeuronLearner>(subjectPath,true);
 trainer=model->GetComponentL<NNeuronTrainer>(subjectPath,true);
 if(!learner && !trainer) throw std::runtime_error("Saved Subject is absent");
 if(int(model->GetTimeStep())!=2000) throw std::runtime_error("Expected archived 2000 Hz integration");
 if(learner) { learner->IsNeedToTrain=false; learner->ExperimentMode=false; }
 else trainer->IsNeedToTrain=false;
 if(job.contains("context_subjects")) legacyBindContext(job);
 if(!model->Build()) throw std::runtime_error("Saved model Build failed");
 if(job.contains("context_subjects")) legacyBindContext(job);else legacyBind(job);
 // Build can initialize a partial subtree. Complete the normal Init/UnInit/Init
 // lifecycle after the entire saved graph exists, including the environment.
 model->Init(); model->UnInit(); env->UnInit(); env->Init(); model->Init();
 if(!env->Reset()) throw std::runtime_error("Saved model Reset failed");
 auto subject=learner?static_cast<UNet*>(learner.Get()):static_cast<UNet*>(trainer.Get());
 if(subject->GetActivity() && !structureReadback().at("all_initialized").get<bool>())
  throw std::runtime_error("Active saved physical graph is not fully initialized");
 const double threshold=learner?learner->LTZThreshold.GetData():trainer->LTZThreshold.GetData();
 const double fixed=learner?learner->FixedLTZThreshold.GetData():trainer->FixedLTZThreshold.GetData();
 if(std::abs(threshold-fixed)>1e-12) throw std::runtime_error("Recognition threshold does not equal archived FixedLTZThreshold");
}

json legacyInference(const json& job, const std::vector<json>& data, bool independent, bool trace) {
 auto subject=learner ? static_cast<UNet*>(learner.Get()) : static_cast<UNet*>(trainer.Get());
 auto n=subject->GetComponentL<NPulseNeuron>("Neuron",true);
 auto ltz=n->GetComponentL<NLTZone>("LTZone",true);
 auto pulseZone=dynamic_pointer_cast<NPulseLTZoneCommon>(ltz);
 if(!ltz) throw std::runtime_error("Saved LTZone missing");
 std::vector<UEPtr<NPulseMembrane>> somaNodes;
 std::vector<UEPtr<NPulseGeneratorTransit>> sourceNodes;
 std::vector<UEPtr<NPulseGeneratorTransit>> drives;
 for(int i=1;i<=5;++i) {
  somaNodes.push_back(n->GetComponentL<NPulseMembrane>("Soma"+std::to_string(i),true));
  sourceNodes.push_back(subject->GetComponentL<NPulseGeneratorTransit>("Source"+std::to_string(i),true));
  drives.push_back(model->GetComponentL<NPulseGeneratorTransit>("Drive"+std::to_string(i),true));
 }
 const auto before=structureReadback();
 const int target=job.at("target_class");
 const double frequency=learner ? learner->SpikesFrequency.GetData() : trainer->SpikesFrequency.GetData();
 const int ticks=int(std::ceil(2000.0/frequency));
 json answers=json::array(), ids=json::array(), peaks=json::array(), firstSpikes=json::array();
 json zonePeaks=json::array(),wrapperAnswers=json::array();
 int tp=0,fp=0,fn=0,tn=0;
 for(const auto& sample:data) {
  if(independent && !env->Reset()) throw std::runtime_error("Independent Reset failed");
  const auto p=sample.at("pattern").get<std::vector<double>>();
  const auto& previous=learner?learner->InputPattern.GetData():trainer->InputPattern.GetData();
  bool patternChanged=false;
  for(int i=0;i<5;++i) if(previous(i,0)!=p[i]) patternChanged=true;
  pattern(p);
  if(job.contains("input_owner")) {
   auto owner=model->GetComponentL<NSpikeClassifier>(job.at("input_owner").get<std::string>(),true);
   if(!owner) throw std::runtime_error("Full-context classifier is absent");
   owner->InputPattern=matrix(p);
  }
  for(int i=0;i<5;++i) if(drives[i]) {
   drives[i]->Delay=(learner?learner->Delay.GetData():trainer->Delay.GetData())+p[i];
   drives[i]->Frequency=frequency;
   if(patternChanged || job.value("reset_drive_on_equal_pattern",true)) drives[i]->Reset();
  }
  bool fired=false,wrapperFired=false; double peak=0,first=-1,zonePeak=0; std::vector<double> somaMax(5,0.0),somaTime(5,0.0);
  const double start=time();
  const bool saveTrace=trace && (sample.at("id")==job.value("target_id",0) || sample.at("id")==22 || sample.at("id")==51 || sample.at("id")==61 || sample.at("id")==129);
  for(int tick=0;tick<ticks;++tick) {
   step();
   double sum=0; std::vector<double> soma,sourceValues;
   for(int i=1;i<=5;++i) {
    auto m=somaNodes[i-1];
    const double value=m ? m->SumPotential(0,0) : 0.0; sum+=value; soma.push_back(value);
    if(value>somaMax[i-1]) { somaMax[i-1]=value; somaTime[i-1]=time()-start; }
    if(saveTrace) sourceValues.push_back(sourceNodes[i-1]->Output(0,0));
   }
   peak=std::max(peak,sum);
   if(pulseZone && pulseZone->OutputPotential.GetRows()>0) zonePeak=std::max(zonePeak,pulseZone->OutputPotential(0,0));
   const auto& wrapper=learner?learner->Output.GetData():trainer->Output.GetData();
   if(wrapper.GetRows()>0 && wrapper(0,0)>.001)wrapperFired=true;
   if(ltz->Output(0,0)>.001) { if(!fired) first=time()-start; fired=true; }
   if(saveTrace) waveforms << json({{"case",key},{"repeat",repeat},{"input_id",sample.at("id")},{"tick",tick},
    {"time",time()-start},{"sum_soma",sum},{"soma",soma},{"sources",sourceValues},{"LTZone",ltz->Output(0,0)}}).dump()<<'\n';
  }
  ids.push_back(sample.at("id")); answers.push_back(fired?1:0); peaks.push_back(peak); firstSpikes.push_back(first<0?json(nullptr):json(first));
  zonePeaks.push_back(zonePeak);wrapperAnswers.push_back(wrapperFired?1:0);
  if(time()-start<.66) throw std::runtime_error("Model time did not advance through the stimulus window");
  bool own=sample.at("class").get<int>()==target;
  if(own) { if(fired)++tp;else ++fn; } else { if(fired)++fp;else ++tn; }
  history<<json({{"case",key},{"repeat",repeat},{"input_id",sample.at("id")},{"answer",fired?1:0},{"peak_sum",peak},{"soma_maxima",somaMax},{"soma_peak_times",somaTime}}).dump()<<'\n';history.flush();
 }
 waveforms.flush(); const auto after=structureReadback();
 return {{"status","completed"},{"kind",kind},{"protocol",independent?"independent_reset":"continuous"},{"input_ids",ids},{"answers",answers},
  {"peaks",peaks},{"zone_potential_peaks",zonePeaks},{"wrapper_answers",wrapperAnswers},{"first_spikes",firstSpikes},{"TP",tp},{"FP",fp},{"FN",fn},{"TN",tn},
  {"target_class",target},{"ticks_per_input",ticks},{"dendrites",dend()},{"synapses",syn()},
  {"readback_before",before},{"readback_after",after},{"structure_unchanged",before==after},
  {"training_disabled",!needs()},{"cache_adapter","native object pointers, observation buffers, native computation order; no graph reconstruction"}};
}

void legacy() {
 const auto job=manifest.at("legacy_job"); key=job.at("id").get<std::string>();
 const auto config=repo/fs::u8path(job.at("config").get<std::string>());
 legacyLoad(job,config);
 const auto loaded=structureReadback();
 if(!saveSnapshot(out/"loaded")) throw std::runtime_error("Loaded snapshot save failed");
 if(job.value("audit_only",false)) {
  const auto audit=legacyInitializationAudit(model.Get(),"Model",true);
  writeResult({{"status",audit.at("uninitialized").empty()?"completed":"initialization_incomplete"},{"kind",kind},{"job",job},
               {"loaded_readback",loaded},{"initialization_audit",audit},{"training_disabled",!needs()}});
  if(!audit.at("uninitialized").empty()) throw std::runtime_error("Some active objects are not initialized");
  return;
 }
 std::vector<json> data;
 for(const auto& sample:manifest.at("dataset")) data.push_back(sample);
 if(job.contains("input_ids")) {
  data.clear();for(int id:job.at("input_ids").get<std::vector<int>>()) data.push_back(manifest.at("dataset").at(id-1));
 }
 auto result=legacyInference(job,data,job.value("independent_reset",false),job.value("trace",false));
 result["job"]=job; result["loaded_readback"]=loaded;
 if(job.contains("context_subjects")) result["whole_initialization_audit"]=legacyInitializationAudit(model.Get(),"Model",true);
 if(!saveSnapshot(out/"after")) throw std::runtime_error("After-inference save failed");
 if(job.value("roundtrip",false)) {
  legacyLoad(job,out/"after/project.ini");
  result["roundtrip_readback"]=structureReadback();
  result["roundtrip"]=legacyInference(job,{data.front()},false,false);
  result["roundtrip_same_first_answer"]=result["answers"].at(0)==result["roundtrip"]["answers"].at(0);
  result["roundtrip_same_first_peak"]=result["peaks"].at(0)==result["roundtrip"]["peaks"].at(0);
  if(!saveSnapshot(out/"roundtrip-loaded")) throw std::runtime_error("Roundtrip snapshot save failed");
 }
 writeResult(result);
}

void legacyBindContext(const json& job) {
 const auto savedLearner=learner;const auto savedTrainer=trainer;
 for(const auto& path:job.at("context_classifiers")) {
  auto classifier=model->GetComponentL<NSpikeClassifier>(path.get<std::string>(),true);
  if(!classifier) throw std::runtime_error("Missing saved classifier");
  ClassifierAccess::bind(*classifier);
 }
 for(const auto& component:job.at("context_subjects")) {
  learner=nullptr;trainer=model->GetComponentL<NNeuronTrainer>(component.at("subject_path").get<std::string>(),true);
  if(!trainer) throw std::runtime_error("Missing full-context trainer");
  legacyBind(component);
 }
 learner=savedLearner;trainer=savedTrainer;
}

json legacyInitializationAudit(UContainer* node, const std::string& path, bool parentActive) {
 const bool active=parentActive && node->GetActivity();
 json result={{"active_components",active?1:0},{"uninitialized",json::array()}};
 if(active && !node->IsInit()) result["uninitialized"].push_back(path);
 for(int i=0;i<node->GetNumComponents();++i) {
  auto child=node->GetComponentByIndex(i);if(!child)continue;
  const auto childResult=legacyInitializationAudit(child.Get(),path+"."+child->GetName(),active);
  result["active_components"]=result["active_components"].get<int>()+childResult["active_components"].get<int>();
  for(const auto& name:childResult["uninitialized"]) result["uninitialized"].push_back(name);
 }
 return result;
}
