# Подготовленный физический граф и свежий контроллер

Кандидат этапов4/5/6. В обоих learner добавлен InstallNativePreparedModel;
общий commit/adoption находится в PulseLib NativeModelOwner.h. Адресная
серверная проверка ещё не выполнена.

Назначение — native Neuron/DatasetMatrix, подготовленные полным import,
установить в свежий owner до его Init, сохранив всю физику. Старые references,
search/history, C0 checkpoint, calibration controller и certificate не
копируются. Типовой источник — полное stopped state, проверенное отдельно;
текущий API принимает только уже подготовленные physical components и явный
NativeModelSpec. Он не делает вывода, было ли это состояние обучено.

Owner уже owned/initialized/configured либо с непустым native controller
отклоняется до изменения графа. Committed children получают штатные aliases,
order и mirrors через общие native commit/adoption paths. Legacy AAddComponent
не перезаписывает Dataset во время native commit. Промежуточная холодная модель
не строится: у неё могла бы отличаться численная допустимость. Build/Init/Reset
и scheduler сохраняют общую семантику; вложенный Calculate не добавлен.
Ошибка после commit — Failed/modelMayHaveChanged с требованием отбросить свежий
контекст. При раннем Rejected source и ownership остаются прежними.

Подготовлены две native функции на Classic/Branch2000/20000Гц с настоящими
storage/Environment, derived gain0 images, полным graph/Dataset import,
неодинаковыми per-input Rs86e6/91e6, source/refusal/repeat controls. Четыре
actual fixture records читаются отдельными production graph-auditor tests;
проверяются неизменность source, полный candidate graph и пустые controller
references/history/search/certificate/request. Это не waveform proof:
следующий обязательный gate — реальный Console protocol и paired baseline.


Первая [проверка на M40](PreparedModelInstallJobs.json) завершилась compile failure.
[Failed primary](PreparedModelInstallFailureVerification.json):27 members и785
source hashes сверены с Git; native/reader tests не запускались. Шесть ошибок
относятся к трём временным UEPtr в двух template instantiations нового fixture;
ещё две QJsonObject diagnostics являются следствием неверного выражения after.
Core library собрана, но это не runtime-проверка API. Группа закрыта/lease released.

В fixture использовано GetComponent с правильным общим UEPtr<UContainer>;
Rdk не изменялся. Failed-a1 остаётся failed. Исправленная постановка сохраняет
26 native functions/29 readers и ещё должна пройти серверную проверку.


Исправленная [a2 проверка запущена на M40](PreparedModelInstallJobs-a2.json).
На последней kernel-проверке worker1489286 жив, идёт сборка. Ошибочный fixture
уже скомпилирован, общий SDK ещё не принят. Pulse2726bdf не менялся; изменение
native root относительно a1 ограничено Test_PulseLib_PreparedModel.cpp. Новый
runtime отделён от failed-a1; cache используется после fresh closure/released
lease. Постановка26 native/29 readers сохранена.

В App добавлен черновой TimeLearnerFeedbackProfileImport.h для следующего
Console протокола. Он проверяет source package, создаёт derived images,
переносит физический граф и Dataset и вызывает свежий installation API.
Helper пока не подключён к CLI и не проверен компилятором; текущий server job
его не содержит. Новый job schema/reader, парные waveform проверки и научная
интерпретация остаются не реализованными. Нельзя использовать его как действующий
параметр эксперимента или считать частью принятого SDK.
