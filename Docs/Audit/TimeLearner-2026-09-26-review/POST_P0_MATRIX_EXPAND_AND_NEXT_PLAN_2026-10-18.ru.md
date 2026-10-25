# Post-P0: расширение матрицы и план дальше

> **Superseded** рабочим планом: [POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md](POST_P0_SYNTHESIS_AND_NEXT_CYCLE_2026-10-19.ru.md) (2026-10-19). Ниже — исторический срез GATE.

Дата: 2026-10-19 (GATE закрыт: M0 + PASS×3 + preinh).  
PulseLib: `20c3e22` (D7+D2). Console `.17` d2v4 `6f6624ab`.

## 1. Что завершено

| Track | Run | Итог |
|---|---|---|
| PASS regress | `tl-m1-pass-regress-d2v4-17-20261018-21-57` | **3/3 PASS** fires=`10000000` |
| D2 preinh | `tl-m1-d2v4-preinh-17-20261018-21-36` | **Need=0**, L=`[16,13,3,1]`; C++ **silence** |
| M0 D7 | `tl-m0-d7-20261018-20-27` | **DONE** `not_converged_at_stop` Need=1; L=`[81,97,89,1]` N=`[12,12,128,1]` sync=`[0,1,1,1]` peak=`[0,1,1,1]` D7_bad=**0** (класс **D6 pulse0**) |

## 2. Расширение «успешных» кейсов

### C++ PASS (fires=`10000000`, detected) — остров **не расширился числом**, но **укрепился**

| До dualtrack 11-36 | После роста-фикса / P0 | После Post-P0 (D2/D7) |
|---|---|---|
| hist seed nextseg@25 | + nextseg@25 cold PASS (короче L) | **удержан** regress |
| — | + preinh@50 PASS | **удержан** |
| — | + preinh@100 PASS (M1-ext) | **удержан** |

Итого стабильный **PASS×3**: `br25_nextseg`, `br50_preinh`, `br100_preinh`. Регресс d2v4 подтвердил, что D7/D2 **не ломают** остров.

### Train Need=0 (сходимость без C++ PASS) — **расширение**

| Case | Было | Стало |
|---|---|---|
| `br25_preinh` | refuse@3 → Incomplete L-thrash | **Need=0** + full sync (D2) |
| `br25_gen` | Need=0 + silence | без изменений (D3) |

Класс «train OK / Test silence» вырос: **gen@25 + preinh@25**. Это не PASS-остров, но снимает блокер обучения на preinh@25.

### Incomplete / открытые границы — без прогресса кодом

| Case | Класс | Статус |
|---|---|---|
| nextseg@50/100 | D6 peak-blind | evidence only |
| M0 pulse0 | D6 peak-blind (не D7) | **подтверждён** финалом |
| gen/preinh@25 Test | D3 mid/PostTune | evidence; общий рычаг mid |

### Сжатая оценка расширения

- **PASS-матрица (C++ selective):** ширина **3 кейса**, глубина доказана повторным regress на новом SHA — **качественное** расширение (регрессионная устойчивость), не количественное.
- **Сходимость Train:** +1 кейс (`br25_preinh` Need=0) — **количественное** расширение «обучаемого» острова @25 мс (nextseg/gen/preinh все Need=0).
- **Качество @25 preinh/gen:** оба silence → следующий рычаг **один** (D3), не growth.

```
@25ms Branch HIST после Post-P0:
  nextseg  → PASS
  preinh   → Need=0 + silence   (было Incomplete)
  gen      → Need=0 + silence
@50/100:
  preinh   → PASS
  nextseg  → Incomplete D6
```

## 3. План дальнейших экспериментов и доработок

### Приоритет A — качество после Need=0 (D3)

**Цель:** хотя бы один из `{br25_gen, br25_preinh}` → C++ PASS или `target_detected`.

1. Сравнительная трасса TipR final / train_mid / cpp_mid / CanonRmin для gen vs nextseg PASS (один span 25 мс).
2. Гипотезы (по одной, cold after each): PostTune off / keep TipR; mid margin; не трогать L/N.
3. Unit: не обязателен до гипотезы с числовым порогом.

### Приоритет B — D6 nextseg@50 (peak-blind)

**Цель:** PeakSeen≠0 на soft-cold tip-1 @50; затем рост L.

1. Audit-инструментация: PeakLock window vs NextSeg-inh mute (без смены PartsVec/мембраны).
2. Сопоставить measure path @25 PASS vs @50 Incomplete на одном SHA.
3. Точечный фикс только после доказательства окна/inh.

### Приоритет C — M0 Mode=0 ✅ классификация

1. ~~`matrix_result`~~ — получен: Need=1, D7_bad=0, peak0=0.
2. **Следующий шаг:** diagnostic PeakSeen[0]=0 при synced 1..2 / L0=81 N0=12 (общий класс с D6 nextseg@50, но другая фаза reverse-train).
3. Полную W04 480-матрицу не запускать, пока нет гипотезы по pulse0 peak.

### Приоритет D — расширение PASS-оси (только после A или явного PASS на silence)

1. `br50_gen` / margin-half — только если D3 снят на @25.
2. Classic W01 — точечный Need0+silent контроль при смене SHA, не основная ось.
3. Полная матрица 312 — **вне скоупа**.

### Параллель / изоляция (как сейчас)

- `.11` ≤8 Console, `.17` ≤12; отдельный `TIMELEARNER_MATRIX_RUNS_ROOT` на кампанию.
- A и B можно параллелить на разных хостах после фикса M0/poll.

## 4. Критерии следующего цикла

- D3: ≥1 кейс из silence-пары → C++ detected **или** документированный предел mid (не игнор).
- D6: evidence с трассой PeakLock/inh **или** PeakSeen@50 ≠ all0.
- M0: ✅ `matrix_result` без D7-deadlock; вердикт = **peak-blind pulse0**, не Need=0.
- PASS×3 regress зелёный на том же SHA, что фикс D3/D6.

## 5. Автопроверка — остановлена

Скрипт: `/home/user/TimeLearnerAudit-20261017/dualtrack/check_postp0_status.sh`  
GATE выполнен: M0 + PASS×3 + D2 preinh. Loop остановлен после `ALL_EXPERIMENTS_DONE=1`.
