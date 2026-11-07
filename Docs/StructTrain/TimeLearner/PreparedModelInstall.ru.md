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
Rdk не изменялся. Failed-a1 остаётся failed. Исправленная
[a2 проверка на M40](PreparedModelInstallNormalVerification.json) завершена:
26/26 native функций и29/29 readers без skips. Все234 members и785 source
hashes сверены с точным compiled rootc5a32/Pulse2726. Четыре actual prepared
owner records подтверждают candidate graph, индивидуальные параметры,
неизменность source, пустые references/history/search/certificate/request и
отказ повторной установки без изменения ownership. Группа закрыта, lease
released; семь прежних runtime не изменились. Это scoped normal gate:
waveform equivalence, archived stopped-state Console intervention, ASan нового
API, второй сервер и полная матрица остаются открытыми.

В App подключён кандидат TimeLearnerFeedbackProfileImport.h к Console job schema5.
Он проверяет source package, создаёт derived images, переносит физический граф
и Dataset и вызывает свежий installation API до attachment/Init owner.
Поддерживаются native burst и single-pulse presentation; Rs-intervention и
изменение stimulus запрещены. Source history/references/certificate не копируются.
До и после native lifecycle проверяются полный candidate graph и Dataset;
замороженные пробы сохраняют прежние проверки неизменности.

Production Python builder/admission и execution auditor поддерживают schema5.
Аудит проверяет source digest, полный graph delta, пустую controller history,
Dataset identity, image metadata/dependency closure и fingerprint.
Проверка metadata/XML hashes не заменяет native readback или waveform proof.
Кандидат ещё не скомпилирован и не принят на сервере; старые job schemas1–4
сохраняют отдельные контракты. Добавлены адресные admission controls на фактических
archived source cases. Локально выполнены только AST parsing и diff whitespace
checks; numerical/reader execution, compiler, paired baseline и actual gain0
study должны выполняться на серверах. До их приёмки не считать schema5
проверенным научным инструментом или завершением этапов4/5/7/11.


Admission candidate root367b811 прошёл9/9 Python controls на M40 (7 прежних
single-pulse admission и2 profile job controls) на actual archived Classic/Branch
stopped cases. Проверены обе presentation, baseline/gain0, canonical signing,
запрет malformed factors/mixed Rs/stimulus edits. Native compilation и candidate
waveforms этим не проверены. [Primary опубликован и сверён](FeedbackProfileProbeAdmissionVerification.json):
7 archive members и432 tool source hashes совпали с Git; группа закрыта, lease
released. Scope остаётся admission-only, native compiler/waveforms не запускались.
Первая попытка запускателя завершилась до worker/tests: отсутствовал runtime_identity;
во второй добавлены штатные runtime_content_identity/digest_json. Это ошибка
orchestration manifest, не алгоритма модели; попытки не объединяются в один PASS.


[Console/storage проверка a2](FeedbackProfileConsoleJobs-a2.json) запущена на M40.
Сборка actual Console schema5 прошла; далее требуются26 native controls,
29 прежних readers,12 реальных diagnostic probes и11 admission/execution controls.
[Первая попытка](FeedbackProfileConsoleFailureVerification.json) отклонена начальным
runtime guard до reservation/source updates/build; все5 primary members и785 hashes
фактического прежнего sourcec5a32/Pulse2726 сверены. Запрошенный root844 не был
скомпилирован в a1. Во второй попытке отдельный runtime; Pulse Core неизменен
относительно ранее проверенного2726, gitlink1f97 включает обновлённую документацию.
Восемь прежних runtime защищены byte hashes. Все12 заданий фиксируются до native
operations; четыре exact baseline comparisons должны пройти до gain0. Серия не
обучает и не оценивает классификацию; CapturedPerInput/threshold не меняются.
