# Подготовка научных документов Word

Соблюдать [правила отчётов](../../../../Docs/StructTrain/TimeLearner/ScientificReportRules.ru.md)
и [порядок подготовки](../../../../Docs/StructTrain/TimeLearner/AlgorithmDescriptions/README.ru.md).

Использовать настроенный runtime документов. Для диаграмм необходимы Node.js,
`@viz-js/viz` и `sharp`; для графиков — Python, Matplotlib и Pillow; для сборки
Word — python-docx. Генераторы не собирают и не рассчитывают нейронную модель.

`render_algorithm_diagrams.cjs --spec SPEC --output FRESH_DIR --node-modules DIR`
сохраняет DOT, SVG, PNG и контрольные суммы. `plot_algorithm_trials.py --sources
SPEC --output FRESH_DIR` читает полные валидные наблюдения и сохраняет сопоставимый
масштаб потенциала в пределах примера. `plot_algorithm_measurements.py` использует
штатный читатель первичных JSON/CSV проб и сохранённые измеренные кандидаты.
При необходимости путь к отдельным библиотекам Matplotlib задаётся через
`--matplotlib-libs`; он не изменяет глобальную среду вычислительного worker.

`build_algorithm_docx.py --source SOURCE_DIR --output FRESH_DIR --diagrams
MANIFEST --figures CATALOG` строит оба отчёта. Входные файлы иллюстраций связаны
контрольными суммами; при нехватке обязательных источников финальная сборка
отклоняется. Формулы сохраняются редактируемыми объектами OMML, псевдокод —
явным шрифтом с кириллицей. Математические символы помечаются литеральными,
чтобы их значения не менялись при импорте в LibreOffice.

Состояния `visually_reviewed` и `visual_acceptance_complete` генераторы оставляют
ложными. Их меняет отдельная документированная приёмка после просмотра страниц.
Тяжёлые выходные файлы хранятся вне корневого Git.
