# PostTune: транзакция кандидата — рабочая реализация

Ветка `stage08/posttune-boundary-transaction` создана от develop; проверенные
prerequisites объединены через --no-ff. Этот подэтап пока не принят в develop.

## Реализованная основа

NativeLearnerGraphCheckpoint в Core/TimeLearner/NativeModelBuilder сохраняет
immutable native snapshots обоих детей: Neuron и DatasetMatrix. Снимок делается
до изменения кандидата. Сохраняются реальный граф, индивидуальные параметры,
heterogeneous C, generator и настройки Dataset. Нейрон при восстановлении
соединяется с новым Generator1, не с возвращаемым старым объектом.

Capture проверяет uniform ready/initialized дерево и возможность безопасной
замены. Restore допускается для того же owner/storage/environment/frequency.
Новая lifecycle-защита также требует сохранения штатного lifecycle owner: явный
Reset/Build/Default/переиспользование не должны продолжать старую транзакцию.
Это не ограничение явного model import в новом scope.
Изменение множества детей owner или внешний listener приводит к rejection.
Сначала оба новых объекта создаются через common native Load/Init, затем
подключаются. Старые объекты не возвращаются в pool до успешной проверки обоих
графов и порядка вычисления. Ошибка attach возвращает текущий speculative graph;
она не выдаёт его за восстановленный source. После устранения ошибки можно
повторить Restore из того же immutable source. Вызывающая сторона обязана
обновить cached child aliases после любого результата.

Здесь нет nested Calculate, перезаписи общих образов, parent C fallback или
распространения ошибок через bool Build/Reset/Calculate. Возвращается отдельный
NativeModelBuildResult. Snapshot не обещает восстановления физической динамики
посреди пробы или старого model time. Это same-storage edit state, не архив
публикуемого научного результата и не training certificate.

## Текущие проверки

Source root `8e7b9e8800d30e88eabd84799f97169cb5acb946`, PulseLib
`436e7020136e18d4ab95a2ac96c684cf8ec96aa4`: запущены normal Elder-1 и ASan M40, attempt s08-boundary-*-a1.
Normal Elder-1 завершён: 24/24 native cases; independent c174c98b — 10/10 Python,
10 boundary cases / 16570 sample pairs, byte-exact до/после. ASan M40 A1 намеренно
прерван SIGTERM из-за стоимости полного IdentifyModel на каждом отсчёте: частичные
успехи не объявляются полной приёмкой. Сохранены marker, signal stack и логи.
Стек SIGTERM сам по себе не является ASan memory-error finding.

Десять новых native cases: Classic/Branch × N0/N1 × 2000/20000 Гц и attach failure
для обеих топологий. Изменяются child C, реальный Rs, stimulus amplitude, матрица,
Delay и one-pass policy Dataset. Проверяются возврат исходных значений, Ns=3
для N0, отсутствие продвижения часов и повторный Restore. Полный native Probe
до/после сохраняет первичные CSV/evidence и сравнивает stimulus/soma samples.
В том же запуске выполняются ранее проверенные reconstruction/transient cases.

## Остаток до полной транзакции

Этот graph checkpoint ещё не подключён к production Enter/Finalize/candidate
loop. Следующий шаг — отдельный typed controller/threshold boundary state:
training goal, policy Fixed/Auto/Calibrated thresholds, conversion provenance,
история кандидатов и counters. Он должен захватываться до scaling/mode edits.
После commit/reject требуется новая verification именно конечной модели.
Полная матрица mode/failure/timeout/external stop и реальная проверка выбранного
порога остаются обязательными. Снимок графа не закрывает этап 8.

Independent audit source `c174c98b237cd241fbae1d46850d7cbdc0d0c100` добавляет
проверку всех primary ProbeEvidence/CSV общим production audit_probe и точное
сравнение пар CSV. Normal A1 анализ завершён; анализ interrupted ASan A1 не запущен. Этот source
не подменяет SHA native binary.

## Lifecycle checkpoint и следующая проверяемая версия

Baseline root `c4fccab86e6dbce939288c77e9379f9aff88c5e0` с новым guard fixture и
pre-guard PulseLib 436e7020: на Elder-1 4 cases, один ожидаемый failure после
owner.Reset; остальные три проверки прошли. Старый helper вместо rejection
подключал новый граф. После неожиданного commit fixture дополнительно читала
старые aliases и получила editor_fixture_identity: это следствие failed contract
в test body, а не отдельный установленный runtime defect алгоритма. Позднейший
fixture commit c850f7db останавливает такой тест сразу на неверном статусе.
Baseline относится к новому edit API, не объясняет августовские результаты.

Fixed native source `325052a0802e431f45ed91619c089fbc0eef7922`, PulseLib
`32dc2e0223cab8adca8280eb1c4586764b6a9c86` прошёл normal/ASan A2: по 14/14 native tests, terminal exit 0 возвращён
сохранёнными SSH-сессиями. После восстановления связи independent A2 audit
завершён на обоих workers: по 2/2 Python tests, 10 graph cases, 4 guards,
16570 exact sample pairs; совпадают 20 Elder и 8 полных M40 A1 CSV. Пакеты
[Elder](../../../Reports/StructTrain/TimeLearner/s08-boundary-elder1/README.md)
`241c10f2ec01a50e95f3f0d2edcc8273fc08a857` и
[M40](../../../Reports/StructTrain/TimeLearner/s08-boundary-m40/README.md)
`45d55b03d4c6d0d56aad964c62321bafa8591078` опубликованы; локально проверены
426 stored / 424 raw и 241 / 239 hashes соответственно. Состав:
10 graph cases и 4 guards (owner Reset, другой owner, изменённое множество
детей, внешний listener). Два waveform probes используют уже существующий
production ModelRevisionObserver: фактические параметры/связи проверяются на
каждом тике, full identity выполняется на границах. Это оптимизация fixture,
не изменение интегратора, Dataset protocol или амплитудной цели. Общие raw CSV
с A1 должны сравниваться отдельно. Успех native tests не подменяет независимую проверку и доступность raw артефактов в Git.

## Owner policy boundary — реализация и история до серверной проверки

Root `2a9357afa73e485d3461683c4ee7e597bb7fc176` / PulseLib
`d9b4199cfb6644962cff678763c98eaaecbfa7c0` добавляет NativePostTuneOwnerBoundary;
последующее уточнение проверяет retained lifecycle до callback с typed owner.
Эта версия ещё не собрана на серверах и не входит в native приёмку A2 выше.

Scope ограничен native-owned моделью без активного обучения, незавершённой/
непотреблённой пробы и legacy free-run. Capture требует остановленного управления.
Source NativeTrainingService не копируется и не сбрасывается: запоминается его
identity (state/outcome/attempt/epoch/capture/certificate), которая проверяется
до rollback. Сохраняются owner mirrors L/Ns/Rs и bounds, threshold policy,
phase/result flags, loaded individual Rs и related private bookkeeping.

Перед восстановлением проверяются та же native declaration/configuration,
неизменность training goal и отсутствие connected/external owner properties.
SetDataDirect в Rdk может писать во внешний data source; поэтому такая связь
является причиной rejection до изменения графа, а не игнорируется. Retarget не
перезаписывается старым target. После native graph restore обновляются cached
Neuron/Dataset aliases, owner values возвращаются адресно без setter и проверяются
readback. Source solo certificate сохраняет прежний scope; recognition certificate
из него не получается автоматически.

Добавлены восемь production-path native tests: завершённое обучение до настоящего
сертификата, изменение индивидуальных параметров и threshold policy, возврат
исходных значений и waveform: Classic/Branch × N0/N1 при 2 кГц и N1 при
20 кГц; отдельно
connected scalar property и retarget. До сборки это постановка проверок,
а не подтверждённая работоспособность.

Новые подключения к jump host дают TCP/SSH timeout. A2 native jobs завершены,
их повтор не требуется. После восстановления связи сначала выполнить независимый
A2 audit и Git-публикацию, затем отдельную сборку owner-policy tests. Не менять
SHA старых manifests и не объявлять новую owner-policy версию покрытой A2.

Этот owner boundary не является полноценным legacy controller checkpoint.
Общий Native PostTune controller со своей историей кандидатов, commit выбранной
модели, real-threshold calibration и production wiring остаются следующими
пунктами исходного плана; stage 8 не закрыт.

Owner-policy версия с guard перед typed callbacks: PulseLib
`d186b5746d1bfbec67874637f4f68f50b9387405`; также пока без серверной сборки.

## Дополнительная сверка до сборки owner-policy версии

Controller identity расширена полными reference/final/observed packets.
Одного совпадения status/attempt/epoch и EncodeTrainingCertificate недостаточно:
последний не содержит исходные reference trial IDs. Добавлен девятый negative
control: production RestoreBoundary дважды проверяет настоящие наблюдения;
во втором вызове намеренно изменяется только provenance reference IDs.
Числа, certificate, reason, attempt и epoch остаются прежними. Старый owner
boundary обязан отклонить возврат к предыдущему набору доказательств.
Изменённые ID являются corruption control, не новыми наблюдёнными trials.
Runtime результат этой проверки пока отсутствует.

Исправлена постановка положительных tests: EditingRig использует CalculateMode=1,
поэтому завершение NativeTrainingService не снимает внешний IsNeedToTrain.
Теперь при 2 кГц flag явно снимается через штатный setter после проверенного
Exact, а при 20 кГц тестируется автоматический CalculateMode=0. Это соблюдение
общего контракта, а не изменение алгоритма или автоматического завершения.
Fixture использует объявленный SyncTolerance=1 s, чтобы изолировать rollback
от научного поиска синхронности; амплитудный критерий и native reference/final
пробы настоящие. Такая fixture не проверяет сходимость при default 0.02 s.

Для проверки происхождения source certificate сохраняются все native training
packets и первичные CSV через реальные onPrepared/onSample/observationSink.
После отката дополнительно проверяется material Neuron.TrainingPattern.
Новая версия остаётся unvalidated до серверной сборки; сохранять/публиковать
Source SHA предыдущих A1/A2 как якобы её результаты запрещено.

Текущий unvalidated owner-policy source для следующей сборки:
root `912ef71b36fbc040c6177a82070a796ee5eb99de`, PulseLib
`c7266dcb93ec51a765125bc30647cf1b59129c91` (девять tests).

## Серверная проверка owner-policy после восстановления связи

Приведённые выше пометки «ещё без сборки» описывают состояние до восстановления
связи. Root 912ef71b / PulseLib c7266dcb теперь собран на обоих workers.
Elder normal A1 завершён: 23/23 native cases, включая девять owner-policy и
14 graph/guard regressions. Independent Python root
`664ced2346171cd6b50f3f79af217dde83dde86f` проверил 4/4 tests, все 42 actual
training packets и 8646 owner waveform sample pairs. Это проверка первичных
probes, привязки final trials к source certificate и точного waveform replay;
полный training summary с повторным выводом всех условий сходимости не заявлен.
M40 ASan A1 также завершён: 23/23 native. Independent A1 и A2 — по 4/4 tests
на обоих workers; Python A2 `54b3d56073ebbe9e2cc3ef9edacb5085bf817293`
добавляет сверку sample-count summary с raw CSV, без повторного native расчёта.
У каждого worker проверены 42 actual training packets / 8646 waveform pairs;
20 graph CSV совпадают с предыдущим A2.

Опубликованы [Elder owner artifacts](../../../Reports/StructTrain/TimeLearner/s08-owner-elder1/README.md)
`640a39df9f5a83bff84a06294c1c5d10ee6a4913` и
[M40 owner artifacts](../../../Reports/StructTrain/TimeLearner/s08-owner-m40/README.md)
`ec944b447468c2d20ad308b069ef6136bc41aabc`. Локально сверены по 324 stored /
322 raw hashes. Это адресная приёмка boundary API, не whole controller transaction.
PulseLib `8683bbff4f587946239d3cb4ebde37869493cb93` меняет только документацию
после native source c7266dcb. Full normal regressions root 912ef71b на обоих
workers и последующий independent audit ещё выполняются; develop merge ожидает
их результатов и сквозной проверки изменённого объёма.
