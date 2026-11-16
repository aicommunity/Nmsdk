# Fast Branch N1: завершение измеренного поиска сопротивления

Цель — проверить, может ли штатный bounded N1 search завершить настройку input2 и перейти к остальным входам на текущем принятом native ядре. Это холодное обучение; mid-probe checkpoint не используется. Успех эксперимента оценивается по измеренным остаткам и свежей all-input проверке. Отрицательные исходы сохраняются.

## Основание

В предыдущем fast wall3600 опыте на Pulse5052cfe1683ca38920b514aedfc3c37f4bd41aef при L122/122/121/1 зарегистрированы timing-valid точки input2: Rs8.090169943749473MΩ, amplitude residual+.004187080333055593, timing−.0005с; Rs26.377160862429008MΩ, residual−.016065083269602654, timing0; Rs10.871143923391603MΩ, residual−.0023612200739181466, timing−.0005с. Имеется измеренный интервал с разными знаками ошибки; глобальная монотонность и достижимость всей модели не доказаны. Terminal Rs9.772503178596893MΩ не получил завершённого измерения, поэтому ему не присваивается остаток предыдущей точки.

Предыдущий primary7d9c5bf2e527cd5955d3ea1cf39a173b5233237c6af332bf0baa48f425cd687e доступен через experiments/2026-11-15/fast-profile-physics/uniform-profile3-N1-train-a3.json внешнего архива. Отчёт предыдущего снимка — FastProfileWallBudgetScientificReport-20261116.ru.md.

## Заранее фиксируемые условия

Два новых cold runs на одном неизменяемом текущем runtime root7b495ebf753259ae8b78c6d0eadd561fb3d2c835/Pulse9e7653a400761d6c2f3ea68fddcd40a4307d85e7: native wall3600с и7200с. Их producer, модель, математическая цель, логические бюджеты и native binary одинаковы. Различаются только wall budget и идентификатор попытки. Сравнение со старым Pulse5052 дополнительно содержит различие версии алгоритма и не называется чистым эффектом wall budget.

Branch N4/N1, штатный TLNativeFast3F2000_Neuron: C2.5e-10F, DissociationTC.002с,2000Гц; LTMembrane отсутствует. Начальные L1/Ns1/Rs86M, maximum cable length256, anchor input3 length1. CapturedPerInput, amplitude_absolute1e-5, amplitude_relative0, sync.02;128 probes/1280 edits/128 candidates,4 sweeps,4 recoveries, maximum model time7200с сохраняются. References захватываются заново. Из закрытого старого characterization используются только координаты для full-window guards; амплитудные цели, параметры и search history не импортируются. Native обязан подтвердить корректность собственных references и effective window[0,3600].

Каждый process получает отдельные controller/output/leases. Native finalization300с отделена от search wall; внешний deadline wall+5400с включает preflight и DATA audit. Внешний deadline не продлевает native поиск. До старта проверяются общий запас памяти/диска, fixture fingerprints, package fingerprint и обе декларации. Запуски могут идти параллельно; фактические wall/CPU/resource readback сохраняются. Число завершённых кандидатов при wall limit зависит от нагрузки; совпадение измеренных prefixes проверяется по данным, а не предполагается.

Обёртка test_uniform_profile_train больше не фиксирует единственный переход1800→3600: она проверяет явно объявленные before/after, SHA исходного job и полное равенство остальных полей. Существующий исторический сценарий сохраняет прежний ожидаемый SHA по умолчанию. Это изменение допускает постановку следующего опыта и не является исправлением математического алгоритма.

## Обязательная приёмка

Для каждого run: completed/valid execution и закрытие всех owned groups; effective cold graph и сохранность физики при росте; все complete/invalid measurements и revision-bound histories; per-input timing/amplitude residuals, bracket и resistance-domain evidence; конечное состояние и честная причина остановки; свежий all-input certificate только при фактическом выполнении. Перед сравнением проверять различие условий и фактический общий prefix. На исходном одиночном reference или локальном input2 не основывать вывод о всей модели.

Для состояний с полным валидным экспортом выполнить frozen8 и реальную проверку объявленного порога по отдельному протоколу; незавершённый Train маркировать diagnostic. Временные отчёты должны показывать потенциал сомы, фактические входные импульсы, omission controls для Train и все предъявленные паттерны Test, с читаемым native zoom. Полные данные/галереи сохраняются в /media/user/Data/Nmsdk-StructTrainExpArchive; Git содержит компактные refs.

Начальный статус: протокол подготовлен; новые расчёты ещё не выполнены. Полный план остаётся активным.

## Production подготовка следующего запуска

Подготовка переносится из временного launcher в команду пакета:

```text
python -m Scripts.StructTrain.TimeLearner.uniform_profile_study prepare-cold ORIGINAL PROFILE REFERENCE_NATIVE OUTPUT --variant 3 --maximum-wall-seconds 7200 --run-label current-wall7200
```

Команда проверяет подпись исходного job, класс и протокол reference-пакета, полный DATA audit координат, допустимость явного wall budget и неизменность входов. Она создаёт original-before-budget.json, original.json, profile.json, job.json, declaration.json, reference-characterization.json и preparation.json. Runtime, ожидаемый cold graph, controller и output выполнения привязываются отдельно штатным runner. Команда не рассчитывает модель, не импортирует амплитуды или обученные параметры и не выдаёт сертификат. Совпадение с обоими уже объявленными actual cold jobs проверяется на сервере через production CLI; чужой профиль/target, NaN budget, повторная запись и запись внутрь reference tree должны отказываться до изменения входных данных.
