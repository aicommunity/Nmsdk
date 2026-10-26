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
