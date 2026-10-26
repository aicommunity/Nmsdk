#pragma once
#include <QJsonObject>
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "ModelBoundary.h"

namespace NmsdkTools {
// Readback of the actual graph. Does not Build, Reset, Calculate or modify it.
QJsonObject InspectModel(RDK::UEPtr<RDK::UContainer> model,
                        const ModelBoundarySources& boundarySources = {});
}
