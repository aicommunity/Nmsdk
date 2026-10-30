# Графики первичных обучающих проб

Рабочий подэтап stage09/native-probe-reports дополняет recognition renderer.
Native training probe — отдельный объект измерения; он не превращается в
frozen target/foil trial ради использования общего plotting backend.

## Команды и данные

```text
python3 -m Scripts.StructTrain.TimeLearner report probe.json --format probe --trace probe.csv --output NEW_REPORT
python3 -m Scripts.StructTrain.TimeLearner report report-spec.json --format probe-set --output NEW_REPORT_SET
```

Spec набора schema 1:

```json
{
  "kind": "timelearner_probe_report_spec",
  "schema_version": 1,
  "trials": [
    {"trial_id": "ACTUAL_PRIMARY_TRIAL_ID", "packet": "probe-0000.json", "trace": "probe-0000.csv"}
  ]
}
```

Все пути относительны spec directory, без выхода через '..', absolute paths
или escaping symlinks. Дубли trial ID, неверная identity, отсутствующий файл
или повреждённый CSV отвергаются до создания итогового report directory.
Положительный primary audit требует фактический packet schema 3 и полный CSV;
никакой строки с NaN/Inf не удаляют и не заменяют нулём.

Набор должен задавать ожидаемое множество проб. Для native training suite
оно выводится из references, candidate input/anchor IDs и final certificate;
сопоставляется с реальными файлами, а не выбирается удобным glob без сверки.
Сам по себе пользовательский subset spec не доказывает полноту кампании.

## Масштабы и семантика

Каждая проба получает отдельные крупные figures всех записанных soma channels:
overview, 100-native-tick zoom tiles и явно подписанные local-detail Y views.
PNG 1920×960, SVG и PDF создаются тем же production plotting.py. Ограничения
четырьмя soma нет. Рисуется actual SumPotential из native CSV и фактический
общий stimulus; сплошной pulse waveform не восстанавливается по догадке из ISI.

probe-set предварительно вычисляет общие Y limits каждого канала по всем
первичным samples набора, включая отрицательные значения/extrema. Исходный
shared view сохраняется рядом с detail, нормировки нет. Требуются одинаковые
stimulus profile, routing и число каналов; смешивать несопоставимые наборы
молчаливым автоскейлом запрещено. SI descriptors пока отсутствуют и подпись
model units / SI unverified остаётся обязательной. Actual absolute model time
сохраняется, model base/effective revisions указаны отдельно.

При record_spikes=false отсутствие spike markers означает **unknown**, не
нулевой spike count. Report не присваивает target/foil label или scientific
verdict обучающему измерению. Raw source packet/trace копируются без изменения
значений; их SHA, primary audit, runtime versions и y_limits хранятся в manifest.
Короткий trial suffix на графике связан с полным trial ID в index и manifest.

Каждый отчёт автономен: primary/probe.json и trace.csv, SVG/PDF/PNG, manifest
и SHA256SUMS. Набор дополнительно сохраняет report-spec.json с путями к своим
встроенным primary files; его можно повторно построить из чистого Git checkout.
Никакого CDN, HTTP server или исходного абсолютного server path не требуется.

## Выполненные проверки и открытые gates

Source 5315140e67193bbba8105a5fe367d12084a76484 прошёл по 12/12 tests на обоих
workers без skips/errors: три actual-probe report controls, четыре scale tests
и пять analyze CLI regressions. Реальный report CLI строит Classic/Branch,
проверяются все записанные soma, actual primary hashes, PNG size, shared axes,
unknown spikes, duplicate/wrong/missing trials и NaN. Elder input — native root
42d1b58803d6b2060bd8993b60f17c0d74577d5b (N0 A2), M40 input — native root
a721fe4975a09f1d8473cef5f1054a286bc7b307 (terminal N0 A1). Это не один и тот же
native run; version-specific provenance не смешивается.

На Elder строится полный набор восьми native cases / 132 primary trials,
включая references, search anchors/inputs и fresh final gate. До окончания,
публикации hashes и визуального QA этот набор не считается принятым. M40 N0 A2
пока выполняет ASan native tests; строить его окончательные графики следует
только после terminal status и primary audit.

Открыты: итоговая публикация/визуальная приёмка полного набора, реальный N>4,
вся physics/frequency matrix, достоверные unit descriptors, partial/censored
invalid-trace diagnostic adapters и общий report completeness gate в runner.
Первый adapter требует complete valid primary observations и явно отказывает
в остальных случаях; это ещё не полное выполнение VisualTestReports.ru.md.
