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
7. Primary/source/runtime/process closure опубликованы в Git; отдельные графики Exc/Inh/LT ещё требуются.

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

Не закрыты ASan, второй сервер, direct schema3 False, весь interruption/
intervention/profile scope и новые channel graphics. Reader не подтверждает
Exc/Inh независимо от native producer. До контролируемого вмешательства
не объявляется установленной общая причинная природа дополнительных максимумов.
