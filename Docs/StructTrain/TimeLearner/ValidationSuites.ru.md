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

Первый профиль объединяет автономные проверки и runner contracts с реальными
1599 Project.ini из Bin14. Серверная приёмка нового runner пока не завершена.
Остаётся объявить dependencies/IDs всех остальных suites и связать их с
production prepare/runner и publication. Полные этапы9/10 этим не закрыты.

Алгоритмические gaps не отменены: C-trim V2 явно unsupported, per-channel C0
и learned correction state должны сохраняться через рост/import; Quantized/
BestEffort и полная mode/physics матрица остаются требованиями stage7/8.
