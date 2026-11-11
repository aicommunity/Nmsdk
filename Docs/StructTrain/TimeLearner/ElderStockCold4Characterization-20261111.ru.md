# Холодные N4 burst-пробы на Elder — 11.11.2026

Реальный Console SDK22e9714/Pulse165 завершил8/8 свежих проб Classic/Branch; наблюдения valid/complete, initial model сохранён,8 дочерних process groups и контроллер закрыты, единственная managed lease released. Controller validation1/1 PASS; полное время54.419695s. Это измерение исходной модели, без обучения, нормализации, калибровки или классификационного verdict.

Профиль NSPNeuronGen без LT-мембраны,2000Hz, N4, L1/Ns1/Rs86MΩ, threshold100. Четыре входных импульса в0.01/0.09/0.25/0.49s; полное окно0–1.8s. Каждый input измерен в отдельном свежем native process. Train использует максимум закреплённого импульса; широкое диагностическое окно не является будущим окном Train.

| Закреплённый импульс | Время пика, s | Задержка, s | Амплитуда, native units |
|---|---:|---:|---:|
|0|0.0245|0.0145|0.015781441626431136|
|1|0.1045|0.0145|0.015828572406203167|
|2|0.2645|0.0145|0.01578146659932167|
|3|0.5045|0.0145|0.015781441636542715|

Измерения Classic и Branch совпали с M40 в этой исходной однородной геометрии. Это не доказывает эквивалентность алгоритмов после growth и не даёт независимых случайных повторов. Индивидуальные амплитуды различаются из-за динамики пачки; сохраняется CapturedPerInput, общей амплитудой они не заменяются.

[Точная постановка и closure](ValidationPlans/ElderStockCold4Probes8A2-20261111/actual-result.json), [исходные измерения](ValidationPlans/ElderStockCold4Probes8A2-20261111/native-measurements.jsonl). Первая декларация ошибочно указала hostname Elder вместо фактического Elder-1 и была отклонена до запуска; [исходный отказ](ValidationPlans/ElderStockCold4Probes8-20261111/prelaunch-refusal.json) сохранён. Допуск host guard не ослаблен.

Полные compact primary обоих cold8 сохранены в `Reports/StructTrain/TimeLearner/StockCold4-20261111/{Elder,M40}`:334 regular originals+8 glog aliases,342 archive members на worker. Elder134508bytes, SHA256 `4e78e61ff2974a4b3d30fd347aae74497e502a6697032ab5ada71d5d529e1ccb`; M40134500bytes, SHA256 `2f32dca682e5bc324a00a0c910c31b2fb672261ac527a1b13497fe1b5ce52f65`. Обе упаковки завершены,9 original units закрыты до/после; передача через Git, archive/pack SHA сверены. Независимое восстановление и временные графики этих проб ещё не приняты. Все исходные этапы1–12 остаются частичными.
