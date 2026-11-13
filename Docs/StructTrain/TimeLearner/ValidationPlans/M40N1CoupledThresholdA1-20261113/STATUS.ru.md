# Проверка одного Same-Matrix порога выполняется

M40 s07-n1-coupled-threshold-m40-a1, control143dd3956252ac8d8d821649b5403f0db0023e78; source/tool563b21fb501f341da5453349d9ce1b0d80c33423. Закреплённый SDK runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. [Полные условия](controls/PLAN.ru.md).

Источник — принятый frozen8 diagnostic фактического terminal Branch N4/N1 state, а не модель после завершённого обучения. Production diagnostic_threshold_study сначала повторяет исходный threshold100 и требует побайтово равных массивов samples/model_before. Затем единственный candidate определяется midpoint(target LT maximum, highest strictly lower foil LT maximum) и проверяется реальными8native spiking пробами. Никакого подбора по фактическим FP/FN, изменения модели или независимого Test.

Native whole-window counts и ранние ответы относительно последнего input будут опубликованы после полного закрытия и DATA audit. Полная разделимость и какой-либо положительный target результат не заданы условиями приёмки. Исход ещё не установлен. Полный набор временных графиков всех8pattern×soma и LT decision с actual inputs/spike markers будет построен штатным read-only renderer после завершения.
