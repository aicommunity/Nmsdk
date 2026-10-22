# TECH_DEBT TimeLearner

Реестр открытых инженерных и алгоритмических долгов кампании AGENT_PLAN (2026-10-20+). Сводная машиночитаемая копия: [`TECH_DEBT.tsv`](TECH_DEBT.tsv). Постановка и выводы — развёрнутыми предложениями; cold-прогоны по этому тикету **не** запускались.

---

## Обновление 2026-10-22 (docs-only, post-RERUN)

**G1_S1_RERUN dual-host закрыт** (последняя волна W02 rep3, `launch.exit=1`). В отборе [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv) **13 волн**; **3/13** exit-clean (W01/W13/W33), **10/13** с последним `launch.exit` ∈ {1,2}. Политика: [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md) — `SYNTHESIS_FINAL` по полной матрице запрещён; разрешён PARTIAL rollup. Ниже — блокеры, которые остаются открытыми.

**DEBT-D2-silent-test (variant A offline + mid policy patch, 2026-10-22):** на bundle `G1.S1.W01-11-20261021T113257Z-15892` парный Test-gate: **`candidate_mid=0.0024126668029073456`** → `fires=01000101`, Acc 4/8, Цель нет; **cpp thr=1** → `fires=00000000`, Acc 7/8 (как G1 partial). **H3 подтверждена** offline; **код:** `UseCandidateMidOnNonSeparableTest` (default **off**) + `ApplyCandidateMidOnNonSeparableTest` в `FinalizePostTuneMid` (Classic+Branch) — [`MID_POLICY_H3_2026-10-22.ru.md`](MID_POLICY_H3_2026-10-22.ru.md). **Cold harness (flag=1):** **PASS** — [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md) (Console `4a0658f3…`, root `e44c8f20a`, PulseLib `5e5a59d`). **H1** — слабая форма (thr=1 маскирует partial fires), **target_hit=0** при обоих порогах. **H4 / sep_margin (2026-10-22):** сильная форма («flat TipR@Rmin ⇒ нет mid &lt;1 с fires») **ослаблена**; слабая (target LTZ≈0.00223 &lt; candidate_mid при gap&lt;0; E1.1b γ(L)≈const → равномерный TipR scale не чинит ranking) — [`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md). **W13/W33 mid replicate (2026-10-22):** H1-weak/H3 на exit-clean тройке — W13 Test mid → `fires=01000101` (как W01); W33 flag/CSV тот же Test mid/gap и TipR **20M×3+86M** (H2-сигнатура есть, Цель не чинит) — [`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md). **H2 KeepDone cold W33:** progon1 `H2.KeepDone-17-20261022T081725Z-74503` — smash `child_rc=-6` (pre-pin, infra-inconclusive). **Retry after glog 0.4** `H2.KeepDone-17-20261022T104632Z-66270`: Train ~31 мин **без** smash, L=`27 22 15 1`, TipR **flat `86M×4`**, Need=1, PostTune не complete → interrupt SIGTERM `child_rc=-15`, SKIP_GATE `fires=` пусто → H2 TipR-mode path **ослаблена** (KeepDone не сохранил midband) — [`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md). **DEBT-17-console-glog → done** (pin confirmed cold) — [`DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md`](DEBT_17_GLOG_ABI_FIX_2026-10-22.ru.md). **H2 TipR overlay** (`H2.TipROverlay-17-20261022T125500Z`): thr=1 silent на всех overlays → H2 **ослаблена** также на frozen TipR — [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md). **DEBT-D2-silent-test** остаётся **partial** (silent thr=1 + H3; H2 weakened).

## Обновление 2026-10-21 (docs-only)

На срезе после **E2 R8×3 SERIES_DONE** и частичного **G1 S1** (drv `SERIES_DONE` на всех волнах, но только **3** волны с `launch.exit=0`; счёт «3/12» в тиках того дня был неточен — в TSV **13** `wave`) нижеперечисленные пункты оставались блокерами для `SYNTHESIS_FINAL` и для честного сравнения C2↔Console.

### P0 — алгоритм и качество оценки

**silent-Test (`DEBT-D2-silent-test`, связанный `DEBT-TRACE-NOCSV`).** На W01 Classic×N0 train сходится с `converged_need0`, но Test даёт `fires=00000000` и/или `child_rc=-15` на gate. Offline sweep (2026-10-22) показал, что **thr=1** скрывает partial soma-fire, достижимый при `candidate_mid`, без восстановления target hit на N0 flat TipR. **H4 ослаблена** как sole-cause: flat Rmin даёт тесный sep_margin (target&lt;mid), но E1.1b γ≈const по TipR — [`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md). **W13/W33** реплицируют H1-weak/H3 при TipR 20M×3+86M ([`SILENT_TEST_W13_W33_MID_2026-10-22.ru.md`](SILENT_TEST_W13_W33_MID_2026-10-22.ru.md)). **H2 KeepDone cold W33** после pin — **ослаблена** (Need=1, TipR flat `86M×4`, SKIP_GATE; `H2.KeepDone-17-20261022T104632Z-66270`) — [`SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md`](SILENT_TEST_H2_KEEPDONE_2026-10-22.ru.md). **H2 TipR overlay `.17`** — **ослаблена** (thr=1 silent на flat/midband/keep_snap; mid=`01000101`) — [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md); **`DEBT-17-console-glog` done** (pin confirmed). F5 γ noop. E2: ось detection/mid ([`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md)). Evidence: [`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md).

**Classic N1 stall (`DEBT-CL-N1`, `DEBT-D2b5-W02`).** W02 `W02_CL480_N1_PSIoff` на всех плечах E2 заканчивается `not_converged_at_stop` с L=`54 44 1 1` (или близким `53 44 1 1` на ранних PulseLib) и разносом TipR — картина согласуется с [`CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md`](CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md). D1 фаза 1: **нет** good→bad converged в окне 11.09–19.10 ([`D1_BISECT_VERDICT_2026-10-20.ru.md`](D1_BISECT_VERDICT_2026-10-20.ru.md)); фаза 2 (L₀ 53→≥54): **CLOSED** lo=`5308aa5`(53) … hi=`3cefd64`(L=`100 72 1 1`, MaxL escape); первый L₀≥54 = **`3cefd64`** — [`D1_BISECT_2026-10-22.ru.md`](D1_BISECT_2026-10-22.ru.md).

**S0 C++ поля (`DEBT-S0-cpp-fields`) — partial 2026-10-22 (sep_margin closed).** PulseLib эмитит `delay_residue` / `amp_over_target` / `sync_exit` / `done_be` и **Train `sep_margin`/`sep_gap`/`sep_tgt`/`sep_max_foil`** в audit `kind=done` + `posttune_complete.flag` после `FinalizePostTuneMid`; harness переносит в `matrix_result.json` ([`S0_CPP_EMIT_2026-10-22.ru.md`](S0_CPP_EMIT_2026-10-22.ru.md)). Формула: `sep_gap = tgt − max_foil` (как `ComputeMidThreshold`), `sep_margin = sep_gap/tgt` при finite && `tgt>0`, иначе NaN. **Остаётся open:** amp-quantized BE mark в `done_be` (отдельный флаг amp BE).

### P1 — фиксы и пилоты

**F5 OPEN (`DEBT-F5-gamma`).** Патч `CorrectAttenuationGammaForTipR` на PulseLib `6d746ac` (default off). One-shot γ=1 ([`F5_GAMMA_COLD_2026-10-21.ru.md`](F5_GAMMA_COLD_2026-10-21.ru.md)) и **paired** γ=0 vs γ=1 на `W01_CL50_N1_PSIoff` ([`F5_GAMMA_PAIRED_2026-10-22.ru.md`](F5_GAMMA_PAIRED_2026-10-22.ru.md), `launch.exit=0` обоих) **не** закрывают A7: Need=0, бит-в-бит одинаковые TipR/L/mid/fires, silent Test `quality_fail`. Paired baseline на том же case **завершён**; PASS по фиксу **нет** ([`R3_FIX_QUEUE_2026-10-20.ru.md`](R3_FIX_QUEUE_2026-10-20.ru.md) A7).

**F1b senior (`DEBT-F1b`) — still OPEN.** Console-пилот «быстрый EPSP + NAxoneDelay» не стартовал; docs-ready checklist добавлен в карточку ([`F1_fast_epsp_pilot.md`](../plans/AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md) §F1b) и в [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) §5 — cold только после senior approve. F1a офлайн закрыт (DEBT-F1a-offline done). F1b питает этап 4 Controller v2 ([`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md)).

**Controller DRAFT refresh (2026-10-22):** sibling входы E1/H*/D1/open decisions — [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md); Train `sep_margin` emit **закрыт** ([`S0_CPP_EMIT_2026-10-22.ru.md`](S0_CPP_EMIT_2026-10-22.ru.md)); SPEC ещё не писать (tol margin, mid policy, TipR mode).

### P0 infra — G1 exit-gate и диск

**Ложный «зелёный» SERIES_DONE (`DEBT-G1-exit-gate`) — harness DONE 2026-10-22.** `wait_run.sh` / `run_series.sh` теперь пробрасывают значение `launch.exit` в exit-код драйвера ([`DEBT_G1_EXIT_GATE_FIX_2026-10-22.ru.md`](DEBT_G1_EXIT_GATE_FIX_2026-10-22.ru.md)). Исторический G1 RERUN по-прежнему **3/13** exit-clean ([`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md)); rollup не опирается на старые drv `EXIT=0`.

**Политика offload диска (`DEBT-disk-offload-policy`).** Soft-cold на `.17` смотрит Avail **корня** `/` (≥80 ГБ), тогда как `$DATA` на отдельном томе; неиспользуемые lanes и `_repro` offload на Data поднимали Avail корня до ~90–108 ГБ ([`STATUS_SNAPSHOT_2026-10-20T2325.ru.md`](STATUS_SNAPSHOT_2026-10-20T2325.ru.md), [`STATUS_SNAPSHOT_2026-10-21T0514.ru.md`](STATUS_SNAPSHOT_2026-10-21T0514.ru.md)). На 2026-10-21 корень снова ~76 ГБ — риск повторного `worker_exit=1` (E2 rep3 W01). Операционное правило: перед новым cold на `.17` — offload lanes/`_repro`, не трогая активные G1 runs; human rule `.11` DATA≥200G без STOP ([`CAMPAIGN_STATUS_2026-10-20.ru.md`](CAMPAIGN_STATUS_2026-10-20.ru.md)). Исправление gate в скриптах — открытый пункт (см. TSV).

### Прочие открытые (без изменения статуса)

- `DEBT-H-A15b` — не подтверждён на E2 R8, но формально open до отдельного SoftCold-среза.
- `DEBT-A3-trace-hang`, `DEBT-A1-preinh-silent`, `DEBT-G1-432` (полная 432-матрица v1/v2 — этап 5).
- Закрытые: A15 inputs, cpu-gate, disk-200G, disk-freegib-root (разовый offload), matrix-prepare-wave, F1a-offline, F7 confirmed→F2.pref, **G1-exit-gate harness**.

---

## TSV (канон)

```tsv
debt_id	opened_utc	stage_id	source	item_ref	priority	blocker_for	status	owner_arm	notes	closed_utc	fix_run_id
DEBT-A0-ctest	2026-10-20T13:22Z	A0	card	BranchInvalidPeakNoRecovery×2	P2	—	open	—	baseline 85/87		
DEBT-cpu-gate-pgrep	2026-10-20T13:48Z	R2	companion	cpu_gate false positive	P1	D1	done	.11	pattern fixed	2026-10-20T13:48Z	local
DEBT-A15-matrix-inputs	2026-10-20T13:23Z	R2	audit	45 FAIL Test	P0	B2	done	B2	repaired 98ac830d	2026-10-20T14:05Z	98ac830d
DEBT-H-A15b	2026-10-20T13:22Z	R	audit	SoftCold tip1 fan-out	P1	E2	open	E2	E2 R8 EQUIVALENT — не подтверждён на R8; см. E2_R8_SYNTHESIS		
DEBT-CL-N1	2026-10-20T13:22Z	R	audit	Classic N1 stall	P0	G1/SYNTH	open	D1/E2	W02 L0 CLOSED 5308aa5(53)…3cefd64(100); first>=54=3cefd64; D1_BISECT_2026-10-22		
DEBT-G1-432	2026-10-20T13:22Z	E2G1	plan	432 optional full matrix	P2	S5	open	—	canon 24-32 selected for G1		
DEBT-F1a-offline	2026-10-20T15:45Z	S1	card F1a	offline ideal/sweep	P2	S1	done	F1a	C2_MATCH margins	2026-10-20T15:45Z	F1a_20261020
DEBT-F1b	2026-10-20T13:22Z	S1	card F1b	Console NAxoneDelay pilot	P1	Controller v2	open	senior	docs-ready checklist; DEBT-F1b still open; no cold		
DEBT-S0-cpp-fields	2026-10-20T13:56Z	S0	audit	residue/margin/Done_BE C++ emit	P0	G1 rollup/SYNTH	partial	stage0	S0_CPP_EMIT_2026-10-22; sep_margin Train DONE; amp-BE mark still open		
DEBT-CTRL-V2-DRAFT	2026-10-22T12:46Z	S4	docs	Controller DRAFT refresh	P1	SPEC	open	docs	CONTROLLER_V2_DRAFT_INPUTS_2026-10-22; not C++ SPEC		
DEBT-disk-200G	2026-10-20T13:06Z	A0	card/human	DATA≥200G not STOP	P2	—	done	.11	EventsLog→.17 Data	2026-10-20T15:16Z	offload
DEBT-A3-trace-hang	2026-10-20T14:19Z	R2	card	A3 TRACE hang corrupt+repaired	P1	A3	open	A3	kill after stall		
DEBT-C1-silent-soma	2026-10-20T15:20Z	C1	card	soma_0/2 silent set1	P1	physics E1	open	C1	L43/L1 MODEL_MATCH		
DEBT-D2-silent-test	2026-10-20T16:05Z	R2	D2.0/D2.2	W01 converge fires=0 Test hang	P0	SYNTH/G1	partial	D2/E2	H2 weakened: TipR overlay+KeepDone W33 TipR flat Need=1 SKIP; SILENT_TEST_H2_KEEPDONE		
DEBT-17-console-glog	2026-10-22T12:10Z	R2	infra	.17 EmitToGlog stack-smash phase9	P0	H2 TipR/KeepDone	done	.17	glog 0.4 pin; keep on sync; DEBT_17_GLOG_ABI_FIX	2026-10-22T12:55Z	

DEBT-A1-preinh-silent	2026-10-20T15:15Z	R2	card A1	br25_preinh silent fires	P0	G1 labels	open	A1	BASELINE_DEGRADED		
DEBT-F7-rmin-tol-mask	2026-10-20T17:00Z	R3	D2b.1	RminTol×4 masks measured dt	P0	F2 Done_BE	confirmed	F7	F2.pref cold	2026-10-20T17:12Z	F2.pref
DEBT-TRACE-NOCSV	2026-10-20T17:10Z	R2	gate	Test hang no TRACE CSV	P1	silent-Test	open	gate	kill etime>180; rc=-15; linked DEBT-D2		
DEBT-D2b5-W02	2026-10-20T17:15Z	R2	D2b.5	W02 Signed+RminTol not_converged	P0	CL-N1	open	D2b	L0 first>=54=3cefd64 after 5308aa5; phase2 CLOSED		
DEBT-disk-freegib-root	2026-10-20T20:11Z	E2	infra	free_gib root vs DATA	P1	E2 soft-cold	done	.17	lanes offload 2026-10-20	2026-10-20T20:17Z	lanes-offload
DEBT-matrix-prepare-wave	2026-10-20T20:20Z	E2	queue	whole-wave prepare vs stale	P0	E2 R8	done	Bin	case-ids only 774704fc	2026-10-20T20:24Z	774704fc
DEBT-F5-gamma	2026-10-21T08:00Z	R3	F5/A7	CorrectAttenuationGammaForTipR no PASS on W01 N1	P1	F8 chain/R3	open	F5	paired 2026-10-22 γ=0≡γ=1; F5_GAMMA_PAIRED		
DEBT-G1-exit-gate	2026-10-21T16:36Z	G1	infra	run_series launch.exit gate	P0	G1 SYNTH	done	drv	wait_run+run_series propagate; DEBT_G1_EXIT_GATE_FIX_2026-10-22	2026-10-22T06:30Z	harness
DEBT-disk-offload-policy	2026-10-21T05:14Z	E2	ops	root Avail<80G vs DATA free	P1	new cold .17	open	ops	repeat offload; STATUS_SNAPSHOT 2026-10-21T0514; do not kill active G1		
```

---

*Последнее docs-обновление: 2026-10-22 (H2 KeepDone retry T104632Z — H2 weakened TipR-mode; DEBT-17 pin confirmed; DEBT-D2 partial).*
