# Классические эксперименты структурного обучения

| Этап | Отчёт | Книга |
| --- | --- | --- |
| Проверка сохранённых моделей | [DOCX](LegacyModelChecks.docx) | [XLSX](LegacyModelChecks.xlsx) |
| Сравнение с историческими экспериментами | [DOCX](ScientificComparisons.docx) | [XLSX](ScientificComparisons.xlsx) |
| Повторение исторического обучения | [DOCX](TrainingReproducibility.docx) | [XLSX](TrainingReproducibility.xlsx) |
| Диагностика расхождений | [DOCX](DiscrepancyDiagnosis.docx) | [XLSX](DiscrepancyDiagnosis.xlsx) |
| Интеграция в autoPreset | [DOCX](AutoPresetIntegration.docx) | [XLSX](AutoPresetIntegration.xlsx) |

Локальная папка [`_work/`](_work/) хранит журналы, снимки, рабочие таблицы,
диаграммы, промежуточные отчёты и [планы](_work/plans/). Git игнорирует эту папку.
В ней сохранены исходные имена серий и индексы архивов двух исследований.

- [Архив воспроизводимости](_work/TrainingReproducibility-20261123/Evidence/bundle.json)
- [Архив диагностики](_work/DiscrepancyDiagnosis-20261124/Evidence/verification.json)

Отчёты и архивные записи сохраняют исходное содержимое. Путь из старого журнала
можно преобразовать из корня репозитория командой
`python Scripts/ClassicStructTrain/report_paths.py "<путь>"`.
Для повторного анализа после клонирования нужна локальная копия `_work/`.
Настройки запусков, которые использует стенд, находятся в `Bin/Configs/StructTrainClassic`.
