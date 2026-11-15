# Независимый DATA reader archive2 и штатный анализ сохранённого case

Статус: подготовка исходников, локально выполнены только AST/Git/text checks.
Численные unit tests, actual archive2 replay, CLI на actual шести A4 exports
и остальные серверные gates этим изменением не объявляются пройденными.

Основа Root: `4f68328c8e54daaed445dea7337563d50711a0bf`. Контракт сверялся с
Root `7ad96da0e66fe1ef51fc76acb2114174ab6a4e68` и PulseLib
`4b70b0bfb41510691971de86ce5c4993bb382b8b`, прежде всего
`NativeCompositeTrainingEvidence.cpp`, `CandidateWindowProposalReplay.cpp`,
`CandidateWindowPortableReferences.cpp`, `CandidateWindowMeasurementEvidence.cpp`,
`CandidateWindowPolicy.cpp`, `NativeDeclaredWindowBasinAssignment.cpp`.

## Область реализации

`audit_composite_measurement_archive` делает явный dispatch archive2 в отдельный
`candidate_window_archive_evidence.py`. Старое тело archive1 остаётся прежним.
`candidate_window_contract.py` проверяет cold7/common-policy2 и protocol5/contract2
через частный неизменяющий исходный документ common-field view; публичные
парсеры cold1–6 и CLI Train не получают разрешения принимать cold7. Версии
package6/certificate3/summary7/execution4 здесь не реализованы и не должны
неявно обрабатываться старыми codecs.

Reader проверяет точные поля, типы, конечность и целочисленность счётчиков,
размерности до индексирования, source/model/storage/C0, callback/packet/raw
inventories, actual masks и ISI hashes, clock declarations, первичные байты,
повтор полного burst, фактические сетки/события, reset/instance/model bindings,
chronology и объявленные бюджеты. Embedded primary обязательны. Если задан
external resolver, каждый соответствующий файл также обязателен и должен
побайтно совпасть; скрытого fallback нет.

Как и существующий Qt codec, новый wire принимает конечные integral JSON
numbers (например, 1 и 1.0 имеют одну numeric семантику), но не bool, строки
или дробные индексы. Частный integral-number view не меняет canonical binary64
digest и не изменяет исходные JSON bytes; публичные старые readers не
переводятся на новую политику типов.

`candidate_window_binding_evidence.py` заново читает L/Ns/Rs, ordinal, attachment,
ExcChannel receiver и каждый ExcSynapse/member/link из полного semantic model,
а не только из `physical_readback` или его hash. Различные Rs разных входов
поддерживаются. Неоднородные Rs ВНУТРИ одного управляемого банка пока
не поддерживаются C++ DATA-контрактом: каждый член должен иметь bank control Rs.
Это ограничение представления/редактора, а не физическая невозможность.
Данные не выравниваются и storage-образы не переписываются. В production
`NativeModelEditor.cpp::ReadNativeInputParameters` явно отвергает такую
неоднородность (`heterogeneous_native_input_bank_resistance`) до создания
service actor/дорогих N+2 групп. Расширение владения параметрами и корректный
heterogeneous-bank control остаются отдельным regression TODO плана.

Reference seed возникает только после независимого replay полной primary,
geometry и proof исходных allN references. P0/C0/source/grid/family остаются
исходными. Partial staged references не считаются consumed completeRefSet.
Warm не переснимает seed с обученного графа. Для каждого search/final заново
вычисляются только объявленные integer arithmetic features, окно, recipe и
measurement instance hashes; самосогласованный чужой hash не заменяет replay.

Окно candidate_frame проецируется на retained actual timestamps full-before,
без dt-интерполяции, clamp и автоматического допуска в один шаг. Экстремумы
и basin necessity пересчитываются независимым существующим Python geometry
selector по полной waveform; версия influence-exclusive v1 пересчитывается
как часть portable witness, её validity не используется как Train admission.
Peak должен следовать actual assigned event. Scalar arrival/plateau_end
отсчитываются от actual protocol origin event этой группы. Нет замены peak
прогнозом, глобальным максимумом или difference waveform.

Archive2 проверяет append-ledger order, неизменность caps внутри attempt,
суммы groups/raw probes/samples, bytes каждого attempt и retained prefix
против действовавшего тогда cap, а также весь retained prefix против текущего
cap. Выбранные final принадлежат одному current/latest OBSERVED final run,
одному графу/epoch; исторические references могут принадлежать старому attempt.
Незаписанное live intent из JSON не выводится.

Временные поля остаются declarations/observations: complete portable context
даёт проверяемый нижний предел model span; wall_enforcement сохраняет
утверждение producer о проверке перед mint. End wall time не подставляется
вместо несуществующей checked-before-mint отметки. Старые deadlines закрытых
references не продлеваются через все последующие группы. Partial context
не дополняется вымышленными reset/model witnesses, peaks или packets.

## Штатная команда анализа

```text
python -B -m Scripts.StructTrain.TimeLearner analyze CASE_DIR --format native-composite-measurements --output NEW_REPORT.json
```

Обязательны `initial-configuration.json`, `runtime-plan.json`,
`composite-measurements/index.json` и все внешние CSV по сохранённым paths.
Новые отчёты должны находиться вне исходного case; существующий отчёт
не перезаписывается. Используется общий version dispatcher, новые launcher,
orchestrator или команды Train не добавлены.

Результат содержит полный компактный DATA audit, exact-byte hashes трёх JSON,
coverage и статусы каждой группы, записанные причины с явным флагом их
независимого пересчёта, geometry и измерения/arrival/proof. Base64/CSV/models
повторно не вкладываются. Нулевое число measured видно непосредственно.
`native_execution_verified`, `live_authority_restored`,
`training_certificate_verified` остаются false; scientific verdict отсутствует.

## Проверки и доказательный предел

Новые controlled tests разделяют arithmetic, graph DATA, proposal replay,
ledger, timestamp projection, полный portable context/new geometry и CLI
transport. Искусственный semantic graph не называется actual native model;
положительный mock используется только на границе CLI transport и не является
semantic acceptance. Actual archive2 и Train5 по нему не принимаются.

Подготовлены 39 DATA unit methods и 6 CLI transport methods; ещё один новый
CLI method требует actual шесть exports. Старый actual suite сохраняет 7
methods. Это AST inventory, не результат исполнения: будущие unit и actual
gates надо объявлять и выполнять отдельно на сервере.

Существующие actual-seven tests сохранены как семь методов. В первом теперь
есть явная ненулевая measured coverage четырёх positive case. Ожидания взяты
только из шести `index.json` Git evidence
`b4feb38aeed9940c4292b532b3de0e3ab853685e`,
`Reports/StructTrain/TimeLearner/s07-composite-cold6-m40-asan-a4/primary.tar.xz`:

| Case | Groups | Complete | Measured | Consumed | Refs/finals | Attempts |
|---|---:|---:|---:|---:|---:|---:|
| classic-service | 6 | 6 | 6 | 6 | 2/2 | 1 |
| branch-service | 6 | 6 | 6 | 6 | 2/2 | 1 |
| branch-C0 | 6 | 6 | 6 | 6 | 2/2 | 1 |
| classic-warm | 6 | 6 | 6 | 6 | 2/2 | 2 |
| branch-ambiguous | 1 | 1 | 0 | 0 | 0/0 | 1 |
| classic-partial | 1 | 0 | 0 | 0 | 0/0 | 1 |

Локально читалась только metadata index JSON; CSV, peaks и residuals не
анализировались. Отдельный actual CLI test должен на сервере сохранить шесть
отчётов по этим исходным шести case, через новый публичный analyze format.
Седьмой native bundle не создаётся. Future actual2 gate требует настоящих
экспортов R20/следующего native window gate и независимого replay всех primary;
synthetic tests и A4 archive1 не заменяют его. Отдельные mechanical A/B,
callback/lifetime, native growth N4/N6, Train consumers и CLI Train→Test gates
остаются обязательными в исходном плане.
