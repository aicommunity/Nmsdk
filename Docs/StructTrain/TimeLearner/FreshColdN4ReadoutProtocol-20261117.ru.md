# Свежие Classic/Branch N4: короткий Train и отдельная проверка readout

Это продолжение научной работы на той же Fast3-физике, а не повтор Test
старой terminal21600 модели. Оба production Train завершили240000 native
тактов с actual stopped state, reference_complete=true и external_stop.
Общего TrainingCertificate нет, completed_boundary=false. Эти состояния
нельзя называть полностью обученными или checkpoint для продолжения посреди
пробы.

| Топология | Actual L | Actual Rs | Размер stopped package |
|---|---|---|---:|
| Classic |3,1,1,1|86000000 для каждого входа|43417149 байт|
| Branch |3,3,3,1|86000000 для каждого входа|18542650 байт|

Источник — `s10-finite-train-native-m40-a2`, controls
880586ad267d116940f55c9117506f7b44a62d3d. Python actor
6a5d3d63af4ff5dd01bac88df15588466e1ee51f, native SDK
9b7fb0eac7107093d2fd87748b85c532c4f2ad9e/PulseLib
9883f9493d0672e603dfb4a03dc572955469ccdf. Применены CapturedPerInput,
N1,2000Гц, C-trimOff, исходные допуски1e−5/0/.02, порог100 при Train.
Менялись только явно записанные бюджеты, имя попытки и топология Classic.
Собственные caps4ГиБ owner/8ГиБ native и общий host reservation12ГиБ
проверены во время работы. Это не доказывает сохранение свежей759-probe
истории при прежнем OOM-сценарии.

Следующий опыт — `s11-fresh-matrix-baseline-m40-a1`, controls
0ecf6068f30ec57669340b737793f6f3568a0e9a. Полная фактическая модель каждого
Train импортируется через штатный путь. Предъявляются восемь PhaseA-паттернов,
все окна2с, reset-per-trial, исходный порог100. Это исходный неспайковый
baseline. Результаты нового readout до фактического закрытия не заявлены.

Затем production `diagnostic_threshold_study.propose` может предложить порог
между максимумом target и ближайшим строго меньшим максимумом foil. Это
Same-Matrix proposal, не готовая классификация. Отсутствие интервала является
отдельным отрицательным результатом. Если кандидат есть, его значение
фиксируется в новом request до запуска, затем проверяется реальными native
спайками на всех восьми паттернах. Положение строки не выбирает target.

Для такого опыта `recorded_diagnostic_matrix` принимает необязательное
числовое `diagnostic_threshold` на конкретном case. Отсутствие поля сохраняет
старый протокол; null, bool, NaN/Inf и строка не являются рабочим фактором.
Producer использует существующий diagnostic-evaluate job schema2, auditor
проверяет actual threshold и роль diagnostic_threshold_experiment. Source
training threshold остаётся100, новая физика и обучение не подставляются.
Это не независимый Test или сертификат сходимости.

Для отчёта нужны все actual Soma/LT traces с входами, полное восстановление,
отдельные подписанные увеличения и native zoom без прореживания. Не меньше
8px на timestep в увеличениях. Новые TP/FP/FN/TN публикуются даже при худшем
результате. В Word рабочие варианты включаются по TP≥1/TN≥2; число уникальных
foil и условия остаются явными. Старый7/8 результат другой модели не заменяется
этими короткими Train и не отменяется ими.

Полные primary/models/figures находятся во внешнем M40 archive. В Git только
код, протокол и refs. До полной публикации, проверки и merge эта ветка
не является приёмкой всего этапа11.
