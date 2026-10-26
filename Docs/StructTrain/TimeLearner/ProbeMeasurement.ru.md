# ProbeSpec/Observation: измеритель и проверки интеграции

Добавлен production-модуль PulseLib
`Core/TimeLearner/ProbeObservation.h/.cpp`: неизменяемая спецификация,
ограниченный recorder и явная validity измеренного результата. Полный API,
алгоритм выделения пика и ответственность адаптера описаны в
[TimeLearnerProbeObservation](../../../Libraries/Nmsdk-PulseLib/Docs/Analysis/TimeLearnerProbeObservation.ru.md).

Это часть этапов 6–7, не завершение этих этапов. Legacy-контроллеры продолжают
работать прежним путём; новый контроллер версии 2, его управляющие действия,
автоматическая интеграция revision/growth/retarget и TrainingCertificate ещё
не реализованы. Нет подмены model export/Train→Test измерительной структурой.

## Доказательная область

Адресные проверки используют production recorder, реальные storage-образы,
Environment, NModel и оба learner в frozen characterization. Для Classic
читаются текущие потенциалы физических сом; для Branch — физическая общая сома.
Строки SomaNeuronAmplitude[1..N] у Branch содержат MaxIterSomaAmp старого
контроллера и не используются как поток новых отсчётов.

До первого стимула строится immutable профиль (LTZ threshold=1 для этой
subthreshold characterization), выполняется штатный cold Reset/первый tick,
затем снимается IsNeedToTrain. Это external stop управления, а не convergence.
Native scheduler рассчитывает дерево один раз. Recorder получает фактические
потенциалы и stimulus edges с native tick-start timestamps. Baseline измерен
на физических каналах и передан явно.

Проверяется штатная пачка из четырёх импульсов при 2000/20000 в Classic и
Branch, окно до 0.56 s. Контрольный индивидуальный Rs намеренно меняется
посреди пробы; semantic identity становится другой и recorder запрещает
valid результат, сохраняя complete покрытие окна. Это fault injection, не
production способ управления общей физикой.

Другие проверки: N>4 окон, ненулевой baseline, plateau без интерполяции,
missing/ambiguous/clipped peak, досрочное закрытие, разрывы/дубли времени,
NaN/Inf и overflow deviation, неверные размеры и schema, исчерпание бюджета,
неполные/повторные stimulus IDs, поздний спайк, отключённый spike capture,
peak до фактического стимула и запрет записи после Close.

Формат внутренней training-пробы schema=1 отличается от recognition CSV
schema=4. Native CSV и JSON fixture сохраняют raw soma/stimulus, полные
windows/baseline/параметры измерения, фактические stimulus events, configured
pattern hash и hash фактических событий, model identity до/после и причины
отказа. Полный production serializer/CLI adapter этого формата ещё требуется.
Spike API проверен адресно; native spike capture/recognition здесь не заявлены.

## Обнаруженные зависимости storage/lifecycle

### TL-017: метаданные TimeStep зависели от предыдущего использования

На root 0ade87374662709ca40720b16be2e4d280e9d50d адресные 17 checks проходили,
но полный CTest на обоих серверах не мог зарегистрировать пять новых neuron
profiles. Диагностический root 69e2df9c0c2cf4d256ea649a01e7ebd7af18c1ee с Rdk
84920e75e07f3940e5f30ea3c7dc2eab26657aa6 уточнил причину:
`$:TimeStep:property_type(expected=769,actual=513)`.

Возвращённый из individual-rate модели экземпляр сохранял public-system mask;
SetEnvironment не восстанавливал режим текущей среды. Rdk
33e8b3a1114cafd065d4088477e55900297af90a синхронизирует эту метаинформацию
при SetEnvironment для каждого узла. Численные частоты и динамика не меняются,
дополнительных Build/Reset нет. Generic Rdk fixture проверяет оба режима и
сохранение heterogeneous 20000/4000; native image fixture проверяет registration.

### TL-018: runtime-видимость ошибочно участвовала в физике образа

После TL-017 общий CTest прошёл, но отдельный native контроль root
0d642dcdddbf03e749054b06c868ac37a843a763 воспроизвёл ложный image_name_collision:
повторная регистрация одной физики
после individual→global считалась другим образом. Rdk
e7690e4a1c0b769951409176c1c2c7bae819181f вводит RdkClassImage-v2: только два
штатных visibility mask TimeStep нормализуются к системному виду. Остальные
type bits и численная частота не исключаются. Проверяются переключения в обе
стороны и обязательная коллизия при изменении 2000→20000.

Описание сравнения остаётся process-local, не научным fingerprint модели.
Исторические v1 артефакты сохраняются как снимки прежней схемы. Generic native
copy diagnostic называет узел/свойство/типы без вывода значений произвольных
параметров. Это исправления владельца Rdk, а не learner-specific wakeup logic.

## Проверки и артефакты

Финальный проверенный root: 2cc43c02df48c071194bc056739d0d77850d0d28,
PulseLib a30bc0cd559eaf9f7ed9bf29b068358f1879ad9b,
Rdk e7690e4a1c0b769951409176c1c2c7bae819181f. На обоих серверах прошли
20 адресных checks, четыре Rdk frequency/mode checks и 4/4 maintained CTest
suites. В PulseLib полном наборе 183 cases: 174 passed, девять skipped
(opt-in long controls и helper, используемый native archive parent fixtures).
На M40 отдельно прошли 16 PulseLib/recorder/image checks и четыре Rdk checks
под ASan с detect_leaks=0. Full ASan CTest и отсутствие утечек не заявляются.

Артефакты: `Reports/StructTrain/TimeLearner/s06-probe-elder1` и `s06-probe-m40`.
Они включают первичные CSV/JSON, pre-test runtime manifests и hashes бинарников,
XML/logs, исходные полные failing suites и cross-mode failure. Невалидные пики
и ещё не определённые задержки имеют optional/null, а не подставленный ноль.
Финальный вариант также отвергает overflow длительности/интервала при конечных
исходных timestamps. Успешные и неуспешные промежуточные сборки подписаны
собственной source closure и не выдаются за финальный tested root.

## Оставшиеся ограничения

### Проверяемая граница повторной native-пробы

Добавлен `NativeProbeRestart.DatasetAndPhysicalResetAtNonzeroModelTime`:
Classic/Branch × 2000/20000 Гц, один построенный граф, три пробы на абсолютном
времени 0.1, 0.9 и 2.0 секунды. Между пробами исполняется обычный scheduler;
Dataset остановлен через StateGeneration=0. На границе сбрасываются только
Neuron и Dataset, затем StateGeneration=2. Повторных Build, learner Reset,
перестройки морфологии и возврата часов к нулю нет. Проверяются полный интервал,
четыре реальных импульса, неизменность semantic model identity/TrainingPhase и
сравнение физических soma samples с первой пробой. Baseline считывается
из компонентов после Reset, а не подставляется в спецификацию.

Dataset Reset устанавливает ResetDelay; его следующий штатный Calculate вызывает
BeginSpikeTrainSample(now). Именно этот tick задаёт SampleStartTime. Поэтому
adapter обязан задавать окна в абсолютном времени относительно фактического
начала пробы, а не относительно нуля Environment или прошлого burst. Сам
ResetDelay ещё не является событием предъявления.

События читаются после native children из NPulseGenerator.OutputPulseTimes,
с удалением уже прочитанных timestamps в пределах текущей пробы. PulseCounter
не является монотонным счётчиком: Dataset сбрасывает генератор перед каждым
FireOneShot. NativeDatasetEvents подаёт четыре соседних импульса и сопоставляет
реальные emission timestamps с четырьмя фронтами. В этом конкретном playback
между ними виден спад; меньшего числа фронтов контроль не обнаружил. Это
генераторные события, а не доказательство приёма импульса каждым downstream-синапсом.

Новая проверка выявила TL-019: Default/Reset/выключенная генерация представляли
пустую OutputPulseTimes как матрицу [0]. При чтении истории это добавляло
несуществующий импульс до первого предъявления. В baseline считались пять событий
вместо четырёх, первое t=0. Исправление для NPulseGenerator и Multi хранит 1×0
без событий и сохраняет настоящий t=0 как отдельную запись. ABuild также
согласует выход с уже очищенной внутренней историей. У старого альтернативного
NPulseSimpleLTZone::ACalculate2 удалено безусловное обращение (0,0) к истории
генератора: передаётся целая матрица. Динамика Output/Potential, расписание и
число импульсов этим изменением не корректируются. Нулевые placeholders в
собственных OutputPulseTimes других LTZone не объявляются исправленными этой
проверкой; их контракт требует отдельного включения в spike adapter.

Первый production adapter должен явно проверять поддерживаемый источник и
порядок вычисления. Это правило не обобщается автоматически на UseTransitSignal,
multirate, неизвестные генераторы или несколько вызовов дочернего генератора
между чтениями. OutputPulseTimes — ограниченная текущая история, не persistent
event log: после Reset она очищается. События необходимо забирать на каждом
штатном tick; между пробами cursor создаётся заново. Zero-ISI записи Dataset
не следует считать одновременно предъявленными: фактический playback может
развести их по ticks. Hash фактических событий остаётся отдельным от hash ISI.

Описанные controls проверяют frozen-граф в режиме all-input; Branch solo-routing,
приём действия контроллера из learner и передача результата FinalVerification
ещё не реализованы этим изменением. Прежняя Git closure ниже относится к API
recorder; новые controls и исправления имеют отдельную версию проверки.

### Серверная проверка повторных проб и TL-019/020

Проверенный root a9f985a3b3a3a436e01205ddb50341952d57c83e, PulseLib
d9b6d1529aa2a1b8d900978ac0d4127103909435, Rdk
f924023e78eb2f0775cca301272606b98de0f8f1, Bin
1c1c2e5064373b47d523fd6735aebe6785f2787d. На Elder-1 и M40 прошли шесть
адресных controls и четыре maintained CTest suites. Полный PulseLib: 210 cases,
201 passed, девять skipped — прежние opt-in long controls и archive helper,
исполняемый в дочернем процессе по вызову parent fixtures. M40 ASan: шесть
адресных controls с detect_leaks=0; полный ASan CTest и отсутствие утечек не
заявляются. Полный численный набор выполнялся только на серверах.

Строгий baseline root f18bbd7 (полный SHA находится в runtime manifest)
воспроизводит шесть failures на каждом сервере. Отдельный диагностический
root a279e57 с уже очищенной историей выделяет TL-020: Single проходит, Multi
не публикует emission timestamps и имеет несогласованный default count.
Исправление d9b6d15 восстанавливает публикацию Multi и native dimension ownership.
Контроль реального t=0, последующего Frequency=0, Reset и смены 1→2→1 путей
использует настоящие storage-компоненты и scheduler, без тестовых копий функций.

В трёх повторных пробах каждого frozen-графа сохранено по 1121 soma frames при
2000 Гц и по 11201 при 20000 Гц. Повторный анализ исходных CSV на каждом сервере
дал maximum raw-potential difference=0 для всех общих отсчётов. Сохраняются все
отсчёты, absolute/relative time и stimulus output. Complete/valid и model identity
проверяются отдельно; фазу learner тест не продвигает. Это начальные all-input
графы, а не доказательство сходимости обученной модели или её robustness.

Артефакты находятся в Reports/StructTrain/TimeLearner/s07-pulse-elder1 и
s07-pulse-m40: baseline/исправленные runtime manifests, binary hashes, CSV/JSON,
CTest и ASan logs/XML, повторный серверный анализ и checksums. Ранняя
диагностическая версия теста ошибочно ожидала меньше четырёх фронтов; исправленный
baseline подтверждает четыре фронта и пять timestamps с лишним нулём. Старый
diagnostic log не является финальным критерием приёмки.

Bin commit 9fb8d6122aa8b80625101403be75e5c9de2a3b83 уточняет только три
ClDesc: пустую историю, signed counters, размерности и неподдерживаемую случайную
ветвь Multi. XML и соответствующие поля проверены из Git на обоих серверах;
эта metadata-проверка не выдаётся за проверку UI или повторную численную сборку.

CapturedPerInput сохраняет сравнение с rawPotential, соответствующим прежней
InitialSomaPotential. Дополнительное amplitude=peak−baseline нельзя молча
превращать в другую математическую цель. Новый recorder хранит оба значения.

Recorder обнаруживает только revision, переданную адаптером. Cache требует
владения всеми model edits; start/end hash сам по себе не доказывает отсутствия
неучтённого изменения и восстановления внутри пробы. Native fixture использует
замороженный граф и явный revision provider при fault injection. Обобщённый
producer revision всей ModelSpec/reset policy ещё предстоит подключить.

Эта серия не является обучением, проверкой всех solo-входов, независимым Test,
историческим replay августа или доказательством сходимости. Ни valid peak,
ни complete process не превращаются в Exact/Done. Августовские визуальные
4/8–6/8 сохраняют свою доказательность исходного протокола.

## Принятая Git closure

| Репозиторий | Develop merge |
|---|---|
| Rdk | f924023e78eb2f0775cca301272606b98de0f8f1 |
| PulseLib | dddd1d1187f22ff03832a5f44837a9ae47199b04 |
| Bin | 1c1c2e5064373b47d523fd6735aebe6785f2787d — без изменений этого подэтапа |

Child commits опубликованы до корневого merge. Production Core совпадает с
проверенными e7690e4a (Rdk) и a30bc0cd (PulseLib); после них менялись только
документы. Все 933 artifact hashes и gzip payloads проверены локально как
данные; численные/интеграционные проверки выполнялись на указанных серверах.

### Принятая closure подэтапа повторных проб / TL-019/020

- PulseLib develop merge: a78437fcf7750d271da1676b7eadc6a5e8559c4e.
- Bin develop merge: e78596e9639a841cd1989d73df7fe614419770ce.
- Rdk не менялся: f924023e78eb2f0775cca301272606b98de0f8f1.

Production Core совпадает с проверенным d9b6d1529aa2a1b8d900978ac0d4127103909435;
дальнейший PulseLib commit 0a228be меняет только документацию. Bin меняет только
ClDesc, проверенные из Git отдельно от численного runtime. Детальные source
closures до сборки/тестов сохранены в каждом manifest; merge SHA их не заменяет.
После получения результатов через Git проверены 1321 artifact hash во всём
поддерживаемом Reports-разделе и целостность gzip payloads; численный повторный
анализ первичных CSV выполнен на серверах. Эти проверки не закрывают остальные
требования исходных этапов 4, 6 и 7.
