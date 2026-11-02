# Поправка общего wall budget CI163

В job ASan-a1 был ошибочно задан общий лимит7200 seconds. Уже опубликованный
ASan16 inherited baseline занимал9447.088 seconds, что больше этого лимита
ещё без147 остальных случаев. Источник: commit
`b127bb3d7ab903ab97cd908b540f753711e5c5b4`, архив
`Reports/StructTrain/TimeLearner/s01-inherited-native-gate-asan-a1/primary.tar.xz`,
`native-run/gtest.xml`:16 tests,0 failures, time9447.088. В частности,
ClassicActivity20000=1629.064s, ClassicN0Activity20000=1701.427s.

Это ошибка постановки агентского CI задания, а не численный/алгоритмический
дефект или доказательство несходимости. До нового запуска исходный процесс
остановлен SIGTERM через pidfd после проверки PID/start_ticks, boot_id,
uid и executable realpath/hash из его committed owned receipt. Не использовались
поиск по имени с массовой остановкой или изменение runtime/source файлов.
Событие записано в ASan-a1/cancellation-event.json; native_gate должен сохранить
неполный/неуспешный execution и partial primary без PASS.

Новая отдельная попытка ASan-a2 использует21600 seconds. Изменяется только
общий execution timeout, без смены163 IDs, математических допусков, частоты,
model-time budget, алгоритма, source closure или immutable executable.
Elder-a1 с7200 не прерывается: его timings существенно меньше, а сам job ещё
должен завершиться фактически. Spec default исправлен на21600 для будущих jobs;
уже записанные a1 specifications не редактируются.

Baseline служит обоснованием планирования ресурсов, не гарантией длительности
нового кода под другой нагрузкой. Все причины остановки и обе попытки нужно
публиковать отдельно. Частичный old JUnit/stdout не считается полным gate.

Прерванный ASan-a1 опубликован commit
`bdebe7cd4686c93358ef326b13686894ecef1ec1`:424 verified members,1,209,742 bytes.
Сохранены actual -15 exit,942.008s elapsed, incomplete/not_assessed результат,
событие pidfd cancellation и проверенный baseline JUnit. ASan-a2 запущен
отдельно с21600; источники/runtime не менялись. Elder-a1 завершился163/163
без расширения его исходного7200s лимита.

ASan-a2 впоследствии завершился163/163 с исходным21600s execution budget,
stderr пуст. Публикация44548f908365f5030445e4ced11a71147d044331 содержит
неизменённые inputs, полный JUnit, runtime и первичные данные.8/8 inventory
readers прошли;407 CSV побайтно и413 native probe packets семантически равны
normal. Это не устраняет6 untraced packets/5 observability gaps.
Подробности: [завершённые gates](CompletedASanGates-2026-11-02.ru.md).
