# Ненужная временная телеметрия в native model archive

Статус: подтверждённый адресный дефект размера/стабильности артефактов;
исправление реализовано в отдельной ветке, серверная проверка ещё требуется.
Отрицательный научный результат отсюда не следует.

Normal A1 root420befe14 выявил чрезмерные ожидания нового теста. В 2000 Гц
между двумя exports различались transient buffers отдельных image instances:
InputFeedbackSignal 0×0 → 1×1 с нулём. После native Load/Init пересчитывался
производный NPulseChannel.TimeConstant, соответствующий индивидуальной C.
Это не остаток StepDuration и не обещанный dynamic checkpoint. Исходные
failed assertions и witness packages сохраняются. Проверка уточнена:
полный snapshot живого графа до/после изменения только counters должен быть
побайтно одинаковым; storage closure должна иметь одинаковую полную semantic
identity; legacy import — сохранять все параметры/связи и иметь нулевую
StepDuration в новом export. После import полный native XML может отличаться
пересчитанными производными State. Fresh-process waveform проверяется отдельно.
Другие transient image buffers этим изменением не канонизируются. Очередь
ASan для прежнего420befe14 отменена; действующий C2 не прерывался.

PulseLib `dc7edb2384633d4a1ce65bb40d2f5c8927482896` нормализует только
`State/StepDuration` приватной native XML-копии. Проверяет соответствие реальному
графу, scalar/type layout и полноту дочерних компонентов; живые значения не
меняет. Root spec `native-archive-telemetry-v1.json` содержит шесть проверок:
две новые 2000/20000 Гц, включая fresh-process matrix/boundary waveform, и
четыре прежних отрицательных/совместимых archive controls. Ещё требуется
normal/ASan и регрессия schema2 learned/stopped/recognition transfer.

При проверке transport evidence `abac5800c0ec93c1ecec100b37480982ec176f00`
относительно `c17f7f61f11a05c7ea8992e77593528690c956c5` совпали 52/52 CSV,
48/48 сравниваемых probe packets и 8/8 solo model revisions. В одном проверенном
исходном learned-state package единственное различие вне digest-полей находится
в `neuron.graph.native_xml`: StepDuration 1 вместо 0. Вложенные package hashes
из-за этого изменились, включая calibration/conversion references в большом
PostTune пакете. Один такой пакет занимает 38 985 829 несжатых байт; это не PNG.
Данная проверка относится к указанному примеру, не утверждает единственность
причины для всех исторических пакетов.

Причина: PulseLib `ModelArchive.cpp::Snapshot` сохраняет native XML с
ptPubParameter | ptPubState | pgSystem. Rdk UContainer::StepDuration —
ptPubSysState измеренной длительности вычисления. Physical model identity
этого runtime-значения не содержит, но побайтовый digest XML содержит.
Exact-file reuse закономерно не устраняет близкие, но разные JSON.

Исправление делать у владельца физического archive, без изменения общего
Save/Load Rdk и без присваиваний живой модели. Приёмка будущего изменения:

1. Выявить все такие runtime metrics; не путать StepDuration с частотой TimeStep,
   MaxCalculationDuration и CalculationDurationThreshold, влияющими на scheduler.
2. В native serialization-копии физического snapshot явно нейтрализовать только
   разрешённую телеметрию. Сохранить все параметры, graph bindings и порядок.
3. Поддержать чтение прежних signed packages; не переписывать исторические primary.
4. Реальные storage/fresh-process roundtrip должны сохранять model identity,
   полные входные/соматические массивы и честное состояние certificate.
5. Отдельно проверить стабильность физического snapshot при изменении только
   runtime counter и сохранность действующих wall-duration ограничений.

До исправления опубликованные delta archives сохраняют необходимые точные
байты. Нельзя просто удалить различающиеся model packages как «одинаковые».
