// Audit probes assert the desired contract. Failures are evidence, not fixes.
#include "NNeuronPostTrainTune.h"
#include "UModernDiagramLinkRouter.h"
#include <gtest/gtest.h>
#include <limits>

TEST(PostTuneAudit, GapMustIncludeEveryFoil)
{
    double mid = 0, gap = 0;
    const std::vector<double> foils{0.2, 0.6};
    NMSDK::PostTrainTune::ComputeMidThreshold(0.5, foils, mid, gap);
    EXPECT_FALSE(NMSDK::PostTrainTune::LandscapeOk(0.5, foils));
    EXPECT_NEAR(gap, -0.1, 1e-12) << "mid=" << mid;
}

TEST(PostTuneAudit, NonFiniteMetricsMustNotBeAccepted)
{
    EXPECT_FALSE(NMSDK::PostTrainTune::LandscapeOk(
        0.5, {std::numeric_limits<double>::quiet_NaN()}));
}

TEST(RouterAudit, ThinObstacleMustBeDetectedBetweenSamples)
{
    const QVector<QPointF> line{QPointF(0, 0), QPointF(1000, 0)};
    const QList<QRectF> obstacles{QRectF(55, -10, 10, 20)};
    EXPECT_GT(UModernDiagramLinkRouter::obstacleHitsOnPolyline(line, obstacles), 0);
}
