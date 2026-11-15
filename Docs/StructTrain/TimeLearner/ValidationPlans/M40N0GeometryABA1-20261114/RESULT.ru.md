# Независимый N0 controller A/B на M40 принят

M40 s07-n0-geometry-ab-m40-a1: wrapper1/1 PASS, outer completed/closed80.98258342500776с, heartbeat errors0. [Unit log](completed/worker/validation/unittest.log), [исходный A/B result](completed/worker/tmp/n0-geometry-controller-ab/result.json), [closure](completed/process/whole-group-closure.json).

Повторён тот же исправленный шестисценарный корпус, те же root/Pulse SHA и GoogleTest58d77fa8070e8cec2dc1ed015d66b454c8d78850, что в [Elder A4](../ElderN0GeometryABA4-20261114/RESULT.ru.md). Baseline: пять ожидаемых failures и успешный немонотонный fallback. Candidate:6/6 PASS. Same test source hashes подтверждены; оригинальные baseline failures/JUnit сохранены, общий assertion_status=failed не переписан. Двенадцать полных production C++ units и100 headers компилируются отдельно для каждой версии, без извлечения функций или замены объектов Rdk.

Это независимая серверная проверка controller decisions на заданных наблюдениях, не нейронный эксперимент: native_rdk_integration_verified=false, scientific_verdict=null. Следуют штатная свежая сборка SDK, расширенные реальные regressions и same-budget physical N0 A/B; математическая цель, допуски и глобальные budgets не меняются.

Actor8dbfa1f6db2d9c7e17e3084f02dfaca812a4c89c, control12f33b7c3b623a27ccf6dbe21af383679d2fc146. Producer3417a938a449ba8c57d392875581f33b88c7146d, pack94862B SHA25667163890ad9feede19f6e8fe035fa508ba71bb26ba02c8d72542e535ed71e427;46 исходных blobs импортированы без JSON rewrite.
