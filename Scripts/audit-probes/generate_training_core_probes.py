"""Extract production TimeLearner gate/controller methods into C++ unit probes.

The probes execute unchanged C++ bodies with small property adapters. Python only
locates source method boundaries and carries header constants into the test TU.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "Libraries/Nmsdk-PulseLib/Core"


def method(file: str, signature: str) -> str:
    raw = (CORE / file).read_text(encoding="utf-8")
    clean = re.sub(
        r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
        lambda m: "".join("\n" if c == "\n" else " " for c in m[0]),
        raw,
    )
    start = clean.index(signature)
    brace = clean.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return raw[start:end]


def pending_length_loop(file: str) -> str:
    raw = (CORE / file).read_text(encoding="utf-8")
    clean = re.sub(
        r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
        lambda m: "".join("\n" if c == "\n" else " " for c in m[0]),
        raw,
    )
    start = clean.index("bool NNeuronTimeLearner" + ("Branch" if "Branch" in file else "") + "::ApplyPendingDendriteLengthChanges(void)")
    loop = clean.index("for(int i = 0; i < NumInputDendrite - 1; ++i)", start)
    brace = clean.index("{", loop)
    depth = 1
    end = brace + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return raw[loop:end]


def build_length_floor_loop() -> str:
    source = method("NNeuronTimeLearnerBranch.cpp", "bool NNeuronTimeLearnerBranch::BuildStructure()")
    clean = re.sub(
        r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"',
        lambda m: "".join("\n" if c == "\n" else " " for c in m[0]),
        source,
    )
    loop = clean.index("for(int i = 0; i < NumInputDendrite; ++i)")
    brace = clean.index("{", loop)
    depth = 1
    end = brace + 1
    while depth:
        depth += (clean[end] == "{") - (clean[end] == "}")
        end += 1
    return source[loop:end]


def constants(header: str) -> str:
    raw = (CORE / header).read_text(encoding="utf-8")
    names = (
        "kMinMeasurableSomaAmp",
        "kResistanceAdjustGainDefault",
        "kAmpNormEps",
        "kAmpOscillationBand",
        "kGainOvershootFactor",
        "kGainUndershootFactor",
        "kUndershootBoostRatio",
        "kNoImproveResistanceLimit",
        "kRminLengthTolFactor",
        "kMaxSynapsesPerDend",
        "kMaxLengthStep",
    )
    out = []
    for name in names:
        match = re.search(rf"^\s*static constexpr (?:double|int) {name} = [^;]+;", raw, re.M)
        if not match:
            raise ValueError(f"missing production constant {name} in {header}")
        out.append(match.group(0).strip())
    return "\n".join(out)


prefix = r'''
#include <gtest/gtest.h>
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <string>
#include <utility>
#include <vector>

struct FakeLogger { template<class... T> void LogMessageEx(T...) {} };
namespace RDK { inline FakeLogger* GetLogger() { return nullptr; } }
constexpr int RDK_EX_DEBUG = 1;

template<class T> struct P {
 T value{};
 P() = default;
 P(const T& v): value(v) {}
 P& operator=(const T& v) { value = v; return *this; }
 const T& GetData() const { return value; }
 void SetDataDirect(const T& v) { value = v; }
 operator T() const { return value; }
 template<class U = T> auto size() const -> decltype(std::declval<const U&>().size()) { return value.size(); }
 auto& operator[](std::size_t i) { return value[i]; }
 const auto& operator[](std::size_t i) const { return value[i]; }
};
'''


def learner_class(name: str, header: str, branch: bool) -> str:
    extra = " P<int> ActivePulseIndex{0}; std::vector<bool> PulseSynced{true,true,true};\n" if branch else ""
    delay_len = "double DelayLenOf(int i) const;" if branch else "double DelayLenOf(int i) const { return DelayLength.at(static_cast<size_t>(i)); }"
    constants_src = constants(header)
    return f'''
class {name} {{
public:
{constants_src}
 P<int> NumInputDendrite{{2}};
 int CountIteration = 0;
 P<double> SyncTolerance{{0.01}}, ResistanceMin{{20.0}}, ResistanceMax{{100.0}};
 P<double> ResistanceAdjustGain{{0.4}}, SynapseResistanceBase{{80.0}};
 P<bool> EnableDebug{{false}};
 P<std::vector<double>> TipSynapseResistance{{std::vector<double>{{50.0,86.0,86.0}}}};
 P<std::vector<double>> InitialSomaPotential{{std::vector<double>{{1.0,0.0,0.0}}}};
 P<std::vector<int>> NumSynapse{{std::vector<int>{{1,1,1}}}};
 P<std::vector<int>> DendriteLength{{std::vector<int>{{1,1,1}}}};
 P<int> MaxDendriteLength{{8}};
 std::vector<double> MaxIterSomaAmp{{1.0,0.0,0.0}}, DendLastAbsDt{{0.01,0.0,0.0}};
 std::vector<int> ResistanceStatus{{0,0,0}}, NoImproveResistanceCount{{0,0,0}}, SynapseStatus{{0,0,0}};
 std::vector<int> DendStatus{{0,0,0}}, OldDendriteLength{{1,1,1}};
 std::vector<bool> RmaxOvershootLengthGrow{{false,false,false}};
 std::vector<double> Dissynchronization{{0,0,0}};
 std::vector<double> DelayLength{{0,0,0}};
 double EstDelayPerSeg = 1.0, LastLengthDelta = 0.0;
 int LastLengthDeltaDendrite = -1;
 P<bool> EnableNextSegmentInhibition{{false}};
 std::vector<double> PrevAmpError;
 std::vector<bool> SomaPeakValid{{true,true,true}}, PrevPeakValid{{true,true,true}};
 std::vector<bool> PeakSeen{{true,true,true}}, DendBestEffortSynced{{false,false,false}};
 bool HasPrevPeakSnapshot = true;
 bool parametric = true;
 {extra}
 bool IsParametricNormalization() const {{ return parametric; }}
 double ClampResistance(double r) const {{ return std::max(ResistanceMin.GetData(), std::min(ResistanceMax.GetData(), r)); }}
 double ComputeModelTipResistance(int) const {{ return SynapseResistanceBase.GetData(); }}
 bool AllDendritesSynced() const;
 bool AllSynapsesNormalized() const;
 int SelectActiveDendrite() const;
 double ComputeDampedTipResistance(int, double, double, double, double, double&) const;
 {delay_len}
 int PulseAttachPos(int i) const;
 void DetachBranchExcSynapseAtSegment(int) {{}}
 void DetachBranchInhSynapseAtSegment(int) {{}}
 void EnforceSegmentMonotonicity(int) {{}}
 void ApplyPendingLengthLoopForProbe();
 void NormalizeBranchLengthsForBuildProbe();
}};
'''


methods = "\n".join(
    [
        method("NNeuronTimeLearner.cpp", "bool NNeuronTimeLearner::AllDendritesSynced(void) const"),
        method("NNeuronTimeLearner.cpp", "bool NNeuronTimeLearner::AllSynapsesNormalized(void) const"),
        method("NNeuronTimeLearner.cpp", "int NNeuronTimeLearner::SelectActiveDendrite() const"),
        method("NNeuronTimeLearner.cpp", "double NNeuronTimeLearner::ComputeDampedTipResistance(int dendrite_index0, double r_old,")
        .replace("NNeuronTimeLearner::ComputeDampedTipResistance", "NNeuronTimeLearner::ComputeDampedTipResistance"),
        method("NNeuronTimeLearnerBranch.cpp", "bool NNeuronTimeLearnerBranch::AllDendritesSynced(void) const"),
        method("NNeuronTimeLearnerBranch.cpp", "bool NNeuronTimeLearnerBranch::AllSynapsesNormalized(void) const"),
        method("NNeuronTimeLearnerBranch.cpp", "int NNeuronTimeLearnerBranch::SelectActiveDendrite() const"),
        method("NNeuronTimeLearnerBranch.cpp", "double NNeuronTimeLearnerBranch::ComputeDampedTipResistance(int dendrite_index0, double r_old,"),
        method("NNeuronTimeLearnerBranch.cpp", "double NNeuronTimeLearnerBranch::DelayLenOf(int num) const"),
        method("NNeuronTimeLearnerBranch.cpp", "int NNeuronTimeLearnerBranch::PulseAttachPos(int pulse_k) const"),
    ]
)
methods += "\nvoid NNeuronTimeLearner::ApplyPendingLengthLoopForProbe() { std::vector<int> changed; " + pending_length_loop("NNeuronTimeLearner.cpp") + " }\n"
methods += "\nvoid NNeuronTimeLearnerBranch::ApplyPendingLengthLoopForProbe() { std::vector<int> changed; " + pending_length_loop("NNeuronTimeLearnerBranch.cpp") + " }\n"
methods += "\nvoid NNeuronTimeLearnerBranch::NormalizeBranchLengthsForBuildProbe() { " + build_length_floor_loop() + " }\n"

tests = r'''
TEST(TimeLearnerCore, ClassicSyncToleranceAndInvalidPeakAreExplicit) {
 NNeuronTimeLearner learner;
 learner.NumInputDendrite = 2;
 learner.DendLastAbsDt = {.01, 0.0};
 EXPECT_TRUE(learner.AllDendritesSynced());
 learner.DendLastAbsDt[0] = .010000000001;
 EXPECT_FALSE(learner.AllDendritesSynced());
 learner.DendLastAbsDt[0] = .01;
 learner.SomaPeakValid[0] = false;
 learner.TipSynapseResistance[0] = 50.0;
 learner.MaxIterSomaAmp[0] = .5e-6;
 learner.DendLastAbsDt[0] = .011;
 EXPECT_FALSE(learner.AllDendritesSynced());
}

TEST(TimeLearnerCore, ClassicAmpEpsilonUsesFractionalDoubleBoundary) {
 static_assert(NNeuronTimeLearner::kAmpNormEps == 1e-5, "production epsilon changed");
 NNeuronTimeLearner learner;
 learner.NumInputDendrite = 2;
 learner.InitialSomaPotential = std::vector<double>{1.0, 0.0};
 learner.MaxIterSomaAmp = {1.0 - NNeuronTimeLearner::kAmpNormEps * .5, 0.0};
 learner.DendLastAbsDt = {.01, 0.0};
 EXPECT_TRUE(learner.AllSynapsesNormalized());
 learner.MaxIterSomaAmp[0] = 1.0 - NNeuronTimeLearner::kAmpNormEps * 2.0;
 EXPECT_FALSE(learner.AllSynapsesNormalized());
}

TEST(TimeLearnerCore, ClassicRminLengthSlackHasAnExactUpperBoundary) {
 NNeuronTimeLearner learner;
 learner.NumInputDendrite = 2;
 learner.TipSynapseResistance = std::vector<double>{20.0, 86.0};
 learner.InitialSomaPotential = std::vector<double>{1.0, 0.0};
 learner.MaxIterSomaAmp = {.5, 0.0};
 learner.DendLastAbsDt = {.04, 0.0};
 EXPECT_TRUE(learner.AllSynapsesNormalized());
 learner.DendLastAbsDt[0] = .040000000001;
 EXPECT_FALSE(learner.AllSynapsesNormalized());
}

TEST(TimeLearnerCore, ClassicPeakAttemptIsRequiredForDeadTipGate) {
 NNeuronTimeLearner learner;
 learner.NumInputDendrite = 2;
 learner.InitialSomaPotential = std::vector<double>{1.0, 0.0};
 learner.MaxIterSomaAmp = {0.0, 0.0};
 learner.DendLastAbsDt = {.01, 0.0};
 learner.PeakSeen[0] = false;
 EXPECT_FALSE(learner.AllSynapsesNormalized());
 learner.PeakSeen[0] = true;
 EXPECT_TRUE(learner.AllSynapsesNormalized());
}

TEST(TimeLearnerCore, ClassicTipResistanceMovesTowardAmpTargetAndClamps) {
 NNeuronTimeLearner learner;
 double gain = 0.0;
 const double lower = learner.ComputeDampedTipResistance(0, 50.0, .5, 1.0, .5, gain);
 EXPECT_LT(lower, 50.0);
 const double upper = learner.ComputeDampedTipResistance(0, 50.0, 1.5, 1.0, -.5, gain);
 EXPECT_GT(upper, 50.0);
 EXPECT_DOUBLE_EQ(learner.ComputeDampedTipResistance(0, 20.0, .5, 1.0, .5, gain), 20.0);
 EXPECT_DOUBLE_EQ(learner.ComputeDampedTipResistance(0, 100.0, 1.5, 1.0, -.5, gain), 100.0);
}

TEST(TimeLearnerCore, BranchReverseSelectionStartsAtReferenceAndMovesDown) {
 NNeuronTimeLearnerBranch learner;
 learner.NumInputDendrite = 4;
 learner.PulseSynced = {false, false, false, false};
 EXPECT_EQ(learner.SelectActiveDendrite(), 3);
 learner.PulseSynced[3] = true;
 EXPECT_EQ(learner.SelectActiveDendrite(), 2);
 learner.PulseSynced[2] = true;
 EXPECT_EQ(learner.SelectActiveDendrite(), 1);
 learner.PulseSynced[1] = true;
 EXPECT_EQ(learner.SelectActiveDendrite(), 0);
}

TEST(TimeLearnerCore, BranchEndGateRequiresEveryPulseAndOnlyTunesActivePulse) {
 NNeuronTimeLearnerBranch learner;
 learner.NumInputDendrite = 3;
 learner.PulseSynced = {true, true, true};
 EXPECT_TRUE(learner.AllDendritesSynced());
 learner.PulseSynced[1] = false;
 EXPECT_FALSE(learner.AllDendritesSynced());
 learner.PulseSynced[1] = true;
 learner.ActivePulseIndex = 0;
 learner.InitialSomaPotential = std::vector<double>{1.0, 1.0, 0.0};
 learner.MaxIterSomaAmp = {1.0, .2, 0.0};
 learner.DendLastAbsDt = {.01, .01, 0.0};
 EXPECT_TRUE(learner.AllSynapsesNormalized());
 learner.ActivePulseIndex = 1;
 EXPECT_FALSE(learner.AllSynapsesNormalized());
}

TEST(TimeLearnerCore, BranchTipResistanceDirectionAndBoundsMatchClassicContract) {
 NNeuronTimeLearnerBranch learner;
 double gain = 0.0;
 EXPECT_LT(learner.ComputeDampedTipResistance(0, 50.0, .5, 1.0, .5, gain), 50.0);
 EXPECT_GT(learner.ComputeDampedTipResistance(0, 50.0, 1.5, 1.0, -.5, gain), 50.0);
 EXPECT_DOUBLE_EQ(learner.ComputeDampedTipResistance(0, 20.0, .5, 1.0, .5, gain), 20.0);
 EXPECT_DOUBLE_EQ(learner.ComputeDampedTipResistance(0, 100.0, 1.5, 1.0, -.5, gain), 100.0);
}

TEST(TimeLearnerCore, ClassicForcedRmaxLengthGrowthIsAppliedExactlyOnce) {
 NNeuronTimeLearner learner;
 learner.NumInputDendrite = 2;
 learner.DendriteLength = std::vector<int>{2,1,1};
 learner.MaxDendriteLength = 6;
 learner.DendStatus = {0,0,0};
 learner.RmaxOvershootLengthGrow = {true,false,false};
 learner.SomaPeakValid = {true,true,true};
 learner.DendLastAbsDt = {.001,0,0};
 learner.ApplyPendingLengthLoopForProbe();
 EXPECT_EQ(learner.DendriteLength[0], 3);
 EXPECT_EQ(learner.DendStatus[0], 1);
 EXPECT_EQ(learner.LastLengthDelta, 1);
}

TEST(TimeLearnerCore, BranchForcedRmaxLengthGrowthIsAppliedAndBounded) {
 NNeuronTimeLearnerBranch learner;
 learner.NumInputDendrite = 2;
 learner.DendriteLength = std::vector<int>{2,1,1};
 learner.MaxDendriteLength = 3;
 learner.DendStatus = {0,0,0};
 learner.RmaxOvershootLengthGrow = {true,false,false};
 learner.ApplyPendingLengthLoopForProbe();
 EXPECT_EQ(learner.DendriteLength[0], 3);
 EXPECT_EQ(learner.DendStatus[0], 1);
 learner.ApplyPendingLengthLoopForProbe();
 EXPECT_EQ(learner.DendriteLength[0], 3);
 EXPECT_EQ(learner.DendStatus[0], 0);
 EXPECT_FALSE(learner.RmaxOvershootLengthGrow[0]);
}

TEST(TimeLearnerCore, BranchBuildNormalizesReferenceZeroToPhysicalSegmentOne) {
 NNeuronTimeLearnerBranch learner;
 learner.NumInputDendrite = 4;
 learner.DendriteLength = std::vector<int>{1,1,1,0};
 learner.NormalizeBranchLengthsForBuildProbe();
 EXPECT_EQ(learner.DendriteLength.GetData(), std::vector<int>({1,1,1,1}));
 EXPECT_DOUBLE_EQ(learner.DelayLenOf(3), 0.0);
 EXPECT_EQ(learner.PulseAttachPos(3), 1);
 learner.DendriteLength[3] = 1;
 EXPECT_DOUBLE_EQ(learner.DelayLenOf(3), 0.0);
 EXPECT_EQ(learner.PulseAttachPos(3), 1);
}
'''


output = prefix + method("NNeuronTimeLearnerBranch.cpp", "int BranchAttachSegment(const int attach_pos)") + "\n"
output += learner_class("NNeuronTimeLearner", "NNeuronTimeLearner.h", False)
output += learner_class("NNeuronTimeLearnerBranch", "NNeuronTimeLearnerBranch.h", True)
output += methods + tests
Path(sys.argv[1]).write_text(output, encoding="utf-8")
