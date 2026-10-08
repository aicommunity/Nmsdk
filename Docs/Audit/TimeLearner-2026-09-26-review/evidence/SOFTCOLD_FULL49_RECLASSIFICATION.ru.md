# Повторная классификация SoftCold full49 и threshold sweep `br25_on`

Дата: 2026-10-08. Это продолжение [повторной диагностической проверки](REPEAT_CHECK_RESULT.ru.md). Полный full49 повторно не запускался.

## Источники и проверка происхождения

Для 49 строк из удалённого `_repro/SOFTCOLD_HEAD_rcs.txt` сопоставлен последний run bundle на момент записи строки RCS с `root_git=76acde3ae9a1b0c852a70a771c2ee7de14af00ed`. Все **49/49** имеют подходящий `provenance.json` и существующий `work_root`. Финальные `Need` взяты из сохранённого `Train/Parameters_00.xml`; статус PostTune — из `Train/posttune_complete.flag`; наличие результата Test — из сохранённого Test CSV и provenance. На исходной `/home/user/Nmsdk` проведено только чтение; архивы не копировались и не удалялись.

| Компонент full49 | Значение |
|---|---|
| Console SHA-256 | `18f0ef414b1f9c064121f018884b6d8a6589805c369b359272cb7fe3f5881adc` |
| PulseLib | `dc2866af4d75e42c72f240221d79d1b5bd8b090e` |
| Bin | `5bea3b3f56c4653aa48ccbbe8f83cbc06460eafb` |
| RCS | `/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/_repro/SOFTCOLD_HEAD_rcs.txt` |
| Runs | `/home/user/Nmsdk/Bin/Configs/SpikeSamples/StructTrain/_repro/runs/` |

## Что означают 36 FAIL

| Состояние | Bucket / случаи | Доказанные наблюдения | Классификация и решение |
|---|---|---|---|
| **26 не завершили обучение в данном бюджете** | D (20): `phase6_thr_only`, `pa00_baseline`, `pa01_ltz_sweep`, `pa02_ltzone_avg`, `pa06_ltzone_int`, `psi01_050`, `psi14_260`, `psi15_270`, `psi21_100`, `psi31_200`, `psi32_300`, `psi33_300`, `psi34_400`, `psi35_400`, `ltz100_preinh`, `ltz50_preinh`, `phase6_ltzcal_twin`, `phase6_preinh250`, `tn_classic`, `phase6_480`; B (4): `br480_nextseg`, `br480_preinh`, `br480_tiprmin`, `ltz25_preinh`; A (2): `br100_nextseg`, `br50_nextseg` | Во всех 26 финальное `Need=1`; `Train/posttune_complete.flag` отсутствует; PostTune и Test не достигнуты. Сохранённые длины и TipR различаются, но в части D/Phase6 видны TipR у `Rmax` и продолжающееся изменение длин. | **Не сошлось за ограниченный бюджет.** Это не доказывает невозможность решения и не локализует ошибку реализации. Не менять алгоритм по одним конечным параметрам; долгий прогон оставить отдельным решением, а не повторять матрицу. |
| **8 сошлись, но CanonRmin quality/detection не прошли** | E (6): `asym100_gen`, `fs100_gen`, `fs50_preinh`, `ltz100_gen`, `ltz25_gen`, `br25_preinh`; N (1): `br25_on`; A (1): `asym25` | Финальное `Need=0`, `PostTuneResult=2` (`NonSeparable`), стандартный Test gate `rc=1`, Test CSV отсутствует (`fires_missing`). Для части строк gap положителен, но `landscape_ok=0`; одного gap недостаточно для PASS. | **Обучение завершилось, CanonRmin-модель не прошла quality/detection gate.** Причина «ошибка реализации или ограничение алгоритма» для каждого случая ещё не доказана. Не ослаблять quality gate. |
| **1 отдельный Keep-протокол** | G Keep: `br100_keep` | `Need=0`, `PostTuneResult=2`, Test gate `rc=1`, Test CSV отсутствует. | **Keep quality/detection FAIL**; не объединять с CanonRmin Cold и Search. Причина не доказана. |
| **1 отдельный Search-протокол** | G Search: `br100_search` | `Need=0`, `PostTuneResult=2`, но итоговый статус `search_diff_after_revert...`; C++ mid отсутствует, Test CSV нет. | **Сбой критерия Search/revert**, не стандартное измерение детекции Cold-модели. Держать отдельно до отдельной проверки Search. |

Итого: **26 budget-limited incomplete + 8 CanonRmin quality/detection FAIL + 1 Keep FAIL + 1 Search/revert protocol FAIL = 36**. Keep/Search остаются отдельными от CanonRmin Cold. Это подтверждает предложенное разделение «не сошлось за данный бюджет» и «сошлось, но качество/детекция не прошли». Ни одна из категорий сама по себе не означает математическую невозможность обучить другую модель.

## PASS-контроли и граница протоколов

12 обычных PASS с `Need=0`, успешным gate и Test CSV: `asym50_preinh`, `asym25_preinh`, `asym50`, `fs25_gen`, `br50_gen`, `br100_preinh`, `br25_nextseg`, `br50_preinh`, `fs100_preinh`, `asym100_preinh`, `fs25_preinh`, `ltz50_gen`.

Тринадцатый PASS — `br25_off`, отдельный режим **SoftColdOff**. Он не является дополнительным подтверждением SoftCold Cold-обучения. Среди 12 обычных PASS C++ PostTune также записал `result=2` на тренировочной метрике; Test gate при этом прошёл. Значит, `PostTuneResult=NonSeparable` нужно отчитывать отдельно от детекции на Test, а не автоматически трактовать как отсутствие полезной модели.

## Исследование порога для `br25_on`

На изолированном checkout `/home/user/Nmsdk_timelearner_audit_20261008` клонирован уже обученный `Test` из `br25_on_20261008T072517Z_934477_e878e970_work`. На каждой копии менялся только фиксированный LTZ threshold; обучение и PostTune выключены. Восемь независимых Console-процессов работали параллельно около 180 секунд, каждый записал все 8 строк Test CSV. Намеренное завершение процессов после получения 8 строк дало `rc=-15`; CSV целые, метрики обработаны успешно. Изменений trainer weights/Train не было.

| LTZ threshold | Fires | Target hit | Ложные срабатывания на 7 foil | Acc | Результат |
|---:|:---:|:---:|---:|---:|---|
| 0.1070 | `11111101` | да | 6 | 2/8 | target + много foil |
| 0.1075 | `11111100` | да | 5 | 3/8 | target + много foil |
| 0.1080 | `11110100` | да | 4 | 4/8 | target + 4 foil |
| 0.1083 | `11110000` | да | 3 | 5/8 | target + 3 foil |
| 0.1086 | `11110000` | да | 3 | 5/8 | target + 3 foil |
| 0.1089 | `00110000` | **нет** | 2 | 5/8 | target пропущен, 2 foil firing |
| 0.1092 | `00000000` | **нет** | 0 | 7/8 | тишина, target пропущен |
| 0.1095 | `00000000` | **нет** | 0 | 7/8 | тишина, target пропущен |

Ни одна из восьми точек не дала ожидаемую маску `10000000`. На 0.1083–0.1086 legacy-поле `ok=1`, но остаются 3 ложных срабатывания, `ok_strict=0` и `ok_audit=0`; считать это PASS нельзя. При повышении порога до 0.1089 цель уже не детектируется, хотя два foil ещё firing. Выборка не является исчерпывающим доказательством для всех непрерывных порогов, но показывает, что простая подкрутка threshold на этой готовой модели не устранила недостаточное разделение.

Это **ограничение разделения для данного результата обучения и набора из 8 тестов**, а не доказательство невозможности обучения/разделения другими весами. Предыдущая Python-mid проба `br25_on` тоже давала `11110000` (5/8 и 3 false alarms); новый sweep подтверждает, что это компромисс качества, а не приемлемая детекция.

### Артефакты порогового sweep

| Поле | Значение |
|---|---|
| Output | `/home/user/Nmsdk_timelearner_audit_20261008/Bin/Configs/SpikeSamples/StructTrain/_repro/runs/br25_on_threshold_grid_20261008T082655Z/` |
| Console SHA-256 | `6157579ddfca1918be340ccd25d2b3f7c20614118ca136026636bbaf550b70f8` |
| `results.json` SHA-256 | `a62c7d8074c62a70963cad9252e8c2ffcc2b498e8065c95e3d9a1df3a9b7b5d7` |
| `manifest.json` SHA-256 | `91e135abce01af8cf5f66db9495ad222b4ad188d0bb9e04e7640637467a3387f` |
| Orchestrator SHA-256 во время запуска | `322459ea1ea24e7366dc68d1c564fc75fb7843c63c55ef73a08167bafbc826c3` |
| Committed orchestrator SHA-256 | `2fb7d33cbffebb1610b2b075676157c20a783b53cba77688443e25a037fbf576` |
| Сохранено | manifest, 8 Test-копий, 8 CSV, threshold stdout logs, `results.json` |
| Удалено после анализа | Только созданные этим sweep каталоги `StatisticLog` и `EventsLog`; результат уменьшен с 1.3 ГБ до 1.9 МБ |

Текущий [`run_fixed_threshold_grid.py`](../../../Scripts/audit-probes/run_fixed_threshold_grid.py) — оркестратор и анализатор результатов C++ inference, без реализации обучения. Версия во время sweep выполняла ту же сетку/параметризацию; в закоммиченной версии дополнительно выключен debug/event output и добавлена очистка крупных временных `StatisticLog`/`EventsLog` только внутри новых копий.

## Дальнейшее решение

1. Исправления доказанных ошибок измерительного harness и отчётности оставить; подтверждённого trainer-кодового дефекта по этой выборке нет.
2. 8 завершённых CanonRmin quality/detection отказов оставить как ограничения результата в текущей конфигурации; `br25_on` threshold-only вариант не продолжать как путь к PASS. Keep и Search учитывать отдельно.
3. 26 случаев `Need=1` оставить «недостаточно данных о дальнейшей сходимости». Не запускать полную матрицу. Для вопроса о длительности можно позже выбрать один D-представитель и один positive control с тем же ограниченным параллельным запуском и C++ audit.
4. `br100_search` повторно классифицировать только отдельным экспериментом Search/revert; не смешивать с Cold baseline.

Алгоритмическая логика обучения остаётся в C++-тренерах. Скрипт sweep меняет только параметры фиксированного Test inference и собирает CSV/метрики.
