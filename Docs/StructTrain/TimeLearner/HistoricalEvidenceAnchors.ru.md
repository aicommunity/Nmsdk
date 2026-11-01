# Исторические опорные состояния августа: точные Git-источники

Часть реестра этапа 1: шесть условий, четыре корневых снимка и 65 адресованных
файлов (commit + путь). [JSON-реестр](HistoricalEvidenceAnchors.json) содержит
все записанные gitlinks, наличие commit objects, blob SHA-1/SHA-256, модели,
Parameters/Project/Interface, исходные CSV и отчёты. Выполнена проверка Git-объектов;
численные прогоны, пересчёт CSV и runtime-проверка полноты локально не выполнялись.

## Наблюдения и области утверждений

Визуально подтверждённые пользователем августовские 4/8, 5/8 и 6/8 остаются
рабочими наблюдениями исходного порядка и ITI при плохой разделимости. Пользователь
не сообщил однозначную привязку каждого визуального просмотра к конкретному CSV,
поэтому такая привязка не выдумывается. Перестановки и увеличенный ITI проверяются
как отдельный протокол. Историческая точность не доказывает текущий Exact.

| Условие | Точность в историческом отчёте | Target / FP по отчёту | Root данных |
|---|---|---|---|
| aug-phase-a-baseline | 4/8 | да / 2, 4, 5, 6 | `de02a380` |
| aug-phase-a-threshold-0130 | 5/8 | да / 2, 4, 6 | `de02a380` |
| aug-phase-a-threshold-0135 | 6/8 | да / 4, 6 | `de02a380` |
| aug-psi-k25 | 6/8 | да / 4, 6 | `bf2a6895` |
| aug-branch-ampeq | 6/8 | да / 2, 6 | `50b0cac1` |
| aug-branch-nextseg | 7/8 | да / 6 | `50b0cac1` |

Числа перенесены из конкретных архивных отчётов/README, не пересчитаны новым
scorer. Для PSI k=2.5 отчёт явно указывает target hit и FP trials 4/6. Branch 7/8
является сообщением прежнего критерия, не новой научной приёмкой и не отдельным
утверждением о визуальном подтверждении пользователем. Late-response критерии
более поздних версий нельзя автоматически приписывать CSV этой даты.

Phase A 5/8 и 6/8 получены Test-only подбором FixedLTZThreshold на прежней
матрице. PSI и Branch описаны как cold train в отчётах; начальная холодность
самих процессов пока не доказана новым replay. Независимый holdout не установлен.

## Уточнение Branch: данные и отчёт — разные commits

`50b0cac1ade4f468be82a3d35e4ac6f5514ceb56` записывает Bin
`26c1770dfdb27664b806ef5f760fa7b03e731e7c`, PulseLib
`df1bdfaec03a9603258ed59ba7db10ac0b717c5c`, Rdk
`941920d390054fe5dfd458742ec6bc9dc89b8d0c`. Модели и CSV существуют в flat layout:

- `TimeNeuronTimeLearnerBranch` — Train;
- `TimeNeuronTimeLearnerBranchTest` — baseline Test;
- `TimeNeuronTimeLearnerBranch_NextSegInh` — Train с торможением;
- `TimeNeuronTimeLearnerBranchTest_NextSegInh` — его Test.

Каталога `TimeNeuronTimeLearnerBranch/Train` в этом снимке нет. Сам
`REPORT_ampeq_nextseginh.md` тоже ещё отсутствует. Он добавлен Bin commit
`82ec58711cb116b3c20ddcca774a8a4018bc8960`, которому соответствует root
`d8a1e711fc6edb0432ac09ad579860172e516db9`. Проверено: единственное изменение
Bin между этими снимками — добавление отчёта; остальные корневые gitlinks
совпадают. Поэтому отчёт можно связать с прежними данными, сохранив два source SHA.
Путь отчёта тогда: `Configs/SpikeSamples/StructTrain/TimeNeuronTimeLearnerBranch/REPORT_ampeq_nextseginh.md`.
Современный путь с `/Train/` нельзя использовать для исторического checkout.

## Наличие в Git и полнота воспроизведения

Дополнительный контроль EXP02 Test_avg1: все шесть файлов модели/конфига/CSV
есть в августовском Bin `1c1464e248f8744e858bd66df0be99e39969fd65`, хотя такого
каталога нет в текущем checkout. Это не потерянные исторические артефакты.

В Project.ini сохраняются декларированные DefaultTimeStep/GlobalTimeStep/
UseIndTimeStepFlag; они не заменяют effective runtime readback. Для найденных
условий ещё не восстановлены все reset/ITI/normalization/pattern identities,
разрешение внешних ресурсов, actual worker HEAD и binary/library hashes.
Полнота окна старого CSV остаётся unknown: отсутствующие поля не достраиваются.

Root/gitlinks доказывают восстанавливаемый снимок исходников и файлов, но сами
по себе не удостоверяют код загруженного тогда процесса. В реестре это разные поля.

Дальнейшая приёмка: saved-state replay в исходных условиях, отдельно cold retrain,
затем order/ITI controls на серверах через jump host. Оставшиеся августовские
серии и сентябрьско-октябрьские волны ещё не охвачены этим частичным реестром.
