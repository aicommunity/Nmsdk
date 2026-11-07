# Native channel diagnostics: candidate contract

Адресный observer прошёл ограниченную приёмку на M40 для воспроизведённых
low/Retry Classic и Branch. Это измерительный инструмент, не исправление
assignment и не завершение этапа7. [Verification](NativeChannelDiagnosticsVerification.json).

Probe job schema3 добавляет явный boolean `channel_diagnostics` к full stopped
import schema2. False не создаёт дополнительных файлов. True записывает
`probe_diagnostics_N.json` отдельно от прежних probe JSON/CSV. Job1/2 и их
execution schemas сохраняются; job3 выдаёт execution4 с явным inventory.
Новый фактор не меняет target, storage, модель, порог или scheduler.

Точка наблюдения — уже существующий native `onSample` после расчёта детей.
Observer не вызывает Build/Reset/Calculate и не пишет component properties.
Для каждого soma читаются SumPotential, Feedback, Exc/Inh Output и
SumChannelInput; дополнительно LT Potential/Output и реальные новые
OutputPulseTimes. Metadata фиксирует пути, фактические classes и sample phase.
Для stock Classic4 это26 scalar signals, для Branch1 —8. SI units не установлены.
Поля разных компонентов относятся к их штатному порядку расчёта; чтение в одной
фазе не означает одинаковую причинную задержку внутри дерева.

SumSynapticInput исключён: в NPulseChannel.cpp ACalculate2 он не обновляется.
GetSynOutput базового канала также возвращает0. Эти значения нельзя выдавать
за независимое измерение синаптического тока. Исправление их общего контракта
требует отдельного аудита владельца и подтверждения использующих классов.

Reader строго проверяет schema/inventory, source revision и component classes,
размерность, finite values, clock, полноту, равенство soma с прежним primary CSV,
монотонность LT timestamps и отсутствие будущих events. Exc/Inh физика этим
reader не реконструируется независимо: их источник доказывает native producer,
source closure и actual graph. Частичные captures не дают positive measurement.

Выполненная область M40 и оставшиеся проверки:

1. Изолированная Console/Test сборка; прежний runtime неизменен.
2. Два exact archived source × observer Off/On, все4 jobs до первого probe.
3. Actual graph identity, idle controller, unchanged model; native source import.
4. Побайтное равенство Off/On CSV и точное совпадение с исходными волнами.
5. Восемь checks на actual corpus: capture, invariance, повреждённый soma value,
   class, future spike, missing sample, duplicate clock и non-boolean factor.
6. Действующие scoped ISI/observation12 и waveform/prefix10 controls.
7. Primary/source/runtime/process closure опубликованы в Git; приёмка графиков приведена ниже.

CLI нового study:
`python -m Scripts.StructTrain.TimeLearner.stock_channel_diagnostics STUDY --runtime RUNTIME --output NEW`.
Запуск — только через managed worker с leases и resource limits. Этот CLI
не выполняет Train и не выдаёт классификационный verdict.


## Фактические результаты M40 — 07.11.2026

Compiled root18d4d77b90d01168a5cf9b8831ba0bea57967e91 / Pulsefe382a0.
12/12 native controls и18/18 Python readers прошли без skips. Четыре реальные
пробы (две топологии × schema2 Off/schema3 On) завершены. CSV Off/On совпали
побайтно; потенциалы и стимулы воспроизвели исходный Train, relative clock
совпал с исходным допуском округления. Model graph и controller не менялись.

Branch записал четыре LT events:0.0295,0.1095,0.2695,0.5095с.
Classic записал восемь:0.011,0.0285,0.091,0.1085,0.251,0.2685,0.491,0.5085с.
Таким образом, до второго входа0.09с у Classic два LT events, у Branch один.
Это реальные OutputPulseTimes, а не спайки, восстановленные по пикам сомы.
Эти пробы не являются восьмипаттерновой оценкой классификации.

Первая попытка root3bdef559 не скомпилировалась из-за обращения GetSize к
UProperty; расчётов не было. Исправление использует штатный GetData().GetSize().
Неудачный source/log/terminal сохранён вместе с успешной попыткой. Все485+22
members и source hashes обеих попыток сверены с точными commits; группы
закрыты и leases released. Два предыдущих runtime проверены на сервере до/после.

Не закрыты второй сервер, direct schema3 False и весь interruption/
intervention/profile scope. Reader не подтверждает
Exc/Inh независимо от native producer. До контролируемого вмешательства
не объявляется установленной общая причинная природа дополнительных максимумов.


## Адресный ASan и совместные графики

Тот же compiled root18d4d/Pulsefe382a0 прошёл на M40 адресный ASan:
12 native controls, четыре реальные Off/On пробы и18 Python readers без skips.
В пяти процессах подтверждена загрузка libasan; detect_leaks=0, поэтому это
не доказательство отсутствия утечек. Off/On CSV и исходные Train волны
сохранены; прежние runtime не изменились. [Приёмка](NativeChannelDiagnosticsAsanVerification.json).

Построен [совместный временной отчёт](NativeChannelJointVisualVerification.json):
пять сом,216 views,652 файла/73375213B в кэше M40
`/media/user/Data/TimeLearnerRefactor/ReportsCache/native-channel-joint-normal-a3`.
Plot source root96431ad; первичные native данные взяты из e98df4e и сверены
с Git перед построением. Новых расчётов моделей для графиков не выполнялось.
Каждый рисунок показывает потенциал сомы с фактическим входом, изменения
Exc/Inh относительно первого отсчёта, Feedback/LT Output и LT Potential
с фактическим порогом. Начальные Exc=-1 и Inh=+1 не считаются нулём.
Полные окна имеют общий Y по панели; детали максимумов — явно отмеченный
локальный Y и все native samples. Это разные масштабы, их нельзя сравнивать
по высоте кривой на странице. Реальные LT timestamps нанесены пунктиром.

Четыре выбранных PNG (два первых50мс окна и две детали максимумов) сверены
с Git и просмотрены по отдельности. [Ручная QA](NativeChannelJointSelectedVisualQA.json)
не распространяется на весь кэш. В детали Classic около0.0485с виден третий
максимум при нулевых текущих Feedback/LT Output; потенциал LT ещё отрицателен.
В детали Branch около0.1945с разрешён слабый максимум порядка1.87e-5.
В обеих деталях новых входных импульсов нет. Эти наблюдения сами по себе
не доказывают причинную независимость от предшествующей обратной связи:
она воздействует также на дендриты, а состояние каналов сохраняет историю.

Для причинного разбора требуется отдельный single-pulse characterization
и контролируемое вмешательство. Он не должен подменять штатную пачку Train,
менять target или выдавать диагностическое наблюдение за сертификат обучения.
