# Phase 3 — harness reset contract + failure_class

**Status:** done 2026-09-26

## Code

- [`repro_cold_lib.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/repro_cold_lib.py): `assert_train_cold_xml_before_nm`, `write_cold_reset_contract` → `Train/cold_reset_contract.json` (XML before NM vs expected Branch L last=0).
- [`posttune_verify.py`](../../../../Bin/Configs/SpikeSamples/StructTrain/scripts/posttune_verify.py): `classify_failure_class`; `accept_run` no longer labels `done*_gate_FAIL` as `train_incomplete`; provenance `config_sha256_after` / `source_sha256_after` / `inputs_mutated_during_run` / `failure_class`.
- [`POST_TRAIN_VERIFY.ru.md`](../../../../Bin/Configs/SpikeSamples/StructTrain/POST_TRAIN_VERIFY.ru.md): bullets 1–3 updated.

## Not changed

Branch `ResetToUntrained` last-length=0 semantics (await owner confirmation).
