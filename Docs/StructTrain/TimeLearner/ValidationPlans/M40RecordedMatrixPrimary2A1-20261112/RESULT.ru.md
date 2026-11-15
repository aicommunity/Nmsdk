# Full matrix gallery A1: plotting runtime unavailable

Job `s11-recorded-matrix-primary2-m40-a1` завершён отказом. Source `557decacf`, system Python3.12 не содержит matplotlib; `plotting_runtime_unavailable:No module named matplotlib` возник в renderer после 1624.835 s setUpClass. Выполненных test cases0/2; scientific/visual acceptance не получена. Сам actual Console diagnostic16 A2 этим отказом не отменяется.

Controller process_error, original whole group closed, единственная lease released, heartbeat errors отсутствуют; source/tool/fixtures before/after побайтно равны. 14 raw proofs, включая полный unittest traceback и exception, в `failed-plot-runtime/`. Исходный каталог A2 и работающее compact1 задание не изменялись.

Причина — выбор неверного Python для задания отчётности и слишком поздняя проверка backend. Production report_matrix теперь вызывает plotting_runtime перед дорогим audit_matrix. Проверены существующий owned-copy interpreter `/media/user/Data/TimeLearnerRefactor/plot-python-owned-copy-a1/bin/python` и его зависимости: Python3.12.3, matplotlib3.9.4, Pillow13.0.0. Это окружение уже использовалось успешной прежней галереей. Новый A2 получает отдельный job/output и сохраняет отказ A1; устанавливать пакеты в системный Python не требуется.
