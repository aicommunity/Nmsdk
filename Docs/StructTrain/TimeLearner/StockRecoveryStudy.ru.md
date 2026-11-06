# Штатное cold обучение: парная проверка candidate recovery

Проверка этапа7, ещё не научная оценка классификации. Production-модуль:
`Scripts/StructTrain/TimeLearner/stock_recovery_study.py`.

CLI: `python -m Scripts.StructTrain.TimeLearner stock-recovery-study prepare|run SOURCE
--runtime-manifest RUNTIME.json --code-identity CODE.json --output NEW_DIRECTORY`.
Для анализа: `stock-recovery-study analyze STUDY --output ANALYSIS.json`;
runtime и code identity повторно не задаются. Обёртка worker добавляет lease,
ограничение cgroup и сохраняет исходный код запуска как текстовый артефакт.

До первого native вызова сохраняются восемь условий: Classic/Branch × исходный
порог0.0117/обучающий100 × RetrySameCandidate/AdvanceUnassignedBurst. Один
неизменяемый SDK Pulse416 используется для обеих политик. От исходных четырёх
stock jobs опубликованной серии e5fa71d745119af0d818059f497dd226f4c7c25d меняются
только ID попытки и общий invalid allowance32; у advance дополнительно задаётся
schema5 envelope поверх base1. Нулевой прежний allowance не является парным
контролем для advance, которому нужен ненулевой бюджет. Старые результаты
остаются самостоятельными наблюдениями.

Сохраняются CapturedPerInput, referenceN−1, TARGET [0.01,0.08,0.16,0.24],
2000Гц, N1, original tolerances 1e-5/0/0.02, bounds и search/time budgets.
Используется штатный NSPNeuronGen, без дополнительной LTMembrane, custom
storage overlays, C-trim, PostTune и калибровки. Влияние двух порогов не
смешивается: политики сравниваются только внутри своей пары.

Все восемь preflight должны подтвердить точный исходный effective graph до
первого Train. После каждого Train production reader проверяет полный native
пакет/CSV/history; cold graph и физика выросшей модели сверяются отдельно.
Stopped-state допустим как честный отрицательный результат, но не заменяет
completed certificate и не передаётся в Test как обученный. Ошибка процесса,
неполные данные либо несовместимый reader останавливают серию с сохранением
частичных первичных данных. Исчерпание бюджета не доказывает PhysicalInfeasible.

Для допуска production-модуля предусмотрены шесть серверных проверок на реальных
stock templates/runtime: полнота восьми условий, равенство прочих факторов,
неизменность исходных jobs, повреждение матрицы и budget, идентичность условий
при переносе executable и смене run ID, запрет неизвестной политики/повторного
преобразования шаблона. Эти проверки не исполняют Train.

После Train необходимы native export/import и frozen recognition для валидно
завершённых моделей; эти операции и графики сомы с входными импульсами пока
не объявляются выполненными. СерияD не возобновляется.
