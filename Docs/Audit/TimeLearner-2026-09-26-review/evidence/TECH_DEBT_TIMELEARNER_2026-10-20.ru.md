# TECH_DEBT TimeLearner 2026-10-20

```tsv
debt_id	opened_utc	stage_id	source	item_ref	priority	blocker_for	status	owner_arm	notes	closed_utc	fix_run_id
DEBT-A0-ctest	2026-10-20T13:22Z	A0	card	BranchInvalidPeakNoRecovery×2	P2	—	open	—	baseline 85/87		
DEBT-cpu-gate-pgrep	2026-10-20T13:48Z	R2	companion	cpu_gate false positive	P1	D1	done	.11	pattern fixed	2026-10-20T13:48Z	local
DEBT-A15-matrix-inputs	2026-10-20T13:23Z	R2	audit	45 FAIL Test	P0	B2	done	B2	repaired on agent/tl-a15-inputs 98ac830d; FAIL Test 0	2026-10-20T14:05Z	98ac830d
DEBT-H-A15b	2026-10-20T13:22Z	R	audit	SoftCold tip1	P1	E2	open	E2			
DEBT-CL-N1	2026-10-20T13:22Z	R	audit	Classic N1 stall	P0	R3	open	D1	W02 both ends not_converged; not in PulseLib 780→d52 window; W01 OK		
DEBT-G1-432	2026-10-20T13:22Z	E2G1	plan	432 optional	P2	S5	open	—	canon 24-32		
DEBT-F1a-offline	2026-10-20T15:45Z	S1	card F1a	offline ideal/sweep	P2	S1	done	F1a	margins MATCH; W13/W37 not_converged	2026-10-20T15:45Z	F1a_20261020_11
DEBT-F1b	2026-10-20T13:22Z	S1	card	F1b pilot	P1	S1	open	F1b			
DEBT-S0-cpp-fields	2026-10-20T13:56Z	S0	audit	residue/margin/Done_BE report fields	P0	S0/R8	open	stage0	summarize columns ready; C++ emit still missing		
DEBT-disk-200G	2026-10-20T13:06Z	A0	card/human	DATA≥200G not STOP	P2	—	done	.11	human: no STOP <200G; EventsLog→.17 Data; ~288G free	2026-10-20T15:16Z	offload
DEBT-A3-trace-hang	2026-10-20T14:19Z	R2	card	A3 TRACE hang corrupt+repaired	P1	A3	open	A3	repaired: kill after stall; peaks from partial trace		
DEBT-C1-silent-soma	2026-10-20T15:20Z	C1	card	soma_0/2 silent set1	P1	physics E1	open	C1	L43/L1 MODEL_MATCH; L51/L25 meas=0		
DEBT-D2-silent-test	2026-10-20T16:05Z	R2	D2.0/D2.2	W01 converge but fires=0	P0	E2/R8	open	D2	A9/A11 mid axis		
DEBT-A1-preinh-silent	2026-10-20T15:15Z	R2	card A1	br25_preinh silent fires	P0	E2/G1 labels	open	A1	BASELINE_DEGRADED; nextseg MATCH; br50_gen better-than-expected		
DEBT-F7-rmin-tol-mask	2026-10-20T17:00Z	R3	D2b.1	RminTol×4 masks measured dt	P0	F2 Done_BE	confirmed	F7	abs_dt 0.0031>tol; factor1 stalls; F2.pref Done via ×4	2026-10-20T17:12Z	F2.pref
DEBT-TRACE-NOCSV	2026-10-20T17:10Z	R2	gate	Test hang no TRACE CSV	P1	quality	open	gate	kill etime>180; child_rc=-15		
DEBT-D2b5-W02	2026-10-20T17:15Z	R2	D2b.5	W02 Signed+RminTol not_converged	P0	CL-N1	open	D2b	L=54 44 1 1		
DEBT-disk-freegib-root	2026-10-20T20:11Z	E2	infra	free_gib()=Bin volume not DATA	P1	E2 soft-cold	done	.17	offload unused lanes /→Data; Avail≈108G; assert still on /	2026-10-20T20:17Z	lanes-offload
DEBT-matrix-prepare-wave	2026-10-20T20:20Z	E2	queue	whole-wave prepare vs stale snapshots	P0	E2 R8	done	Bin	queue prepare --case-ids only; Bin 774704fc	2026-10-20T20:24Z	774704fc
```
