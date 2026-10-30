# Состояние рефакторинга на 30.10.2026

Это дополнение к аудиту 27.10 и снимку 29.10, а не объявление завершения плана.
Полностью принят этап 0. Остальные этапы сохраняют незакрытые требования;
этапы 8 и 11 в полном сквозном виде не приняты. Научные 8/8 не являются
условием приёмки. Августовские визуальные 4/8–6/8 сохраняют исходный смысл.

## Новые проверенные изменения

- N0 получил явную политику повторов кандидата, default 1 сохранён. Режим
  2..128 требует свежие anchor/input pairs и проверяет все измерения;
  ранжирование использует худший остаток, а не среднее. Неполная группа
  сохраняется с причиной и не выдаёт готовность. CapturedPerInput, anchor N−1,
  исходные допуски и штатный scheduler сохранены.
- Cold configuration schema 2 и repeated training summary schema 2 проверяются
  строго; N1 с этим фактором запрещён. Обновлены документация PulseLib и оба
  русских ClDesc. Изменений Build/Reset/Calculate bool-контракта нет.
- На Elder Release и M40 ASan финальный native A2 прошёл по 35/35 native и
  38/38 Python/infrastructure tests без skips/errors. Восемь summaries / 132
  primary trials каждого worker независимо проверены, включая десять групп
  повторов. SearchUnresolved остаётся отрицательным результатом fixtures.
- Native probe renderer предоставляет отдельные крупные overview/zoom/detail
  PNG 1920×960 и SVG/PDF для всех soma, с actual input samples. На каждом
  worker опубликованы все 132 trials / 198 trial–soma pairs текущего контроля.
  Общий Y-scale сохраняется рядом с явно подписанными detail views. Спайки
  при record_spikes=false остаются unknown, не нулём.
- Объединённый production Python контур root
  `2b7267526c834484be12549f3614d3d967b4bc9b` прошёл по 53/53 теста на каждом
  worker: повторные N0 evidence, process runner, publisher, condition/runtime,
  probe renderer, scale, analyze CLI и полный readback графиков. Дополнительно
  распарсены и проверены оба actual ClDesc из Bin
  `34a9e60d0b8e38522e1cce4d59378b6a9bda7844`.

Источники: [N0](N0CandidateRepeats.ru.md),
[графики и их область приёмки](NativeProbeVisualReports.ru.md).
PulseLib develop merge `b2b670a22f849e0d0d2b6789b8242308521b1c37`,
Bin develop merge `cbb3bf453d82f58672541ed8a42f7b5da54a5508` опубликованы.
Корневое объединение и fresh recursive closure отмечаются отдельно после
фактической проверки; наличие child merges ещё не доказывает root closure.

## Ошибки подготовки проверок и публикации

Объединённые попытки a1/a2 сохранены как неуспешные: сначала были неверно
указаны input directories и затронуто имя environment variable в шаблоне,
затем выбран устаревший domain-preview kind. В a3 пути и схема проверены
до тестов. Никакие assertions production auditor ради прохождения не ослаблялись.

Первые commits новых combined-report branches ошибочно содержали только sparse
Reports tree. Это обнаружено до root develop merge; незавершённое локальное
объединение отменено. Исправляющие commits восстановили полный parent tree
без переписывания истории. Для приёмки этих веток обязательно проверить,
что diff от tested parent содержит только соответствующий новый report path.
Этот дефект временного publisher script не выдаётся за дефект native модели.

## Что остаётся до завершения полного плана

1. Доказательства: закончить исторический реестр с августа, сопоставление волн
   аудитов и semantic review всех параметров/инструментов; не смешивать старые
   критерии с текущими.
2. Lifecycle/storage/export: полная матрица reuse/Copy/Load/growth, heterogeneous
   physics и частот, completed/stopped/warm состояния новой repeat policy,
   full model transfer и независимый frozen Test.
3. Алгоритмы: оставшаяся матрица N0/N1, invalid/ambiguous measurements,
   quantization, shared Branch effects и optional C-trim; final repeatability
   отдельно от локальных повторов кандидата.
4. Conversion/PostTune/calibration: все режимы, реальные candidate probes,
   commit/rollback, реальное подтверждение порога; версии 2 пока недостаточно
   для рекомендации всей матрице. Scientific PASS не выводится из Done/Need.
5. Pipeline: сквозные preflight/prepare/train/export/calibrate/evaluate/history,
   полнота конфигов и expected trials, полная миграция старых скриптов,
   очереди/leases/ресурсы/восстановление и владение деревом процессов.
6. Эксперименты: historical saved-state replay, cold retrain, legacy/V2 A/B,
   порядок/ITI/reset/continuous и вся обязательная physics/mode matrix на
   обоих workers. Серия D автоматически не возобновляется.
7. Отчётность: единицы всех каналов, реальные N>4, invalid/censored adapters,
   полнота графиков в общем runner, визуальная приёмка всей матрицы. Просмотр
   четырёх контрольных панелей не означает просмотр всех опубликованных figures.
8. Документация: согласовать оставшиеся root/PulseLib/Bin/Rdk спецификации и
   исторические оговорки с принятыми production-путями и матрицей проверок.

Все эти требования остаются в исходной цели. Новый набор адресных проверок
закрывает конкретный подэтап, а не целые этапы 1–12 автоматически.
