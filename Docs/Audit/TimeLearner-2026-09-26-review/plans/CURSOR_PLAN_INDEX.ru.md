# Индекс: исходный Cursor-план кампании TimeLearner

**Назначение.** Сохранить в репозитории текст рабочего плана агента из Cursor (`.cursor/plans/…`), чтобы он не потерялся вне git, и явно связать его с аудитом, по которому велась кампания.

## Архивная копия плана

| Поле | Значение |
|------|----------|
| Файл в репозитории | [`CURSOR_PLAN_timelearner_agent_plan_1d9a3d4d.plan.md`](CURSOR_PLAN_timelearner_agent_plan_1d9a3d4d.plan.md) |
| Исходник Cursor (вне git) | `/home/user/.cursor/plans/timelearner_agent_plan_1d9a3d4d.plan.md` |
| Идентификатор | `timelearner_agent_plan_1d9a3d4d` |
| Имя в Cursor | TimeLearner Agent Plan |
| Дата архивации в repo | 2026-10-23 |
| Тело файла | **verbatim** копия на момент архивации (включая YAML `todos` / overview) |

Файл в `.cursor/plans/` может меняться или исчезнуть; **канон для истории кампании — копия в этом каталоге.**

## Связь с исходным аудитом (по чему работали)

План агента — исполняемая / операционная проекция аудита от 20.10.2026, а не замена ему.

| Слой | Путь | Роль |
|------|------|------|
| **Исходный аудит + поэтапный план** | [`../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) | Канон выводов, физики, этапов 0–6; дополнение 23.10 (τ per Span → аксоны) |
| **Исполняемый пакет карточек** | [`AGENT_PLAN_2026-10-20/`](AGENT_PLAN_2026-10-20/) | Команды, ворота, tools/patches для агентов |
| **Cursor-план (эта копия)** | [`CURSOR_PLAN_timelearner_agent_plan_1d9a3d4d.plan.md`](CURSOR_PLAN_timelearner_agent_plan_1d9a3d4d.plan.md) | Граф R→0→E1→F*→G1→Controller, V-gate, overrides, dual-host |
| **Стратегия 23.10** | [`../evidence/STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md`](../evidence/STRATEGY_TAU_PER_SPAN_THEN_AXON_2026-10-23.ru.md) | τ(Cm) per Span (дендрит) → затем F1b как аксонный тренер |
| **Карточка H0** | [`AGENT_PLAN_2026-10-20/cards/H0_tau_cm_per_span.md`](AGENT_PLAN_2026-10-20/cards/H0_tau_cm_per_span.md) | Ближайший дендритный фокус |
| **Карточка F1** | [`AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md`](AGENT_PLAN_2026-10-20/cards/F1_fast_epsp_pilot.md) | F1a done; F1b = фаза A |
| **Оперативный статус** | [`../evidence/CAMPAIGN_STATUS_LATEST.md`](../evidence/CAMPAIGN_STATUS_LATEST.md) | Tip HEAD / open debts |
| **Техдолг** | [`../evidence/TECH_DEBT_TIMELEARNER_2026-10-20.ru.md`](../evidence/TECH_DEBT_TIMELEARNER_2026-10-20.ru.md), [`../evidence/TECH_DEBT.tsv`](../evidence/TECH_DEBT.tsv) | Долги кампании |

В шапке самого Cursor-плана указаны те же первоисточники: аудит `TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`, пакет `AGENT_PLAN_2026-10-20/`, коммиты сверки `c0d19a90` / `ce6fd020`.

## Как читать дальше

1. Аудит (что верно про физику и этапы) →  
2. Cursor-план (как кампания R/V-gate/overrides это исполняла) →  
3. AGENT_PLAN cards (конкретные команды) →  
4. STRATEGY 23.10 + H0 (куда идём после idle: дендрит τ(Cm), потом аксоны F1b).

Не считать YAML `todos` в архивной копии «живым» трекером: актуальный статус — `CAMPAIGN_STATUS_LATEST` + `TECH_DEBT*`; стратегия 23.10 может опережать старые формулировки Cursor-плана про F1b как блокер дендритного Controller.
