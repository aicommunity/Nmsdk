# Общее извлечение измеренных вершин

Это отдельный механический шаг этапов6/7 перед изменением назначения импульсам.
PulseLib `MeasuredResponse.h/.cpp` содержит production extractor, которым уже
пользуются оконное измерение и full-burst recorder. Меньшие вершины не теряются
на уровне признаков; действующие policies по-прежнему сами решают, что принять.

API описан в PulseLib `Docs/TimeLearner/MeasuredResponse.ru.md`. Два признака
clipping разделяют обрезку общего максимума и обрезку другого положительного
отклика на границе. Признаки содержат actual sample indices/timestamps и raw
potential с явным baseline; predicted delay и stimulus labels отсутствуют.
Неполнота окна и принадлежность отклика остаются отдельными проверками.

Добавлены семь feature tests в существующий production test source. Те же
источники входят в lightweight ProbeAlgorithms и полный StorageComponents.
Все три lightweight targets, которые компилируют ProbeObservation.cpp,
линкуют настоящий MeasuredResponse.cpp. Копий тела функции для тестов нет.

Критерии приёмки: прежние observer/verification/subset tests; malformed/finite,
late larger peak, ties, plateaus, clipping и absolute-clock cases; native
Classic/Branch и storage checks. Совпадение этих результатов не доказывает
готовность нового алгоритма атрибуции: schema3 сохраняет прежний смысл.

На Elder принята normal-проверка:78 unit и15 отдельных native cases, включая
Classic/Branch,2000/20000 Гц, N=1/2/4/6, shared-vertex guard и single-impulse
maximum. Все93 JUnit IDs сверены с заданиями; пять изменённых source bindings
совпали с Git. Текущий и прежний runtime неизменны, группы закрыты, lease released.
[Независимая квитанция](MeasuredResponseNormalVerification.json), Git-primary
`0e7a30ff19b4d67846cc98f27b98ed9dd3862d74`:625 members,457932 compressed bytes.
Новых обученных моделей и результатов классификации этот gate не создаёт.

Служебный stderr сборочного worker содержит только проверенные сообщения Git
о detached checkout трёх объявленных commits. Его точные1102 bytes/SHA сохранены
в приёмке отдельно от model-process diagnostics. Первоначальный publisher
ожидал пустой служебный stderr и отказал до создания evidence commit; после
проверки конкретных сообщений повторялась только упаковка, не модели.

Статус: ASan/native и A/B на M40 ещё выполняются: [точные задания](MeasuredResponseJobs.json).
Продолжать наблюдение этих же групп; неполный gate не перезапускать по таймауту
наблюдения. Математическую цель,
CapturedPerInput, reference N−1, tolerances, протокол подачи и частоты не меняет.
