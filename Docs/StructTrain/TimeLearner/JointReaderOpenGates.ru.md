# Приёмка совместного C-search/ModelSpec2 среза

Актуализация: [normal owner8/readers128 принят](JointOwnerReplayNormal.ru.md).
Ниже сохранены причины failed attempts и исходный перечень: пункты1–5 выполнены
для normal SDK802, пункт6 и прочая исходная матрица остаются открытыми.

Native normal304 source8021301e894368aefd045f9d77274fcce9f60245 прошёл.
Это не приёмка всех readers, отдельного процесса импорта, ASan или научной
классификации. Алгоритмический feature Pulsecc97149c и root802 ещё не merged
в develop; текущий accepted child Pulse9ec4566d сохраняется.

## Сохранённые неуспешные attempts

Proof7db349bcea8c313ed73ee89b4a5d66a644ec88b7 имеет accepted parent8b231dae9;
он добавляет только Reports, не pending algorithm code.

- A1 не создал unit: launcher неправильно вызвал start API.
- A2 kernel завершил reader group по памяти при256MiB. Частичные файлы и
  closure сохранены; исходный native dataset не менялся.
- A3 source802:95/119 выполнены,18 CLI subtest failures и2 setUpClass errors.
  Первое — local import shadowing analyze; второе — старые фиксированные
  counts не учитывали дополнительные объявленные ModelSpec2 cohorts.
- A4 source4c6208344e467558aa1bd7691ad9f22af8ed5ed9:119/124 выполнены,
  failures0, errors9. Восемь ошибок — ожидавшиеся *_fresh_process.json отсутствуют
  у ModelSpec2 recognition cases; девятая — source native304 не содержит
  *_domain_preview.json для отдельной AnalysisCliTest suite.

[Независимая сверка](JointReaderFailureVerification.json) проверяет оба полных
archive/member hashes,293/299 соответствующих Python Git blobs и ранние
partial/launcher/OOM artifacts. Предыдущие отказы не перезаписаны PASS.

## Что исправлено отдельно

[Analysis dispatcher](AnalysisDispatchRegression.ru.md) исправлен и проверен
5 actual CLI checks на каждом worker. Отдельный normal native2 создал настоящие
domain previews; M40 получил их через Git. Этот CLI hotfix уже принят без
изменения native physics/SDK и не означает успешного нового reader124 gate.
В source4c расширена строгая проверка объявленных ModelSpec2 cohorts:
C-Off4,C-On4,codecs8; baseline counts не ослаблены до len>=N.

## Что реально ещё необходимо

1. Для восьми ModelSpec2 boundary случаев выбрать реальный recognition protocol.
   C++ LearnedBoundary при заданном recognition вызывает RecognitionChecks
   и возвращается до solo *_fresh_process writer. Вариант OwnedFreshIdentity
   означает другой owner/компонент в том же процессе. Нельзя выдавать его
   за отдельный процесс и нельзя создавать отсутствующий CSV из ожидаемых данных.
2. На прежнем immutable SDK802 выполнить восемь новых отдельных процессов
   через уже существующий NativeRecognitionOwner.FreshProcessImport: обе
   топологии ×N0/N1 ×C-Off/On. Подать сохранённые owner_recognition_state и
   owner_recognition_probe_spec через штатные fixture variables; сохранить
   actual native-gate JUnit/runtime/process records и actual response JSON/CSV.
   Нельзя записывать их поверх старого native304 dataset.
3. Проверить исходные owner packages с audit_owner_recognition, затем actual
   fresh responses с audit_fresh_owner_process: полное окно, native begin/end,
   model/frozen hashes, controller version, все samples/stimuli и побайтное
   совпадение проекции paired waveform. Сам evidence auditor не является
   подтверждением process provenance; это отдельный native-gate слой.
4. Для новых recognition cohorts адаптировать соответствующие reader checks к
   этим реальным external replay artifacts; старые baseline solo-process checks
   сохранить. Пропуск восьми случаев не считается исправлением.
5. Domain CLI fixture для reader124 брать из отдельного проверенного native2,
   а не объявлять его существующим в native304. Повторить полный declared gate
   без skips/errors с actual replay data и отдельно сохранить каждый отказ.
6. После закрытия normal prerequisites и живого K1 — joint ASan44/304 и readers
   на ASan primary. Ранее подготовленный ASan802 build сам по себе не runtime pass.

Допуски, CapturedPerInput, threshold100 engineering controls, pulse/ITI/reset
protocol не меняются ради PASS. Source CPP/App/CMake/Pulse в reader4c совпадают
с802; библиотечная CLI правка не требует нового numerical Train.
Engineering LT fixture не является августовской stock моделью;8/8 не критерий
рефакторинга. Исторические4/8–6/8 и прежние режимы остаются своими наблюдениями.
