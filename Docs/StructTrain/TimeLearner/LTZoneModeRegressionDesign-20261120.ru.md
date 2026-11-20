# Проверка режимов интегрирующей LT-зоны

Статус: подготовлены четыре production integration tests; сборка и выполнение
ещё не проводились. Это продолжение открытых source-only вопросов
[аудита08.11](LTSomaSignalSourceAudit-20261108.ru.md), а не новое измеренное
объяснение результатов текущих N4 Train.

## Граница исследования

Проверяется конкретный C++ класс NPulseLTZone с внутренними PrePotential,
TimeConstant, UseLTZIntegtation и UseSpikeStabilizer. Он отличается от
NPulseLTZoneThreshold и отдельного дочернего компонента нейрона LTMembrane.
Наличие одного механизма не доказывает присутствия остальных.

Для разрешённых scalar-threshold классов native recognition записывает
именно Potential, используемый CheckPulseOn. Другие C++ реализации требуют
адаптера и отклоняются RequireNativeScalarSpikeThreshold; имя storage-образа
само по себе не определяет C++ класс.

В NPulseLTZone::ACalculate2 source-аудит обнаружил input=0 при integration=true,
stabilizer=false. SetUseSpikeStabilizer также присваивает TimeConstant=0.00144.
Их runtime-эффекты и влияние на перенос пользовательского tau должны быть
проверены до изменения физики. Текущие научные sources/runtime и их условия
сохраняются; в этом изменении production-физика не исправляется.

## Сценарии

Все случаи находятся в Test_PulseLib_LTZoneModes.cpp, suite LTZoneDynamics,
и включены в штатный Test_PulseLib_StorageComponents. Это реальный TakeObject,
Environment, NModel и штатный Calculate дерева; тело интегратора не копируется.

| Case | Цель |
|---|---|
| NonspikingFeedbackModesHaveTheSameDrivenResponseAt2000Hz | При отсутствии спайков выключение стабилизатора не отключает афферентный вход |
| NonspikingFeedbackModesHaveTheSameDrivenResponseAt20000Hz | Та же проверка при второй используемой частоте |
| DisabledIntegrationIsAWorkingPositiveControlForBothFeedbackFlags | Ненулевой вход действительно достигает LT-зоны, обход фильтра даёт ненулевой отклик |
| CopyAndStorageImagePreserveTheEffectiveCustomTimeConstant | Реальные Copy/RegisterClassImage/Take сохраняют эффективные tau и флаги |

Один изолированный leaf конфигурируется до финального Init, без Default после
TakeObject и без записи параметров на каждом тике. Используется32 тика,
постоянный вход0.02, threshold100, tau0.004. На каждом тике отдельно проверяются
NeuralPotential и отсутствие спайков, чтобы не спутать отсутствие входа с
неправильной интеграцией. Сравниваются реальные отклики при одинаковой физике,
а не тестовая копия формулы интегратора. Частоты2000/20000 устанавливаются
до построения. Допуск1e−12 относится к сравнению одинаковых откликов этого
контроля; он не заменяет допуски обучения.

Новый test source не входит в уже запущенный native86 Rootde528 и не меняет
его cohort. Следующий запуск этих четырёх случаев требует отдельного
неизменяемого source/build/runtime и объявленного gate после освобождения
worker. Научные Train и Test имеют приоритет. Отказ теста будет исходным
runtime-свидетельством, после которого исправление и повтор проверяются
отдельно. До этого режима не присваиваются статусы «исправлен» или «принят».
