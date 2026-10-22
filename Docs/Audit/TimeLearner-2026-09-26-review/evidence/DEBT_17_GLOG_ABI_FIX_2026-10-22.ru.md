# DEBT-17 — glog ABI pin на `.17` (2026-10-22)

**Постановка.** На host `.17` (`10.245.1.17`) Elder-синхронизированный `NeuroModelerConsole` (`sha256` prefix `4a0658f3…`) при phase9 diagnostic / soft-cold Train стабильно падал с `*** stack smashing detected ***` → `SIGABRT` в `RDK::Logging::detail::EmitToGlog()` / `__stack_chk_fail` (`child_rc=-6`, нет `results.csv`). Это блокировало измерение H2 TipR overlay и KeepDone cold (W33), маскируя физику silent-Test под инфраструктурный abort. Цель фикса — восстановить работоспособный loader path для того же бинарника Console **без** локальной пересборки и без затрагивания D1 bisect на `.11`.

---

## Корневая причина

Elder-сборка Console слинкована против **glog 0.4** (`libglog.so.0.4.0`). В `~/tl-agent/lib/` симлинк `libglog.so.0` указывал на системную Ubuntu **0.6** (`/usr/lib/x86_64-linux-gnu/libglog.so.0.6.0`). При `source ~/tl-agent/env.sh` (`LD_LIBRARY_PATH=$HOME/tl-agent/lib:…`) loader подставлял ABI 0.6 в бинарник, собранный под 0.4 → повреждение стека внутри `EmitToGlog`.

Ранние симптомы той же цепочки: H2 TipR overlay `H2.TipROverlay-17-20261022T090300Z` — `rc=127` (glog not found без `env.sh`); `…T090800Z` — все шесть клеток `fires=null`, diagnostic `rc=-6` (smash при glog 0.6 в path). KeepDone W33 (`H2.KeepDone-17-20261022T081725Z-74503`) — тот же класс abort на Train.

---

## Фикс (не откатывать)

1. Скопирован Elder `/usr/lib/x86_64-linux-gnu/libglog.so.0.4.0` → `~/tl-agent/lib/libglog.so.0.4.0`.
2. Симлинк `~/tl-agent/lib/libglog.so.0` → `libglog.so.0.4.0` (предыдущая ссылка на 0.6 сохранена как `libglog.so.0.bak.*`).
3. Заметка: `~/tl-agent/lib/README_glog_pin.txt`; в `~/tl-agent/env.sh` — комментарий DEBT-17 про pin 0.4.
4. При любом sync Console с Elder **сохранять** pin 0.4 в `tl-agent/lib/` (не подменять обратно системным 0.6).

Проверка loader: `ldd NeuroModelerConsole | grep glog` → `/home/user/tl-agent/lib/libglog.so.0` при активном `env.sh`.

---

## Smoke PASS (после pin)

| Поле | Значение |
|------|----------|
| Host | `.17` |
| Console | `~/tl-agent/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole` (`4a0658f3…`) |
| Bundle | frozen `H2.TipROverlay-W01-src` (G1 W01 Classic×N0) |
| Gate | `phase9_preinh_bc_gate.py --skip-tipr-mid --diagnostic-threshold 0.0024126668029073456 --span-ms 50` |
| **fires** | **`01000101`** |
| Stack smash | **нет** |
| GATE_RC | 0 по метрикам CSV; Console после CSV может получить SIGTERM → `gate_rc=-15` (известный TRACE hang, `DEBT-TRACE-NOCSV`) — метрики валидны |

Иерархия smoke: Trainer×Mode **Classic×N0** → Span **50** → NeuronModel **AsymRm** → Mod **gen**. Конфиги: [Train](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Train), [Test](../../../../Bin/Configs/SpikeSamples/StructTrain/TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/Test).

---

## Статус долга

**DEBT-17-console-glog → done** (с оговоркой: pin 0.4 держать при sync). Физика H2 TipR overlay измеряется отдельным retry после pin — [`SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md`](SILENT_TEST_H2_TIPR_OVERLAY_2026-10-22.ru.md). G1 RERUN не запускался.

---

*Docs 2026-10-22; ветка `timelearner_fix2`.*
