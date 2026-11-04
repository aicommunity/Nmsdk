# Штатная проба без обучения

Ветка `codex/timelearner-native-probe`; реализация ещё проходит серверную
приёмку. Обычный серверный контур и тот же набор под ASan проверены.
Команда Console `--timelearner-probe job.json --timelearner-output NEW`
строит явно заданную холодную модель через `ConstructNativeModel`, затем
использует обычные Build/Init/Reset и `QueueNativeProbe`. Дочерние компоненты
вычисляет только штатный scheduler корневой модели. ControllerVersion=2,
CalculateMode=1, IsNeedToTrain=false; поиск, захват references, сертификация,
PostTune и калибровка не запускаются.

Задание `timelearner_native_probe_job`, schema 1, содержит ModelSpec 1/2,
storage profile archives, эффективный stimulus profile, выбранный input_index,
идентификаторы run/trial/sample/protocol, полное окно и лимиты. Это штатная
пачка: Classic подаёт её на все пути и измеряет выбранную сому; Branch временно
оставляет активной выбранную точку подключения, сохраняя генерацию всей пачки.
Команда не реализует отдельный single-pulse characterization.

Отчёт сохраняет исходное задание, внутреннюю idle-конфигурацию владельца,
полный semantic graph и индивидуальные параметры до/после, фактические CSV
и ProbeEvidence JSON. Потоковый writer общий с Train. Временная маршрутизация
Branch восстанавливается исполнителем пробы; проверка неизменности проводится
после восстановления. Завершение процесса, закрытие окна и валидность пика —
разные признаки. Нет training certificate или положительного verdict.

Отмена и wall/tick budget закрывают фактически записанную частичную пробу
через обработку ошибки sample sink, с восстановлением маршрутизации. Reset
learner в середине пробы не вызывается. Внешнее принудительное завершение
процесса всё равно требует классификации как неполное наблюдение.

Первое применение — контроль Rs при неизменной stock-морфологии на границе
потери волн. До причинного сравнения необходимо подтвердить совпадение
контрольного semantic graph с исходным остановленным состоянием; совпадения
только L/R недостаточно. Измерения не являются обучением или Test завершённой
модели. Ни пороги min amplitude, ни исходные допуски обучения не меняются.

Обязательная приёмка: Classic/Branch; выбор входа >0; ModelSpec 1/2;
нормальная и ASan сборки; полное валидное и полное невалидное наблюдения;
частичный tick budget; неверный index/schema/digest/profile; неизменность
модели и idle-контроллера; regression существующих Train/preflight writer.

## Пакет и проверенные первичные данные

`python -m Scripts.StructTrain.TimeLearner probe-job prepare TRAIN_JOB
--input-index N --trial-id ID --output PROBE_JOB` переносит физику и протокол,
удаляя все факторы поиска и финализации. `probe PROBE_JOB --runtime-manifest R
--wall-seconds S --output NEW` использует общий production supervisor,
кооперативный захват фактически загруженных библиотек и обычный run-manifest.
`probe-job analyze NEW/native --output AUDIT` независимо проверяет первичные
данные; общий `audit_run_manifest` дополнительно проверяет привязку процесса,
runtime и полного состава файлов. Сам анализ первичных данных не доказывает
происхождение произвольно подложенного отчёта процесса.

Source root `111d0b578566342a6159a50977c6bcdab9f9c647`, PulseLib
`541bf89b9966f63ca5131fa57a31a9ae3f5820ea`, Rdk
`10e9d05aa658dd2203c89bc84ba9166595b50014`. Elder A6: восемь реальных
проб (четыре полные валидные, две частичные по tick budget, две полные
с отсутствующими волнами при явно заданном diagnostic min amplitude=100),
пять отказов до наблюдения (index/schema/spikes/digest/stimulus mismatch),
пять проверок данных без skip. Дополнительный холодный Train дал 121 первичный
файл, побайтно равный прежнему positive-control Train. Это инженерный профиль
с LT-мембраной, а не stock NSPNeuronGen и не научный результат классификации.

Proof commit `76d62276a33e271b0320f13d899a4be4c806f96d`, компактный архив
`Reports/StructTrain/TimeLearner/s03-native-characterization-elder-a6/primary.tar.xz`:
357 членов, 634052 байта. Независимо проверены все члены и 322 source blobs:
[receipt](NativeCharacterizationNormalVerification.json). Ранние неуспешные
сборки/подготовки оставлены на сервере: недостающий include, неверный путь
к локальному Git cache и несовпадающий gitlink Rdk. Последний отказ устранили
точным checkout принятого commit; Rdk Core tree не менялся. Отказы не были
сбоями научного эксперимента или доказательством проблемы SSH/диска.

M40 ASan A3 повторил все восемь проб, пять ранних отказов и пять primary
readers; 121 файл холодного Train также побайтно совпал с исходным ASan
контролем. Proof `692961f9ae587242e39a44b23827c2133a122725`, архив
`Reports/StructTrain/TimeLearner/s03-native-characterization-m40-a3/primary.tar.xz`:
357 членов, 548656 байт. Все члены и 322 source blobs проверены независимо;
в фактически загруженных файлах каждой пробы присутствует libasan. Leak
detection выключен. [Receipt](NativeCharacterizationASanVerification.json).

Отдельные cancel/wall-budget controls также пройдены: source root
`07ff1081f88dd020eafa345c3dc0cf4594a0941c`, шесть запусков на каждом worker
(Classic/Branch × completed/timeout/cancelled), по девять data readers без skip.
Непрерванные CSV/JSON и initial/final state побайтно равны предыдущим пробам.
Timeout с явно заданным бюджетом 1 ns проверяет контракт прерывания и не
является benchmark: в каждом случае сохранён один реальный sample. Отмены
поступили после появления записанной трассы, сохраняют фактические samples,
точный cancel.request и восстановленный граф. Контроллер остался idle.

Execution schema 2 добавляет `probe_wall_seconds` (steady clock). Schema 1
сохраняется для чтения прежних результатов. Auditor связывает причину
прерывания с native packet/end_reason; для отмены требует сохранённый request,
для tick budget — достигнутый лимит, для schema2 timeout — измеренное время
не меньше заданного. Внешний timeout supervisor, который принудительно
завершает процесс, остаётся отдельным исходом и не доказывает наличие
завершённого native packet.

Proof commits `7d5604cdd60fbb5b024f86326843bbb74a76e6f6` (Elder, 122256 B)
и `a7a1407f138adc5b652f23bd7a5501d2202eacdc` (M40 ASan, 131872 B).
На каждом независимо проверены 145 primary members и 323 source blobs:
[receipt](NativeProbeInterruptionsVerification.json). ASan detect_leaks=0.

Уточнение 04.11.2026: полное восстановление двух stock-графов из остановленного
состояния и fixed-geometry Rs interventions проверены на обоих worker:
[протокол и артефакты](StoppedStateResistanceControls.ru.md). Приняты непрерванные
запуски с полным import, сохранённой controller history и реальной вспомогательной
пробой перед разрешённым изменением Rs. Прерывание этой вспомогательной фазы
пока не имеет полного phase-aware execution envelope и остаётся открытым;
проверенные выше cold cancel/timeout controls не доказывают этот случай.
Новая команда пока не объединена в develop и не закрывает этапы 6–8 или
научную матрицу.
