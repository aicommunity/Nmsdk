"""Explicit diagnostic provenance; ordinary recognition validators stay strict."""
from .native_evidence import EvidenceError
from .recognition_evidence import _audit_derivation
from .recognition_trial_evidence import _audit_recognition_trial


def audit_diagnostic_recognition(package, source_case):
    try:
        if package.get('kind') == 'timelearner_diagnostic_threshold_candidate':
            from .threshold_candidate_evidence import audit_diagnostic_threshold_candidate
            result = audit_diagnostic_threshold_candidate(package, source_case)
        else:
            result = _audit_derivation(package, source_case, diagnostic=True)
        return {**result, "diagnostic_only": True, "certificate_present": False,
                "training_outcome": source_case[0]["training_outcome"],
                "training_reason": source_case[0]["reason"], "evaluation_verdict": None}
    except EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as error:
        raise EvidenceError("malformed_diagnostic_recognition:"+str(error)) from error


def audit_diagnostic_recognition_trial(observation, package, source_case):
    proof = audit_diagnostic_recognition(package, source_case)
    measured = _audit_recognition_trial(observation, package, diagnostic=True)
    return {**measured, "diagnostic_only": True, "training_outcome": proof["training_outcome"],
            "certificate_present": False, "evaluation_verdict": None}
