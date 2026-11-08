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

Статус: кандидат, серверная сборка и A/B ещё не приняты. Математическую цель,
CapturedPerInput, reference N−1, tolerances, протокол подачи и частоты не меняет.
