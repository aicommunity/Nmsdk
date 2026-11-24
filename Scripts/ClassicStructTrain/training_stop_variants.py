"""Isolate amplitude stopping criteria without importing the mixed fcaa969 commit."""
from pathlib import Path
import sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent))
from training_repro import ROOT,WORK,save
from training_variants import CORE,span

def apply(crossing=False):
 path=CORE/'NNeuronTrainer.cpp';text=path.read_text(encoding='utf8');a,b=span(text,'bool NNeuronTrainer::SomaSynapseNormalization');body=text[a:b]
 # The baseline stops a channel immediately when removing the last extra
 # synapse. Replace this stopping rule only; signal math and timing stay intact.
 needle='dend_status[i] = 0;'
 active=[line for line in body.splitlines() if needle in line and not line.strip().startswith('//')];assert len(active)==1
 body=body.replace(active[0],active[0].replace(needle,'// Diagnostic amplitude criterion: keep the channel active after removal.'),1)
 start=body.index('if(max_iter_dend_amp[i] < InitialDendritePotential[i] + 0.000005)')
 stop=body.index('if (EnableDebug && RDK::GetLogger())',start)
 criterion='std::fabs(amplitude_difference) <= 1.0e-6'
 prefix='const double amplitude_difference = max_iter_dend_amp[i] - InitialDendritePotential[i];\n'
 suffix=''
 if crossing:
  prefix+=' const bool crossed = HasPreviousSynapseAmplitudeDifference[i] && amplitude_difference * PreviousSynapseAmplitudeDifference[i] < 0.0 && std::fabs(amplitude_difference) <= std::fabs(PreviousSynapseAmplitudeDifference[i]);\n'
  criterion+=' || crossed'
  suffix=' PreviousSynapseAmplitudeDifference[i]=amplitude_difference;\n HasPreviousSynapseAmplitudeDifference[i]=true;\n'
 body=body[:start]+prefix+' if('+criterion+') dend_status[i]=0;\n else if(amplitude_difference<0) dend_status[i]=2;\n else dend_status[i]=-2;\n'+suffix+'\n '+body[stop:]
 text=text[:a]+body+text[b:]
 if crossing:
  needle='InitialDendritePotential.assign(num_input_dendrite,0);';assert text.count(needle)==1
  text=text.replace(needle,needle+'\n PreviousSynapseAmplitudeDifference.assign(num_input_dendrite,0.0);\n HasPreviousSynapseAmplitudeDifference.assign(num_input_dendrite,false);')
  header=CORE/'NNeuronTrainer.h';h=header.read_text(encoding='utf8');needle='std::vector<int> SynapseNum;';assert h.count(needle)==1
  h=h.replace(needle,needle+'\n std::vector<double> PreviousSynapseAmplitudeDifference;\n std::vector<bool> HasPreviousSynapseAmplitudeDifference;');header.write_text(h,encoding='utf8')
 path.write_text(text,encoding='utf8')
 save(WORK/'variants'/('FZC-adaptation.json' if crossing else 'FZ-adaptation.json'),{
  'classification':'Isolated diagnostic adaptation of amplitude stopping, not an identified historical binary',
  'source':'fcaa969 amplitude crossing concept and its strict parent criterion',
  'baseline_rule':'The autoPreset baseline fixes a channel when removing the last extra synapse',
  'criterion':'Absolute amplitude error <= 1 microvolt'+(' or closer sign crossing' if crossing else ''),
  'other_changes':'Only required previous-error storage for the crossing variant' if crossing else 'None',
  'unchanged':'Physical signal equations, initialization fix, synapse profile, calculation order, stimulus protocol and iteration timing'})
 print('Applied isolated stopping criterion',crossing)
if __name__=='__main__':apply('--crossing' in sys.argv)
