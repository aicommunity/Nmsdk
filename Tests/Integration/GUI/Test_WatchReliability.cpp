#include "Plot/TimeSeriesEnvelope.h"
#include "UParameterFormEdits.h"
#include "WindowWorkArea.h"

#include <QApplication>
#include <QCheckBox>
#include <QDoubleSpinBox>
#include <gtest/gtest.h>
#include <stdexcept>

namespace
{
TEST(WatchWindowGeometry, FitsAnOversizedRestoredWindowOnASmallerScreen)
{
    const QRect workArea(-1280, 180, 1280, 680);
    const QRect restored(-500, 100, 1500, 980);
    EXPECT_EQ(NMSDK::Gui::fitWindowFrameToWorkArea(restored, workArea), workArea);
}

TEST(WatchWindowGeometry, KeepsAVisibleWindowAndClampsAnOverlappingFrame)
{
    const QRect workArea(1920, -240, 960, 500);
    const QRect visible(1940, -212, 650, 400);
    EXPECT_EQ(NMSDK::Gui::fitWindowFrameToWorkArea(visible, workArea), visible);
    const QRect overlapping(2690, 220, 640, 350);
    EXPECT_EQ(NMSDK::Gui::fitWindowFrameToWorkArea(overlapping, workArea),
              QRect(2240, -90, 640, 350));
}

TEST(WatchReliability, KeepsOneTickExtremaWithinTheDrawBudget)
{
    std::list<double> times;
    std::list<double> values;
    for (int tick = 0; tick < 20000; ++tick)
    {
        times.push_back(tick);
        values.push_back(tick == 4121 ? -0.875 : tick == 4122 ? 0.875 : 0.0);
    }

    const auto overview = NMSDK::Plot::timeSeriesEnvelope(times, values, 0.125);
    ASSERT_LE(overview.size(), 8000);
    EXPECT_EQ(overview.first(), QPointF(0, 0.125));
    EXPECT_EQ(overview.last(), QPointF(19999, 0.125));
    EXPECT_TRUE(overview.contains(QPointF(4121, -0.75)));
    EXPECT_TRUE(overview.contains(QPointF(4122, 1.0)));
    EXPECT_TRUE(std::is_sorted(overview.begin(), overview.end(),
                              [](const auto& a, const auto& b) { return a.x() < b.x(); }));

    const auto zoomed = NMSDK::Plot::timeSeriesEnvelope(times, values, 0.0, 4119.0, 4124.0);
    ASSERT_EQ(zoomed.size(), 8);
    EXPECT_EQ(zoomed.first(), QPointF(4118, 0.0));
    EXPECT_EQ(zoomed.at(3), QPointF(4121, -0.875));
    EXPECT_EQ(zoomed.at(4), QPointF(4122, 0.875));
    EXPECT_EQ(zoomed.last(), QPointF(4125, 0.0));
}

TEST(WatchReliability, HandlesEmptyAndMismatchedHistories)
{
    EXPECT_TRUE(NMSDK::Plot::timeSeriesEnvelope({}, {}, 0.0).isEmpty());
    const auto one = NMSDK::Plot::timeSeriesEnvelope({0.0, 1.0}, {2.0}, 0.0);
    ASSERT_EQ(one.size(), 1);
    EXPECT_EQ(one.first(), QPointF(0, 2));
}

template<class T>
struct Property
{
    T data;
    int setterCalls = 0;
    bool reject = false;

    const T& GetData() const { return data; }
    std::string GetName() const { return "test property"; }
    void SetData(T value)
    {
        ++setterCalls;
        if (reject)
            throw std::runtime_error("test rejection");
        data = value;
    }
};

TEST(ParameterFormEdits, AppliesOnlyEditedFieldsAndPreservesUnroundedValues)
{
    QCheckBox train;
    QDoubleSpinBox frequency;
    Property<bool> trainProperty{true};
    Property<double> frequencyProperty{1.5051234};
    train.setChecked(true);
    frequency.setValue(frequencyProperty.data);

    UParameterFormEdits edits;
    edits.remember(&train, train.isChecked());
    edits.remember(&frequency, frequency.value());
    edits.apply(&frequency, frequencyProperty, frequency.value());
    EXPECT_EQ(frequencyProperty.setterCalls, 0);
    EXPECT_DOUBLE_EQ(frequencyProperty.data, 1.5051234);

    frequency.setValue(2.25);
    edits.apply(&train, trainProperty, train.isChecked());
    edits.apply(&frequency, frequencyProperty, frequency.value());
    EXPECT_EQ(trainProperty.setterCalls, 0);
    EXPECT_EQ(frequencyProperty.setterCalls, 1);
    EXPECT_DOUBLE_EQ(frequencyProperty.data, 2.25);
}

TEST(ParameterFormEdits, StopsAfterARejectedChange)
{
    QCheckBox first;
    QCheckBox second;
    Property<bool> denied{false, 0, true};
    Property<bool> other{false};
    UParameterFormEdits edits;
    edits.remember(&first, false);
    edits.remember(&second, false);
    edits.apply(&first, denied, true);
    edits.apply(&second, other, true);
    EXPECT_EQ(edits.failedField(), QStringLiteral("test property"));
    EXPECT_EQ(other.setterCalls, 0);
}
}

int main(int argc, char** argv)
{
    QApplication app(argc, argv);
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
