# Campaign status — latest

**Активный план:** [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../plans/PLAN_2026-10-25_dendrite_limits.md) (+ §H)  
**Ветка:** `plan/2026-10-25-dendrite-limits`  
**Обновлено:** 2026-10-24T16:35Z (проверка 19:05 МСК)

Метрика: `sep_margin` + детекция цели; Done_exact / Done_BE раздельно.

---

## W0 br25_nextseg — честный вердикт (не PASS)

Четыре SoftCold-прогона (3× Elder + 1× M40 ctrl) дали **побитно одинаковые** `results.csv` (md5 `f82febbc…`): SoftCold детерминирован, «×3 повтора» без seed/jitter **не** измеряют устойчивость.

| Критерий плана | Факт | Вердикт |
| --- | --- | --- |
| Детекция цели (target fires, 7 foil silent) | да | **PASS** |
| `sep_margin = (tgt−max_foil)/tgt ≥ 0.10` | `(0.100254−0.099137)/0.100254 ≈ **0.011**` | **FAIL** |
| W0 волна в целом | запас ≪ 0.10; E1.5 FRAGILE согласуется | **W0 PASS не объявляем** |

Train/Test: [`SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Train) · [`…/Test`](../../../../Bin/Configs/SpikeSamples/StructTrain/SelectivityBranch/EXP_br_span25_packA_nextseginh_C1e9/Test).

**Seed/jitter (в полёте на Elder):** 5 SoftCold с TipR tip-каналом × `{0.97…1.02}` **после** `soft_cold_reset_train` (патч архива до reset SoftCold стирает — поэтому post-reset). Логи `w0_br25_nextseg_logs/W0.br25_nextseg.seed*.log`, launcher `tools/w0_br25_seed_jitter_launch.sh`.

---

## R0 replay — FAIL (разобрать до W1)

`R0_SUMMARY`: `ltz_train=0.0115`, `ltz_test=0.0475917`, `rel≈3.14` ≫ 5%.

**Причина:** в золотом пакете HIST уже разные `FixedLTZThreshold` (Train `0.0115` / Test `0.0475917`); скрипт `r0_branch_nextseg_replay.sh` сравнивает их as-is после `IsNeedToTrain=0`, **без** overlay Train→Test. Это не регрессия SoftCold W0, а дефект протокола R0 / расхождение gold LTZ. До интерпретации W1: починить R0 (синхрон FixedLTZ Train→Test перед replay **или** сравнивать SelectivityLog peaks / mid), затем переиграть.

---

## C1 Console dose (M40)

| Проблема 19:05 | Причина | Фикс |
| --- | --- | --- |
| `TypeError: PosixPath` в `one()` / `json.dumps(job)` | `template: Path` в job; фикс meta не покрывал job | `jsonable()` рекурсивно |
| Все 28 × `TIMEOUT 180s` | не зависание: gen Test `-t 40` ≈ **537 с** wall (smoke); 180 с мало, stdout буферизуется до выхода | default `--timeout 900` |

Smoke `psi_k0.0`: rc=0, et≈536.6s, `results.csv` OK → полный C1 relaunch LIMIT=7 timeout=900.

---

## Диск Data

Порог free **5%**; journal-archive (только `*.log`/Audit) на M40 largest-first; Elder через `DATA_OFFLOAD_HOST`. Стоп при free&lt;5% → запись сюда.

---

## Очередь

| Блок | Статус | Note |
| --- | --- | --- |
| W0 baseline ×3+ctrl | **done, not PASS** | det PASS / margin FAIL (~0.011) |
| W0 TipR-jitter ×5 | **running** Elder | post-reset tip ±1…3% |
| R0 | **FAIL** | gold LTZ mismatch; fix protocol before W1 |
| C1 | **relaunched** | after smoke OK |
| genasym (.11) | Test phase / done? | |
| W1 | **blocked** | ждём R0 protocol + W0 margin context |

---

## Ядра

| Host | note |
| --- | --- |
| Elder-1 (8) | keep ≥2; ~5 seed SoftCold |
| M40 (12) | C1 ≤7; idle до relaunch |
