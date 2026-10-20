# TECH_DEBT TimeLearner 2026-10-20

```tsv
debt_id	opened_utc	stage_id	source	item_ref	priority	blocker_for	status	owner_arm	notes	closed_utc	fix_run_id
DEBT-A0-ctest	2026-10-20T13:22Z	A0	card	BranchInvalidPeakNoRecovery×2	P2	—	open	—	baseline 85/87		
DEBT-cpu-gate-pgrep	2026-10-20T13:48Z	R2	companion	cpu_gate false positive	P1	D1	done	.11	pattern fixed	2026-10-20T13:48Z	local
DEBT-A15-matrix-inputs	2026-10-20T13:23Z	R2	audit	45 FAIL Test	P0	B2	done	B2	repaired on agent/tl-a15-inputs 98ac830d; FAIL Test 0	2026-10-20T14:05Z	98ac830d
DEBT-H-A15b	2026-10-20T13:22Z	R	audit	SoftCold tip1	P1	E2	open	E2			
DEBT-CL-N1	2026-10-20T13:22Z	R	audit	Classic N1 stall	P0	R3	open	D1	W02 both ends not_converged; not in PulseLib 780→d52 window; W01 OK		
DEBT-G1-432	2026-10-20T13:22Z	E2G1	plan	432 optional	P2	S5	open	—	canon 24-32		
DEBT-F1b	2026-10-20T13:22Z	S1	card	F1b pilot	P1	S1	open	F1b			
DEBT-S0-cpp-fields	2026-10-20T13:56Z	S0	audit	residue/margin/Done_BE report fields	P0	S0/R8	open	stage0	C++ instrumentation pending		
DEBT-disk-200G	2026-10-20T13:06Z	A0	card/human	DATA≥200G not STOP	P2	—	done	.11	human: no STOP <200G; EventsLog→.17 Data; ~288G free	2026-10-20T15:16Z	offload
DEBT-A3-trace-hang	2026-10-20T14:19Z	R2	card	A3 TRACE hang corrupt+repaired	P1	A3	open	A3	repaired: kill after stall; peaks from partial trace		
DEBT-C1-silent-soma	2026-10-20T15:20Z	C1	card	soma_0/2 silent set1	P1	physics E1	open	C1	L43/L1 MODEL_MATCH; L51/L25 meas=0		
DEBT-A1-preinh-silent	2026-10-20T15:15Z	R2	card A1	br25_preinh silent fires	P0	E2/G1 labels	open	A1	BASELINE_DEGRADED; nextseg MATCH; br50_gen better-than-expected		
```
