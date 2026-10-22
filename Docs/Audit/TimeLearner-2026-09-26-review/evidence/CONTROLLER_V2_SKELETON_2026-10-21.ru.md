# Controller v2 — каркас спецификации (этап 4/6)

**Статус:** **DRAFT** — черновик для согласования. G1 S1 RERUN закрыт с **3/13** exit-clean; опора для порогов v2 — PARTIAL метрики ([`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md), [`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md)), не drv-only SERIES_DONE. Обогащение входов 2026-10-22 (E1 библиотеки, H1–H4, D1 bounds, F1b checklist, open decisions) — sibling [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md). Не является заданием на реализацию в C++ и не заменяет [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) §«Этап 4».

**Канон этапа:** один общий контроллер для Classic и Branch за флагом `ControllerVersion=2`, стратегия топологии вместо двух независимых копий тренера.

---

## 1. Цели (зачем v2)

Текущее ядро v1 смешивает в одной пачке калибровку mid, оценку задержки, шаг по длине и решение о Done; это даёт ложные exact Done (F7/RminTol), «сходимость» при silent Test и неустойчивый запас 2–6% на границе разделимости. Этап 4 должен разделить физически достижимую цель \(A^\*\) (минимум по входам) от локального пика на коротком L, явно отработать `infeasible_len` при MaxL и согласовать порядок входов Branch с той же машиной состояний, что у Classic.

**Ворота этапа 4 (из аудита, без ослабления):** в области, которую офлайн-предсказатель (C2/F1a) считает допустимой, доля exact Done ≥ 90%, среднее число пачек до Done не хуже v1, запас не ниже предсказанного минус 2 п.п.

---

## 2. Входы из завершённых или частично закрытых веток плана

### 2.1 C2 — офлайн-таблица «модель × span»

Источник: карточка [`C2_sync_table.md`](../plans/AGENT_PLAN_2026-10-20/cards/C2_sync_table.md), ожидания [`C2_expected_sweep.jsonl`](../plans/AGENT_PLAN_2026-10-20/cards/data/C2_expected_sweep.jsonl).

C2 задаёт для каждой пары (τ, span) длины синхронизации `L`, поля `m_equal` / `m_ampnorm` / `m_oracle`, флаг `feasible=false` при L > MaxL и эталон `ideal_delay` (узкий EPSP + задержка без дисперсии). Для v2 это **библиотека стартовых точек** для bracketed-поиска L\* и верхняя граница ожидаемого запаса на G1-матрице ([`G1_predictions_2026-10-21.tsv`](G1_predictions_2026-10-21.tsv)).

### 2.2 G1 — сокращённая матрица границ (PARTIAL после RERUN)

Источник: [`G1_READY_2026-10-21.ru.md`](G1_READY_2026-10-21.ru.md), [`G1_selected_2026-10-21.tsv`](G1_selected_2026-10-21.tsv), exit [`G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md`](G1_S1_RERUN_EXIT_STATUS_2026-10-22.ru.md), метрики [`G1_S1_PARTIAL_METRICS_2026-10-22.ru.md`](G1_S1_PARTIAL_METRICS_2026-10-22.ru.md).

G1 даёт эмпирическую карту Trainer×Mode×Span×NeuronModel×Mod на **v1** (arm S1). Числовые пороги v2 пока опираются только на **exit-clean** подмножество (W01/W13/W33) плюс `failure_class` для остальных; silent 7/8 без цели на clean-волнах — обязательный вход в detection/mid, не в «уже зелёную» матрицу.

### 2.3 E2 — A/B R8 (S0/S1/S2)

Источник: [`E2_R8_SYNTHESIS_2026-10-21.ru.md`](E2_R8_SYNTHESIS_2026-10-21.ru.md), [`E2_matrix_2026-10-21.tsv`](E2_matrix_2026-10-21.tsv).

E2 показал **EQUIVALENT** всех пар S0↔S1 и S1↔S2 на R8: патчи B1/E0 и флаги E1 (defaults) не меняют категории train/L/fires. Для v2 это означает, что регрессии обучения на HEAD не объясняются проводкой SoftCold (H-A15b) на этом срезе; системный **Classic×N1 stall** ([`CL-N1`](CLASSIC_BOUNDARY_MAP_2026-10-19.ru.md)) и **silent Test** остаются дефектами алгоритма/оценки, а не инфраструктуры E2.

### 2.4 Смежные пилоты (не блокируют каркас, но питают этап 6)

- **F1a** (закрыт): офлайн-подтверждение, что пассивный кабель не даёт oracle-margin > 0; [`F1a`-отчёт в TECH_DEBT](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md).
- **F1b** (OPEN, senior): Console-пилот `NAxoneDelay` — прототип «тонкой задержки» (п. 3 этапа 4); карточка [`F1_fast_epsp_pilot.md`](../plans/AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md) §F1b + docs-ready checklist; **`DEBT-F1b` still open**.
- **E1.0 / E1.1 / E1.1b** (PARTIAL): δ≈9.5–10 мс/сег, Gen amp×1.067, AsymRm oracle, N sat≳16 — см. DRAFT inputs §1.

---

## 3. Машина состояний v2 (скелет, без API)

Для **каждого входа** (Branch — в обратном порядке относительно v1, если сохраняется текущая семантика):

| Шаг | Состояние | Действие | Выход / переход |
|-----|-----------|----------|-----------------|
| 1 | `LEN_SEARCH` | Bracketed integer search L\* по **измеренной** задержке; старт из C2/E1.1 | `L*` или `infeasible_len` |
| 2 | `AMP_ALIGN` | При фиксированном L\* — бисекция/секущие по log Rs (N0: по N); цель \(A^\* = \min_k A_{\max}(k)\) | Rs/N на входе |
| 3 | `FINE_DELAY` | Остаток dt после L\* — Rs в пределах amp-tol **или** аксонная задержка (F1b) | residual_dt |
| 4 | `VERIFY` | Verify-проход со всеми входами; foil ≠ Test (отложено Stage0) | pass / один повтор цикла |
| 5 | `MID_CALIB` | Mid на калибровочных foil со смещением к цели (напр. 0.75·gap), **без** CanonRmin | threshold |

**Отличия от v1 (намеренные):** measured delay — источник истины для Done (F2); RminTol не маскирует exact Done (F7 → только `Done_BE`); пол Rmin из XML/устойчивости (F6), без midband→Rmin скачка.

---

## 4. Конфигурация и совместимость

- Флаг: `ControllerVersion=2` (XML Train + fingerprint очереди).
- Classic и Branch: **одна** реализация + стратегия топологии (разветвление только там, где семантика входов различается).
- PostTune: вне scope этапа 4; пары ON/OFF по-прежнему только `--force-posttrain-tuning` (скилл structtrain-experiments).
- Отчётность прогона: сходимость (exact / `Done_BE` / Need=1), residue, margin, fires, Acc — поля Stage0 ([`V_S0_UPDATE_2026-10-20.ru.md`](V_S0_UPDATE_2026-10-20.ru.md)); C++ emit residue/`amp_be`/`done_be`/`sep_margin` готов; **`DEBT-S0-cpp-fields` = done**.

---

## 5. Открытые вопросы (DRAFT — решать после G1 exit-clean)

1. **N0 для span > 50 мс:** если C2/E1.4 подтверждают T_max ≈ 41 мс, нужен ли чистый N0 или только N1 + задержки (этап 6)?
2. **Связь F5 (γ по TipR)** с шагом `AMP_ALIGN`: фиксированная γ из E1.1 vs online-коррекция — влияет на L\* или только на Rs?
3. **Reset перед пачкой (F3)** и E1.3 релаксация: детерминированный Reset обязателен в v2 или опциональный режим с паузой?
4. **Verify vs реальный Test:** пока Test silent ([`DEBT-D2-silent-test`](TECH_DEBT_TIMELEARNER_2026-10-20.ru.md)), критерий «VERIFY pass» не может быть единственным gate качества.
5. **F1b → v2:** если Console-пилот подтверждает margin ≥ модели, переносится ли `NAxoneDelay` в train loop или только в финальный verify?
6. **480 мс:** запускать только если G1+C2 согласованы; иначе — аксонные задержки (этап 6 аудита).
7. **Test mid policy (H3, 2026-10-22):** при NonSeparable / `candidate_mid` finite **не** оставлять `FixedLTZ=1` как единственный классификатор Test — иначе silent Acc 7/8 маскирует foil fires ([`SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md`](SILENT_TEST_OFFLINE_MID_SWEEP_2026-10-22.ru.md)). Решение v2: явный Verify vs Test threshold contract (best-effort mid / refuse silent-as-PASS).
8. **sep_margin / TipR (H4, 2026-10-22):** flat CanonRmin на Classic×N0 W01 кладёт Pack A LTZ в полосу ~2–3×10⁻³ с target&lt;candidate_mid; E1.1b γ(L)≈const → равномерный TipR не чинит gap — Verify должен смотреть ranking/margin, а AMP_ALIGN — дифференциальный Rs/N ([`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md), [`CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md`](CONTROLLER_V2_H3_H4_NOTE_2026-10-22.ru.md)).
9. **Явные решения до SPEC** (полный список — [`CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md`](CONTROLLER_V2_DRAFT_INPUTS_2026-10-22.ru.md) §4): когда включать `candidate_mid` на Test; TipR KeepDone vs CanonRmin (H2 **ослаблена**, `DEBT-17` **done**); Train emit `sep_margin` (**DONE**, emit path закрыт — остаётся tol в SPEC).

---

## 6. Зависимости и запреты до G1

- **Не** объявлять v2 реализованным по результатам E2/F* alone.
- **Не** менять алгоритм v1 в mainline без R8 A/B на каждый флаг (правила AGENT_PLAN `00_RULES.md`).
- **Не** писать `SYNTHESIS_FINAL` по полной 13-волновой матрице, пока большинство волн без `launch.exit=0`; PARTIAL уже опубликован ([`SYNTHESIS_PARTIAL_2026-10-22.ru.md`](SYNTHESIS_PARTIAL_2026-10-22.ru.md), политика [`G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md`](G1_S1_EXIT_POLICY_PARTIAL_2026-10-22.ru.md)).

---

## 7. Следующие документы (после G1)

| Артефакт | Содержание |
|----------|------------|
| `CONTROLLER_V2_SPEC_*.ru.md` | Замена DRAFT: числовые tol, порядок Branch, псевдокод, миграция v1→v2 |
| `SYNTHESIS_FINAL_*.ru.md` | Сводка Trainer×Mode → Span → NeuronModel → Mod с Train/Test ссылками |
| R8-план v2 | Отдельный commit + 12 серий по аналогии E2 |

См. также черновой оглавление: [`SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md`](SYNTHESIS_DRAFT_OUTLINE_2026-10-21.ru.md).
