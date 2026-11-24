// Boundary-level port of the archived relearning TreatDataFromFile protocol.
// The absent historical ACalculate caller is not invented: this diagnostic
// explicitly places the file hook before the environment tick. Training itself
// remains the native NNeuronLearner implementation. Invalid extraction is logged
// and never assigns the uninitialized local used by the old unchecked snippet.
void reproFileProtocol() {
 const auto job=manifest.at("repro_job");kind="learner";key=job.at("id");
 const auto sequence=job.at("file_sequence");
 fs::create_directories(out/"native");
 const fs::path input=out/"native/input_data.txt";
 {
  std::ofstream stream(input);
  stream.precision(17);
  for(size_t row=0;row<sequence.size();++row) {
   const auto p=sequence.at(row).at("pattern").get<std::vector<double>>();
   const size_t count=job.value("truncate_last",false)&&row+1==sequence.size()?3:p.size();
   for(size_t i=0;i<count;++i) {if(i)stream<<'\t';stream<<p[i];}
   if(row+1<sequence.size()||job.value("trailing_newline",true))stream<<'\n';
  }
 }
 std::ifstream fin(input);std::ofstream events(out/"file-events.jsonl");
 if(job.value("file_parser_only",false)) {
  size_t accepted=0;
  while(true) {
   const bool eof=fin.eof();size_t extracted=0;double value;
   if(!eof)for(int i=0;i<5;++i){if(!(fin>>value))break;++extracted;}
   events<<json({{"eof_before",eof},{"extracted_values",extracted},{"accepted",extracted==5}}).dump()<<'\n';events.flush();
   if(extracted!=5){writeResult({{"status",extracted==0?"completed":"incomplete_input_record"},{"record_type","file_parser_probe"},{"job",job},{"records_accepted",accepted},{"failed_read_values",extracted},{"eof_before",eof},{"model_values_assigned",false}});return;}
   ++accepted;
  }
 }
 bool first=true,newPattern=true,written=false;size_t index=0;
 int ticks=0;double started=0;auto wallStart=std::chrono::steady_clock::now();
 while(true) {
  if(newPattern && (first||LearnerAccess::first(*learner))) {
   const bool eofBefore=fin.eof();
   std::vector<double> p;double value;bool valid=true;
   if(!eofBefore)for(int i=0;i<5;++i){if(!(fin>>value)){valid=false;break;}p.push_back(value);}
   else valid=false;
   events<<json({{"event","read"},{"index",index},{"eof_before",eofBefore},{"extracted_values",p.size()},
     {"accepted",valid},{"model_time",first?0:time()},{"hook_order","before_environment_tick"}}).dump()<<'\n';events.flush();
   if(!valid) {
    writeResult({{"status",eofBefore||p.empty()?"completed":"incomplete_input_record"},{"record_type","file_protocol_end"},
     {"job",job},{"records_accepted",index},{"failed_read_values",p.size()},{"eof_before",eofBefore},
     {"safe_eof_guard",true},{"historical_call_chain_available",false}});
    break;
   }
   if(first) {
    load(kind);learner->ExperimentMode=false;learner->CalculateMode=1;learner->IsNeedToTrain=true;pattern(p);
    if(!model->Build()||!env->Reset())throw std::runtime_error("File protocol initialization failed");
    env->SetCurrentDataDir((out/"native").string()+"/");first=false;
   }else {pattern(p);LearnerAccess::resetCount(*learner);}
   ++index;ticks=0;started=time();wallStart=std::chrono::steady_clock::now();newPattern=false;written=false;
  }
  const int before=LearnerAccess::count(*learner);step();++ticks;
  if(LearnerAccess::count(*learner)>before) {
   auto h=state();h["case"]=key;h["repeat"]=repeat;h["iteration"]=LearnerAccess::count(*learner);h["file_record"]=index;
   history<<h.dump()<<'\n';history.flush();
  }
  const bool trained=zero(LearnerAccess::ds(*learner))&&zero(LearnerAccess::ss(*learner));
  std::string status;
  if(trained&&!written&&LearnerAccess::count(*learner)>=1)status="completed";
  else if(LearnerAccess::count(*learner)>=maxIterations)status="iteration_limit";
  else if(ticks%1024==0&&std::chrono::duration<double>(std::chrono::steady_clock::now()-wallStart).count()>wallTimeout)status="wall_timeout";
  if(status.empty())continue;
  auto r=state();r["status"]=status;r["record_type"]="training";r["job"]=job;r["stage_index"]=index-1;
  r["stage"]={{"target_id",sequence.at(index-1).at("id")},{"target_class",sequence.at(index-1).at("class")}};
  r["pattern"]=sequence.at(index-1).at("pattern");r["iterations"]=LearnerAccess::count(*learner);r["ticks"]=ticks;
  r["native_need_to_train"]=needs();r["completion_rule"]="archived external boundary: zero statuses and CountIteration >= 1";
  r["elapsed_model_time"]=time()-started;r["elapsed_wall_seconds"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-wallStart).count();
  r["whole_initialization_audit"]=legacyInitializationAudit(model.Get(),"Model",true);
  r["snapshot_saved"]=saveSnapshot(out/(index==1?"trained":"stage-"+std::to_string(index-1)));writeResult(r);
  if(status!="completed"||!r["whole_initialization_audit"]["uninitialized"].empty())break;
  newPattern=true;written=true;
 }
}
