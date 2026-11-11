# Холодная характеристика штатной N=4 — 11.11.2026

Цель — измерить исходные assigned burst отклики до выбора окон нового холодного обучения. Это отдельная характеристика, не Train и не результат классификации.

Декларация: Classic/Branch,по четыре отдельных новых процесса для input0–3; все четыре импульса исходной пачки сохраняются. NSPNeuronGen из штатного storage, без импортированных образов и без LT-мембраны;2000Hz,N1,initial L=1,Ns=1,Rs=86MΩ,threshold100,ISI=[.01,.08,.16,.24]. N1 здесь принадлежит объявлению модели; нормализация не выполняется. C/Rm/кинетика не исправляются learner-записями: проверяется действительное дочернее дерево по stock-профилю.

Все8 jobs объявляются до первого native probe. Окно0–1.8s — диагностическое; оно не становится автоматически окном Train. Измеритель остаётся assigned_burst_wave: глобальный пик вместо закреплённого импульса не подставляется. Невалидная принадлежность сохраняется как диагностический результат отдельно от корректности записи.

Команды пакета: `stock-cold-characterization prepare --topology both --output JOBS`; `stock-cold-characterization run --source JOBS --runtime-manifest RUNTIME --controller OWNED_CONTROLLER --output RESULT`. Требуются immutable runtime и managed controller, который действительно владеет lease.

Первая попытка: одна native проба рассчитана и проверена, затем runner ошибся в формировании пути progress-отчёта (Path+str). Остальные7 не выполнялись. Исправление a2b28a542fa4796b48f27f0baec761eb6a4ab06b. [Исходный отказ](ValidationPlans/M40StockCold4Probes8-20261111/original-unittest.log). Held lease первой попытки закрыт только после независимого подтверждения outer+native closure; исходный failed outcome сохранён, SQLite before сохранён с SHA в recovery receipt.

Вторая попытка: все8 native probes рассчитаны, первичные данные и графы проверены; test завершился error при чтении schema3 lease DB без managed_units=True. Это ошибка завершающей проверки, не ошибка модели. Исправлен только аргумент reader в b7a8b2602c78c902e51007d561b55c42b906d27e. [Оригинальные8 результатов и error](ValidationPlans/M40StockCold4Probes8A2-20261111/actual-result.json).

Третья попытка запущена отдельно, без изменения модельных условий или бинарника. [Exact source/runtime/fixtures/request](ValidationPlans/M40StockCold4Probes8A3-20261111/request.json). Compiled root22e9714bbe66d29a661bb6829e1c992f24fc1362,Pulse165d49da7e65cd6ac59bca2812ce52884ddd50c2. Третья попытка завершена:8/8 native probes, все observations valid/complete, штатная физика без LT-мембраны и неизменность графов подтверждены. Controller1/1 PASS,50.471030s,8 native units и outer закрыты; inner/outer leases released. [Фактические результаты и назначенные пики](ValidationPlans/M40StockCold4Probes8A3-20261111/actual-result.json). Full compact primary и временные отчёты этих проб пока не опубликованы.

Следующий шаг: на проверенных waveform выбрать и зарегистрировать reference windows и бюджет candidate-window cold7 N4 при исходном SyncTolerance=.02; затем настоящий cold Train. Полная научная матрица и приёмка всех этапов0–12 остаются отдельными требованиями.

Измеренные назначенные пики обеих топологий совпали по времени:0.0245,0.1045,0.2645,0.5045s от начала пробы; задержка после каждого собственного actual onset14.5ms. Амплитуды native (SI не подтверждены):0.015781441626431136,0.015828572406203167,0.01578146659932167,0.015781441636542715. Различия амплитуд сохраняются как per-input наблюдения; общая A* не вводится. Совпадение времён в свежих графах не доказывает эквивалентность алгоритмов обучения Classic/Branch.


Уточнение11.11: [такие же8/8 fresh native пробы завершены на Elder](ElderStockCold4Characterization-20261111.ru.md), actual assigned peaks совпали в исходной геометрии. Полные compact primary обоих workers сохранены в Reports/StructTrain/TimeLearner/StockCold4-20261111;342 members/~135kB на worker. Перекрёстное восстановление и960 временных видов приняты; [8 выбранных PNG просмотрены вручную](StockCold4TemporalReports-20261111.ru.md).
