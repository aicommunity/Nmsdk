# Автоматическое владение исходной C₀

Следующий пункт этапа7 после explicit C₀ API. Он не включает bounded C-trim
search: V2 SyncCapacitanceTrimOn остаётся запрещённым до его отдельной проверки.
Capturing per-input amplitudes, anchor и исходные допуски не меняются.

Исходный Core Pulse develop `8b41ffe4c438b188ef83406cfda1b616e2f3b199` сохраняет
NativeLearnedCapacitanceState только при import. Bound edit и обычные L/Ns/Rs
edits не владеют полной картой исходных C₀/абсолютных scales; первый export
требует ручной передачи correction. Проверять этот риск надо на native owners,
а не копии helper-функции. Baseline gate8 добавляет Classic/Branch × N0/N1 ×
2000/20000 Гц и сохраняет физические waveforms и JSON каждой фазы. Результат
gate пока не получен; исходный Core в baseline не меняется. В первом A1 уже
наблюдается пустой owner state после bound edits. Найдены и исправлены две
ошибки fixture: после Reset необходимо заново завершить реальную probe до
структурного edit; чтение отсутствующего поля через неконстантный QJsonObject
не должно менять локальную копию state. Assertions сохранены, raw A1 остаётся
непринятым из-за этой примеси ошибок теста. Corrected baseline требует A2.

Обязательная последовательность baseline: initial bound trim heterogeneous
Exc/Inh → trim другой мембраны → native Reset → обычный growth без correction
аргумента → реальные probes → попытка recapture/rebase trimmed baseline.
Проверяются полная owner-state карта, исходные C₀, storage-origin новых каналов,
model revision, сохранность прежних поправок и отсутствие изменений при отказе.
Это проверка API владения, не сертификат завершённого обучения и не классификация.

Реализация должна разделять исходную C₀, текущую ёмкость и controller history.
Нельзя захватывать текущую trimmed C как новую исходную baseline или обновлять
метаданные отдельной fallible операцией после необратимого физического commit.

```text
resolve optional correction against owned complete state
validate current owned state against the effective live graph
reject a conflicting/rebased baseline before live mutation
merge requested absolute scales with previous complete scale map
build native preview of L/Ns/Rs/C together
extend original C0 of added channels from verified storage images
encode and validate complete prospective state on preview
commit the verified physical candidate
verify effective graph and assign the already prepared state
on failure: restore graph/aliases and original owner state
```

`NativeEditResult` и `NativeCapacitanceEditResult` должны возвращать заранее
проверенное committed parameter state. Его authoritative owner — learner;
контроллер и отдельные callers не должны хранить конкурирующие копии. Ordinary
structural edits и resistance-domain preview автоматически используют owned
correction. Subset edit сохраняет уже применённые scales остальных мембран.
Первый schema2 bound edit начинает владение; schema1 primitive сохраняется как
legacy API без автоматического provenance. При имеющемся bound state нельзя
обойти его schema1-вызовом. История поиска при изменении влияющей C инвалидируется
штатной revision policy; поправка не применяется заново на каждом тике.

Приёмка далее расширяет baseline: repeated edits, shrink/regrowth, параметры
inhibition, rollback/injected failure, unchanged frozen model, warm continuation,
неявный export после completed/stopped Train и fresh import/re-export. Native
export/import переносит исходную C₀; XML/Copy не объявляются checkpoint этого
private controller/parameter state без самостоятельной проверки. Reset learner
не означает возврат физики к исходному storage image.

Для shrink/regrowth нужно явно определить dormant scales: отсутствие физического
сегмента не означает разрешение забыть исходную C₀ и повторно захватить ёмкость
из trimmed-состояния. Версионированное состояние должно различать применённые
scales существующих мембран и сохранённые scales удалённых мембран. Перед ростом
они заново разделяются на active/dormant по preview-графу. Recreated каналы
получают исходные индивидуальные C₀, новые имена — проверенный storage C₀.
Codec обязан отвергать active/dormant overlap, неизвестный baseline path,
не-конечные/bound-нарушающие scales и dormant запись существующего узла.
Storage closure проверяется целиком, включая исходные образы временно удалённых
каналов; изменение неиспользуемого сейчас образа нельзя скрыть shrink-операцией.
Кандидат Pulse `4ae7e5c7ecb6ee7b05003b0f49a9f514afcd55f1` реализует эти
механизмы, но ещё не прошёл server build/runtime. NativeLearnedState export
дополнительно сохраняет образы dormant-каналов для fresh-process import.
Root candidate расширяет8 ownership tests shrink/regrowth и negative codec
controls, сохраняет48 независимых effective graph/image/state snapshots;
production reader проверяет их физику, исходную C₀ и continuity maps между
фазами. Новый schema2 state не выдаётся за legacy schema1 без dormant history.
Потеря этой истории должна отвергаться даже при пересчитанных envelope hashes.

Ownership gate8 получает wall budget7200s для более тяжёлых наблюдений; model
time, physics, search tolerances и assertions не ослаблены. Более широкая
regression47 объединяет прежние8 legacy C edits,8 bound C cases,13 joint/failure
controls и14 completed/stopped/recognition transfer cases с8 ownership cases:
47 уникальных IDs после удаления4 повторов legacy cases внутри joint-контракта.
Она запускается
после ownership gate; до положительных normal/ASan и полных reader checks
в develop ничего из owner-кандидата не объединяется. Это всё ещё не C-trim
controller search, полная lifecycle/physics матрица либо научное8/8.

Временной report-контракт native-capacitance-ownership-report-v1.json объявляет
48 фактических полных probe traces (serial2/4/6/8/10/12 на каждый case): до C
edit, после Reset с сохранёнными C, после growth и regrowth для обоих input IDs.
Используется production native_test_reports: soma всех доступных каналов,
фактический stimulus overlay и zoom с native samples. После положительных
native gates нужны проверка полноты72 trial-soma pairs, читаемости выбранных
изображений и неизменности первичных CSV. Полные PNG/SVG/PDF — cache на M40;
Git — сжатые первичные данные, модели, метрики и выбранные проверенные рисунки.
До рендера/прямого просмотра визуальная приёмка не назначается.

## Уточнение roundtrip: параметры и полный граф

Первый кандидат B1 выявил избыточное требование теста: одинаковые L/Ns/Rs
после shrink/regrowth не задают весь граф. NativeModelEditor::Transform явно
освобождает прежние learner-owned excitation banks, сохраняя остальные банки
поставленной модели, особенно explicit neuron mode0. Исходный профиль имеет
idle ExcSynapse1 на внутренних мембранах. После временного превращения такой
мембраны во вход этот банк становится owned и при уходе входа освобождается.
В первом Classic2k case idle bank переместился с Dendrite1_1 на Dendrite1_2;
все C₀/scales восстановились, но разные nodes/bindings/caches дали разные SHA.
Это не доказательство потери C₀ и не разрешение удалить все unowned banks.

Исправленный контракт проверяет точный возврат C₀, scales и фактических
L/Ns/Rs, включая их независимое соответствие каждому живому банку. Каждый
полный граф сохраняет собственный реальный fingerprint; их равенство отдельно
измеряется и не подменяется равенством нескольких параметров. Frame schema2
содержит input_parameters плюс полный effective_model и class_definitions.
Production reader возвращает отдельно parameter_roundtrip_cases и
whole_graph_roundtrip_cases. Legacy frame schema1 не дополняется вымышленными
readbacks. B1 с избыточным assertion сохраняется отрицательным; C2 — отдельная
проверка уточнённого контракта, без изменения допусков и физики C₀.

Точное соответствие полного графа при native preview/live commit и model
export/import по-прежнему обязательно. Политика idle/released banks относится
к описанию математической модели и Stage6/7: полный state/revision нельзя
заменить в fingerprint/candidate cache одним L/Ns/Rs. Отдельный профиль с idle
банками0 можно задавать через storage, но это другая явно объявленная модель;
он не заменяет исходные профили незаметно и требует самостоятельной матрицы.

Изменения выполняются в codex/timelearner-capacitance-owner от принятого develop;
server jobs не должны вытеснять текущую invalid-reload проверку. После адресной
приёмки — --no-ff merge Pulse develop, затем root с точным gitlink. Полные
этапы4/5/6/7 и исходная цель остаются частичными.
