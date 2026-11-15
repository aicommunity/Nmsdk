# Branch N0: измеренные предложения длины — 15.11.2026

Гипотеза: текущий N0 теряет предложения длины при штатном росте upstream bank, поскольку семейство таких геометрий разрешено только N1. Предлагается использовать тот же проверенный SameBranchLengthProposalFamily для N0 при неизменных Ns/Rs и C-context. Эти точки служат только предложению следующей длины: каждому предложению нужны новые anchor/input измерения, исходные timing/amplitude tolerances и независимый final gate.

Корпус фиксируется до изменения production C++: Branch N4/N5 с конечным candidate budget, немонотонный fallback, запрет Exact по прогнозу/вне допуска, неизменная upstream bank и Classic. Контролируемые наблюдения проверяют общий production BoundedTrainingSession; они не являются физическими результатами.

Порядок: один и тот же шестисценарный корпус old/new на Linux; прежний 99-case cohort и новые случаи в SDK; затем cold Branch N0 на текущей модели NSPNeuronGen без LTMembrane, 2000Гц, CapturedPerInput. Amp_abs1e-5, amp_rel0, min_amp1e-6, SyncTolerance0.02;1800с native Train/probes128/edits1280/candidates128/sweeps4/invalid4 и finalization300с сохраняются. Сравнивать реально измеренные кандидаты и остатки с прежним corrected-N0 baseline, не требовать8/8 ради PASS и не повышать лимиты ради положительного результата.

Изменение не затрагивает lifecycle, storage physics, алгоритм выбора Ns/амплитудную цель, критерии Exact либо обработку неизвестных пиков. История Ns по-прежнему локальна точной геометрии; семейство используется только для предсказания L. Обычный N0 с неизменной bank, Classic и N1 сохраняют прежний порядок предложений. Матрица всего плана этим не закрывается.

### Уточнение корпуса после первого A/B (A1)

В A1 старый алгоритм не прошёл два контроля роста Branch, новый их прошёл. Два неизменяемых контроля Classic/fixed-bank у обоих алгоритмов не прошли ошибочное ожидание четвёртого кандидата L=16: дискретизация исходного fixture 5 мс даёт измеренный прогноз L=19. В A2 исправлено только это ожидание (19); production C++ остаётся тем же. Исходные JUnit/вывод A1 сохраняются. A2 использует один и тот же уточнённый корпус для обеих версий. Это контроль порядка предложений, не доказательство физической сходимости.

### Проверка kernel A2

M40: один исходный корпус C++ для обоих Git snapshots. Baseline `d074fdf1b6b9d5f196fc4e4d366a94e31f94763c` (Pulse `b300ff1a94a00e2f548c54099277b96c0c2306ea`, production идентичен58c6e6d) не проходит ровно два сценария роста N4/N5. Candidate `a8c5a59f3525c05e6da38f16c55c675152ebb85b` / Pulse `5fc6bb4131d49f8ef884f82ccede66270e9d0c5c` проходит6/6; оставшиеся четыре контроля прошли у обеих версий. Owned wrapper подтверждён1/1, процессы полностью закрыты. Raw aggregate A/B `assertion_status=failed` сохранён, поскольку baseline намеренно содержит реальные отказы. Это соответствует ожидаемому сравнению, а не научному PASS.

Полные A1/A2 JSON/JUnit/logs (137 файлов) хранятся во внешнем архиве M40, объект SHA256 `64ee475e1b751da2ef7f6c16b2bd17d108e6e727e63c4ced0ad2df74ce25d8cf`, 581072 байт. Компактная машиночитаемая квитанция: `N0BranchLengthAcceptance-20261115.json`. Свежий SDK105-case cohort запущен на source `22e0f4cb171a9d7affe94164e517df6d054742c6`; физическое обучение ещё не запускалось.

Elder-1 независимо повторил тот же A2-корпус на своём компиляторе: baseline — те же два ожидаемых отказа, candidate6/6, owned wrapper1/1; heartbeat errors отсутствуют, все процессы закрыты. Это второй kernel-контроль; новая физическая модель запускается отдельно на M40.

### Исправление регистрации SDK-корпуса

В source22e0f4c новый C++ файл добавлен в отдельную TrainingAlgorithms, но пропущен в общем StorageComponents, который собирает native acceptance worker. Поэтому заявленные105 случаев не могут быть приняты в A1. Добавлена регистрация того же файла в StorageComponents. Существующий runtime не дополняется: после закрытия A1 предусмотрена отдельная fresh A2 сборка/runtime; production Pulse5fc6bb4, весь шестисценарный корпус и научные условия прежние. A1 сохранён как ошибочная постановка SDK-gate. Число параллельных задач следующей сборки выбирается по ресурсам сервера; научные budgets не меняются.

### SDK и запуск физического обучения

Fresh SDK A2 на source `549fba9761e4f4be1a9861736170e182cb3567f4` / исполняемом Pulse `5fc6bb4131d49f8ef884f82ccede66270e9d0c5c` прошёл105/105 C++ случаев. Native supervisor/leaf groups закрыты, record errors, heartbeat errors и final capture errors отсутствуют. Raw SDK A1 сохраняет отказ compiled_selected_cohort_missing и0 выполненных случаев; canonical A2 отказал до сборки из-за неподдерживаемого parallel8, canonical A3 со штатным parallel2 принят. Полный архив280 файлов — external SHA256 `a4a2fe182163dc069b9fdf9996c35a5920ae301aa9661d81e432e4030cceba24`, 5570725 байт. Успех105-case cohort не является сходимостью физической модели.

Начат cold Branch N0 `s11-n0-branch-length-train-m40-a1`, runtime fingerprint `64c67d93b53065bed5a31e9b87563804fbca235a5adceeb1ae2212e62b3cadc5`; native preflight завершён, Train выполняется. Исходный математический протокол и бюджеты1800/128/1280/128/4/4 сохранены, finalization300. Итог обучения, certificate и классификация ещё не установлены.

Commit Pulse `0841554de4499cd6fe1479002fc4171ba6cbe5e0` добавляет только документацию: его Core tree совпадает с исполняемым5fc6bb4 (`489559ab94c04ae2ab9365ef753fd2184788d085`). Runtime продолжает использовать исходную неизменяемую Git closure.

Уточнение имени образа по фактическому native `job.json`: `NSPNeuronGen`, initial_threshold100, четыре исходных input attachment1/Ns1/Rs86M. Написание NSPL в первоначальном тексте было опечаткой документации; фактический job и физика не изменялись.

### Заранее заданная frozen-оценка после Train

До просмотра новых Test responses зафиксированы две конечные модели: actual terminal исправленного N0 baseline58c (`s11-n0-geometry-after-train-m40-a2`) и actual terminal нового length search. Для обоих используются те же восемь паттернов исторической Phase A из Bin `1c1464e248f8744e858bd66df0be99e39969fd65` (runtime-ресурсы остаются Bin8cb6dba), один порядок, native reset перед каждой пробой и полное2с окно. Пороги100 (waveform characterization) и0.0117 (заранее выбранный штатный порог NSPNeuronGen) проверяются настоящими прогонами, без offline подбора по spiking CSV. При незавершённом Train используются diagnostic-evaluate/source_stopped, все результаты помечаются unfinished и не создают training certificate либо scientific PASS. При Exact требуется штатный export/recognition путь; прежний Solo certificate не переносится на изменённый threshold graph автоматически. Для каждого режима сохраняются все8 Soma temporal responses с actual input overlays, полный обзор и читаемые увеличения. Это не historical replay августа и не independent Test с новым held-out набором. Порог0.0117 не подбирается по новым данным, повтор обучения и увеличение бюджетов не предусматриваются.

Для новой парной оценки response window target начинается от последнего фактически предъявленного импульса (`anchor=last_stimulus`, reject_target_outside_window=true), foil оценивается по всему окну. Сохраняются TP/FP/FN/TN и отдельный target_trials_with_outside_spikes: ранний спайк нельзя скрыть последующим target hit. Это заранее объявленный критерий новых проб; старые onset-критерии не переоцениваются.
