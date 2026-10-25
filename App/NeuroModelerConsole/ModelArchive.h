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

// Complete self-contained native graph plus immutable image dependency closure.
// metadata declares implementation_id, state_kind, training, calibration and
// conversion. This is not a physical/controller mid-probe checkpoint.
QJsonObject ExportModelArchive(RDK::UEPtr<RDK::UContainer> model, const QJsonObject& metadata);

// Returns a newly acquired model only after native Load/Init and full identity
// verification. Caller owns the instance and must Free/ReturnObject it.
// Existing shared images are verified, never replaced. On failure, newly
// registered unused images may remain; discard that import storage before retry.
RDK::UEPtr<RDK::UContainer> ImportModelArchive(
    const QJsonObject& archive, RDK::UEPtr<RDK::UStorage> storage,
    RDK::UEPtr<RDK::UEnvironment> environment, const QString& implementationId);
}
