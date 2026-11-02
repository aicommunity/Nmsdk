# Диагностическая оценка остановленного Train

Частичный результат этапов5/8/10. Модель незавершённого обучения можно
исследовать, сохраняя исходный outcome/reason и отсутствие сертификата.
Feature не принята в develop; ASan-приёмка остаётся открытой.

## Контракт

Pulse427bf9300a5caeab2ece6dffb0b76c82f6096025 предоставляет отдельные
ConvertNativeStoppedToDiagnosticRecognition,
PrepareNativeDiagnosticRecognitionState и ImportNativeDiagnosticRecognitionState
обоих learner. Они используют общий storage/import/conversion путь,
штатные Build/Init/Reset и scheduler. Вложенного Calculate нет.
Исходный stopped package сохраняется целиком, включая partial references.
У diagnostic recognition собственные kind/state_kind. Ordinary import,
threshold candidate и calibration отвергают этот тип.

Identity conversion допускает неполные references. Historical Branch N1
scaling требует полных положительных references из проверенной модели.
Порог фиксирован и унаследован. Frozen evaluation сохраняет полный package.

Console193fcd3734816be23c96f5419002e19d89cd9084 реализует отдельный флаг
--timelearner-diagnostic-evaluate. Job kind:
timelearner_native_diagnostic_evaluation_job; source_stopped и conversion_spec
явные. У evaluation/execution отдельные diagnostic kinds.

CLI: diagnostic-evaluate SPEC --source-stopped train_stopped_state.json
--runtime-manifest runtime.json --wall-seconds SECONDS --output NEW_DIRECTORY.
Рядом с package нужны оригинальные stopped summary и trial JSON/CSV.
Run-manifest schema3 предназначен только для diagnostic-evaluate;
ordinary schema1/2 и строгие readers сохраняются.
Метрики: diagnostic_only=true, training_completed=false,
training_certificate_present=false, evaluation_verdict=null.

## Серверные проверки Elder normal

Native ecf3a18876df175b012ad2e9a02797fb243fcf1c:18/18 cases.
Для8 diagnostic cases Classic/Branch N0/N1 partial/budget сохранены32 complete
и16 cancelled/gap observations. Первый reader7/8 ожидал full-pattern files
от ordinary paired-impulse controls. Эта попытка сохранена отдельно:
proof5de3b6b3eba87a2b76a27a526141e23f065e9095.

Root bb9666e24848937f79bdf36f8957bdda64b0a69f добавил2 самостоятельных
ordinary full-pattern controls:20/20 native и8/8 Python readers без skips.
Proofc808ce15b84f6a0bd63ab7289a461ee90c7ae3cb:381 members/2792305 bytes.
Положительные controls явно используют SyncTolerance0.2; negative cases
сохраняют0.02. Defaults и математическая цель не меняются.

Console193fcd373 отдельно собран в runtime-a3. Public preflight:
14 positive/6 negative/2 one-tick Train. Первая попытка отвергнута до моделей
из-за отсутствующего обязательного loader_environment и сохранена.

Driver90afd166328570667e7189165f0928d590d35b93 выполнил6 реальных операций:
2 complete diagnostic evaluations,2 interrupted и2 ordinary Console rejections.
Источники — публичные one-tick Train с external_stop/null certificate.
Classic complete вызван настоящим CLI из постороннего cwd;
оценки выполняются в fresh native processes.

Portable reader15ec01e301c2f893c130dfed195d241a2874432d:7/7 без skips.
Проверены closure, frozen package, перестановка строк, пропуски/дубли/NaN,
ordinary rejection и переподписанная подмена метрик/сертификата.
Proof480c7683fb91c237d420f441693cd80a2190f3b2:
Reports/StructTrain/TimeLearner/s05-diagnostic-public-normal-a1,
465 members/4733324 compressed bytes. Все hashes проверены после Git fetch.
Первый reader с2 ошибками ожидания отсутствующих файлов включён в архив.

Обе незавершённые модели молчат: TP0/FP0/FN2/TN2. Это отрицательная детекция,
не успешная классификация и не научная проверка полной матрицы.

## Временные отчёты

report --format pipeline-run поддерживает diagnostic-evaluate.
Общий renderer показывает реальные Soma.SumPotential и входные samples,
overview, увеличения и временной ряд. SI остаются unverified.
render_diagnostic_evaluation требует оригинальный stopped source с traces;
ordinary renderer продолжает отвергать diagnostic kind.

Прерванный процесс сохраняет спецификацию4 проб, но пишет только начатую.
Строгий loader/scorer по-прежнему отвергает missing files. Отдельные
load_partial_diagnostic_evaluation и score_partial_diagnostic_evaluation
перечисляют отсутствующие IDs: validity=invalid, pooled_counts=null.
Файлы и кривые не синтезируются. Реальная partial кривая заканчивается
последним sample. Все объявленные пробы остаются в manifest.

Полные рисунки — кэш M40 Data; в Git compressed primaries, модели, метрики
и выбранные просмотренные рисунки. Render e379f404c на M40 завершён:
4 отчёта,15 observed trial/soma pairs,80 PNG,10/10 automated checks.
Proof4661b39647b204e3ca04ee613bb08bb6d7cadc88:45 verified members/1273432 bytes.
Все9 selected PNG прямо просмотрены1920x960; запись проверки:
[DiagnosticRecognitionVisualQA](DiagnosticRecognitionVisualQA.json).
Все рисунки явно подписаны Stopped Train: external_stop; complete обозначает
полноту окна, не обучение.6 неначатых проб остаются без файлов/кривых.
Elder reader e379f404c также прошёл27/27 ordinary preflight/native diagnostic/
public pipeline checks без skips; proofe85f003d6060f4ea7769ad71b40eacfc7b3cd969.
ASan native20 уже прошёл внутри regression81 на Pulse225, функциональном
потомке Pulse427. Public Console/CLI теперь прошёл6/6, preflight14/6/2,
portable readers12+7; proof44548f908365f5030445e4ced11a71147d044331.
Все10 inline waveform trials и4 source CSV равны normal; отдельный receipt
286f7e1b4499db2bc4e9ad49e5980dbd219866bf связывает их с указанными temporal
reports и9 просмотренными originals. Независимый ASan rerender не заявляется.
ASan163-a2 также завершён без обновления его source/runtime. Широкая матрица
плана и приёмка feature остаются открыты; [scope](CompletedASanGates-2026-11-02.ru.md).
Этот подэтап не рекомендует ControllerVersion2 и не закрывает этапы5/8/10.
