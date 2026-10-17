# Preserve checklist (README §4) + executable gates (PLAN P3)

Do **not** regress these while closing R01–R07:

- Dataset metadata / Branch binding; immutable trial label; no early fired; late observe after timely fire
- Injective spike↔stim matching; all foil spikes count toward FA
- Global gap = tgt − max(**all** foils); MetricsFinite; silent on invalid inference
- TL best reprobe; Search setup failure; clear rejected metrics after fallback; numeric TipR compare
- NAxoneDelay off-by-one; Preinh ApplyElementDefaults; router segment intersection; Console Save/exit latch

Do **not** close:

- A08/A10 via Branch probes alone (stubs miss R03/R05)
- A15 via GUI tests alone
- A01/A02/A16 while R01/R02/R06 lack fresh evidence

## Executable checks still required

| Area | Check |
|------|-------|
| Preinh A13 | Storage/XML registration runtime |
| Delay A11 | N=0/1/2; NPulseDelay pass-through if \|DelayTime\|&lt;0.001 |
| Console A15 | CLI `-S` without `-x`; exit from ini; Save error; multi-channel |

## Claim policy

Full PASS on seven cases only after fresh run-bundles with provenance. Negative model results stay research outcomes — do not mask by relaxing LandscapeOk or expect_fires.
