# Cold6: числовой отказ после same-object JSON proxy assignment

A3 Root `b6d0f752ca1668b6a908a435438020db58d2018e` / Pulse
`88ea9c7ab3583da601b1f01ec84bf6f122875a34` завершился на первом strict cold6
roundtrip:230 PASS,1 FAIL,17 not run. Сообщение
`invalid_native_configuration_number` не является ошибкой интегрирования
нейрона. Отрицательная evidence собирается отдельно; весь248 не принят.

В `ConfiguredNativeTraining.cpp` encoder6 присваивает
`result["base_schema_version"]=result["schema_version"]` перед изменением schema.
Обе операции mutable `operator[]` возвращают Qt JSON proxy. Вставка нового
ключа слева может сдвинуть позицию, на которую всё ещё ссылается правый proxy.
Ранее реализованный recovery5 уже читает owning `result.value(...)` безопасно.
Цепочка source соответствует наблюдаемому отказу строгого числового decoder;
точное испорченное значение конкретного raw-файла ещё требует проверки evidence.

Минимальное baseline-исправление подготовлено в Pulse
`4a5c2ec9df9a9f704dcd8260714323494bfa4415`, отдельная ветка
`codex/timelearner-cold-schema-owned-value`, от исходного88. Оно сохраняет
owning `const QJsonValue baseSchema=result.value("schema_version")` **до**
добавления ключа, затем присваивает эту копию. Range1–4 и strict Number/decoder
не ослабляются; physics, scheduler, learner callbacks и defaults не меняются.
Root regression controls и серверная приёмка этой правки ещё готовятся.

На будущей source-линии обнаружены ещё два таких места: cold7 в Pulse800/b287
и `WrapNativeCompositeExecution` в Console header
`TimeLearnerCompositeArtifacts.h` RootE11. Они требуют отдельных обычных merges
baseline-фикса и targeted follow-up; новый Train5/control-lifetime код не должен
незаметно попасть в baseline A4. Подготовленные E11/BB1 SDK snapshots сохраняют
свои фактические исходники и имеют это известное ограничение; запускать их как
уже исправленные источники нельзя.

Archive23 PASS проверяет native group transport/proofs, но не подменяет cold6
decode: `SaveCompositeBoundary` записывает initial configuration как есть.
Поэтому наличие шести полных CSV/model/runtime документов ещё не доказывает
корректность их initial cold6 envelope. Raw JSON не изменяются, повреждённый
признак не превращается в число неявным coercion, первичные waveform не
объявляются ошибочными автоматически. Нужно отдельно установить область
повреждения и strict reader outcome на фактических artifacts.

Следующий запуск должен сначала достигать двух исходных declaration controls,
focused base1–4/serialized-byte codec checks и ранее не выполненных config paths,
затем расширяться до заявленной regression-матрицы. Очередь/CanonicalSpec
переоформляются до запуска; старый A3 не перезапускается и его source/cache/runtime
не обновляются. Успех маленького codec gate не объявляется полным248 PASS.
