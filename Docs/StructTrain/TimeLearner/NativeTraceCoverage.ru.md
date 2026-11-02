# Полнота временных данных CI163 и дозапись отсутствовавших проб

Исходный immutable numeric root07167d551 на Elder прошёл163 C++ assertions,
но это не полная observability приёмка. Проверка каталога показала407 CSV,
408 top-level native probe packets и5 embedded `/probe` fresh-process packets.
Четыре explicit-Reset diagnostics содержат отдельные raw samples в JSON.

Шесть negative fixtures не сохраняли raw CSV: Classic/Branch external stop,
Branch model-time budget, Classic spoofed pattern hash, Classic/Branch tiny
external physics change. Описание наблюдения не заменяет отсутствующую трассу.
ExactAutoCompletionResetWarmRestartAndRetarget вообще не имел trial recorder.
Эти пробелы нельзя восстановить графиками по peak values или заполнить нулями.

Recorder теперь общий `RecordNativeTrainingProof`, с композиционным сохранением
предыдущих onPrepared/onSample/observationSink. Нельзя терять callbacks,
проверяющие external physics change, остановку, warm reuse и другие причины
невалидности. Записываются исходные кадры до callback-вмешательства. CSV
сохраняется для каждого issued packet: реальные samples либо только header,
если проба отвергнута до измерения. Старые отдельные packet artifacts сохраняются
как aliases; они не являются независимыми измерениями.

Для Exact/warm отдельно сохраняются cold/warm outcome и retarget invalidation.
Изменяются только тестовая instrumentation и полнота артефактов; математическая
цель, лимиты поиска/допуски и Rdk scheduler не меняются. Имена старых helper calls
механически приведены к общему recorder. Source-reviewed18 IDs объявлены в
native-trace-recording-v1.json:7 затронутых cases,4 sweep-boundary,2 sink-policy,
4 PostTune owner2k и один provenance regression. Нужна серверная проверка.

Source/build/runtime ASan163-a2 не обновлять. Дозапись выполняется отдельным
numeric snapshot/runtime на свободном Elder; позднее аналогичный gate на M40.
Исходный163 остаётся своим архивом с явными untraced gaps. Новый short gate не
переписывает его и не заменяет полный CI163 или научную матрицу.
