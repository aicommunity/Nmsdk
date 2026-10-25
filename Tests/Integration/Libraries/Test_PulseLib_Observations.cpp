#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseLTZone.h"

#include <limits>
#include <vector>

namespace {

// Expose observation boundaries, not copied implementations. Framework lifecycle
// integration is tested separately; these cases exercise the production collector.
class ObservationProbe : public NMSDK::NPatternResponseAnalyzer
{
public:
    using NPatternResponseAnalyzer::BeginTrial;
    using NPatternResponseAnalyzer::AppendStim;
    using NPatternResponseAnalyzer::UpdateTrialMetrics;
    using NPatternResponseAnalyzer::RecordNeuronSpike;
    using NPatternResponseAnalyzer::CsvHeader;
    using NPatternResponseAnalyzer::ResetTrialState;

    void BindLtz(NMSDK::NPulseLTZoneCommon* ltz) { ltz_source_ = ltz; }
    const std::vector<double>& Peaks() const { return trial_soma_amp_max_; }
    bool Valid() const { return trial_measurement_valid_; }
    bool Overflow() const { return trial_spike_overflow_; }
};

void SetAmplitudes(ObservationProbe& probe, std::vector<double> values)
{
    RDK::MDMatrix<double> matrix;
    matrix.Resize(static_cast<int>(values.size()), 1);
    for(size_t i = 0; i < values.size(); ++i)
        matrix(static_cast<int>(i), 0) = values[i];
    probe.SomaAmplitudeInput.SetDataDirect(std::vector<RDK::MDMatrix<double>>{matrix});
}

TEST(TimeLearnerObservations, RetainsEverySomaAndSignedMaxima)
{
    ObservationProbe probe;
    probe.Default();
    probe.BeginTrial(10.0);
    SetAmplitudes(probe, {-1.5, -.1, -.2, -.3, -.4, -.5});
    probe.UpdateTrialMetrics(10.0);
    ASSERT_EQ(probe.Peaks().size(), 5u);
    EXPECT_DOUBLE_EQ(probe.Peaks()[4], -.5);
    SetAmplitudes(probe, {-1.4, -.05, -.2, -.3, -.4, -.45});
    probe.UpdateTrialMetrics(10.1);
    EXPECT_DOUBLE_EQ(probe.Peaks()[0], -.05);
    EXPECT_DOUBLE_EQ(probe.Peaks()[4], -.45);
}

TEST(TimeLearnerObservations, NonfiniteCannotBeHiddenByPreviousPeak)
{
    ObservationProbe probe;
    probe.Default();
    probe.BeginTrial(10.0);
    SetAmplitudes(probe, {.3, .1, .2});
    probe.UpdateTrialMetrics(10.0);
    EXPECT_TRUE(probe.Valid());
    SetAmplitudes(probe, {.3, .1, std::numeric_limits<double>::quiet_NaN()});
    probe.UpdateTrialMetrics(10.1);
    EXPECT_FALSE(probe.Valid());
    EXPECT_DOUBLE_EQ(probe.Peaks()[1], .2);
}

TEST(TimeLearnerObservations, OverflowAndDimensionChangeInvalidateEvidence)
{
    ObservationProbe probe;
    probe.Default();
    probe.BeginTrial(10.0);
    SetAmplitudes(probe, {.3, .1, .2});
    probe.UpdateTrialMetrics(10.0);
    SetAmplitudes(probe, {.3, .1});
    probe.UpdateTrialMetrics(10.1);
    EXPECT_FALSE(probe.Valid());
    for(int i = 0; i < 17; ++i)
        probe.RecordNeuronSpike(10.0 + .01 * i);
    EXPECT_TRUE(probe.Overflow());
    probe.ResetTrialState();
    EXPECT_FALSE(probe.Overflow());
}

TEST(TimeLearnerObservations, Schema4IsExplicitAndRequiresActualMeasurementSources)
{
    ObservationProbe probe;
    probe.Default();
    EXPECT_EQ(probe.CsvHeader().find("run_id"), std::string::npos);
    probe.ObservationSchemaVersion = 4;
    EXPECT_NE(probe.CsvHeader().find("run_id,trial_id,sample_id,pattern_hash"), std::string::npos);
    probe.BeginTrial(10.0);
    SetAmplitudes(probe, {.3, .1, .2});
    probe.UpdateTrialMetrics(10.0);
    EXPECT_FALSE(probe.Valid());

    probe.BeginTrial(12.0);
    NMSDK::NPulseLTZoneThreshold ltz;
    ltz.Potential = .2;
    probe.BindLtz(&ltz);
    probe.UpdateTrialMetrics(12.0);
    EXPECT_TRUE(probe.Valid());
}

} // namespace
