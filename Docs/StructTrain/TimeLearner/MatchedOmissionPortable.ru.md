# Полная переносимая запись группы matched omission

Этот подэтап переносит запись из испытательного fixture в production API
PulseLib `MatchedOmissionEvidenceJson`. Он не меняет метод назначения v1 и не
подключает его к Train. Различие собственного окна и всей трассы остаётся
открытым в [постановке интеграции](MatchedOmissionTrainingIntegration.ru.md).

Новый kind — `timelearner_matched_omission_evidence`, schema1. Он отделён от
исторического `native_matched_omission_fixture`. Полная схема, типы и C++ API
находятся в `PulseLib/Docs/TimeLearner/MatchedOmissionEvidenceJson.ru.md`.

Запись включает исходные planned/applied ISI, actual readbacks каждой
предъявленной маски, полный policy с sample/probe budgets, объявления model/wall
budgets, native packets, canonical CSV и их hashes, model/reset/instance/channel
bindings и измеренный assignment. Native group получает applied readbacks из
реального MatrixData до первого импульса каждой пробы. Они не заполняются копией
предполагаемого плана.

При импорте C++ повторяет Capture.Arm/Append/CloseNative на первичных данных и
заново вычисляет assignment. Самостоятельный Python reader
`Scripts/StructTrain/TimeLearner/matched_omission_portable.py` проверяет ту же
схему и воспроизводит измерения независимо от C++. Предыдущий fixture reader
сохраняет свой формат; общий trace helper только получил явный optional input ID
для нового контракта. Его прежнее поведение по умолчанию сохраняется.

Проверяются полные N+2 traces в порядке full-before, omit0..N−1, full-after;
уникальные ID/paths, полнота окон, первичные source waveform/events/grid,
хеши исходного и предъявленных ISI, порядок абсолютных окон, sample/probe
budgets и соответствие выбранного максимума первичным данным. Более высокий
shared/unknown максимум остаётся неоднозначным. Размерность берётся из
фактического source inventory до выделения массивов по заявленным индексам.

Переносимая запись может содержать законченный отрицательный operational
результат, но не частичную группу под видом полной. Partial stop/edit артефакты
по-прежнему сохраняются диагностическим fixture-форматом и не импортируются
как complete witness.

Объявленный time budget не доказывает фактический elapsed wall time. Наблюдаемый
span native окон проверяется только как нижняя граница model time; elapsed поля
остаются null, независимое enforcement неизвестно. Source ISI hashes не
заменяют actual timestamps и не доказывают правило квантования генератора.
Файловый replay не доказывает живую принадлежность объектов, native scheduler
или физические пути. Соответствующие attestation flags и
training_certificate_eligible остаются false. C0 witness, модель, references и
сертификат должны связываться отдельным проверенным Train/import путём.

## Адресная приёмка

Подготовлены 23 новых C++ codec tests и 23 Python reader tests. Дополнительно
нужны прежние 20 fixture reader tests, 35 selector, 2 capture boundary,
10 capture/codec regression и 10 настоящих native groups: из шести полных групп
сохраняется portable witness, четыре stop/edit должны отказать его экспорту.
Проверяются Classic/Branch, 2000/20000 Гц и separated positive controls.
На реальных primary требуется независимый Python replay и сравнение с C++;
исходные CSV контрольного протокола сравниваются с прежним accepted snapshot.

Локально выполнены только AST, literal test inventory и Git metadata checks.
На Elder/normal приняты все 80 C++ и 43 Python tests, включая complete
Missing/Clipped/NonRepeatable. Независимо проверены шесть portable и десять
fixture groups, 28 CSV побайтно совпали с прежними первичными данными.
[Receipt](MatchedOmissionCodecElderA1Verification.json), evidence commit
`9cf4bfa0fcabe605dd83faa0d9fc188f67d52273`.

На M40/ASan первоначальный снимок прошёл 77 C++ и 40 Python tests, но исходная
обёртка завершилась с ошибкой сравнения runtime inventory. Этот terminal=false
сохранён. Независимая post-closure проверка подтвердила все результаты и
неизменность runtime/resources: [receipt](MatchedOmissionCodecM40A1RecoveryVerification.json).
Он не включает три дополнительных complete negative cases и новый setter guard.
Новый отдельный ASan gate прошёл все90 C++/43 Python, включая десять ownership
controls и три дополнительных complete negative outcomes.
[Independent receipt](NativeResistanceStepAndCodecM40A1Verification.json)
связывает точный source и primary; исходный terminal=true, все16 kernel groups
закрыты и lease released. Эти подэтапы не завершают этапы 5–8,
полную матрицу или научное обучение. Метод v1 остаётся диагностическим и
не удовлетворяет автоматически уточнённой цели Train.

Для normal проверки на Elder удалены только13 static AR archives старых
закрытых runtime a1/a2; последний a4, executable/ini, пользовательский Nmsdk и
первичные данные не затронуты. Доступное место увеличилось на136433664 bytes.
[Cleanup receipt](ElderS07StaticArchiveRetirementVerification.json) сохраняет
preimages, журнал, kernel/lease closure и явные ограничения проверки protected
login helpers. Это разрешённая очистка build cache, а не удаление исторических
измерений и не подтверждение новых numerical tests.
