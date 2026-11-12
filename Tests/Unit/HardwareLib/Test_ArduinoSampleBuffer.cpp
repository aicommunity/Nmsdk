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
