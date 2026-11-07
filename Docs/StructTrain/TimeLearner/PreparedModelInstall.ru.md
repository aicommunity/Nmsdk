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


[Адресный gate запущен на M40](PreparedModelInstallJobs.json): root122a3aea6 /
Pulse2726bdf;26 native функций и29 readers. На последней kernel-проверке
worker1483958 жив и выполняет сборку. Новый runtime отделён от шести прежних;
source/build cache используется после закрытия и освобождения previous24 job.
Это статус запуска, не PASS. Ранее принятый physical graph import не проверяет
новый owner installation API; ASan предыдущего SDK также его не покрывает.
