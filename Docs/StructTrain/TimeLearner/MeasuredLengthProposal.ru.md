# Измеренное предложение длины — адресная приёмка

02.11.2026 подэтап принят в области ниже. История промежуточных ожиданий и
отказов сохранена; итог задаёт этот раздел, а не более ранние pending записи.

- Normal после repair Bin:67/67 cases в одном XML, без skips,1868.97s,
  [385 verified primary members](../../../Reports/StructTrain/TimeLearner/s07-measured-length-gate-normal-a2/README.md),
  root proof1701991807a10db5609a3656c468bb18bb1f30c3.
- ASan:39 kernel XML +4 завершённых NativeBoundedTraining cases в исходном
  stdout до timeout7200s +24/24 remaining XML,7072.72s с budget14400s;
  [325 verified primary members](../../../Reports/StructTrain/TimeLearner/s07-measured-length-gate-asan-a2/README.md),
  root proofd6110479ffc5deb5f496eb6e36ae10e6ce4e857a. Наборы67 имён равны;
  первичный процесс не выдал завершённый28-case XML. Actual mappings проверены,
  ASan содержит libasan. Временной budget не меняет tolerances/model budgets.
- Все16 выбранных originals1920×960 непосредственно просмотрены; independent
  rerender8 ASan probes дал16/16 byte-identical PNG:
  [proofbd3ead63b019f8ad2cdbf4223143470f9e25930f](../../../Reports/StructTrain/TimeLearner/s07-measured-length-selected-asan-a1/README.md).
  Полный normal cache4146 PNG/240 trial-soma pairs остаётся на M40; Git содержит
  все688 JSON metadata и выбранные изображения. Full ASan cache не заявлен:
  соответствие остальных кривых опирается на160 byte-identical CSV и160
  semantic-equal observation packets, а не на повторный render каждого файла.
- Прежний normal gate и cold corpus сохраняют явно выявленное ограничение Bin
  provenance. Текущий repair не делает их manifests достоверными задним числом.
  Fresh normal67 проверен с corrected source closure; ASan cold corpus и selected
  rerender являются отдельными источниками evidence. Это ограничение не скрыто
  сравнением CSV. [Диагностика](SourceWorktreeIdentity.ru.md).

PulseLib develop merge a18bf543007c52a3ac7a6fbb148a48cb2c351de3 опубликован
первым; его Core побайтно соответствует проверенному a728d97110b706bd7869039557de957ea299c6ea.
Root записывает exact gitlink этого merge. Приняты bounded measured proposal,
guarded fallback, его integration/regression и описанные temporal controls.
Это не полные этапы6/7/11, не legacy/V2 parity по всем modes и не классификация.

Feature изменяет порядок кандидатов V2, сохраняя CapturedPerInput, исходные
допуски, fixed anchor, topology order, native scheduler и все search budgets.
[Алгоритм в PulseLib](../../../Libraries/Nmsdk-PulseLib/Docs/MeasuredLengthProposal.ru.md).

Исходный контроллер перебирает ближайшие длины. Серверный контроль на Elder
root a558b66beb7e8b5ca33974875cf094dd826a5080 /PulseLib456a5ab воспроизвёл4/4
ожидаемых отказа: Classic/Branch ×N0/N1, четыре разрешённых кандидата, измеряемая
по заданному отклику точка L12 вне ближайшего перебора. Это настоящий production
BoundedTrainingSession/ProbeRecorder, но заданный response oracle не является
физическим нейроном. Supervisor завершил воспроизведение failed assertions;
сами исходные tests не являются PASS.

Proof commit 78c32cb3318b6a614ae5703a3c8c6fe66ee60e42:
[26 primary members/8840 B](../../../Reports/StructTrain/TimeLearner/s07-measured-length-baseline-normal-a1/README.md).

Новый MeasuredLengthSearch использует минимум три различные завершённые длины
при одинаковых Ns/Rs и остальных параметрах. Наблюдаемый monotone interval
предлагает целый bracket midpoint либо bounded secant estimate. Ни прогноз,
ни clipping по bounds не подтверждают существование/время пика или сходимость.
Немонотонность, конфликт повторов или неопределённый знак возвращают обычный
перебор; исходные trial/model revisions остаются в evidence. N0 ждёт все
обязательные повторы; N1 оценивает физический domain новой геометрии штатно.
Shared Branch перемещения остальных attachments не смешиваются в один trend.

В production root package добавлен воспроизводимый эксперимент:

```text
python3 -m Scripts.StructTrain.TimeLearner.length_proposal_experiment \
  --templates PREPARED_JOBS --baseline-runtime OLD.json \
  --current-runtime NEW.json --output NEW_DIRECTORY
```

Четыре byte-identical job declarations для обоих runtime: Classic/Branch,N0/N1,
2inputs/2000Hz, ISI [.01,.08], начальные L[2,1], Ns1 и исходные Rs. Диапазон
L0=2..16, anchorL1, Ns/Rs фиксированы, исходные CapturedPerInput/tolerances/
profiles сохранены. Полное окно0.5s с ordered whole-burst assignment;4 кандидата
N0 или5 N1 учитывают дополнительный native domain realization исходной точки.
Декларация не меняется между baseline/current. Исходы SearchUnresolved допустимы;
приёмка proposal path требует фактического измеренного нового скачка длины,
fresh all-input certificate, normal/ASan и temporal evidence. Это отдельный
контроль алгоритма, не independent recognition Test.

На обоих workers завершены39 production helper/controller checks без skips,
включая14 новых:6 helper и8 контроллерных сценариев. Сборки используют root
1cdbdaa2b072715d623cc00de62e0ca13c1ca918 и PulseLib
a728d97110b706bd7869039557de957ea299c6ea. Native regression28 на каждом worker
ещё выполняется; его результат не выводится из helper PASS.

На Elder завершены8 реальных cold A/B и4 actual-template generator checks.
Byte-identical jobs дают одинаковые initial graphs, CapturedPerInput references
и допуски между baseline/current. Старый порядок измеряет L2/3/4/5 (N1 ещё6),
новый L2/3/4/9 (N1 затем5). Все8 исходов SearchUnresolved с отрицательными свежими
all-input certificates: фиксированные Ns/Rs не восстанавливают амплитуду.
Измеренный скачок не объявляется сходимостью или классификацией.
[Normal primary](../../../Reports/StructTrain/TimeLearner/s07-measured-length-native-normal-a1/README.md),
commit7c8820398466341e6713c5c32ffc3cee585c8988:460 проверенных members/629680 B.
Python experiment root41261d366b4d7537dcb24e7e7e22bafad5c6c8ed; Console/Pulse
code одинаков с binary root1cdbdaa2b. Первый generator attempt остановился до
моделей на progress-array/strict-object mismatch; receipts сохранены в primary.

ASan cold A/B также завершён:8/8 полных SearchUnresolved runs,4/4 generator
checks. [ASan primary и сравнение workers](../../../Reports/StructTrain/TimeLearner/s07-measured-length-native-asan-a1/README.md),
commit56dbd480706ffd1bfe2cd3c07493566b256eec9b:460 проверенных members/634976 B.
Все160 CSV и8 initial-state файлов побайтно равны normal. Это не признак Exact:
во всех16 cold A/B сохранены отрицательные all-input certificates.

Прежние два положительных N1 job declarations повторены неизменёнными на
каждом worker с новым kernel. Все4 Train сохраняют Exact, прежние параметры
и CapturedPerInput references. На каждом worker все84 CSV побайтно равны
соответствующему ранее принятому прогону, чьи full temporal reports/selected QA
описаны в [MeasuredResistanceRefinement](MeasuredResistanceRefinement.ru.md).
Новая классификация/independent Test этими контролями не выполнялись.

- [Normal positive regression](../../../Reports/StructTrain/TimeLearner/s07-measured-length-positive-normal-a1/README.md):
  commitd27bdb89b41b16d9fc030d2429965928e3e40d30,205 verified members/413236 B.
- [ASan positive regression](../../../Reports/StructTrain/TimeLearner/s07-measured-length-positive-asan-a1/README.md):
  commitf4b840290e42db9cfc1d65036f577eb797ac7d91,205 verified members/422136 B.

Native regressions28 на каждом worker, full cold A/B temporal reports,
визуальная проверка выбранных новых кривых и merge children-first пока
не приняты. Full figure cache размещается только на M40 Data; в Git остаются
сжатые primary, metadata и выбранные просмотренные рисунки.
Полные этапы6/7/11 открыты; legacy EstDelayPerSeg/gamma не объявляются действующими
V2 полями. Новые C-trim, общая A* или дополнительная физика не вводятся.

## Уточнение после восстановления VPN и temporal review

Full cold A/B temporal reports готовы:8 scenarios,240 trial-soma pairs,4146 PNG
в M40 cache. Commit10e918079787b170d1bec862f0e1f7b04dae9ac3 публикует688 JSON
metadata members и16 selected originals1920x960. Все16 непосредственно
просмотрены: readable overview500ms и zoom50ms, actual input overlays, shared Y,
без downsampling. L9 даёт более поздний и меньший ответ, не доказательство Exact.
160/160 packet JSON semantic-equal между workers, но0/160 byte-equal из-за
форматирования;160 CSV byte-equal не подменяются этим сравнением.

Normal gate39+28 завершился, но последующая проверка нашла Bin worktree alias
и отсутствие tracked files в запрошенном Elder Bin. Старый HEAD/status manifest
не подтверждает физическое Bin дерево. Primary сохранены commit
df9f3aff210b44191d7053a19ed9e3327f0904ff с ограничением provenance. После
адресного repair выполнен strict source_closure и начат отдельный gate67
на том же frozen runtime. ASan kernel39 прошёл; native attempt7200s завершил
четыре NativeBoundedTraining cases, затем timeout в NativeModelEditor.
Timeout/missing-XML launcher exception сохранены commit
0608878fa3570698fa53571c66fdddcd7e59d8c2. Remaining24 cases проверяются отдельно
на том же runtime с budget14400s. Scoped acceptance и merge children-first
остаются открытыми. Repair не является ретроспективной проверкой прошлых ресурсов.
