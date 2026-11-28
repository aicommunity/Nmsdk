# Записанные входы native-проверок сохранённой модели

## Подтверждённая ошибка постановки

Полный Windows-проход на SDK
`cde0b851a3c156b3c31e6dbadc27b320de9a3884` выявил три случая, которые
пытаются открыть удалённый из Git бинарный fixture по пути относительно
`__FILE__`. В действующем дереве остались корректные descriptor и внешняя
ссылка; самого `learned-state.json.qz` там нет. Первичный JUnit подтверждает
ошибку открытия файла до декодирования и импорта модели:

- `NativeArchiveOwnership.MoveRetainsDecodedPrimaryStorageAndCopyIsIndependent`;
- `NativeClassImageReplay.ActualMembraneCopyAndLoadStages`;
- `NativeClassImageReplay.ClassicActualSavedModelAcrossNativeGraphRelease`.

Это не свидетельства отказа алгоритма импорта. Два отдельных отказа
`NativeImageRestSnapshot` остаются открытыми и этим исправлением не
устраняются. Старые результаты не пересчитываются и не объявляются PASS.

## Исправленный путь данных

Используется существующий production-механизм `native_gate_inputs`:

1. Задание объявляет объект архива как DATA input `classic-package6.qz`.
2. Runner проверяет исходные323020 байт и SHA256, сохраняет descriptor
   и размещает точную копию в собственном `native-inputs`.
3. C++ fixture читает эту копию относительно `TIMELEARNER_EXECUTION_OUTPUT`.
   Он дополнительно проверяет сжатый SHA256, длину qCompress до выделения
   распакованного буфера, все4812359 байт JSON и исходный SHA256.
4. Runner после расчёта проверяет неизменность исходного и staged-файла.

Бинарные данные в source checkout не восстанавливаются. Объявленный
исторический пакет не переписывается, новые defaults не подставляются.
Путь и идентичность приведены в [описании fixture](../../../Tests/Integration/Data/NativeWindowPackage6Classic/README.md).
Linux-контракты5/6 уже поддерживают такие входы. Windows-контракты4/7
пока не поддерживают DATA staging; этот предел сохраняется явно.

## Попутный дефект Windows loader environment

В `native_gate.py` schema7 выбирала `LD_LIBRARY_PATH`, хотя запускает
Windows Job. Теперь schema4 и schema7 одинаково применяют объявленный
runtime `PATH`, `QT_PLUGIN_PATH` и `QT_QPA_PLATFORM`. Linux-контракты
сохраняют свой набор переменных. После запуска исходное окружение
оператора восстанавливается. Две адресные проверки вызывают тот же
селектор и context manager, которыми пользуется production-runner.

## Статус проверки

При подготовке исходной правки новые серверные Python и C++ проверки
ещё не выполнены. Нужны новая изолированная сборка и реальные три
записанных replay, отдельная проверка CSV handle fix, прежние rest-state
контроли с сохранением исходных архивов и waveform. Все неизменные
параметры и методы Rdk сохраняются. Новый исход обучения, научный PASS
и завершение полного этапа плана здесь не заявляются.
