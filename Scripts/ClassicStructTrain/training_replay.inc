// Training observations and native snapshots. No archive structure is injected.
void reproEvaluation(const json& job,int index) {
 if(learner) learner->IsNeedToTrain=false;else trainer->IsNeedToTrain=false;
 std::vector<json> data;
 if(job.contains("evaluation_ids")) {
  for(int id:job.at("evaluation_ids").get<std::vector<int>>())data.push_back(manifest.at("dataset").at(id-1));
 } else for(const auto& sample:manifest.at("dataset"))data.push_back(sample);
 auto measure=legacyInference(job,data,false,false);
 measure["record_type"]="evaluation_in_protocol";measure["job"]=job;measure["stage_index"]=index;
 measure["variant"]=manifest.at("variant");
 measure["snapshot_saved"]=saveSnapshot(out/("stage-"+std::to_string(index)+"-after-evaluation"));
 writeResult(measure);
}
void repro() {
 const auto job=manifest.at("repro_job");
 if(job.value("file_controller",false)){reproFileProtocol();return;}
 kind=job.at("kind").get<std::string>();key=job.at("id").get<std::string>();
 auto p=job.contains("pattern")?job.at("pattern").get<std::vector<double>>():sample(job.at("target_id"));
 auto record=train(p,true);
 // The legacy supervisor can observe all-zero statuses one tick before the
 // native EndOfLearning method clears IsNeedToTrain. Let the native method
 // finalize; do not clear the flag or inject an archive structure here.
 record["controller_observed_completion"]=record.at("status")=="completed";
 record["native_finalization_tick"]=false;
 if(learner && record.at("status")=="completed" && needs() && learner->CalculateMode.GetData()==0
    && zero(LearnerAccess::ds(*learner)) && zero(LearnerAccess::ss(*learner))) {
  step();record["native_finalization_tick"]=true;
 }
 record["job"]=job;record["variant"]=manifest.at("variant");
 record["record_type"]="training";
 record["initial_training"]=true;
 record["whole_initialization_audit"]=legacyInitializationAudit(model.Get(),"Model",true);
 record["native_need_to_train"]=needs();
 record["snapshot_saved"]=saveSnapshot(out/"trained");
 writeResult(record);
 if(record.at("status")!="completed" || !record["whole_initialization_audit"]["uninitialized"].empty()) return;
 if(job.value("evaluate_initial",false))reproEvaluation(job,0);
 if(job.contains("stages")) {
  int index=0;
  for(const auto& stage:job.at("stages")) {
   key=job.at("id").get<std::string>()+"-stage-"+std::to_string(++index);
   auto current=train(stage.at("pattern").get<std::vector<double>>(),false,stage.value("iterations",0),stage.value("synapses_only",false));
   current["job"]=job;current["stage"]=stage;current["stage_index"]=index;current["variant"]=manifest.at("variant");
   current["record_type"]="training";
   current["whole_initialization_audit"]=legacyInitializationAudit(model.Get(),"Model",true);
   current["native_need_to_train"]=needs();
   current["snapshot_saved"]=saveSnapshot(out/("stage-"+std::to_string(index)));
   writeResult(current);
   if(current.at("status")!="completed" || !current["whole_initialization_audit"]["uninitialized"].empty()) break;
   if(stage.value("evaluate",false))reproEvaluation(job,index);
  }
 }
}
