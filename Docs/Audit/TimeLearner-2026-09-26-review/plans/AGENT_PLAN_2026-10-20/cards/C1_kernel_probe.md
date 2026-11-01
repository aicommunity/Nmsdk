# C1. Импульсные ядра Console и модель кабеля

**Цель:** проверить, совпадает ли офлайн-модель кабеля (`tools/cable_model`) с Console по амплитуде пика, времени пика и ширине (FWHM) одиночного EPSP на соме. Нужна точность 10/5/10% для каждой длины дендрита и каждой модели нейрона. При совпадении модель заменяет большую часть дорогих Console-сеток (этап 1 плана), и на неё можно опирать границы «модель ↔ длина паттерна».
**Уровень:** слабый. **Хост:** `.11`. **Console:** 1 за раз. **Время:** 1–2 ч.
**Зависит от:** A0 (numpy, собранный `cable`), желательно A3.2: при `CPP_KEEPS_XML_LINKS` C1 всё равно корректен, потому что `prepare` сам выставляет отводы.

## Что делает `tl_probe_kernels.py prepare`

Копирует Test-шаблон Classic и делает из него пробный эксперимент без обучения:

- `IsNeedToTrain=0`, `StructureBuildMode=1`, порог `FixedLTZThreshold=100` (нейрон не стреляет), PostTune выключен;
- `DendriteLength` = заданные длины, `NumSynapse=1`, TipR = 8.6e7 на всех кончиках;
- один паттерн из 4 импульсов: первый в 0.5 мс, остальные через `ISI = 2 с` (отклики не перекрываются);
- проводка: ровно один отвод генератора на кончик каждого дендрита (через `repair_model_wiring`);
- включён trace `test_trace.csv`.

`analyze` берёт из trace окно первого импульса, считает пик/время/FWHM на `soma_k` и сравнивает с моделью кабеля при тех же C, Rm, DissociationTC и частоте шага.

## Наборы

| # | Шаблон (Test) | Модель | `--lengths` |
|---|---|---|---|
| 1 | `W02/inputs/W02_CL480_N1_PSIoff/Test` | NSPNeuronGen, τ=10 мс, D=5 мс, 2000 Гц | `51,43,25,1` |
| 2 | то же | то же | `30,20,10,1` |
| 3 | то же | то же | `10,4,2,1` |
| 4 | `W01/inputs/W01_CL50_N0_PSIoff/Test` | AsymRmD001C1e9, τ=10 мс, D=1 мс, 20000 Гц | `25,10,4,1` |
| 5 | то же | то же | `20,15,5,2` |
| 6 | `W46/inputs/W46_HIST_FAST_D002_C2_5E10/Test` | D002C25e11, τ=2.5 мс, D=2 мс, 2000 Гц | `52,25,10,1` |
| 7 | то же | то же | `8,4,2,1` |

## Шаги (для каждого набора N)

```bash
source "$HOME/tl-agent/env.sh"
OUT="$REPORTS/C1_$(date -u +%Y%m%d)_$HOSTTAG"; mkdir -p "$OUT"; W="$DATA/scratch/C1"; mkdir -p "$W"
N=1; TPL="$ST/TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/Test"; LEN="51,43,25,1"     # подставить из таблицы
python3 "$TOOLS/tl_probe_kernels.py" prepare --template "$TPL" --out "$W/p$N" --lengths "$LEN" --isi 2.0 | tee "$OUT/prepare_$N.json"
( cd "$W/p$N" && timeout 2h "$NMSDK/Bin/Platform/Linux/NeuroModelerConsole" -c "$W/p$N/Project.ini" -s -t 8 -x -S > console.log 2>&1; echo "rc=$?" )
python3 "$TOOLS/tl_probe_kernels.py" analyze --probe "$W/p$N" --cable-dir "$CABLE" --json "$OUT/kernel_$N.json" > /dev/null
python3 - "$OUT/kernel_$N.json" <<'PY'
import json,sys; d=json.load(open(sys.argv[1]))
print(d['verdict'], 'tau', d['tau_s'], 'D', d['D_s'], 'f', d['f_hz'], 'onset_warn', d['onset_offset_warning'], 'wiring_after', d['wiring_after_run']['ok'])
for x in d['dendrites']:
    c=x['compare']; print(x['L'], *[f"{k}: meas={c[k]['measured']} pred={c[k]['predicted']} err={c[k]['rel_err']}" for k in ('peak','t_peak_s','fwhm_s')])
PY
```

**Ожидаемо после `prepare`:** JSON с `"wiring_ok": true`, `"missing": []`, код возврата 0. Если печатается `LENGTH_TOO_LONG`, проверь длины по таблице: не больше числа сегментов шаблона.

**Ожидаемо после Console:** `rc=0`, в `$W/p$N` (или подкаталоге) появился `test_trace.csv`.

## Критерии

- `MODEL_MATCH`: для всех 4 дендритов |ошибка| пика ≤ 10%, времени пика ≤ 5%, FWHM ≤ 10%.
- Ориентиры из модели для набора 1: пик ≈ 0.00269 / 0.00293 / 0.00383 / 0.01563 (L = 51/43/25/1, над базой), время пика ≈ 0.489 / 0.413 / 0.242 / 0.0145 с, FWHM ≈ 0.164 / 0.151 / 0.115 / 0.027 с. Это закон δ ≈ τ на сегмент.
- `onset_offset_warning: true` значит, что у trace свой сдвиг времени. Это допустимо, но записать величину `pulse_onset_used_s`.
- `wiring_after_run.ok: false` значит, что Console при сохранении изменил проводку. Записать нарушения.

## Сводка

В `REPORT.md` — таблица: набор × L → ошибки пика/времени/FWHM и вердикт. Общий вывод по каждой модели нейрона:

- все наборы модели — `MODEL_MATCH` → «модель кабеля валидна для <модель>»;
- систематическое расхождение одного знака (например, все пики на 20% выше) → записать коэффициент: это калибровка, а не провал;
- AsymRm (наборы 4–5) расходится, а NSPNeuronGen совпадает → вероятная причина: у AsymRm Rm тормозного канала 1e8, а модель кабеля его не учитывает. Записать для senior.

## СТОП

`NO_TRACE` при `rc=0` для набора 1: значит, trace не включается. Тогда остальные наборы не запускать; приложить `console.log` и `grep -n TraceLog "$W/p1/Model_00.xml"`.
