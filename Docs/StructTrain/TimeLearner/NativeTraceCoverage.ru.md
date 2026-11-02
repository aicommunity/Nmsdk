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

## Явный учёт долга в отчёте

`native_test_reports` schema2 добавляет `untraced`, `packet_aliases` и
`observability_gaps`; schema1 продолжает читаться без изменения контракта.
Список ожидаемых C++ cases задаётся отдельно от реально найденных файлов.
`integrated-wall-search-report-v2.json` описывает исходный CI163:18 фаз,
153 standalone traced probes,6 untraced packets,407 CSV,413 primary packets.
Все найденные probe packets и CSV должны быть явно учтены; наличие долга
не разрешает пропустить файл. Для untraced обязательны исходный packet,
его hash, читаемая схема и причина отсутствия трассы; `data_complete=false`.

Alias допустим только при полном равенстве JSON с первичным packet,
без цепочек aliases и повторного учёта измерения. Различная сериализация
может иметь разные hashes; равенство проверяется по strict decoded JSON.
Gap ссылается на существующий test ID; дубли запрещены. HTML перечисляет
пробелы явно, без синтетических кривых. `data_complete=false`, если есть
любой gap, untraced либо неполное/невалидное traced observation.

Четыре raw explicit-Reset diagnostics не превращаются в closed probes:
в schema2 они отдельно отмечены как необходимость raw-only отчёта.
Полный рендер407 проб и отдельные Reset-графики, проверка масштаба и
визуальный просмотр ещё не выполнены этим изменением.

## Подтверждённая серверная проверка

Elder numericd06585dfc2a739f2244f7ca59328721fe21475dd:18/18 cases,
88 packet/CSV pairs и6 точных aliases. CI163 reader8/8 и recording/schema1
reader15/15 без skips. Сохранены fault callback на10-м отсчёте,10 samples
external stop,4 samples deadline, prearm hash rejection с header-only CSV,
cold2+4/warm0+4 и retarget invalidation. Это не научный PASS.

Proof5f84cdf009b9d1537f464635b16a8096cb00741b содержит299 members,
835002 compressed bytes; archive/member hashes проверены после Git fetch.
Сохранена неудачная первая reader-попытка: prefix glob принимал saved model
за probe. Исправление2e785da3e проверяет только числовые ordinals и сохраняет
глобальное обнаружение любого неучтённого packet. ASan instrumentation18
и full temporal/visual acceptance пока открыты. Рабочий checkpoint:
[CurrentStatus-2026-11-02](CurrentStatus-2026-11-02.ru.md).
