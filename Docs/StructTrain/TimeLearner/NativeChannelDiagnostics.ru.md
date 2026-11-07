# Native channel diagnostics: candidate contract

Новый адресный observer готовится для воспроизведённых low/Retry Classic и
Branch. До серверной приёмки не является исправлением assignment или этапа7.

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

План серверной приёмки:

1. Изолированная Console/Test сборка; прежний runtime неизменен.
2. Два exact archived source × observer Off/On, все4 jobs до первого probe.
3. Actual graph identity, idle controller, unchanged model; native source import.
4. Побайтное равенство Off/On CSV и точное совпадение с исходными волнами.
5. Восемь checks на actual corpus: capture, invariance, повреждённый soma value,
   class, future spike, missing sample, duplicate clock и non-boolean factor.
6. Действующие scoped ISI/observation12 и waveform/prefix10 controls.
7. Primary/source/runtime/process closure в Git, затем отдельные графики Exc/Inh/LT.

CLI нового study:
`python -m Scripts.StructTrain.TimeLearner.stock_channel_diagnostics STUDY --runtime RUNTIME --output NEW`.
Запуск — только через managed worker с leases и resource limits. Этот CLI
не выполняет Train и не выдаёт классификационный verdict.
