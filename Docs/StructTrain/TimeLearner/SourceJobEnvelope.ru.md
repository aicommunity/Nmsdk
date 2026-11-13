# Побайтное восстановление job вокруг сохранённого source package

Статус: [узкая серверная проверка4/4 пройдена](ValidationPlans/M40SourceJobEnvelopeDataA1-20261113/RESULT.ru.md) на12 настоящих Python/Qt job files из закрытого A4 corpus. Работающий N4 эксперимент, его source/runtime и файлы не меняются. Это подготовка компактной публикации, не изменение способа расчёта; весь N4 publication/restore контур ещё не принят.

В stopped probe один и тот же большой source_stopped включён в исходный job, input/job.json и native/job.json. Сохранение всех этих копий как независимых XZ members избыточно. Сам source package уже должен быть сохранён в Git как необходимый первичный материал; ссылка на абсолютный путь M40 его не заменяет.

Codec сохраняет оригинальные prefix/suffix bytes и тип известного вложенного представления source_stopped. Поддержаны production Python indent2 и Qt indent4. Python-вариант воспроизводит существующий json.dumps с ensure_ascii=False/indent2/allow_nan=False; Qt-вариант добавляет ровно один уровень отступа к исходному Qt document. Применение разрешено только при полном побайтном совпадении вычисленного payload с оригинальным span. Неизвестный layout остаётся literal, без попытки нормализовать или исправить данные.

Recipe хранит размер/SHA256 reference document и оригинального job, codec version и base64 prefix/suffix. Restore проверяет reference bytes, допустимый schema/codec и бюджеты, затем восстанавливает весь исходный файл и сверяет его размер/SHA256. Вывод в новый файл разрешён только после успеха. Recipe не содержит исполняемых команд или путей.

Исходные jobs, run manifests, native execution records и их hashes не переписываются. Перед production audit восстанавливаются исходные bytes; аудитор не читает recipe вместо настоящего job. Любая экономия размера считается доказанной только после actual-file roundtrip. Сам codec не подтверждает валидность JSON, native execution, обучение, принадлежность пика или классификацию.

Для публикации N4 нужны recipe index, проверка полного восстановленного namespace и повторный production audit на его больших файлах. Узкие primitive-тесты сами по себе этого не доказывают; последующий пакетный контур описан ниже. Внешнее переиспользование source из другого Git archive/member требует отдельно закреплённой dependency и ещё не реализовано.

## Подготовка пакетного применения

Добавлен source_envelope_bundle: finite source map и явные target/source роли, literal compact_native_primary schema2 плюс recipes и общий индекс исходных byte hashes. Source document остаётся literal member; ссылки на другой recipe target запрещены, циклов нет. Неподдержанные layouts остаются literal с явной причиной. Restore сначала восстанавливает literals штатным portable_primary, затем исходные jobs, после чего проверяет весь namespace/размеры/SHA256. Glog aliases используют прежний явный compatibility adapter.

closed_primary_bundle manifest3 добавляет только source_envelopes; прежние manifest1/2 сохраняются. Семантика manifest3 — bytes/closure, без controller-join attestation из manifest2. Максимальный archive budget применяется ко всему пакету, включая recipes и индекс. Упаковка допускается лишь после полного закрытия исходного задания и проверки его конечного namespace.

Пакетный путь принят в узкой области фактического A4 corpus: [5/5 DATA checks](ValidationPlans/M40SourceEnvelopeBundleA1-20261113/RESULT.ru.md), [штатный manifest3 collector](ValidationPlans/M40SourceEnvelopeCollectA1-20261113/RESULT.ru.md), [actual produced package restore и шесть primary audits](ValidationPlans/M40SourceEnvelopeProducedA1-20261113/RESULT.ru.md). Большой N4 corpus этим не проверен. Для N4 пока не обещано внешнее Git source reuse: пакет хранит один literal source внутри себя. Вынос уже опубликованного source в проверяемую Git dependency остаётся отдельным шагом. Работающий эксперимент не переключается на новый формат.

[Независимый Elder Git-only restore](ValidationPlans/ElderSourceEnvelopeGitReplayA2-20261113/RESULT.ru.md) также принят: исходные bytes706 files/18 jobs восстановлены из опубликованного формата перед шестью production primary audits. Проверка относится к N2 corpus; large-file N4 и научный verdict не заявлены.
