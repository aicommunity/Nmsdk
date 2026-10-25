#pragma once
#include <QJsonObject>
#include "../../../Rdk/Deploy/Include/rdk.h"

namespace NmsdkTools {
// Read-only semantic identity of a complete, ready, self-contained graph.
// Dynamic state, names/IDs of the root and presentation/diagnostic settings are
// excluded. Unsupported parameter types or unresolved bindings invalidate it.
// The code/runtime identity and controller certificate remain separate records.
QJsonObject IdentifyModel(RDK::UEPtr<RDK::UContainer> model);
// Validate the archived identity itself, then compare against an independently
// captured native model. Never trust a stored hash without checking its data.
QJsonObject VerifyModelIdentity(const QJsonObject& expected, RDK::UEPtr<RDK::UContainer> model);
}
