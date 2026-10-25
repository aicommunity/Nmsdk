#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPatternResponseAnalyzer.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseLTZone.h"

#include <limits>
#include <vector>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <cstdlib>

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
    using NPatternResponseAnalyzer::CloseTrial;
    using NPatternResponseAnalyzer::AttributeNeuronToActiveTrial;

    void SetFixtureIdentity(int sample, int label)
    {
        trial_sample_id_ = sample;
        trial_target_class_ = label;
    }

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

TEST(TimeLearnerObservations, Schema4WriterRoundtripFixture)
{
    const char* configured = std::getenv("TIMELEARNER_OBSERVATION_TEST_DIR");
    const std::filesystem::path directory = configured ? std::filesystem::path(configured) :
        std::filesystem::temp_directory_path() / ("nmsdk-observation-" +
        std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directories(directory);
    {
        ObservationProbe probe;
        probe.Default();
        probe.SavePath = directory.string();
        probe.ObservationSchemaVersion = 4;
        probe.RunId = "fixture,quoted\"run";
        probe.ModelRevision = "collector-unit-fixture";
        NMSDK::NPulseLTZoneThreshold ltz;
        ltz.Potential = .2;
        for(int trial = 0; trial < 8; ++trial)
        {
            const double onset = 10.0 + trial * 3.0;
            probe.BeginTrial(onset);
            probe.SetFixtureIdentity(trial, trial == 0 ? 1 : 0);
            probe.BindLtz(&ltz);
            probe.AppendStim(onset + .01 + .001 * trial);
            probe.AppendStim(onset + .03 + .001 * trial);
            probe.AppendStim(onset + .06 + .001 * trial);
            SetAmplitudes(probe, {.15, .01, .02, .03, .04, .05});
            probe.UpdateTrialMetrics(onset + .06 + .001 * trial);
            if(trial == 0)
                probe.AttributeNeuronToActiveTrial(onset + .1);
            probe.CloseTrial(onset + .06 + .001 * trial + 1.5);
        }
    }
    std::ifstream csv(directory / "results.csv");
    ASSERT_TRUE(csv.good());
    std::string line;
    std::getline(csv, line);
    EXPECT_NE(line.find("run_id,trial_id,sample_id,pattern_hash,model_revision"), std::string::npos);
    int count = 0;
    while(std::getline(csv, line))
    {
        ++count;
        EXPECT_NE(line.find("\"fixture,quoted\"\"run\""), std::string::npos);
        EXPECT_NE(line.find("fnv1a64:"), std::string::npos);
    }
    EXPECT_EQ(count, 8);
    // A caller may retain this clearly labelled unit fixture for the production
    // Python scorer roundtrip. It is never a scientific model evaluation.
    if(!configured)
        std::filesystem::remove_all(directory);
}

} // namespace
