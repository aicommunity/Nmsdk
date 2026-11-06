# Frozen оценка моделей recovery study

Подготовлен следующий production-модуль `stock_recovery_evaluation.py`.
Пять server role/job guards прошли на реальных stock stopped packages;
CLI help и отказ неполной Train матрицы также проверены. Полный native
evaluate/export/report этого модуля ещё не выполнен.
[Git primary и сверка](StockRecoveryEvaluationGateVerification.json).

Исходник — полностью завершённая и проверенная восьмиусловная серия
StockRecoveryStudy. Неполную матрицу передать нельзя. Все восемь фактических
моделей сохраняются в популяции независимо от успеха обучения.

- Completed source: штатный identity export полного Solo, затем frozen evaluate.
- Stopped source: только diagnostic-evaluate с полным stopped пакетом, без
  сертификата и без подстановки начального шаблона.

Для каждой модели — все восемь исторических векторов PhaseA из точного Bin Git
commit1c1464e248f8744e858bd66df0be99e39969fd65; метки берутся из исходника, а
первый stimulus delay проверяется по XML. Новый протокол: reset-per-trial,
полное2с окно, rotations1, унаследованный порог0.0117 либо100. Калибровки нет.
Это не воспроизведение исторического scheduler/ITI и не независимый набор.
Проверка всех позиций target и continuous/ITI robustness остаются следующими
явными протоколами, а не приписываются этим64 предъявлениям.

До native операций фиксируются матрица и данные всех восьми моделей. После
оценки проверяются actual input job, полный manifest/наблюдения, source hash,
model-before=model-after и штатная физика выросшего графа. Silent target
остаётся FN. Diagnostic metrics не получают положительный scientific verdict.

CLI: `python -m Scripts.StructTrain.TimeLearner stock-recovery-evaluation
prepare|run SOURCE --bin-repository BIN_REPO --output NEW_DIRECTORY`.
`analyze STUDY --output ANALYSIS.json` повторно не принимает Bin repository.
`report STUDY --output CACHE_DIRECTORY` создаёт полный воспроизводимый cache
на M40 Data:64 trials и160 trial/soma pairs, все сомы и входные импульсы,
overview и штатные100-tick zooms. Сам render не считается визуальной приёмкой.
В Git предполагаются сжатые primary, metrics и выбранные рисунки.


## Зависимое задание

M40 s07-stock-recovery-frozen-normal-a1 поставлено в очередь с tool root
5d0ac867ac9786b5b6b846eec1cd5b2aae8a62c1. Оно ждёт свежего kernel closure
и released lease всей s07-stock-recovery-normal-a1, проверяет её положительный
execution/audit terminal, затем повторяет5 guards на фактических новых пакетах,
исполняет64 frozen/diagnostic предъявления и render160 trial/soma pairs.
Если исходная серия не прошла audit, native оценка не запускается. Успех Train
не является условием запуска diagnostic пути; его provenance сохраняется.

[Наблюдение очереди](StockRecoveryEvaluationJobs.json) отражает только момент
проверки PID/start_ticks; последующее состояние нужно читать заново. У legacy
launcher строка role ещё описывает прежний transport25 build; эта подпись
не соответствует новому заданию. Фактический worker выполняет только проверки,
export/evaluate и render по указанному модулю, без сборки. Исходное описание
не переписано, ограничение учтено в job observation.
