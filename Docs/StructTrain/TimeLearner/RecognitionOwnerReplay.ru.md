# Отдельный процесс импорта recognition state

Историческая спецификация feature982; её normal SDK802 gate принят в [JointOwnerReplayNormal](JointOwnerReplayNormal.ru.md). Включение в integrated candidate не заменяет проверку новой комбинации. ASan counterpart остаётся открытым.

Production module `Scripts.StructTrain.TimeLearner.recognition_owner_replay`
запускает существующий NativeRecognitionOwner.FreshProcessImport в неизменённом
SDK. Это replay, без Train, подбора порога, retarget и scientific verdict.
Внешний worker отвечает за kernel containment/reservations; module использует
cooperative native-gate schema2. Сам по себе этот CLI не является scheduler
или новым whole-process ownership backend.

Запуск: `python3 -m Scripts.StructTrain.TimeLearner.recognition_owner_replay SPEC.json --output NEW_DIR`.
Spec schema1 содержит source_directory/source_bundle/source_archive/source_prefix,
origin_evidence_commit, native_source_root/runtime_manifest, maximum_wall_seconds
на каждый case, asan_options и список cases с id/package/file_sha256.
Допускаются только уникальные простые имена; package — basename *_owner_recognition_state.json.

До любого native процесса проверяются архив source, hashes/bytes каждого
относящегося к cases исходного файла и audit_owner_recognition полного source
case. Входной model/probe-spec копируется побайтно и сверяется перед launch.
Native runtime/source проверяет сам production native-gate; он сохраняет JUnit,
загруженные libraries/process records. Каждый case имеет отдельные actual JSON/CSV,
gate и source dependency manifest. Старые данные не дополняются и не меняются.

Source archive и его members проверяются по supplied bundle. Поле origin commit
является записанным происхождением: его Git reachability и соответствие archive
проверяет отдельная публикация, а не это поле само по себе. Старый source корпус
уже хранится в Git и остаётся необходимым для повторного анализа; он не копируется
целиком в новый Git archive.

После импорта actual response проходит audit_fresh_owner_process: реальный
begin/end, полные stimuli/samples, immutable model/controller readbacks и
побайтно точная проекция исходного paired waveform. Проверяются сохранность
входов и source dependencies после прогона. Failed case остаётся failed; остальные
cases измеряются отдельно, итоговый passed требует успеха всех объявленных.

Portable audit_case_replay использует переданный original source, проверяет
source SHA, actual JUnit inventory и полный waveform audit. Его transport result
не присваивает process_provenance_verified или native_import_verified: native
execution устанавливается отдельным native-gate слоем, не одним CSV reader.
Ни один слой не присваивает научный PASS классификации.

Для joint ModelSpec2 предусмотрена строгая матрица8: Classic/Branch×N0/N1×C-Off/On.
Reader fixture TIMELEARNER_MODELSPEC2_FRESH_OWNER_REPLAY обязателен для этих
recognition cohorts. Прежние baseline solo-process checks сохранены; новые
recognition cases используют настоящий recognition replay. Требование отдельного
solo-process roundtrip этим не объявляется выполненным для всех режимов.

Добавлены4 actual-corpus controls: все8 waveforms, подмена source binding,
сохранённый PASS при skipped native JUnit и NaN в actual soma CSV.
Полная proposed suite — прежние119+5 domain CLI+4 replay checks=128.
До серверной приёмки runtime pass не присвоен. C++/physical profiles, tolerances,
CapturedPerInput и threshold100 transport controls не меняются.


## Визуальный отчёт replay

Модуль recognition_owner_replay_reports строит actual fresh soma SumPotential
с наложением фактических input samples, без decimation: обзор,100-tick tiles
и локальные amplitude details общим plotting renderer. Для каждой из8 моделей
сохраняются все сомы (12 суммарно) и все записанные ticks. Протокол подаёт один
объявленный transport pattern на модель; это не8-pattern scientific evaluation.
LT spike timestamps этим paired-протоколом не записывались и не домысливаются.

`python3 -m Scripts.StructTrain.TimeLearner.recognition_owner_replay_reports SOURCE REPLAY --output NEW_CACHE`
проверяет replay/source до создания отчёта. Полные PNG/SVG/PDF/HTML хранятся
кэшем на Data M40; в Git идут primary replay, ссылка на исходный corpus, metrics
и выбранные читаемые рисунки. Старые primary в render directory не дублируются.
Один отдельный actual rendering test проверяет8 моделей/12 сом, всеsamples,
покрытие views, tick spacing>=8px и file hashes. В suite128 этот plotting test
не включён: у него отдельные зависимости Matplotlib и отдельная серверная приёмка.
