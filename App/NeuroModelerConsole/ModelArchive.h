#pragma once
#include "ModelIdentity.h"
#include <stdexcept>

namespace NmsdkTools {
class ModelArchiveError : public std::runtime_error
{
public:
    const std::string code;
    ModelArchiveError(const std::string& reason, const std::string& detail)
        : std::runtime_error(reason + ": " + detail), code(reason) {}
};

// Complete native physical graph plus immutable image dependency closure.
// Version 1 is closed; version 2 requires explicitly named external stimulus
// outputs. Source owners must be initialized/ready before native connection.
// metadata declares implementation_id, state_kind, training, calibration and
// conversion. This is not a physical/controller mid-probe checkpoint.
QJsonObject ExportModelArchive(RDK::UEPtr<RDK::UContainer> model, const QJsonObject& metadata,
                               const ModelBoundarySources& boundarySources = {});

// Returns a newly acquired model only after native Load/Init and full identity
// verification. Caller owns the instance and must Free/ReturnObject it.
// Existing shared images are verified, never replaced. On failure, newly
// registered unused images may remain; discard that import storage before retry.
// Before returning a port-bound model or its sources, disconnect it through
// native UNet::BreakLinks; the live source pointers are caller-owned.
RDK::UEPtr<RDK::UContainer> ImportModelArchive(
    const QJsonObject& archive, RDK::UEPtr<RDK::UStorage> storage,
    RDK::UEPtr<RDK::UEnvironment> environment, const QString& implementationId,
    const ModelBoundarySources& boundarySources = {});
}
