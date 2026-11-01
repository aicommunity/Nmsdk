# Август: проверенный cold start и границы повторного обучения

Это продолжение [saved-state replay](HistoricalAugustReplay.ru.md) на исходном
root`de02a3809395dd0bbd11e2ba792bfc04a51c89f3`/PulseLib
`cbf76fbe077a7003dccf72b142d7136721fa1afb`/Bin
`1c1464e248f8744e858bd66df0be99e39969fd65`/Rdk
`237ce0f177280049ab1eae305a09ce3e8c63833a`.
Новый контроллер V2 и C++ исторической версии здесь не менялись.

## Что нельзя считать холодным стартом

`SelectivityPhaseA/EXP00_baseline/Train` содержит сохранённую обученную модель:
IsNeedToTrain=0, L49/41/25/1. Имя каталога Train не доказывает новое обучение.
`TimeNeuronTimeLearner` того же Bin также содержит длинный сохранённый граф,
хотя IsNeedToTrain=1. Снятие/установка этого флага не восстанавливает исходную
физическую модель.

До дорогого Train выполнены четыре owned native операции с пределом0.0005s,
раньше первого входного импульса0.0105s. Проверяются экспортированные дочерние
объекты, их классы/имена, сопротивления, selected physics и состояние генератора.
Проверка возврата true или только parent-полей не используется как доказательство.

| Контроль | Parent L после запуска | Реальных dendrite segments | Итог |
|---|---|---:|---|
| Неизменённый saved trained |49/41/25/1|116|Warm/saved control, не cold|
| Native State-file reset |1/1/1/1|4|References0, Ns1, tip Rs86МОм, gamma−1, Need1, PulseCounter0; one-shot flag потреблён|
| Только parent cold overlay |1/1/1/1|116|Graph/parameter mismatch; запрещён как исходное состояние Train|
| State-file задан, загрузка состояний выключена |49/41/25/1|116|Запрос не применён; входной State-file остался с flag1|

Главная обнаруженная ошибка постановки: parent-only overlay в этой исторической
load-последовательности не заменяет сохранённый дочерний граф. Простая запись
L1/1/1/1, Rs86МОм и references0 создаёт правдоподобный набор полей над116
сегментами. Это не равенство эффективных моделей и не холодное обучение.
Общая причина на уровне всего Rdk этим опытом не доказывается; исторический
код не исправляется learner-specific цепочками повторных Build.

Первая gate-попытка a1 остановилась на неожиданном расхождении после трёх
Console операций. Попытка a2 сохранила его как измеренный отрицательный
контроль и завершила все четыре операции. Изменение относится к валидации
эксперимента, а не к математике исторического алгоритма.

## Штатный lifecycle-путь

ResetToUntrainedState объявлен как bool/ptPubState, default=false. Setter
сам по себе не выполняет реконструкцию. Legacy AReset читает one-shot,
сбрасывает его и отдельно вызывает ResetToUntrained. При отсутствии подходящего
cold snapshot тот задаёт L1/Ns1/references0/tip Rs=SynapseResistanceBase,
gamma-auto−1, очищает управляющую историю и вызывает собственный BuildStructure.
Физическая модель создаётся через штатные storage-образы. Обычный Reset без
явного запроса не приравнивается к этой операции; все каналы не обязаны быть0.

Используется штатный файл состояния:

```xml
<SaveProperties ModelName="Model">
  <Model Class="UModel">
    <Components>
      <NeuronTimeLearner Class="NNeuronTimeLearner">
        <State><ResetToUntrainedState Type="b" PType="258">1</ResetToUntrainedState></State>
      </NeuronTimeLearner>
    </Components>
  </Model>
</SaveProperties>
```

Project.ini сохраняется в реальном диалекте с `<00>`; адресно изменяются
ProjectAutoSaveStateFlag=1 и StatesFileName=States_00.xml. В историческом Rdk
OpenProject загружает Model, Parameters, затем State только при включённом
ProjectAutoSaveStateFlag; после этого применяются частота, InitAfterLoad и
ResetAfterLoad. Само наличие файла/имени не доказывает загрузку. Отрицательный
контроль с выключенным flag подтверждает это в runtime.

Источники: Rdk указанного SHA, UApplication.cpp:2335–2444,
LoadStatesFromFile:3231–3248; UComponent.cpp:88–124 (State/Parameters masks).
PulseLib указанного SHA: AReset, ResetToUntrained,
ApplyLoadedAnchorProperties и объявление ResetToUntrainedState.
Это legacy-путь: native-owned V2 AReset имеет другой контракт, описанный в
[обзоре reset properties](ResetAndLoggingPropertyContracts.ru.md).
Файл запроса one-shot не является checkpoint всей динамики.

## Доказательства и проверки

[Primary](../../../Reports/StructTrain/TimeLearner/s11-august-coldstart-elder-a2/README.md),
commit`b8f8322645019dc74262aeeb86ad2689047eb461`:311 members/59516B xz.
Producer a1`f97c956895795e88306765fda25a5350b2eae70a`,
a2`df739bb450481b4aaaf2d81de98485492991a60b`.
Сохранены обе попытки, original/post-run Model/Parameters/States, runtime,
process receipts и подготовленные входы.49 prepared files семи случаев
восстановлены production prepare после завершения и побайтно подтверждены
исходными сохранёнными pre-run SHA256. Это явно отмеченная реконструкция
точных входов, а не утверждение об их первоначальном отдельном архивировании.
Начиная с`6a32300d48357ceeeca2df141bd5134f71437ab5` prepared copy сохраняется
до запуска автоматически.

Reader/guard`f45239e64a65d4488feb92b6fd30aba10c428f2a`:
[Elder7/7](../../../Reports/StructTrain/TimeLearner/s11-august-coldstart-reader-elder-a1/README.md),
[M407/7](../../../Reports/StructTrain/TimeLearner/s11-august-coldstart-reader-m40-a1/README.md).
Пакет311 members восстановлен через Git на обоих workers; native exports
повторно прочитаны production readback. Проверены49 input hashes, успешный
допуск настоящего gate и отказы для false gate, подменённого readback,
незавершённого процесса и другого runtime. Новые C++ расчёты этими readers
не выполняются. Outer/member hashes дополнительно проверены локально.

## Ограниченный полный Train

Отдельная попытка cold Train a1 остановилась до Console: dict-only JSON loader
был вызван для списка pre-run files. Это исправлено; попытка сохраняется как
ошибка launcher с нулём native операций. Она не считается обучением.

Рабочая попытка a2 использует producer
`6a32300d48357ceeeca2df141bd5134f71437ab5`: те же точные входы native-state
контроля, проверенные по pre-run hashes, четыре входа/N1/2000Гц,160 model seconds,
wall limit1800s, минимум2GiB свободно до подготовки. Sources/runtime не меняются
в ходе задания. Задание завершилось0, legacy phase2/Need0, L49/41/25/1,
116 сегментов; все четыре заново измеренные references совпадают с сохранённым
EXP00 baseline. Primary commit
`8ee71bcb67c9f5325e95517eee8dd26250e61045` сохраняет83 файла/5374628B xz,
включая все девять native training telemetry streams по320000 отсчётов,
подготовленные входы, полный экспорт и неудачную wrapper-попытку a1.

Production `historical_model.serialized_neuron` сравнил весь сериализованный
нейрон с исходными сохранёнными Train и Test:604 компонента,8333 параметра,
496 входящих сериализованных связей, включая порядок компонентов и связей.
Все три представления совпали; identity
`ed11c257e5b0e01c5ed3ccfc5bd397f93984cf6e544ab4ab87681627d445c474`.
Числа нормализуются с сохранением целочисленной точности и проверкой finite;
неизвестные типы сравниваются консервативно. Это отдельная историческая схема,
не V2 ModelArchive и не checkpoint динамики/контроллера/внешнего Dataset.
Reader source`3c14bd295c4597702b88975820ff0626e9e2ac66` прошёл10/10 на каждом
worker: реальные экспорты, Rs/C/class/order, утрата узла/источника связи,
decimal comma, nonfinite и целые за пределами точности double. Proof commits
`d8b7decbc0b162979d3f678fb58223f1193b191e` и
`707fb46f21a0f6c482712dcde3382fd810e8793d`; outer/member hashes проверены локально.

## Перенос и исходная последовательность загрузки Test

Исходный Test задаёт learner StructureBuildMode=1 в Model и0 в Parameters.
Это разные слои штатной загрузки. В первой попытке frozen Test a1 producer
ошибочно поставил0 в обоих файлах. Расчёт записал CSV, но Console завершился
SIGABRT при освобождении памяти; native cached SomaNeuronAmplitude содержал
только два значения вместо пяти. Такой результат классифицируется process_error,
а CSV не принимается как успешное воспроизведение.

Исторический ABuild инициализирует размерные измерительные буферы внутри
BuildStructure; при пропуске этого пути остаётся default N=1. Полная идентичность
физического графа сама по себе не доказывает корректность private workspaces.
В актуальном Classic коде также остаются незащищённые записи этих матриц;
Branch содержит отдельное расширение в Calculate. Применимость дефекта к текущим
путям требует собственного normal/ASan native воспроизведения и исправления у
владельца lifecycle. Исторический C++ не меняется; добавлять повторные Build
или исправляющие записи на каждом тике в pipeline нельзя.

Producer`dcaf6d12d9a94d02051819620b4eebc62fe82f8b` сохраняет исходные Model1 /
Parameters0 и перед каждой полной матрицей выполняет отдельный prestimulus
native import gate: успешное закрытие процесса, полный readback нейрона,
пять cached soma values, отсутствие входного импульса. Полный Test использует
исходную подготовленную пару, а не изменённый post-save Model короткой пробы.
Граф переносится целиком из fresh cold Train; Dataset заменяется явно
объявленной исходной тестовой матрицей. Завершение всех трёх frozen Test и
их визуальная приёмка пока не заявлены.

Process completion и legacy Need0 не означают Exact V2. Итог маркируется
legacy_done_uncertified либо unfinished_at_model_budget; сертификат и
scientific verdict не создаются. После незавершённого Train обычный обученный
Test запрещён: возможен только отдельно объявленный diagnostic evaluation.
Полный перенос графа, post-import readback, frozen evaluation и временные
диаграммы всех Test-паттернов остаются самостоятельными необходимыми проверками.
