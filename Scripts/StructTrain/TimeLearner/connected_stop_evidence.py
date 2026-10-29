"""Native connected-control readbacks plus existing stopped-model evidence.

The baseline may truthfully demonstrate that a stop was ignored. A consistency
audit must not relabel that run as stopped or grant it a training certificate.
"""
from .native_evidence import EvidenceError, count, require
from .stopped_evidence import audit_stopped_state

FIELDS = {"kind", "schema_version", "calculate_mode", "controller_version", "stop_point", "connected",
          "source_value", "learner_need", "stop_requested", "state", "outcome", "reason",
          "certificate_present", "reference_packets", "observed_packets", "probe_state",
          "parameters_preserved", "evaluation_verdict"}


def audit_connected_stop(packet, stopped_case=None):
    try:
        p = packet
        require(set(p) == FIELDS and p["kind"] == "native_connected_training_stop"
                and type(p["schema_version"]) is int and p["schema_version"] == 1,
                "unknown_connected_stop_schema")
        mode, version, point = (count(p[k]) for k in ("calculate_mode", "controller_version", "stop_point"))
        require(mode in (0, 1) and version == 2 and point in range(5), "unsupported_connected_stop_case")
        for key in ("connected", "source_value", "learner_need", "stop_requested", "certificate_present", "parameters_preserved"):
            require(type(p[key]) is bool, "invalid_connected_stop_boolean")
        require(p["evaluation_verdict"] is None and p["connected"] is True
                and p["source_value"] == p["learner_need"], "connected_source_readback_mismatch")
        keep = point == 4
        require(p["source_value"] is keep and p["stop_requested"] is (not keep), "connected_stop_request_mismatch")
        require(p["certificate_present"] is False, "false_connected_stop_certificate")
        refs, observed = count(p["reference_packets"]), count(p["observed_packets"])
        require(type(p["reason"]) is str and p["state"] in ("capturing_references", "searching", "finished")
                and p["probe_state"] in ("idle", "queued", "running", "completed", "rejected", "cancelled"),
                "unknown_connected_stop_state")
        proof = None
        if keep:
            require(p["state"] == "capturing_references" and p["outcome"] == "searching" and p["reason"] == ""
                    and stopped_case is None, "unrequested_connected_stop")
            honored = False
        else:
            honored = (p["state"] == "finished" and p["outcome"] == "external_stop" and p["reason"] == "external_stop"
                       and p["parameters_preserved"] and p["probe_state"] not in ("queued", "running"))
            if honored:
                require(stopped_case is not None, "connected_stop_model_evidence_required")
                proof = audit_stopped_state(*stopped_case)
                package = stopped_case[0]
                require(package["training_outcome"] == "external_stop" and package["reason"] == "external_stop"
                        and count(package["controller_version"]) == version and count(package["calculate_mode"]) == mode
                        and len(package["reference_packets"]) == refs and len(package["observed_packets"]) == observed,
                        "connected_stop_package_mismatch")
            else:
                require(stopped_case is None and p["state"] in ("capturing_references", "searching")
                        and p["outcome"] == "searching", "inconsistent_ignored_stop_evidence")
        return {"schema_version": 1, "calculate_mode": mode, "stop_point": point, "stop_requested": not keep,
                "stop_honored": honored, "keep_true_control_active": keep,
                "stopped_proof": proof, "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise EvidenceError("malformed_connected_stop_evidence:" + str(error)) from error
