# H0a: рабочая τ(Cm) per Span + StorageClassName (2026-10-23)

Постановка: по канону стратегии 23.10 и таблице аудита «Нужна FWHM / τ мембраны при идеальной задержке» назначить **рабочую** пару (τ, Cm) на каждый класс Span при фиксированном AsymRm Pack A (Exc Rm=1e7 / Inh Rm=1e8), не переписывая legacy UploadClass. Новые классы регистрируются только под именами `…TauH0_S*`; исторические `C25e12` / `C25e11` / `C1e9` остаются эталонами неудачных или чужих-спану конфигураций.

Источник теор. оценок: [`TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md`](../TIMELEARNER_AUDIT_AND_PLAN_2026-10-20.ru.md) § «Что это значит для коротких паттернов»; проверка `cable_model/sweep.py` (пассивный кабель, D=1 мс, MaxL≈100) и `ideal_delay.py` (идеальная задержка).

## Рабочая таблица Span → τ → Cm → StorageClass

| Span | Целевая FWHM (теор.) | τ (рабочая) | Cm (Rm=1e7 Exc) | StorageClassName (gen) | StorageClassName (preinh) | ideal margin (D=1 мс) | cable feasible@MaxL | cable FWHM/span | cable m_oracle |
|------|----------------------|-------------|-----------------|------------------------|---------------------------|----------------------|-------------------|-----------------|----------------|
| 25 мс | ≤ 2 мс | 0.5 мс | 5e-11 | `NSPNeuronGenAsymRmD001C5e11TauH0_S25` | `NSPNeuronGenPreinh2_5AsymRmD001C5e11TauH0_S25` | +7.4% | true | 0.344 | −0.049 |
| 50 мс | ≤ 3 мс | 1.0 мс | 1e-10 | `NSPNeuronGenAsymRmD001C1e10TauH0_S50` | `NSPNeuronGenPreinh2_5AsymRmD001C1e10TauH0_S50` | +11.8% | true | 0.338 | −0.031 |
| 100 мс | ≤ 6.5 мс | 2.5 мс | 2.5e-10 | `NSPNeuronGenAsymRmD001C25e11TauH0_S100` | `NSPNeuronGenPreinh2_5AsymRmD001C25e11TauH0_S100` | +11.5% | true | 0.378 | −0.015 |
| 200 мс | по кривой | 5.0 мс | 5e-10 | `NSPNeuronGenAsymRmD001C5e10TauH0_S200` | `NSPNeuronGenPreinh2_5AsymRmD001C5e10TauH0_S200` | +11.9% | true | 0.375 | −0.036 |
| 480 мс | по кривой | 10 мс | 1e-9 | `NSPNeuronGenAsymRmD001C1e9TauH0_S480` | `NSPNeuronGenPreinh2_5AsymRmD001C1e9TauH0_S480` | +14.6% | true | 0.343 | −0.025 |

Cm = τ/Rm при Rm=1e7. Имена gen/preinh зарегистрированы в `NPulseLibrary::CreateClassSamples` (PulseLib tip после коммита H0a); legacy классы **не** изменялись.

## Legacy-негативы (read-only)

| Конфиг / класс | Span, на котором гоняли | Почему негатив | Evidence |
|----------------|-------------------------|----------------|----------|
| `NSPNeuronGenAsymRmD001C25e12` (τ=0.25 мс) на 25–100 мс без согласованной задержки | W13 ltz*, W37 PACKC | `not_converged_at_stop`; FWHM/span пассивного кабеля и EstDelay не согласованы | F1A_OFFLINE, F1B_EXPLAINER |
| Единая τ≈10 мс (`C1e9`) на коротком спане как «универсал» | HIST packA на 25/50 при ожидании быстрой EPSP | mid-pattern / ранняя корона без H0-подбора | MembraneParamsHistory, DIAG_LAST_PULSE |
| A15-повреждённые снимки до порта | W01/W05/… | fan-out tip→все сегменты | A15_PORT evidence |

## Вывод H0a

Рабочие τ per Span зафиксированы теорией идеальной задержки (положительный запас 7–15%) и проверены на `cable_model`: при MaxL≈100 пассивный кабель **достижим по синхронизации L** (`feasible=true`), но oracle-margin остаётся слегка отрицательным (FWHM/span≈0.34) — это ожидаемый потолок чисто дендритного носителя без аксонной задержки и без нелинейных mods. Следующий шаг H0b измеряет, закрывают ли Classic/Branch × N0/N1 × gen/preinh/nextseg × PostTune этот зазор на новых Storage-классах.

Машиночитаемая копия: [`H0A_TAU_CM_TABLE_2026-10-23.tsv`](H0A_TAU_CM_TABLE_2026-10-23.tsv).
EXP-манифест: `Bin/Configs/SpikeSamples/StructTrain/SelectivityTauCm/H0_EXP_MANIFEST.json`.
