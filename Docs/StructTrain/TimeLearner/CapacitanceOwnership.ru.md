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
gate пока не получен; исходный Core в baseline не меняется.

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

Изменения выполняются в codex/timelearner-capacitance-owner от принятого develop;
server jobs не должны вытеснять текущую invalid-reload проверку. После адресной
приёмки — --no-ff merge Pulse develop, затем root с точным gitlink. Полные
этапы4/5/6/7 и исходная цель остаются частичными.
