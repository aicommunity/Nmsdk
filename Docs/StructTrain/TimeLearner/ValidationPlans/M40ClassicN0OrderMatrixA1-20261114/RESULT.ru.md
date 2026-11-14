# A1: служебный отказ до исполнения модели

Whole group закрыта, outer process_error594.4331509582698с; unit1 выполнен,1 failure,0 errors. Проверка сравнила initial_main_pid753407 owned worker с PID773132 дочернего unittest. Это разные штатные процессы одной группы. Новый job/native output не создан:64 пробы не запускались.

Исправление проверяет running и точное членство /proc/self/cgroup в зарегистрированной группе; production reservations и native ownership не ослабляются. [Повтор A2](../M40ClassicN0OrderMatrixA2-20261114/PLAN.ru.md) сохраняет все научные условия. Этот отказ не является результатом проверки порядка.

[Unit log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json), [integrity](integrity.json). Literal producer 6bb77453dace9a6b66670ecca33ef2d9ed812ed4, pack SHA256 95eef946a307c42aaa0d126960fc79495c29a2061d486f71cf77eb47fa63ca31.
