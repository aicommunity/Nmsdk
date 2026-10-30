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

Обновление 30.10.2026: оба native A2 задания завершены. На каждом worker
опубликованы все восемь cases: 132 primary trials / 198 trial–soma пар,
включая references, search anchors/inputs и fresh final gate. Множество ID
сверено с summaries; это полный набор данного native контроля, а не всей
исследовательской матрицы или исторического эксперимента с восемью паттернами.

- Elder: commit `3b5cbeb818de7300ab9d1ad1b5725aad3a7b09ff`,
  [полные рисунки](../../../Reports/StructTrain/TimeLearner/s09-n0-full-probes-elder1-a1/README.md).
- M40: commit `83b9651c4c5f6fa7c15ef30e03381d3b68d82d3c`,
  [полные рисунки](../../../Reports/StructTrain/TimeLearner/s09-n0-full-probes-m40-a1/README.md).

Source `ae5dbc3fdae94cb58e9c18bf589d79151c35b520` прошёл по 15/15 tests
без skips/errors на обоих workers. Дополнительный полный readback при
`7b808c11e0d53234ae449790caa6b9f0e949a291` — по 2/2 на каждом worker:
все 132 пробы / 198 пар, включая явную неизвестность spike count при
`record_spikes=false`. Нативные входные данные обоих — root
`42d1b58803d6b2060bd8993b60f17c0d74577d5b`; это отдельный provenance
от версии renderer. Отчёты не добавляют научного PASS к SearchUnresolved.

Просмотрены четыре source-bound Poppler previews: Classic overview и Branch
zoom с каждого worker. Это крупные 1920×960 панели с различимыми импульсами,
формой ответа, читаемыми осями и легендой без пересечений. Исходные векторные
PDF не менялись; их hashes привязаны к опубликованным commits. Результат
просмотра ограничен этими четырьмя панелями, а не всеми рисунками матрицы:
[Elder QA](../../../Reports/StructTrain/TimeLearner/s09-n0-pdf-qa-elder1-a1/README.md),
[M40 QA](../../../Reports/StructTrain/TimeLearner/s09-n0-pdf-qa-m40-a1/README.md).

Дополнение: [явная partial/censored policy](PartialProbeVisualReports.ru.md)
проверена по 23/23 tests на обоих workers, включая реальный Classic trace с
шестью soma. Default complete-only adapter сохраняет прежнюю строгость;
диагностический режим не создаёт certificate или научный PASS.

Открыты: визуальная приёмка всей матрицы, вся physics/frequency matrix,
достоверные unit descriptors, исторические схемы и общий report completeness
gate в runner. Один six-soma transport control не закрывает все большие
размерности, режимы и частоты. Это ещё не полное выполнение VisualTestReports.ru.md.
