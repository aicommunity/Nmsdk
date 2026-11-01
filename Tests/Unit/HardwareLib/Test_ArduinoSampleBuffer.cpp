#include <gtest/gtest.h>

#include <UArduinoSampleBuffer.h>

#include <Math/MDMatrix.h>

TEST(ArduinoSampleBuffer, AppendAndTrim)
{
    RDK::MDMatrix<double> matrix;
    matrix.Assign(0, 3, 0.0);
    const double row[3] = {1.0, 2.0, 3.0};
    RDK::UArduinoSampleBuffer::appendRow(matrix, row, 3);
    RDK::UArduinoSampleBuffer::appendRow(matrix, row, 3);
    EXPECT_EQ(matrix.GetRows(), 2);
    RDK::UArduinoSampleBuffer::trimRows(matrix, 1);
    EXPECT_EQ(matrix.GetRows(), 1);
}

TEST(ArduinoSampleBuffer, BoundedAppendKeepsRecentRowsAndCapsGrowth)
{
    RDK::MDMatrix<double> matrix;
    matrix.Assign(0, 2, 0.0);
    for (int value = 1; value <= 10; ++value) {
        const double row[2] = {static_cast<double>(value), -static_cast<double>(value)};
        RDK::UArduinoSampleBuffer::appendRowBounded(matrix, row, 2, 4);
    }

    EXPECT_EQ(4, matrix.GetRows());
    EXPECT_DOUBLE_EQ(7.0, matrix(0, 0));
    EXPECT_DOUBLE_EQ(-7.0, matrix(0, 1));
    EXPECT_DOUBLE_EQ(10.0, matrix(3, 0));
}
