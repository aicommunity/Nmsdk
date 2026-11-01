# Перенос положительных N1-моделей в frozen recognition

## Цель и исходное доказательство

Подэтап следует принятому [measured refinement](MeasuredResistanceRefinement.ru.md),
root develop `ff98c7fef96eb4f947eca756528834877d14492d`, PulseLib develop
`d1c3df4cd0749e5869b977fb5e69417400ce1112`. Оба реальных cold Train при2000 Гц,
двух входах, CapturedPerInput и исходных допусках дали Exact на обоих workers.
Теперь требуется проверить полный native export/import и фактические реакции
зафиксированных моделей, не переносить Exact в научный PASS.

Train повторно не выполняется. Используются реальные завершённые пакеты и все
их source probes из `s07-native-n1-refined-{normal,asan}-a1`. Original models,
references, geometry/Rs и порог не меняются. Source corpus проверяется до/после.

## Явный протокол

- Для каждой topology выполняется штатный CLI `export`, conversion identity.
  Этот выбор не проверяет historical Branch parallel rescaling и PostTune.
- Затем native CLI `evaluate` импортирует полный recognition package и
  замораживает модель/порог. На выходе сравниваются model-before/model-after,
  сохранённый source Solo и фактические параметры средствами production audit.
- Target из metadata обученной модели и protocol hash: ISI `[0.01,0.03]`.
  Семь явно объявленных foil ISI: первый интервал0.01, второй
  0.015,0.02,0.025,0.04,0.05,0.08,0.15 секунд.
- Восемь циклических порядков по восемь паттернов: target в каждой позиции.
  У каждого предъявления собственный trial ID; одинаковый sample ID относится
  только к тому же pattern hash/label. Всего64 пробы на модель,128 на worker.
- Reset-per-trial, окно0.4 s, не более805 отсчётов,2000 Гц. Wall budget1800 s
  на native operation и200000 model ticks на evaluation заданы раздельно.
- Порог унаследован из Solo без калибровки. Target hit оценивается после onset
  до конца полного окна; любой foil spike считается FP, ранние/поздние target
  spikes учитываются отдельно. Молчание target остаётся FN независимо от TN.
- Recording включает реальные stimuli, soma/LTZ samples и spike timestamps.
  Полные временные отчёты обязаны включать каждую пробу/сому и входные импульсы,
  overview и читаемые zoom без downsampling. Полный cache хранится на M40;
  compressed primary, модели, метрики, metadata и выбранные рисунки — в Git.

Это инженерный frozen-контроль порядка и переноса с новым объявленным набором
foils. Независимый научный split не доказан. Восемь детерминированных порядков
не являются восемью независимыми обучениями. Continuous stream/изменение ITI,
другие профили/размерности и подбор порога этим подэтапом не проверяются.
Августовские4/8–6/8 сохраняют собственный исторический протокол и критерий.

## Проверки

Production paths: `native_pipeline_worker`, `learned_evidence`,
`recognition_evidence`, `recognition_metrics`, фактический Console runtime.
Новый corpus `tests/native_n1_handoff_corpus.py` не выполняет работу при import.
Четыре independent reader checks проверяют source/operation closure, полный
набор trials и позиции target, frozen model/threshold, независимость scorer от
порядка строк и отказ для пропусков/дублей/censoring. Успех этих checks не
требует положительной классификации: отрицательные реальные метрики сохраняются.

Producer/reader source `764a8faca30d241ea2d3364141a473c4302e7180`.
Новые численные сборки не создаются: используются проверенные immutable runtime
root `6ab3b0b3953b132c54a0c4db3662cec80f7f81b9` / PulseLib
`521df5450c3655e0f08b3a01a7aed7d18351c250`, normal a3 и ASan a2.
ASan leak detection выключен. Запуски и их приёмка фиксируются отдельно;
до чтения результатов успех переноса/классификации не заявляется.
