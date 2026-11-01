# B1. Исправление источника дефекта A15 в Bin (`repro_cold_lib.py`)

**Цель:** функции `fix_generator_tip_links`, `fix_branch_tip_links` и `rewrite_links_to_tip1` больше не переименовывают `<Item>` связей синапс → канал. Они трогают только `Input`-коннекторы `DatasetMatrix.Generator1` и не оставляют висячих связей.
**Уровень:** слабый. **Хост:** любой. **Console:** 0. **Время:** 20 мин.
**Зависит от:** A0 (ветка `agent/tl-audit-20261020` в Bin).

Важно: `rewrite_links_to_tip1` вызывается из `soft_cold_reset_train`, то есть **в каждом запуске очереди** при SoftCold-сбросе Train. Старая версия после срезания сегментов `>1` переименовывает все `<Item>` синапсов в `_1`. В результате остаются висячие связи на удалённые каналы и дубли; новая версия удаляет висячие связи. Пример W01_CL50_N1_PSIoff/Train после SoftCold: старая версия даёт 429 связей, 576 ссылок на несуществующие сегменты и `synapse_fanout Dendrite1_1.ExcSynapse1 -> 25 channels`; новая — 43 связи, 0 висячих, 0 нарушений. Если C++ висячие связи игнорирует, поведение не изменится. **Гипотеза H-A15b:** при наращивании сегментов (`StructureBuildMode=2`) C++ восстанавливает связи по сохранённым именам, и тогда fan-out становится реальным во время обучения. SoftCold в нынешнем виде введён 27.09, то есть совпадает по времени с регрессией. Но это нужно доказать, поэтому в E2 есть отдельное плечо «B1+E0 при baseline Console». `fix_generator_tip_links` / `fix_branch_tip_links` очередь не вызывает: их вызывают `repro_cold_harness.py` и `phase12_wave3.py`.

## Шаги

```bash
source "$HOME/tl-agent/env.sh"; cd "$NMSDK/Bin"
git rev-parse --abbrev-ref HEAD            # ожидаемо: agent/tl-audit-20261020
git apply --check "$PLAN/patches/bin_A15_link_hygiene.patch" && git apply "$PLAN/patches/bin_A15_link_hygiene.patch"
git status --short
cd "$ST/scripts"
python3 -m unittest tests.test_link_hygiene_unit -v 2>&1 | tail -12
python3 -m unittest tests.test_softcold_fix_unit 2>&1 | tail -3
```

**Ожидаемо:**

- `git status` показывает `M repro_cold_lib.py`, `?? tests/test_link_hygiene_unit.py`, `?? tests/data/a15_clean_classic_model.xml`.
- `test_link_hygiene_unit`: `Ran 6 tests … OK`.
- `test_softcold_fix_unit`: результат такой же, как в A0 (`OK` или `OK (skipped=1)`).

Контроль, что тест действительно ловит дефект (на временной копии, не в репозитории):

```bash
T="$DATA/scratch/B1_neg"; rm -rf "$T"; cp -r "$ST/scripts" "$T"
git -C "$NMSDK/Bin" show HEAD:Configs/SpikeSamples/StructTrain/scripts/repro_cold_lib.py > "$T/repro_cold_lib.py"
( cd "$T" && python3 -m unittest tests.test_link_hygiene_unit 2>&1 | tail -2 )
```

**Ожидаемо:** `FAILED (failures=3)`. Если тесты проходят и со старой версией, это СТОП: тест не работает.

Коммит на локальной ветке (не пушить):

```bash
cd "$NMSDK/Bin"
git add Configs/SpikeSamples/StructTrain/scripts/repro_cold_lib.py \
        Configs/SpikeSamples/StructTrain/scripts/tests/test_link_hygiene_unit.py \
        Configs/SpikeSamples/StructTrain/scripts/tests/data/a15_clean_classic_model.xml
git diff --cached --check && git -c user.name=tl-agent -c user.email=tl-agent@localhost commit -m \
 "fix(structtrain): A15 generator-tap rewrites touch only Generator1 Input links [AGENT_PLAN B1]"
git log -1 --format='%H'
```

## Выход

SHA коммита, вывод тестов (позитивный и негативный), `REPORT.md`, `result.json` (`commit`, `tests_ok`, `negative_control_failures=3`).

## СТОП

`git apply --check` не прошёл: Bin не на `e7509263`+refresh. Приложить `git log -3 --oneline`.
