# A3. Влияет ли повреждённая проводка на Console и пересвязывает ли C++ отводы

**Цель:** ответить на два вопроса, без которых нельзя решить судьбу 45 входов (B2) и интерпретировать Test:

- **A3.1** Использует ли Console в Test-режиме проводку из XML как есть, или C++ при загрузке (`StructureBuildMode=1`) её перестраивает? Если использует как есть, повреждённые входы дают другие амплитуды на соме.
- **A3.2** Если в Test задать `DendriteLength`, отличный от отводов генератора в `<Links>`, к какому сегменту реально приходит импульс? Gate-скрипт Classic (`phase9_preinh_bc_gate.py`) переносит обученные длины в Test, но не трогает `<Links>`.

**Уровень:** слабый. **Хост:** любой. **Console:** 1 за раз. **Время:** 30–60 мин.
**Зависит от:** A0, A2.

## A3.1 Повреждённый и починенный вход W09_HIST_asym25

```bash
source "$HOME/tl-agent/env.sh"
OUT="$REPORTS/A3_$(date -u +%Y%m%dT%H%MZ)_$HOSTTAG"; mkdir -p "$OUT"; W="$DATA/scratch/A3"; mkdir -p "$W"
SRC="$ST/TimeLearnerMatrix/W09/inputs/W09_HIST_asym25/Test"
sha256sum "$SRC/Model_00.xml"     # ожидаемо 1af1e953efc6b48923ced4b838f2451b5d27843bb752ff3e3c8e13bab79e1ed9
cp -r "$SRC" "$W/corrupt"; cp -r "$SRC" "$W/repaired"
python3 "$TOOLS/repair_model_wiring.py" "$W/repaired/Model_00.xml" "$W/repaired/Model_00.xml" --params "$W/repaired/Parameters_00.xml"
python3 "$TOOLS/check_model_wiring.py" "$W/corrupt/Model_00.xml" "$W/corrupt/Parameters_00.xml" | head -2
python3 "$TOOLS/check_model_wiring.py" "$W/repaired/Model_00.xml" "$W/repaired/Parameters_00.xml"
for v in corrupt repaired; do python3 "$TOOLS/tl_probe_kernels.py" enable-trace --dir "$W/$v"; done
for v in corrupt repaired; do
  sha256sum "$W/$v/Model_00.xml" > "$W/$v/model_before.sha"
  ( cd "$W/$v" && timeout 3h "$NMSDK/Bin/Platform/Linux/NeuroModelerConsole" -c "$W/$v/Project.ini" -s -t 40 -x -S > console.log 2>&1; echo "rc=$?" > console.rc )
  cat "$W/$v/console.rc"; sha256sum "$W/$v/Model_00.xml"
  python3 "$TOOLS/trace_soma_peaks.py" "$W/$v" | tee "$OUT/peaks_$v.txt" | head -12
done
```

**Ожидаемо:**

- `repair` печатает JSON с `renamed_items` > 0, а проверка после починки — `OK`.
- Оба Console: `rc=0`. `test_trace.csv` найден (иначе `NO_TRACE` — СТОП, приложить `console.log`).
- Сравнить в `peaks_*.txt` строки с `target=1` (целевой паттерн), столбцы `soma_0..soma_2`. **Гипотеза A15:** у `corrupt` они в ≥ 3 раза больше, чем у `repaired`, а `soma_3` (дендрит L=1) отличается не более чем на 20%. Модель кабеля для похожего состояния даёт около 0.047 против 0.005 на дендритах 1–3 и 0.011 против 0.011 на 4-м.

Запиши фактическое отношение `corrupt/repaired` для каждого `soma_k` и вердикт:

- `A15_ACTIVE_AT_RUNTIME` — отношение ≥ 3 для k = 0..2;
- `A15_NO_EFFECT` — все отношения в пределах 0.8…1.25, то есть C++ перестраивает связи при загрузке;
- `UNCLEAR` — всё остальное.

Также запиши, изменился ли SHA `Model_00.xml` после запуска (сохраняет ли `-S` модель). Если изменился, прогони `check_model_wiring.py` на сохранённой модели и приложи вывод.

## A3.2 Пересвязывание отводов при смене DendriteLength

Шаблон Classic с чистой проводкой и одним отводом на дендрит: `W02_CL480_N1_PSIoff/Test` (отводы 51/43/25/1). Ставим `DendriteLength = 30,20,10,1`, но `<Links>` не трогаем (`--keep-links`). Одиночный импульс приходит в момент 0.5 мс. Время пика на соме показывает, с какого сегмента реально пришёл сигнал: задержка ≈ τ·L, где τ = 10 мс.

```bash
source "$HOME/tl-agent/env.sh"; W="$DATA/scratch/A3"
python3 "$TOOLS/tl_probe_kernels.py" prepare --template "$ST/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test" \
   --out "$W/relink" --lengths 30,20,10,1 --keep-links --isi 2.0
( cd "$W/relink" && timeout 1h "$NMSDK/Bin/Platform/Linux/NeuroModelerConsole" -c "$W/relink/Project.ini" -s -t 8 -x -S > console.log 2>&1; echo "rc=$?" )
python3 "$TOOLS/tl_probe_kernels.py" analyze --probe "$W/relink" --cable-dir "$CABLE" --json "$OUT/relink.json" > /dev/null
python3 -c "import json;d=json.load(open('$OUT/relink.json'));print(d['relink_verdict'], d['relink_best_taps']); [print(x['L'], x['compare'].get('relink_test')) for x in d['dendrites']]"
```

`prepare` в режиме `--keep-links` нормально завершается с кодом 2 и печатает `wiring_ok: false`: отводы намеренно не совпадают с `DendriteLength`.

**Ожидаемо:** одна из строк:

- `CPP_RELINKS_TO_DENDRITELENGTH [30, 20, 10, 1]` — C++ сам переводит отвод генератора на кончик по `DendriteLength`, и устаревшие `<Links>` безопасны;
- `CPP_KEEPS_XML_LINKS [51, 43, 25, 1]` — C++ берёт отводы из XML. Тогда **каждый Classic Test, где обученные длины отличаются от длин входа, работает не на тех длинах.** Это новый дефект A16, и о нём нужно сразу сообщить человеку;
- `MIXED_OR_UNCLEAR` — приложить `relink.json`.

## Выход

`peaks_corrupt.txt`, `peaks_repaired.txt`, `relink.json`, таблица отношений, вердикты A3.1/A3.2, `REPORT.md`, `result.json`.

## СТОП

Console `rc≠0` или нет trace. Тогда приложить последние 50 строк `console.log`; повторять не нужно.
