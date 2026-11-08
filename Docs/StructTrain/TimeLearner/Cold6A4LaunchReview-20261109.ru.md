# Cold6 baseline A4: проверенная постановка и начало выполнения

Сборка и набор **250 selected cases /137 leaves** запущены на M40. Это статус начала выполнения, а не приёмка набора или научный результат. Предыдущая отрицательная A3 остаётся опубликованной отдельно: 230 PASS, один FAIL, 17 NOT RUN.

Исходник A4 — Root `478cc35c0f1a314c34ad93aa0095b61836c658ec`, PulseLib `4a5c2ec9df9a9f704dcd8260714323494bfa4415`. В baseline перенесено минимальное исправление cold6 owning-value producer и адресные codec-проверки. Будущие Train5/owner-lifetime изменения сюда не включены. Строгий decoder, физика и допуски не ослаблялись.

Подготовка опубликована в отдельной evidence-ветке commit `eca61ea7ca395b687b7c6709b1b46cccfb70f885`, раздел `Reports/StructTrain/TimeLearner/s10-cold6-a4-production-preparation`. Root независимо прочитал фактическую canonical/job постановку с сервера: semantic hash `10267db2adccc71feeabdb459d3d37f2d2637fbe441c2971f5311afc6904122c` пересчитан, raw SHA256 canonical `1fcab30bbc59dad00f6dac1c35bdeef44bed67ae8b9c8c356d7285b6e637d135` и job `f3655c8b5768bdbc8fb5ac4a19ef5cddcf91c3ee8799f80067f9c7d4cc2c61e1` подтверждены.

Все 250 ID уникальны и присутствуют в source inventory. Порядок: четыре cold6 codec cases, 16 ранее не запущенных cases, затем 230 regression. Сохранены 72 обязательных artifact rules: 42 archive, 24 growth, два generic GTest JUnit sourceguard и четыре codec-wire rules. `native.xml` sourceguard создаётся штатным GTest writer; отсутствие отдельного writer в теле теста не является основанием удалить эти правила.

Старый source/build разрешён к повторному использованию только после закрытия и независимой проверки A3, отдельного source-update и production canonical preparation. Runtime/readbacks A3 защищены. A4 использует новый `runtime-s07-composite-cold6-m40-asan-a4` и одноимённый readback. После запуска исходники и runtime не изменяются.

Root подтвердил через production `contained_process.inspect` фактическое состояние `running`: unit `timelearner-69d33d86-2d26-4e49-aa61-e99d53d363d8.service`, invocation `6ed02749e035459ca3eee0a65c8b650d`, PID `18434`, start ticks `325076930`, binding `19900e040d6e018e249f870fbc120b216fbd22633090b2088e95c52a01282d42`. Supervisor `18316` /start `325076869`. Запуск выполнен один раз; наблюдение timeout не разрешает повторный запуск.

Сборка ограничена двумя потоками, весь worker — 8 GiB и шестью часами. На момент разрешения Data имел около 315 GiB свободного места, available RAM — 46.1 GB. Сохраняется прежняя защита от превышения выделенного дискового бюджета. Это контроль конкретного задания, а не обещание максимальной длительности научной кампании.

[Квитанция Root и сжатая просмотренная постановка](../../../Reports/StructTrain/TimeLearner/s07-composite-cold6-m40-asan-a4-root-launch/review.json). Локально выполнялись только чтение Git/JSON, хеширование и просмотр метаданных процессов; C++ и численные проверки выполняются на сервере. После завершения нужны actual JUnit, kernel closure, provenance и строгая проверка всех шести заново созданных archive configurations; сам запуск этих доказательств не заменяет.
