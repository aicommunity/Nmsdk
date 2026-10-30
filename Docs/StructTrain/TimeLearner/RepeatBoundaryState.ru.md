# Повторы N0 и перенос состояния на границе этапа

Подэтап `codex/timelearner-repeat-boundary`, начат 30.10.2026. Это продолжение
проверки [политики повторов N0](N0CandidateRepeats.ru.md), а не приёмка всей
матрицы export/import или controller checkpoint посреди пробы.

## Выявленный дефект

`RestoreBoundary` / `RestoreStoppedBoundary` штатно восстанавливают модель,
references, certificate либо диагностическую остановку, но не объект поиска.
`EncodeNativeTrainingState` выбирал schema 2 по сохранённой политике повторов,
а обязательный `candidate_repeat_groups` создавал только при наличии Search.
После импорта получалась сводка schema 2 без этого массива. Также отсутствовала
явная граница между историей поиска и proof конечного графа; выдавать actual
parameters за снимок принятого кандидата при отсутствии Search нельзя.

Baseline root `a6cfc24acf00f5bf8a235ad7872741bb9e05da3f` / Pulse develop
`b2b670a22f849e0d0d2b6789b8242308521b1c37`: Elder воспроизвёл все десять
отказов, каждый ровно в двух новых проверках сводки. Прочие проверки native
импорта, графа, frozen отклика, fresh-process и warm boundary не дали отдельных
отказов. M40 ASan baseline также завершён с десятью отказами; точные
assertion locations и post-run runtime readback проверяются до fixed run.

Baseline-пакеты опубликованы с полными первичными данными и XML failures:
[Elder](../../../Reports/StructTrain/TimeLearner/s05-repeat-boundary-baseline-elder1-a1/README.md)
`779d34e7b3522db4c07cd24233de82a6f54518dc`,
[M40](../../../Reports/StructTrain/TimeLearner/s05-repeat-boundary-baseline-m40-a1/README.md)
`b5e0c526bfad1edf2772c9adbbf774402584478f`.
Все 338 stored hashes каждого пакета проверены локально. Native XML каждого
подтверждает ровно двадцать assertion failures на строках 1609/1610 baseline
fixture; terminal runtime readback выполнен успешно перед fixed run.

## Контракт исправления

- Новые сводки schema 1/2 содержат boolean `search_history_retained`.
  `true` означает доступность текущего объекта Search и его записей;
  `false` — отсутствие сохранённого Search, а не нулевую стоимость обучения.
  В старых сводках отсутствие поля остаётся unknown.
- Schema 2 всегда содержит массив `candidate_repeat_groups`, в том числе
  пустой при отсутствии Search. Идентификаторы и значения не выдумываются.
- При `search_history_retained=false` отсутствуют `accepted_parameters`,
  `search_probes`, `applied_edits`; candidates/rejections/domains/groups пусты.
  Для completed boundary анализ проверяет сохранённые reference/final packets,
  certificate, model binding, допуски и допустимость actual parameters.
  Он не утверждает наличие измеренной истории поиска.
- Удаление marker не разрешает пропуск обычных search fields: legacy unknown
  по-прежнему требует имеющийся снимок accepted parameters. False marker с
  непустой историей, неверный тип marker или неподтверждённые группы отвергаются.
- Декларация повторов в full model package связывается со schema/factor сводки.
  Изменение repeat factor и пересчёт package checksum не скрывают расхождение.
- Native evidence auditor получает версию 5; learned/stopped auditors — 2.
  Исторические результаты не пересчитываются молча под тем же идентификатором.

Математическая цель, допуски, порядок предъявлений, storage physics и lifecycle
не меняются. Частичная группа до Stop сохраняется в исходной истории; модельный
архив не объявляется checkpoint этой группы. Warm attempt начинает новый поиск
на сохранённой цели, а не продолжает незавершённую интеграцию.

## Матрица адресных проверок

Обе топологии, configured V2 N0 repeats=2:

1. Completed Train → import → native Build/Init/Reset → frozen сравнение
   полных stimulus/soma traces и fresh-process import.
2. То же с явным SyncTolerance=0.2 для warm boundary control; это не доказательство
   сходимости при исходном 0.02. Сохранённые references и номер новой попытки
   проверяются отдельно.
3. Stop до первого завершённого reference.
4. Stop после первого reference (незавершённый capture).
5. Stop после первого из двух измерений кандидата: incomplete group из одного
   sample, без сертификата. Импорт и новый warm attempt сохраняют диагностический
   статус и физическую модель.

Python-проверки используют эти реальные JSON/CSV, сравнивают исходные и imported
summaries, full package hashes, primary packet identity, partial raw samples и
явно повреждённые копии metadata. Synthetic mutations не являются научными runs.
Для warm completed attempt добавлены actual CSV каждого измерения и отдельная
warm summary: прежний fixture сохранял только JSON этой фазы, чего недостаточно
для обязательных временны́х графиков. Это требует отдельного native-прогона,
а не восстановления waveform из reference/final JSON. Проверка старых полных
графиков дополнительно сравнивает каждый embedded packet/CSV с actual source;
одного совпадения trial ID недостаточно для связи рисунка с запуском.
Исходная неуспешная baseline попытка сохраняется. Ошибка её post-run скрипта
при JSON-сериализации возвращаемого Path — отдельный инфраструктурный дефект;
она не заменяет двадцать native assertion failures. Повторный readback runtime
сохраняется отдельным файлом после завершения.

## Оставшиеся требования

Elder fixed A2 на root `7369ae85cc914c5e3f05d919c35fd9b8890d9d97` прошёл
51/51 native tests без ошибок. Его post-audit остановился из-за неверного
выбора `_service_` вместо `_xmlprobe_` для XML-load fixture; это не отказ
алгоритма или native import. Selector исправлен в final audit и source-bound
plot check. Elder A3 содержит также warm CSV; M40 A3 выполняет тот же C++ код
с warm logging. Отдельные producer/auditor SHA должны сохраняться при readback.

Нужны результаты fixed native/ASan, независимый Python audit, необходимые
временные графики и согласованные develop merges. Частота 20000, N>4, все
PostTune/calibration/conversion варианты и полный controller checkpoint не
закрываются десятью addressed cases автоматически. Общий план остаётся активным.

Elder final A3 на root `02cf1542de6edfd67aa9da15798d34dd1b0eb08f` завершён:
51/51 native и 77/77 Python tests без skips/errors, process status 0.
Проверены новые warm CSV, сохранённые цели, полные исходные/imported proofs,
диагностические stops, повторный source-bound readback старых графиков и
совместимость прежних N0/N1 пакетов.

M40 ASan A3 также завершил 51/51 native tests. Его исходный post-audit сохранил
ошибку XML selector; отдельный readback на auditor root 02cf1542d прошёл 77/77
tests без skips/errors, process status 0. Native producer root 8d73c0fd5
содержит тот же C++ код и gitlinks: это проверено до readback, без нового
запуска моделей. [Elder пакет](../../../Reports/StructTrain/TimeLearner/s05-repeat-boundary-elder1-a3/README.md)
`e5d97b47325fb871584ce61e46d402b3df7c2562`,
[M40 пакет](../../../Reports/StructTrain/TimeLearner/s05-repeat-boundary-m40-a3/README.md)
`fb73b3e5bcdef4612640631f8060310e44e08749` опубликованы;
все 1986/1089 stored hashes проверены локально. Полные новые временные графики,
объединённый Python gate и согласованные develop merges остаются открыты.
