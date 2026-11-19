# Физическая DATA-модель из terminal8: изменение ожидает серверной проверки

Статус: реализация и интеграционные проверки подготовлены в feature-ветке.
На Windows завершены компиляция и линковка. Исходный `descendants_remaining`
сохранён; отдельный closed-build audit готовых артефактов прошёл.
Native78 выполняется, полный runtime-итог и Python3 ещё не приняты.
В первом прогоне новые DATA cases обнаружили ошибку настройки fixture:
fresh owner наследовал EnablePostTrainTuning=true из Default. Configured-owner
Build штатно отклонял незаявленную optional phase; очередь пробы затем получала
native_model_requires_repair_after_failed_edit. Исправлен именно fixture:
optional controller phases выключаются до Install/Init, причина из
NativeModelEditFailure проверяется немедленно. Защитный Build guard, семантика
Idle, допуски waveform и все16 cases сохранены. Исходный отрицательный прогон
должен завершиться и сохраниться; исправленная версия требует нового native78.
[Точная декларация и порядок проверки](ValidationPlans/WindowsTerminalPhysicalData8A1-20261119/PLAN.ru.md).
Текущие научные N4 Train
используют неизменные Root893/Pulsec508; их runtime этим изменением не обновляется.
Приёмка всего этапа5 и полного плана не объявляется.
Pulse implementation commit:3517a691b367719a5f183f189e54181b1fc76313;
дополнение документации:0cf335ae08347f2d042d7eb3f5d05ef70a55789c.

## Причина

Текущий native factory уже читает полный terminal8 learned/stopped package.
Однако PrepareNativePhysicalModelData в Pulse c508392a8c963ceb639050d737717bff0d853b3a
принимает source_boundary.schema_version только1–7. Прямой DATA export такого
solo package получает ссылку версии8 и не проходит обязательный обратный импорт.
Python reader имеет такое же ограничение. Это несогласованность границ версий;
runtime-воспроизведение отказа старого Console ещё не выполнено.

Полный пакет истории может быть значительно больше физической модели. Для
текущего full-history Test объявлены16GiB owner+16GiB native, тогда как registry
Elder допускает24GiB. Проверенный экспорт физической модели позволит оценивать
её без многократного чтения всей истории. Ускорение и фактическое потребление
памяти нового пути пока не измерены. До его приёмки используется прежний
полный source/import путь; результаты Elder можно оценивать на M40.

## Контракт

Для source reference типов timelearner_completed_state/timelearner_stopped_state
разрешается terminal schema8. Для recognition/candidate/calibrated типов
прежний верхний предел7 сохраняется. Неизвестные solo9 и recognition8 остаются
ошибками; расширения схем физической DATA-модели нет.

```text
validate the complete source through its existing native factory
capture its actual graph, effective parameters, storage definitions and dataset
retain source kind/version/hash as a reference
export DATA without history, certificate or controller checkpoint
prepare solo DATA and install its children through InstallNativePreparedModel
for frozen DATA use explicit recognition conversion and ImportNativePhysicalModelData
initialize fresh owners; keep training controllers Idle and IsNeedToTrain=false
compare graph, parameters and actual native burst response
```

Для frozen recognition сначала требуется явное штатное преобразование
solo → recognition, затем DATA export. Ссылка на исходный Exact не становится
сертификатом DATA; законченный или остановленный статус исходного обучения
по одной такой ссылке не доказывается.
Solo DATA не допускается в публичный frozen importer: после PrepareNativePhysicalModelData
используется штатный InstallNativePreparedModel. Frozen hold появляется только
через ImportNativePhysicalModelData уже преобразованной recognition-модели.

Не меняются математическая цель CapturedPerInput, назначение пика, sync/amp
допуски, поисковые бюджеты, физические профили и conversion spec. Здесь не
появляется новый способ подбирать порог либо продолжать обучение из DATA.

## Компоненты

- PulseLib Core/TimeLearner/NativePhysicalModelData.cpp: верхний предел8 только
  для solo source reference; остальные проверки графа/storage остаются общими.
- Scripts/StructTrain/TimeLearner/physical_model_data_evidence.py: та же таблица
  допустимых source kinds/versions; никаких новых proof-claims.
- Tests/Integration/Support/TerminalPhysicalDataTransfer.h и существующие
  CompositeTraining cases: дополнительные реальные DATA roundtrips.
- tests/test_terminal_physical_data_native.py: независимый пересчёт записанного
  отклика и чтение готовых DATA без соседнего source/history.

## Обязательная проверка

Расширены16 существующих native cases:8 configured completed и8 actual
changed-graph terminal restores; Classic/Branch × Fixed4/Window5 × N0/N1.
Исходные package/summary сохраняются до дополнительных проверок, чтобы отказ
не уничтожил материал диагностики. Отдельный test support не копирует алгоритм
обучения и не создаёт синтетических измерений.

Для каждой модели проверяются:

1. Actual graph и параметры; restored модель отличается от historical source.
2. TakeObject → import → Init нового owner при той же частоте; без Default
   после образа, пересборок на каждом тике или вложенного Calculate контроллера.
3. Controller Idle, epoch0, отсутствие certificate/search/live continuation.
4. Два настоящих штатных burst-probe через единый scheduler. Все исходные
   отсчёты времени/входа/потенциала сохраняются; maximum difference пересчитывается
   Python reader, а не принимается из диагностического поля.
5. Одинаковый ненулевой отклик с численной погрешностью≤1e−12. Это допуск
   проверки переноса, он не заменяет допуски обучения.
6. Экспорт DATA из явно преобразованной recognition-модели, native frozen import
   и Python source-only snapshot без history siblings. Полная frozen waveform/
   Console evaluation новой комбинации остаётся отдельной runtime-проверкой.
7. Отказ для неизвестных source versions и сохранность исходного graph/controller.

Приёмка требует fresh SDK, полного прежнего native78 с дополнительными
assertions, прежних физических DATA проверок и3 новых Python test methods
по всем16 фактическим native fixtures. Прежний accepted78 относится к старому
исходному срезу и не доказывает выполнение новых assertions.

До использования этого пути для научных выводов также нужны реальный N4
full-source/DATA response comparison и actual eight-pattern frozen evaluation
с неизменными моделью и порогом. Успешный DATA import сам по себе не означает
сходимости обучения или хорошей разделимости паттернов.
