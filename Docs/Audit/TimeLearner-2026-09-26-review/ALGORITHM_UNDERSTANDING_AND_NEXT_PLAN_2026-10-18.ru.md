# Понимание алгоритмов обучения и план после dualtrack `11-36`

Дата: 2026-10-18. Срезы: PulseLib `2f22c26`, Console `0b25d88f…`.  
Прогоны: M1 `tl-m1-25ms-full-20261018-11-36`, M0 `tl-m0-c-w04-86m-fix-20261018-11-36`.

## 1. Как сейчас работает Branch TimeLearner (сжатая модель)

Обратный порядок пульсов (якорь N−1 → … → 0). На активном пульсе:

1. **Длина (L)** — подгонка delay по `Dissync` / `DendLastAbsDt` (`ChangeDendriteStatus`).
2. После structural ±1 — **scoped invalidate** sync только для пульсов `≤ edited`; якорь и более поздние остаются synced.
3. **Синапсы (N)** — если время не сходится / amp низкая, растёт `NumSynapse` до cap **128**.
4. **TipR (Mode=1)** — параметрическая нормализация амплитуды после/параллельно структуре.
5. **Sync commit** требует PeakSeen + свежий length_ok (не stale Dissync после reopen).
6. **NoImprove** после реальных length-apply: best-effort stop (теперь streak не сбрасывается на scoped edit).
7. **InvalidPeakNoRecovery** — refuse, если много burst’ов с peak, но без полезного действия (не пустые окна).

PostTune TipR CanonRmin — отдельная фаза после Need=0; C++ Test калибрует mid. Train-candidate mid ≠ C++ Test mid (часто fire-all / silence vs selective).

## 2. Что подтвердили прогоны `11-36`

### M1 (Mode=1, W10 hist @25 + br50_preinh)

| Case | Train | C++ Test | Вывод |
|---|---|---|---|
| br25_nextseg | Need=0, L=`[7,6,4,1]` | **PASS** `10000000` | Рост-фикс восстановил остров; структура короче seed `[9,8,5,1]` |
| br50_preinh | Need=0, L=`[15,12,6,1]` | **PASS** `10000000` | Раньше silence — теперь PASS |
| br25_gen | Need=0, L=`[7,6,4,1]` | silence / train-mid fire-all | Структура ок, **амплитудный/порога разрыв** |
| br25_preinh | refuse@3 phase=5 | — | Pulse0: InvalidPeak при TipR↓ и L-скачке 9→16 |

### M0 (Mode=0 structural N0, Step 86 МОм)

- Контрактный thrash **устранён**.
- Успели закрыть pulse2 и pulse1 (N=128), начать pulse0 (L=49, N=86).
- Останов: **poll ceiling / SIGTERM**, Need=1, не algorithmic refuse.
- TipR flat `86e6` — амплитуда на активном пульсе часто ~1e-7 во время +N.

## 3. Рабочая картина дефектов (приоритет)

| ID | Симптом | Класс | Гипотеза |
|---|---|---|---|
| D1 | M0: часы на N→128 при amp≈0 | предел/политика | +N без раннего best-effort / без TipR на Mode=0; cap 128 слишком дорог |
| D2 | br25_preinh refuse@3 на pulse0 | баг/политика InvalidPeak | TipR уходит в ~3e6, peak есть, length/synapse «no action» → счётчик refuse |
| D3 | br25_gen C++ silence при Train sync | PostTune / amp / mid | Train mid завышен (fire-all), C++ mid занижен (silence) — margin нет |
| D4 | nextseg L короче исторической | поведение | Допустимо при PASS; проверить запас по delay/foil |
| D5 | M0 wall budget | ops | 401 polls ×30 s мало для полного N0×3 пульса |

## 4. План исследований и исправлений

### P0 — закрыть понятные алгоритмические дыры (код + unit)

1. **Amp-collapse → early best-effort на Mode=0**  
   Если `peak_amp << initial` и `N` растёт без улучшения `|dt|` / без Peak usable — принимать best-effort sync раньше cap (связка с уже существующим amp-collapse accept).  
   Тест: harness с collapsing amp + rising N → DendBestEffortSynced без N=128.

2. **InvalidPeak / TipR взаимодействие (D2)**  
   Трассировать br25_preinh audit iter 20–24: почему length_status/synapse_status=0 при peak_seen=1 и падающем TipR.  
   Кандидаты: не считать InvalidPeak, пока TipR ещё двигается; или запретить L-jump без fresh delay estimate.

3. **Не ±N при amp≈0 после PeakSeen gate**  
   Убедиться, что gate не обходится веткой «ниже Initial» на субпороге (регресс M0 amp1≈1e-7 при N↑).

### P1 — качество Mode=1 (селекция)

4. **br25_gen silence** — сравнить tipr_final, mid Train vs C++ Test, soma amp target/foil; гипотеза PostTune CanonRmin vs mid calibration.  
5. **Повтор br25_preinh** после фикса D2; при PASS — расширить ось dt (50/100) только для стабильных модификаций.

### P2 — M0 доказательство Need=0

6. Повторить W04 Step86M с **увеличенным poll/wall budget** *или* после P0 early-stop — цель: Need=0 или честный refuse, не SIGTERM.  
7. Опционально: diagnostic overlay Mode=1 TipR на том же Step86M (не смешивать с каноническим N0 row без пометки).

### P3 — карта границ (только после P1)

8. Соседи nextseg PASS: br50/100 nextseg, margin half; не трогать полную матрицу, пока D2/D3 открыты.

## 5. Порядок работ (рекомендуемый)

```
P0.1 amp-collapse best-effort (Mode=0)  → unit
P0.2 InvalidPeak×TipR (br25_preinh)     → unit + cold rerun
P0.3 gate ±N при мёртвой amp            → unit
P1   br25_gen mid/TipR разбор           → 1 cold
P2   M0 rerun с budget/early-stop       → 1 cold
P3   расширение оси dt                  → queue
```

## 6. Критерии успеха ближайшего цикла

- br25_preinh: Train без refuse@3 **или** явная документированная причина refuse ≠ ложный InvalidPeak.  
- br25_gen: C++ Test не silence при Need=0 (хотя бы target_detected).  
- M0 Step86M: завершение с Need=0 **или** стабильный synced=`[1,1,1,1]` без poll-kill; thrash не возвращается.

## 7. Ссылки на evidence

- `evidence/M1_BOUNDARY_MAP_2026-10-17.ru.md` — финал M1 `11-36`  
- `evidence/M0C_W04_CURRENT_REPEAT_2026-10-17.ru.md` — финал M0 `11-36`  
- Runs: `/home/user/TimeLearnerAudit-20261017/dualtrack/runs/tl-*-11-36/`
