// Generated source inputs; see generate_historical_source_contract.py.
#pragma once
#include <array>
#include <string>
#include <vector>
namespace NmsdkTests {
struct AxoneHistoricalTarget { int spanMs; std::array<double,4> isi; std::string recipeSha256; };
inline std::vector<AxoneHistoricalTarget> AxoneHistoricalTargets() { return {
    {25, {0.000520833, 0.00416667, 0.00833333, 0.0125}, "86af76c0ca28df2378e21cf1d50e5d13c0527697a6523d049fa5747ab4d3b5ad"},
    {50, {0.00104167, 0.00833333, 0.0166667, 0.025}, "4c1edb809a2600844e3a9b55cf577bcecb21fa4ab6dfec4adb40ef181dd9b730"},
    {100, {0.00208333, 0.0166667, 0.0333333, 0.05}, "74049a2e418ab9958189d5928cb837a6f2a441aa943a03f9d7382d0a2646c6ad"},
    {200, {0.00416667, 0.0333333, 0.0666667, 0.1}, "470cf7427cb171a3f97106e5e0a57f2ee0c9a76369a93909ea6de402293b062b"},
    {480, {0.01, 0.08, 0.16, 0.24}, "f268d6bb64ad086a9727407c85b930bc04d2c25a41eed2a183baadbe159567c2"},
}; }
}
