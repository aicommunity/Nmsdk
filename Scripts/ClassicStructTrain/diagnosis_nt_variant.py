"""Isolate NT stopping factors in a research-only PulseLib branch."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from training_variants import CORE, span


def apply():
    source = CORE / "NNeuronTrainer.cpp"
    header = CORE / "NNeuronTrainer.h"
    text = source.read_text(encoding="utf-8")
    assert "NMSDK_DIAG_NT_STOP" not in text
    insertion = """
#include <cstdlib>
#include <string_view>

namespace {
enum class NTStop { Default, Tolerance, KeepAfterRemoval, Strict, Crossing };

NTStop ResearchStopRule()
{
 static const NTStop rule=[] {
  const auto* value=std::getenv("NMSDK_DIAG_NT_STOP");
  const std::string_view name=value?value:"";
  if(name=="tolerance") return NTStop::Tolerance;
  if(name=="keep") return NTStop::KeepAfterRemoval;
  if(name=="strict") return NTStop::Strict;
  if(name=="crossing") return NTStop::Crossing;
  return NTStop::Default;
 }();
 return rule;
}
}
"""
    index = text.index("namespace NMSDK")
    text = text[:index] + insertion + text[index:]
    first, last = span(text, "bool NNeuronTrainer::SomaSynapseNormalization")
    body = text[first:last]
    statement = next(line for line in body.splitlines() if line.strip() == "dend_status[i] = 0;")
    assert sum(line.strip() == statement.strip() for line in body.splitlines()) == 1
    body = body.replace(statement, statement.replace("dend_status", """if(ResearchStopRule()!=NTStop::KeepAfterRemoval && ResearchStopRule()!=NTStop::Strict
                   && ResearchStopRule()!=NTStop::Crossing)
                 dend_status"""), 1)
    current = "if(max_iter_dend_amp[i] < InitialDendritePotential[i] + 0.000005)"
    assert body.count(current) == 1
    body = body.replace(current, """const auto rule=ResearchStopRule();
            if(rule==NTStop::Tolerance || rule==NTStop::Strict || rule==NTStop::Crossing)
            {
             const double difference=max_iter_dend_amp[i]-InitialDendritePotential[i];
             const double previous=ResearchPreviousAmplitudeError[i];
             const bool crossed=rule==NTStop::Crossing && difference*previous<0.0
                 && std::fabs(difference)<=std::fabs(previous);
             dend_status[i]=std::fabs(difference)<=1.0e-6 || crossed ? 0 : (difference<0.0 ? 2 : -2);
             ResearchPreviousAmplitudeError[i]=difference;
            }
            else """ + current)
    text = text[:first] + body + text[last:]
    initialization = "InitialDendritePotential.assign(num_input_dendrite,0);"
    assert text.count(initialization) == 1
    text = text.replace(initialization, initialization + "\n ResearchPreviousAmplitudeError.assign(num_input_dendrite,0.0);")
    declaration = "std::vector<int> SynapseNum;"
    h = header.read_text(encoding="utf-8")
    assert h.count(declaration) == 1
    h = h.replace(declaration, declaration + "\n std::vector<double> ResearchPreviousAmplitudeError;")
    header.write_text(h, encoding="utf-8")
    source.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    apply()
