# Native PostTune: сохраняемые кандидаты

Рабочая ветка `codex/timelearner-native-posttune`, этап 8 остаётся незавершённым.
Это следующий алгоритмический слой после исправления границ legacy-наблюдений
TL-037. Normal A2 root `149a1af0aea88b523871a4e3f6a72fc0bf217c2b` прошёл
5/5 native cases (83.454 s), 4/4 conversion regressions и 8/8 independent checks
(31.088 s), без skips. Core — PulseLib `de51a21`, точный SHA записан в closure.
Это адресная приёмка кандидатов, не полного PostTune-контроллера.

Завершён и ASan: 5/5 native (526.211 s), 4/4 conversion regressions, 8/8 reader
(26.405 s), no skips; четыре CSV byte-identical normal. Lossless bundle
`b5f41edd1a4e2f29f7449786a11ada5b4e4baa7a`: 264 files / 349112 bytes, все хэши
проверены. Production Console прошёл 40 отдельных export/evaluate операций и
4 independent checks; [данные](../../../Reports/StructTrain/TimeLearner/s08-native-posttune-worker-normal-a1/README.md).
Все 20 fixed-threshold evaluations молчат и на target, и на foil.

Новые [измерительный controller](NativePostTuneController.ru.md) и его normal gate
уже существуют отдельно от candidate API. Старые «следующий/open» ниже описывают
последовательность первого implementation snapshot; текущие незавершённые
требования — ASan/полная matrix, public dispatch, continuation и новые visuals.

Первая A1 root `8ff51ae2f4648532a931230023001490f509f2be` имела три отказа:
общий test helper ошибочно требовал Branch N1 factor=2 и при identity conversion
Classic/Branch N0, Classic N1. Проверка ограничена фактическим scaled-режимом.
Core между A1/A2 не менялся. Исходные отказы сохраняются вместе с A2.

`NativeRecognitionSpec.postTune` задаёт одно преобразование неизменяемого solo
сначала в исходную recognition-модель, затем в кандидат PostTune. Источник
преобразования связан с точным `source_model_revision` промежуточной модели.
Повторное создание всегда начинается с solo; уже преобразованные живые Rs не
служат входом следующего умножения. Существующие conversion spec schema 1 и их
результаты сохраняются. Наличие PostTune вводит schema 2 спецификации и записи
преобразования; внешний архив recognition schema 1 остаётся прежним.

Режимы кандидата:

- Off и KeepDone сохраняют Rs исходной recognition-модели.
- CanonRmin запрашивает явно заданный floor для первых N−1 входов и last для
  последнего. Floor не подменяет измеренные границы конкретного входа.
- FlatLastR запрашивает last для всех входов.
- SearchSyntheticCandidate задаёт один явный вектор предложенных Rs. Это не
  результат поиска и не утверждение о разделимости.

Для каждого изменяемого входа обязательны собственные bounds, пересекаемые с
эффективными Rm/ratio и configured minimum. Сохраняются previous/requested/applied,
границы и clipping. Неиспользуемые параметры запрещены. Изменения применяются
только к частной native-копии с проверкой подключённых свойств и readback; storage
прототипы, C, L, Ns, частота, тормозные связи и неоднородная физика не меняются.
Разные запрошенные значения одного физического банка Branch должны быть
отвергнуты, а не применены по правилу «последняя запись побеждает».

После изменения проверяются фактические проводимости/интегратор и полный model
identity. Импорт повторно выводит ожидаемый кандидат и сравнивает архив и запись.
Запись содержит `candidate_unmeasured` и `unconfirmed`; recognition certificate
остаётся null. Старый сертификат обучения относится только к source solo.
Порог сохраняется как у исходной модели; новая калибровка не подразумевается.

Корневой `recognition_evidence.py` независимо воспроизводит оба преобразования
по фактическим дочерним параметрам и графу. Native import и научное качество
не выводятся из проверки JSON: для них требуются отдельные execution/probe gates.
Расширенный auditor имеет version 2; старые схемы продолжают читаться.

Адресные проверки предусмотрены на реальных Classic/Branch N0/N1, 2000 Гц:
пять режимов, повторное создание, native import, clipping, подмена источника и
заявленного результата; для CanonRmin — две отдельно импортированные модели и
полные временные CSV фактической реакции сомы с входными импульсами. Независимый
Python reader проверяет 20 кандидатов и четыре транспортных наблюдения, а также
повреждение записи, C и сертификата. Сборка и выполнение — только на workers.

Дополнительно реализован `report --format recognition-transport`: фактические
сома/вход всех записанных тактов, обзор и тайлы по 100 тиков, без decimation.
Показывается модель A; независимый reader проверяет поточечное равенство B.
Full cache предназначен для M40, Git — сжатые primaries и выбранные рисунки.
До выполнения renderer и ручного просмотра visual acceptance не заявляется.

Console `--timelearner-export` использует тот же decoder conversion spec и
поддерживает typed-кандидаты без особого XML-overlay. Следующий runtime gate
создаёт 20 отдельных экспортов и 20 frozen evaluations (target/foil) через
owned-process pipeline. Его код и четыре independent audit checks добавлены,
исполнение ещё не принято. Это diagnostic evaluation с сохранённым исходным
training outcome, а не разрешение PostTrainTune в автоматическом V2 Train.

Открыты: общий измерительный поиск SearchSynthetic, транзакция commit/rollback
всего PostTune с подтверждением выбранного порога реальными пробами, публичный
dispatch learner/Console и полная матрица физических профилей, частот и общих
attach positions. Этот слой сам по себе не завершает ни режим PostTune, ни этап 8.
