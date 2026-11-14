# Classic N0 threshold A1: отказ до новых native-проб

Job s11-stock-n0-classic-threshold-m40-a1 закрыт с process_error763.9719912679866с, unit ERROR после735.684с. Причина `runtime_content_changed:/usr/lib/x86_64-linux-gnu/libc.so.6`: ОС обновила системную libc после фиксации исходного runtime. [Unit log](completed/worker/validation/unittest.log), [controller](completed/controller-result.json), [closure](completed/process/whole-group-closure.json).

Production proposal успел вычислить единственный заранее определённый midpoint0.012765548843211696. [Сохранённый proposal](completed/worker/tmp/threshold-study/proposal.json) имеет **nonspiking proxy**TP1/FP4/FN0/TN3 и отрицательный full-matrix peak margin−0.004697561266010175. Это не реальные спайки и не результат классификации. Первый baseline100 native process не был запущен: verify_runtime отказал до создания его owned unit. Candidate native run также не запускался.

Исходный runtime105ccc и package не переписаны. A2 объявлен отдельным job после закрытия A1: бинарник/INI/compiler побайтово прежние, новый manifest отдельно фиксирует изменённые libc/libm/loader и наследование source/build provenance исходного бинарника. Обязателен настоящий baseline replay с точным совпадением waveform перед тем же единственным candidate; смена среды не скрывается под прежним fingerprint.

Producer7ca01782f5cc9300f3a1414c791a508535bd61a6; pack86340B SHA25649173d8763c17c01c8c31edf0e02cc196e704e66f1f0166c946ce962f74b0510;24 исходных blobs импортированы без JSON rewrite.
