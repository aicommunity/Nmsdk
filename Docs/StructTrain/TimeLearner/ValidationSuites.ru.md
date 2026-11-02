# Декларативные Python validation suites

Новый validation.py исполняет явно объявленную Python suite; это не замена
native-gate или численного runtime. Наличие файлов с тестами не является
доказательством единого полного контура. Из122 прежних modules многие требуют
разных исторических corpora, отчётов и runtime. Ошибки общего запуска сохранены
в acceptance-python-normal-a1 и acceptance-python-m40-a1.

Suite schema1 задаёт все module names, полное ожидаемое множество test IDs,
fingerprint всех Python sources пакета и именованные fixture dependencies.
Каждая dependency имеет pattern, точное число файлов и content fingerprint.
Изменение пакета, тестов или данных требует новой явной декларации, а не
молчаливого изменения области проверки.

Запуск:

```text
python -m Scripts.StructTrain.TimeLearner.validation SUITE.json \
  --fixture TIMELEARNER_CONFIG_CORPUS=/absolute/git-derived/corpus \
  --output /absolute/new/readback
```

До исполнения проверяются source и fixture fingerprints, точные bindings,
уникальность и полнота test inventory. Во время загрузки/запуска suites
необъявленные TIMELEARNER_/TL_ environment bindings удаляются временно и
восстанавливаются после. Existing output directory не перезаписывается.
unittest skip, error, failure или несовпадение числа выполненных тестов
запрещает assertion_status=passed. Scientific verdict всегда null.

Результат содержит suite.json, result.json и unittest.log. После проверки
они публикуются компактно вместе с fixture/source closure. Сырые fixtures
из точного Git commit не дублируются, если manifest позволяет извлечь их
по путям и blob/hash. Нельзя считать unit suite приёмкой отсутствующих
исторических, native или temporal корпусов.

Первый профиль — specs/python-portable-validation-v1.json. Он объединяет
60 автономных проверок и6 runner contracts с реальными1599 Project.ini из Bin14.
На Elder и M40 фактически пройдено66/66 без skips/errors/failures. Suite.json
полностью совпадает между workers; package fingerprint
99d21e32d57d671bb4dbe2438f11d8a2dbf37863d9836a8c5228ea020815f28a,
fixture fingerprint d2818cc32a237850347e5117f67a5b0f45d0ed89966bc4fe80743378ebc2d686.
Отдельно на каждом worker5 реальных отрицательных CLI cases: missing fixture,
stale source, changed inventory, duplicate binding и skipped native class.
Первые4 возвращают2 до создания result directory; последний возвращает1 и
сохраняет отрицательный результат. Для nested mixed native module одна
autonomous environment проверка действительно исполняется, native JUnit class
пропускается; runner не выдаёт PASS. Первое неверное ожидание0 исполненных
tests сохранено в failed a2. Первый short-SHA fetch отказал до checkout;
последующие попытки используют полный commit SHA.

Численный код не менялся. Python source ff3c6a7ffb9ab6b8c6151ac1df4b83f98eb0e284.
Elder proofcbbe489b6ecafe16446b26d022315cdfbbb85117:36 members/7673 bytes;
M40 proof1f17ef405fd5a2a5c9371eb9aa00eac6dcc679e3:36 members/8731 bytes.
Все archive/member hashes проверены после Git fetch. Исходные Configs не
дублируются: полный1599-path/blob/SHA manifest уже находится в предыдущих
acceptance-python proofs, описанных SearchDiagnosticAcceptance-2026-11-02.ru.md.
Копия проверенного suite.json перенесена в specs без изменения Python sources.

Остаётся объявить dependencies/IDs всех остальных suites и связать их с
production prepare/runner и publication. Полные этапы9/10 этим не закрыты.

Алгоритмические gaps не отменены: C-trim V2 явно unsupported, per-channel C0
и learned correction state должны сохраняться через рост/import; Quantized/
BestEffort и полная mode/physics матрица остаются требованиями stage7/8.
