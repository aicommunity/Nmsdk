# Явный начальный порог native-модели

Подэтап следует обнаруженным [различиям профиля](ScientificProfileDrift.ru.md)
и [первому stock Train](StockPhaseAPreflight.ru.md). Исторический legacy Train
использует TrainingLTZThreshold100, тогда как native V2 не применяет этот legacy
knob и сохраняет actual threshold из модели. Сравнение0.0117/100 должно быть
явным, без скрытого изменения default или общего storage prototype.

## Контракт

| Native ModelSpec | Построение |
|---|---|
| schema1 | Прежний wire format и порог из storage, без дополнительных полей |
| schema2 | Обязательный finite scalar `initial_threshold`, применяемый только при cold construction |

Ноль и отрицательное значение разрешены явно, как в native scalar threshold
calibration; boolean/NaN/Inf/unknown fields/schema downgrade отвергаются.
Остальная физика берётся из прежних storage-образов. Для stock-проверки нет
LTMembrane и не меняются C/R/кинетика. Встроенные frequency-encoding LTZone и
неизвестные scalar overrides не получают вымышленной поддержки: используются
те же typed capability guards, что у native threshold candidates.

Последовательность: построить private neuron/структуру/банки → применить
initial threshold к его LTZone → штатный Init → повторно найти **фактический**
LTZone и проверить значение → проверить граф/интегратор → attach и fingerprint.
Ни одного Calculate в этом пути нет. Build/Reset/Calculate возвращаемые bool
не используются как новый канал ошибок; диагностика остаётся typed native.

Inspector, Reset, growth и import не применяют initial threshold повторно.
Поздний recognition/calibration threshold принадлежит текущему графу и своему
происхождению. Старый certificate Exact не переносится на изменённую модель.
Автоматического скрытого перехода к порогу0.0117 после Need=false не добавляется.

## Скрипты и проверка

`stock-phasea-preflight ... --initial-threshold 100` создаёт ModelSpec2.
Отсутствие опции сохраняет ModelSpec1 и штатное значение образа. Production
pipeline и completed/stopped readers проверяют wire version; preflight/Train
дополнительно сравнивают actual initial LTZone.Threshold с декларацией.

Добавлены10 native tests с реальными storage/Environment и обоими learner:
Classic/Branch ×2000/20000 Гц, два legacy controls, strict codec/signed values,
unsupported LTZone до attach, read-only inspection после другой scalar value
и Return→Take после освобождения модели с порогом100.
Проверяются actual child, отсутствие LTMembrane, прототип, clock и повторные
Build/Init/Reset, а не только bool результата. Три Python reader tests требуют
actual ModelSpec2 preflight, отвергают malformed versions и rehashed readback
mismatch. AST/source checks локальны; численные/integration checks — серверные.

До их завершения реализация не принята. Для научного сравнения заранее выбрать
обе threshold values0.0117/100 и выполнить оба варианта на одной новой сборке;
сравнение только старого runtime с новым не выделяет причинный эффект порога.
Все прочие bounds, CapturedPerInput, amp1e-5/rel0 и sync0.02 сохраняются.
После валидного cold Train — полный export/import и реальные calibration/Test
с temporal reports. Отрицательный результат не превращается в неразделимость
всех моделей, а invalid candidate не становится доказательством infeasibility.

## Парный production workflow

`stock-threshold-study prepare/run/analyze` использует прошедший native
preflight100 как источник stock-конфигурации. `run` требует тот же runtime
manifest и code identity (Pulse Core/Rdk Core trees и hash Console driver).
Алгоритмическая идентичность дополнительно привязана к фактическому executable
SHA; путь binary и attempt ID в ConditionSpec не включаются.

Все четыре job specs, ожидаемые полные initial identities и ConditionSpec
создаются до первого нового native вызова. Два значения порога для одной
топологии имеют полностью одинаковые прочие факторы. Все четыре preflight
должны совпасть с ожидаемыми графами прежде, чем начинается хотя бы один Train.
Ожидаемая модель получена из actual stock witness заменой только declared
LTZone.Threshold; это проверяемая гипотеза конструкции, а не подмена actual
readback. Каждый Train создаёт fresh native model и сравнивается со своим
preflight. Никакого warm import или шаблонного Test нет.

Четыре cold runs — по одному на условие. Генератор и остальные декларации не
получают случайности от нового attempt ID. CapturedPerInput, bounds, Ns1,
амплитудные/временные допуски, full-window assignment и budgets остаются ровно
из source preflight. Данные передаются production native_pipeline_worker.
Валидные invalid_observation/search_unresolved/budget_exhausted сохраняются
отдельно от ошибок выполнения; положительная сходимость не требуется для
приёмки достоверности эксперимента.

`analyze` повторно проверяет каждый portable manifest, actual graph/runtime,
параметры источника, все условия и producer outcomes. Три server reader checks
требуют реальные четыре runs и проверяют missing condition и независимость
fingerprint от attempt/path. Classification/calibration этим workflow не
оцениваются. Они следуют отдельным этапом только для фактически полученных
состояний, с честной маркировкой stopped diagnostic при отсутствии certificate.
