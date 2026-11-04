# Пробы полного stopped-state и контроль Rs

04.11.2026. Это диагностическое исследование двух незавершённых stock-моделей
NSPNeuronGen, ControllerVersion=2, N1, четыре входа, 2000 Hz, порог100,
без LT-мембраны. Не завершённый Train, не калибровка и не классификация восьми
паттернов. Измеряется реакция на один исходный target training pattern.

Предыдущая проверка показала, что ModelSpec с совпадающими L/Ns/Rs создаёт
лишние банки синапсов: [cold graph gate](FixedGeometryResistanceControl.ru.md).
Новый job schema2 использует полный `ImportNativeLearnedState`, включая
действительный граф, связи, child_order и индивидуальную физику. Ни один
лишний узел не удаляется вручную, исходные storage-образы не переписываются.

## Протокол и lifecycle

```text
audit source stopped package against all original primary trials
import through native learned-state API
Build / Init / explicit native Reset
verify exact archived graph and actual individual parameters
freeze imported control context, references and observed-packet hash
if an Rs intervention is requested:
    measure a real complete source-state burst
    consume its result, acquiring the legal native edit boundary
    apply individual bank parameters through the native model editor
measure the requested full burst using the native scheduler
verify unchanged model during the probe and unchanged training control
```

Rdk lifecycle не изменён. Возвращаемые bool Build/Calculate/Reset не проверяются
как сигналы ошибки. Дочерние компоненты вычисляет scheduler, вложенного Calculate
нет. Explicit Reset очищает управляющую динамику; сохранённые references и
observed packets остаются историческим контекстом. Пробы не добавляются в
историю Train и не создают сертификат. Его отсутствие проверяется отдельно.

Native editor требует consumed probe boundary. Вспомогательная полная проба
может иметь невалидную идентификацию пиков; это не мешает легальному изменению
физики после закрытого окна. При незакрытом окне изменение запрещено. Если эта
вспомогательная фаза прервана, задача сохраняет baseline CSV/JSON, не применяет
Rs и пока не формирует полный итоговый execution report. Отдельная приёмка
фазовых cancel/timeout исходов schema2 остаётся открытой.

`source-import.json` доказывает точное восстановление до вмешательства.
`initial-state.json` и `final-state.json` описывают фактическую модель измерения.
`controller-before/after.json` фиксируют импортированный управляющий контекст:
переданные в nested summary model arguments относятся к source boundary и
не должны использоваться как физика изменённого кандидата. Для неё нужны
initial/final state. `probe-configuration.json` — внутренний контекст протокола,
не замена полного model archive; один ModelSpec по-прежнему недостаточен.

## Контроль условий

Для каждой топологии выполнены три варианта:

1. Source replay: полный импорт без изменения Rs, основная проба начинается
   при модельном времени0.
2. Matched control: реальная вспомогательная проба, затем запрос прежних Rs;
   основное окно начинается при1.8005 s.
3. Rs intervention: такая же вспомогательная проба, затем новое Rs;
   основное окно тоже начинается при1.8005 s.

Сравнение эффекта Rs использует только варианты2 и3. Проверены одинаковые
абсолютные времена каждого sample, фактические input rows и stimulus events,
runtime и побайтное совпадение вспомогательных source traces. Простой сдвиг
кривых к onset не считается доказательством совпадения условий. Исходный
source replay остаётся отдельным контекстом.

Classic: L=54, изменяется только банк input0. Branch: prefix=[15,15,15,1],
input2 использует один общий банк с логическими владельцами[0,1,2]. Изменение
всех трёх значений обозначает **одно физическое вмешательство**. Rs меняется
с86000000 на69551260.1240013; L, Ns, C, Rm, кинетика, порог и связи сохранены.

## Измеренный результат

| Топология | Максимум выбранной сомы: control → changed | Максимальное абсолютное отличие кривых | Различимые волны |
|---|---|---|---|
| Classic |0.004504819155902173 →0.0055863819453317864|0.0010815627894296131|3 →3|
| Branch |0.006103650024966156 →0.007569154107898268|0.001465504082932112|3 →3|

Потенциалы приведены в native model units; SI-калибровка этих отчётных каналов
не установлена. Normal и ASan дали одинаковые указанные числа. Эффект Rs на
форму/амплитуду есть; совпадение числа максимумов не означает неработающий
параметр. Однако выбранное Rs не восстановило четыре отдельно определяемые
волны по текущему ordered-whole-burst критерию. Это валидный отрицательный
результат данного контроля, а не доказательство PhysicalInfeasible, бесполезности
N1, C-trim или отсутствия работавших августовских4/8–6/8.

Окна закрыты и численно конечны; peak assignment остаётся `missing`. Spike
recording выключен, поэтому spike response неизвестен. Accuracy, FP/FN и
успех распознавания из этих проб не вычисляются. Модели остаются диагностическими.

## Код, проверки и воспроизведение

Native source `a42ff9a0aa8cf1641f87fec1524a272b5430aa5f`, PulseLib
`541bf89b9966f63ca5131fa57a31a9ae3f5820ea`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`. Каждый worker выполнил четыре
исходных run и два дополнительных matched control. Run с вмешательством или
matched control включает одну вспомогательную и одну основную пробу; всего
десять native-проб на worker. Они не являются независимыми обучениями.
На обоих worker шесть readers
проверили import, legal boundary, неизменную историю и отклонение скрытого
изменения C. По два cold controls дали восемь primary files, побайтно равных
ранним schema1 пробам. Leak detection ASan выключен.

CLI: `probe-job prepare-stopped SOURCE_STATE --input-index N --trial-id ID
--output JOB`, опционально `--resistance-intervention JSON_ARRAY`;
`probe JOB --source-stopped SOURCE_STATE --runtime-manifest R --wall-seconds S
--output NEW`. Исходные primary siblings обязательны. Для матрицы контрольных
запусков: `probe-job analyze-matched RUNS --output AUDIT` и
`probe-job report-matched RUNS --output NEW_CACHE`.

Для компактной публикации source snapshots восстанавливаются побайтно из
уже опубликованного Git archive, без изменения run manifests. Базовый source
proof `e5fa71d745119af0d818059f497dd226f4c7c25d`, путь
`Reports/StructTrain/TimeLearner/s07-stock-threshold-pair-normal-a3/primary.tar.xz`.
Команды `primary-reuse pack/restore` проверяют полный commit, archive SHA256,
каждый member и замкнутый набор файлов. Недоступный reference не заменяется
серверным кэшем. Новые compact bundles, их roundtrip и рисунки ещё проходят
приёмку; окончательные proof commits будут добавлены после проверки.

Полные этапы5–12 остаются открытыми. Следующий алгоритмический вопрос —
конечный поиск при неидентифицируемой волне и бюджет допустимых отклонённых
кандидатов; восстановление четвёртого максимума этим контролем не достигнуто.
