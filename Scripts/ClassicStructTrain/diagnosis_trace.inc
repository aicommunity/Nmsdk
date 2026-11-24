// Read actual component state without changing calculation or retaining
// pointers across a structural rebuild. The stream is opt-in.
json componentOrder(UContainer* parent) const {
 json order=json::array();
 for(int index=0;index<parent->GetNumComponents();++index) {
  auto component=parent->GetComponentByIndex(index);
  if(component) order.push_back(component->GetName());
 }
 return order;
}

json observedMatrix(const MDMatrix<double>& value) const {
 return value.GetRows()>0 && value.GetCols()>0 ? json(value(0,0)) : json(nullptr);
}

json observedSignals(bool includeSynapses) const {
 auto subject=learner ? static_cast<UNet*>(learner.Get()) : static_cast<UNet*>(trainer.Get());
 auto neuron=subject->GetComponentL<NPulseNeuron>("Neuron",true);
 json record={{"generators",json::array()},{"drives",json::array()},
              {"synapses",json::array()},{"soma",json::array()}};
 if(!neuron) return record;
 auto ltz=neuron->GetComponentL<NPulseLTZoneCommon>("LTZone",true);
 if(ltz) {
  record["zone_V"]=observedMatrix(ltz->OutputPotential.GetData());
  record["zone_output"]=observedMatrix(ltz->Output.GetData());
 }
 record["wrapper_output"]=observedMatrix(learner?learner->Output.GetData():trainer->Output.GetData());
 double somaSum=0.0;
 const auto lengths=dend(),counts=syn();
 for(int channel=0;channel<5;++channel) {
  const auto number=std::to_string(channel+1);
  auto source=subject->GetComponentL<NPulseGeneratorTransit>("Source"+number,true);
  auto drive=model->GetComponentL<NPulseGeneratorTransit>("Drive"+number,true);
  auto soma=neuron->GetComponentL<NPulseMembrane>("Soma"+number,true);
  record["generators"].push_back(source?observedMatrix(source->Output.GetData()):json(nullptr));
  record["drives"].push_back(drive?observedMatrix(drive->Output.GetData()):json(nullptr));
  const double potential=soma?soma->SumPotential(0,0):0.0;
  record["soma"].push_back(potential);somaSum+=potential;
  if(!includeSynapses || int(lengths.size())<=channel || int(counts.size())<=channel) continue;
  const auto segment="Dendrite"+number+"_"+std::to_string(lengths[channel]);
  for(int i=1;i<=counts[channel];++i) {
   auto synapse=neuron->GetComponentL<NPulseSynapseCommon>(segment+".ExcSynapse"+std::to_string(i),true);
   if(!synapse) continue;
   const auto physical=dynamic_pointer_cast<NPulseSynapse>(synapse);
   record["synapses"].push_back(json::array({channel+1,i,observedMatrix(synapse->Input.GetData()),
     observedMatrix(synapse->Output.GetData()),synapse->Resistance.GetData(),
     physical?json(physical->SecretionTC.GetData()):json(nullptr),
     physical?json(physical->DissociationTC.GetData()):json(nullptr)}));
  }
 }
 record["sum_soma_V"]=somaSum;
 return record;
}

void writeDiagnosticTick(const std::string& phase,int tick,const json& before,const json& after) {
 auto record=observedSignals(true);
 record["phase"]=phase;record["case"]=key;record["tick"]=tick;
 record["before"]=before;record["after"]=after;
 record["time"]=time();
 waveforms<<record.dump()<<'\n';
}
