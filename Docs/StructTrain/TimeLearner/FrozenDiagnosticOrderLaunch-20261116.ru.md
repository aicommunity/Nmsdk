# Fixed terminal21600: запуск order-протокола на Elder —16 ноября2026

После [независимой проверки всех primary](FastN1FullTrainingThresholdIndependentReplayAcceptance-20261116.json) запущен s11-frozen-order-native-elder-a2. [Точная декларация и внешние refs](FrozenDiagnosticOrderLaunch-20261116.json). Source ce6fc73a6bec591b3b3203904322d9315702bfc0, controls6430e0b7434d0b83f3698d1c53b233793a6a55e6, runtimef9f50022feeddca391b4bbb9d1ea0e7dfb4dd4dc69fb86b4052eec2ab1705b57. Fresh SDK принят154/154; всё ещё используется та же нативная реализация, что в M40 опыте.

Первый этап —actual native repeat исходных8 паттернов с фиксированными candidate2f22a5732cff349873805d1c6ba637f262ed27792739129b85cbf5a411fa0764 и threshold0.054353792695896797. Полные native samples сравниваются с источником при явно объявленном platform absolute tolerance1e-10; это не изменение амплитудного1e-5 или временного0.02 допуска обучения. Проверяется equality actual counts и physical model identity. До прохождения этого контроля rotations не начинаются.

Второй этап —56 проб rotations1..7, вместе с control rotation0 target в каждой позиции. Входные ISI/hash/labels, исходные полные2с окна и reset_per_trial сохраняются. Это64 детерминированные пробы одной stopped-модели; не64 обучения и не новая независимая матрица. Порог/модель не подбираются по результатам порядка. Continuous и ITI —отдельные последующие протоколы. Каждая rotation получит собственные actual TP/FP/FN/TN и timestamps; желаемое качество классификации не является условием приёмки корректного опыта.

На14:18UTC жив owned PID2352165; выполняется проверка источника внутри controller. Native baseline/study outputs ещё не появились. Итог неизвестен; launch не является пройденной native64 приёмкой. Бюджеты: baseline3600с, study21600с, outer32400с; memory8GiB, tasks32/leaf128, output4.5GiB и minimum free8GiB. В source-selection оставлены443 проверенных файла1,539,995,801байт. Удалены только977 заново восстановленных и повторно проверенных byte-exact cache files3,609,782,276байт; complete primary64c9d5.../58.74MB сохранён в M40 CAS. Source используется совместно без новой тяжёлой копии.

## Ошибка декларации первой попытки

A1 был запущен как python-validation: этот штатный режим создаёт отдельный интерпретатор тестов. Runner использует lease identity основного contained controller, поэтому проверка frozen_order_owned_controller_required правильно отказала до первого native процесса. Unittest0.007с, native processes0; это ошибка постановки запуска, не отрицательный научный результат. Request/исходный отказ сохранены отдельно, failure proof6a81de08ea40d3c27809e51e5e010cde7aa04cc04f07663f4b9f0a001d308438.

A2 использует предусмотренный python-controller-validation, при котором production run_suite выполняется в основном owned controller с теми же source path и commit. Строгая проверка PID/lease не менялась. Научные условия, код алгоритма, SDK, threshold, исходный source и бюджеты прежние; изменены только режим orchestration и attempt/output пути. Source snapshot и fixtures проверяются до и после теста.

Полный исходный план остаётся активным: принят этап0, этапы1–12 частичны. Source feature с новым order runner опубликована, но ещё не объединена в develop до требуемой actual native приёмки. Тяжёлые данные и будущие графики хранятся только в Nmsdk-StructTrainExpArchive.
