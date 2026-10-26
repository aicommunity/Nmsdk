#pragma once
#include <QString>
#include <map>
#include "../../../Rdk/Deploy/Include/rdk.h"

namespace NmsdkTools {
// Caller-owned stimulus sources outside the physical neuron graph. Names are
// stable protocol port IDs, not component paths or sampled signal values.
using ModelBoundarySources = std::map<const RDK::UIProperty*, QString>;
}
