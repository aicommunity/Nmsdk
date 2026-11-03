---
name: structtrain-experiments
description: >-
  Runs and documents approved TimeLearner experiments through the root
  Scripts/StructTrain/TimeLearner package, preserving native model ownership,
  evidence provenance, historical protocols and explicit status axes.
---

# StructTrain: воспроизводимые эксперименты

Использовать утверждённый план и текущие контракты
[Docs/StructTrain/TimeLearner](../../../Docs/StructTrain/TimeLearner/PlanCompletionAudit-2026-11-01.ru.md)
и [корневой CLI](../../../Scripts/StructTrain/TimeLearner/README.ru.md).
Справочник прежних case→EXP: [reference.md](reference.md); его legacy команды
и критерии не являются текущей инструкцией запуска.

## Выполнение

1. Выполнять задания в пределах согласованного пользователем плана. Старую серию D
   автоматически не возобновлять. Учитывать ограничения текущей проверенной области;
   наличие ControllerVersion=2 не доказывает поддержку всех моделей/режимов.
2. Сборки и численные проверки выполнять на user@10.245.1.11 и user@10.245.1.17
   через user@10.245.1.12. Пароли в документах/манифестах не хранить. Источники,
   конфиги и результаты синхронизировать через Git.
3. Использовать неизменяемые source/build/runtime и отдельные attempt directories.
   До запуска подготовить явные job spec и runtime manifest. Активные leases,
   sources и runtime не обновлять. Число workers определять по ресурсам; прежние
   8/12 — только начальные верхние ограничения.
4. Новые задания запускать только через `python3 -m Scripts.StructTrain.TimeLearner`:
   prepare → preflight → train → export → calibrate/evaluate → analyze/report → publish.
   Точные аргументы и схемы брать из CLI README и `--help`; не подставлять legacy
   --case в новый CLI. Общая поддержка всей исторической матрицы ещё не принята.
5. Неполный Train допускает отдельный diagnostic-evaluate, но не обычный Test
   завершённого обучения. После передачи модели сверять фактический граф и semantic
   fingerprints; frozen evaluation не меняет обученное состояние или порог.
6. Публиковать child commits и проверять их remote reachability до root commit.
   Работать в отдельных codex/ ветках с --no-ff merges children-first; без rebase,
   squash, cherry-pick и переписывания истории. Точные gitlinks задают комбинацию.

## Метрики и отчёты

Разделять выполнение, валидность наблюдений, исход обучения, калибровку и научную
оценку. Process rc0, Need=0, Done и training Exact не равны classification PASS.
Проверять метки/ID, полноту окон, числовые поля и фактические target/foil ответы.
Silent threshold и большинство правильно молчащих foil не доказывают target hit.

Группировать по Trainer Classic/Branch × N0/N1, затем span, физической модели,
торможению и PostTune. Указывать протокол reset/order/ITI, Train/Test inputs,
модель/порог и их provenance, full SHAs, runtime и артефакты. Постановку и выводы
писать предложениями с явными границами подтверждённого результата.

Исторические августовские4/8–6/8 сохраняют доказательность исходного протокола;
изменённые order/ITI — отдельная проверка. Saved replay, cold train, warm continuation
и Test-only tuning различать. Старые registry/Working criteria маркировать версией,
не пересчитывать их задним числом под новый критерий.

Для каждого фактического Test нужны временные графики выхода сомы на все паттерны
с наложенными фактическими импульсами, читаемым масштабом, общими осями сравнения
и detail views. Полный кэш хранить на M40 Data; Git — сжатые primary, модели,
метрики и выбранные проверенные рисунки. Указывать scope прямого просмотра.

## Владение моделью

Общую физику задают storage-образы; индивидуальные Rs/C принадлежат learned state.
Не менять shared prototypes или дочерние параметры исправляющими записями на каждом
тике. Использовать штатные Build/Init/Reset/Calculate и native scheduler, без
вложенного Calculate. Ошибки передавать диагностикой; lifecycle bool остаются true.
Текущее CapturedPerInput, опорный последний вход и исходные допуски не заменять
общей амплитудной целью или произвольной численной эвристикой.

Исторические SoftCold/OpenGaps/T2/T4 shell-запускатели удалены без wrappers.
[Полные Git retrieval records](../../../Docs/StructTrain/TimeLearner/SoftColdLauncherRetirement.ru.md).
Остаток legacy analyzer/runner migration не считается завершённым.
