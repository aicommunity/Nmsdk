Дополнение06.11: [новый SDK2e/Pulse12d full normal304 принят](SharedSdkNormal304Acceptance.ru.md). Прежнее ожидание normal304 ниже относится к предыдущему снимку; ASan и научные проверки отдельные.

# Перенос модели в отдельный ASan-процесс и анализ: адресная приёмка

06.11.2026 на M40 завершены восемь fresh-process replay и 128 проверок анализа.
Предшественник — опубликованный isolated ASan304 на SDK802/Pulsecc; этот результат
не относится к новой shared SDK2e/Pulse12d.

## Подтверждённый результат

Classic/Branch × N0/N1 × C-Off/On: восемь различных настоящих C++ процессов,
в каждом реально загружена libasan, returncode=0 и исходный JUnit содержит один
успешный случай без пропусков. Executable SHA256:
`ec2a840511ef93f5011aa849d47ff035473447043b05a4d19d44647bdcabe6e4`.
На сервере production `audit_case_replay` повторно проверил native import,
граф и точное воспроизведение waveform по оригинальным моделям предшественника.
Исходные модели не заменены шаблонными. Это инженерные fixtures, не независимые
обучения или классификация всей научной матрицы.

Reader suite:128/128, без failures/errors/skips; точный список ID и fingerprint
совпадают с декларацией. Reader source:
`0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d`.

## Первичные данные и независимая сверка

[Полный bundle](../../../Reports/StructTrain/TimeLearner/s07-joint-asan-owner-readers-a3/bundle.json),
data commit `b15569b6030b82be92e733562aba9b739aa6def8`:
195 файлов,462240 сжатых bytes, SHA256
`281396f223a622fdc6095a0b2c87a96c8e1ad6670630e00fbc7de42e9b76b858`.
Архив включает исходные XML/CSV/JSON, process/runtime mappings, fixture bindings,
результаты suite и production worker. Серверный publisher сохранён отдельно.

[Независимая локальная сверка](JointOwnerReplayASanVerification.json) проверила
все195 member hashes,8 уникальных boot/PID/start identities, исходные JUnit,
libasan mappings, совпадение hash каждого input-model с опубликованным
предшественником и323 source hashes с Git blobs reader commit.
Локальных численных тестов и повторного анализа waveform не запускалось:
production graph/waveform audit выполнен на сервере и сохранён в primary.
Свежий operational dependency подтверждает закрытие всей группы и released lease.

## Границы и дальнейшие проверки

Leak detection выключен; отсутствие утечек не доказано. Same-process перенос
не подменяется fresh-process проверкой и наоборот. Этот корпус не доказывает
влияние LTMembrane, независимое обобщение или сходимость stock четырёхвходовой модели.

Последующий оперативный опрос06.11: сборка shared SDK2e/Pulse12d ASan и focused8
завершились успешно по серверным terminal records; полный normal304 этой SDK
также завершился304/304. Их первичные данные требуют отдельной публикации и приёмки,
поэтому здесь им не присваивается принятый PASS. ASan lifecycle133 подтверждён
kernel-live: PID713838/start300968475 выполнял NativeBoundedTraining.Classic20000,
partition0088. Это наблюдение работающего задания, не его итог.

Полностью принят только этап0 исходного плана; этапы1–12 остаются частичными.
