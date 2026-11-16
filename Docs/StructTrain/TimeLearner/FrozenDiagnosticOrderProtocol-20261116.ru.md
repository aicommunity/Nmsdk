# Fixed terminal21600: объявление проверки порядка —16 ноября2026

Используется остановленная Branch N4/N1 Fast3 модель с identity conversion, candidate revision2f22a5732cff349873805d1c6ba637f262ed27792739129b85cbf5a411fa0764. Threshold0.054353792695896797 фиксирован по завершённому Same-Matrix опыту [7/8](FastN1FullTrainingRecognitionScientificReport-20261116.ru.md). Новый подбор порога, Train, изменение storage physics и перенос старого Exact не допускаются. LTMembrane отсутствует.

## Последовательность

1. Принять свежий Elder SDK на всей объявленной154-case матрице с закрытием процессов. Использовать записанный immutable runtime manifest.
2. Восстановить полные primary фактической candidate из M40 CAS. Проверить content hashes, portable provenance и production audit. Не читать отсутствующие M40 абсолютные пути как будто они доступны на Elder.
3. Выполнить новый native same-order control всех8 проб. Сравнить source/candidate semantic model revision, effective threshold, actual production counts и **все native sample fields** исходного и повторного прогона. Явный platform absolute tolerance1e-10 касается только сравнения записанных waveform; амплитудный допуск обучения1e-5 и SyncTolerance0.02 не меняются. При отличии остановиться до перестановок и сохранить отрицательную квитанцию.
4. При принятом control выполнить циклические rotations1..7 исходных8 паттернов. Вместе с control rotation0 target будет в каждой позиции. Во всех пробах сохраняются original pattern IDs/hashes/ISI, полное2с окно, reset_per_trial, recorded LT и frozen threshold. Это64 детерминированные пробы одной модели, не64 независимых обучения.
5. Аудировать execution, numerical validity, completeness и model fingerprints штатным diagnostic-evaluate/scorer. Сохранить TP/FP/FN/TN и timestamps отдельно для каждой rotation. Не требовать желаемого качества классификации для приёмки корректного опыта.
6. Опубликовать compressed primary, controls, runtime refs, метрики и Soma/LT report со всеми входами. В Git только компактные ссылки и текст; кэш и архивы в Nmsdk-StructTrainExpArchive.

Первый выпуск проверяет только order при reset_per_trial и прежнем окне. Continuous dynamics, ITI и независимая матрица —отдельные последующие протоколы. Удлинение окна нельзя объявлять чистым изменением ITI.

## Реализация и бюджеты

Корневой production module Scripts/StructTrain/TimeLearner/frozen_diagnostic_order.py; CLI:

    python -m Scripts.StructTrain.TimeLearner frozen-diagnostic-order SOURCE_MANIFEST CONTROLS

Controls содержат declaration.json и immutable runtime.json. Запуск требует действующий owned controller; дочерний native процесс рассчитывает дерево штатным scheduler. Во время опыта runtime и source не изменяются. Baseline и study используют один production run_job/scorer; частичный или censored результат не становится положительным scientific verdict.

Для Elder A1: baseline wall3600с, study wall21600с, outer32400с; leaf memory8GiB, outer8GiB, tasks32/leaf128, reservation disk8GiB. До запуска проверить фактический свободный диск и отсутствие другого принадлежащего плану native scientific процесса. Если заявленный бюджет не хватает, исход остается incomplete/timeout; автоматически не увеличивать и не менять порог. Математическая цель CapturedPerInput, C-trim Off и исходные допуски не меняются.

Contract tests: все позиции/unique IDs и неизменность stimuli/window; отказ duplicate identity/неоднозначных labels/continuous/unrecorded LT/invalid rotations; повреждение любого sample/channel, missing sample, NaN/Inf, расширение platform tolerance. Native acceptance исполняет настоящие64 пробы через production путь, не копию тела функции. Перед запуском native64 проверить contract suite на сервере.

На момент объявления execution_performed=false. Это часть этапов8/10/11; весь исходный план остаётся частичным.
