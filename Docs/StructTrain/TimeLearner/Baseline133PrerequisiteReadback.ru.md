# Baseline133:119 passed,14 failed; зависимые attempts сохранены

Неизменяемый SDK802/Pulsecc выполнил все133 заявленных tests,0 skips.119 passed,14 failures относятся к NativeLiveFinalization controls, требующим queued/completed cold boundary; core18 целиком passed. [Полные primary и summary](../../../Reports/StructTrain/TimeLearner/s06-baseline133-and-prerequisite-readbacks-a1/README.ru.md), proof d135320775e719da4e8a7d715950a7e35eec4146. Это отрицательная приёмка, не разрешение merge общего dispatcher.

В сохранённой постановке cold Train завершился budget_exhausted/maximum_sweeps_exhausted до queued state. Архивная конфигурация saved-state/interruption источника не была подтверждённой положительной cold декларацией:ISI[.01,.08],4 candidates/input,1 sweep. Для Classic input0 L2..3/Rs86..172MOhm. Это не доказывает PhysicalInfeasible или lifecycle regression и не отменяет исходный saved-state результат.

Зависимый candidate build A1 корректно отказался до создания SDK/lease; Pulse8644 не компилировался и не исполнялся. Independent rollback A1 тоже не запускал модели/не создавал lease: его условие ошибочно требовало recovery-event у candidate, который вообще не резервировал ресурсы. Ошибка dependency handling сохранена, общее различение lease_not_created/released остаётся задачей scheduler. Для независимого rollback A2 выбран уже закрытый metadata predecessor с фактическим release; сама проверка и runtime не изменены.

Elder metadata gate затем подтвердил все141 candidate migration records, отказал negative tree с возвращённым старым файлом и проверил exact36 changed paths/unchanged runtime code и child gitlinks. На момент этого readback M40 ещё ожидался. Затем [M40 gate и merge группы](CableFamilyRetirement.ru.md) завершены: текущий manifest141 records,20 cable/E1 scripts удалены без копий/wrappers.

Независимо проверены24 опубликованных файла,814 archive members и1202 source Git blobs:319 baseline,320 uncompiled candidate,286 rollback A1,277 history utility. [Receipt](Baseline133PrerequisiteVerification.json). Все созданные operational leases released после kernel closure; у двух failed prerequisites lease не создавался.

Corrected baseline source33fc48278cff860d20c570cb703198847f028065 отделяет cold declarations и cold profile registration от saved-state replay. Он собирается в отдельном SDK; старый802 сохраняется. Планируются focused25, затем те же133, без skips. Никаких гарантий PASS до фактического результата. Исходные допуски и алгоритмы обучения не меняются; другие входы означают отдельный контроль.

Corrected baseline33fc затем прошёл25/25 и133/133: [новая приёмка и точная граница](CorrectedColdBaselineAcceptance.ru.md). Это отдельная cold-постановка; прежние отрицательные результаты и исторические saved-state controls сохраняют свои источники. Общий dispatcher8644 остаётся непротестированным.
