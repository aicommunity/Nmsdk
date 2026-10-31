#pragma once
#include <QString>

// Called after the standard UAppCore.Init and before project autoexecution.
// Owns a fresh single-clock model; no test framework or alternate engine init.
int RunTimeLearnerCalibrationJob(const QString& input,const QString& output);
