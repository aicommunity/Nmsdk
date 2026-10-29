# Идентичности условий, runtime и анализа

Рабочий подэтап 10; новый runner/queue/publisher ещё не реализован. Source
`670f2ff79d843d72f0703783cab49defc4159274` прошёл адресные проверки ниже на обоих
workers; это приёмка codec/relocation scope, а не всего этапа.

## ConditionSpec

`Scripts/StructTrain/TimeLearner/condition.py` задаёт immutable descriptor schema 1.
В нём обязательны ControllerVersion 1/2, CapturedPerInput и одиннадцать content refs:

| Role | Что обязано быть в соответствующем semantic artifact |
|---|---|
| algorithm | Релевантная реализация алгоритма/интегратора и версия |
| model_spec | Native ModelSpec, topology/frequency, параметры структуры |
| storage_profiles | Неизменяемые определения используемых образов и зависимости |
| initial_state | Явный cold declaration, saved state либо warm boundary; исходная модель |
| training_plan | Поиск, tolerances, разрешённые изменения и budgets |
| input_data | Реальное содержимое паттернов, метки/ID и partition |
| presentation_protocol | Порядок, timestamps/ITI convention, reset policy, полные окна |
| calibration_spec | Fixed / Historical Same-Matrix / independent protocol и данные |
| evaluation_spec | Замороженная модель/порог, данные и критерии оценки |
| execution_policy | Существенные условия остановки/лимиты, включая stall_autosave_n |
| randomness_spec | Детерминизм либо реальный RNG/seed и контракт Reset |

Даже режим Off задаётся явным artifact. Descriptor не принимает поля case label,
server/output/binary paths: они относятся к RunManifest/attempt provenance.
Смена directory или постороннего case не должна менять condition ID.
Для condition artifacts рекурсивно запрещены распространённые attempt/deployment
поля (run/trial/attempt/case ID, host/PID, deploy/output/executable paths).
В частности, полный EncodeConfiguredNativeTraining с run_id нельзя передавать
без semantic projection. Стабильные sample IDs и trial templates остаются
частью data/protocol; уникальный runtime trial_id относится к observations.
Это guard известных полей, а не универсальное распознавание смысла любой строки.
Вся семантика существенного параметра должна попасть в artifact; одно имя/номер
версии без содержимого недостаточно.

Каждый artifact — закрытый envelope с kind/schema/role/payload/digest. Payload
хешируется существующим production `canonical_model_sha256` (length-framed
UTF8/binary64), с domain separation по role. Descriptor producer/reader используют
один codec. Проверяются все refs, role и digest, duplicate keys (включая escaped),
unknown/missing fields, NaN/Inf, неверный Unicode и целые вне точной binary64
области. Большие integer IDs/uint64 seeds должны кодироваться строкой в своей
схеме. Представления 1/1.0 и ±0 нормализуются, bool не превращается в число.

Это **проверка целостности descriptor**, не semantic preflight. Нативные codecs,
capability/property registry, effective readback, реальная принадлежность RNG,
полнота data split и доступность артефактов ещё должны проверяться runner.
Наличие digest не доказывает применение фактора или готовность к Train.

## Раздельные оси identity

- Condition fingerprint содержит только descriptor одного условия.
- Matrix fingerprint содержит отображение case ID → condition; duplicate IDs запрещены.
  Перестановка перечисления cases не меняет matrix ID; изменение другого case
  меняет матрицу, сохраняя identity исходного условия.
- Attempt ID — отдельный UUIDv4; не seed, не повторяемость и не scientific condition.
- Model fingerprint берётся из фактического semantic model readback.
- Runtime fingerprint описывает загруженные binary/library contents и build context.
- Analysis fingerprint связывает condition/model/runtime, observation set, scorer
  и calibration result. Смена scorer не требует изменения прежнего condition ID
  и не переписывает старый verdict.

## Runtime manifest schema 2

В прежней schema 1 `runtime_fingerprint` включал CMake paths. Поэтому одинаковые
бинарники, перенесённые в другой deploy root, могли получить иной fingerprint.
Новая `runtime_content_identity` исключает только CMAKE_C_COMPILER,
CMAKE_CXX_COMPILER, NMSDK_DEPLOY_ROOT и NMSDK_RESOURCE_ROOT из identity flags.
Полные paths/flags остаются в provenance. Хеши executable, app.ini, compiler,
resolved libraries, остальные flags и optional loaded mapping snapshot остаются
существенными. Изменение содержимого INI — изменение identity, даже если причиной
стала строка пути внутри INI: это не автоматический анализ эквивалентности ресурсов.

Отсутствующие loaded maps (unknown) не равны пустому либо известному набору.
Снимок maps не доказывает историю загрузки plugins за весь runtime. Capture
по-прежнему проверяет owned executable/файлы; чистая identity projection сама
не читает filesystem и не подтверждает процесс. Schema 1 manifests/results
сохраняются историческими и автоматически не пересчитываются как schema 2.

## Постановка проверки

Подготовлены tests codec roundtrip/all refs, повреждения/duplicate/unknown schema,
числовая канонизация, stall/presentation sensitivity, matrix isolation, scorer и
attempt separation. Для runtime — relocation/suffix/compiler path, реальные
content/flags changes и unknown/known mappings. Все 18 tests прошли на Elder/M40.
Дополнительно production snapshot на каждом worker прочитал настоящий A2 runtime
до/после копирования executable/INI в другой каталог и добавления `.rs2` к имени.
Bytes INI сохранены, deploy/resource flags различны, identity/fingerprint равны.
Binary действительно запускается и перечисляет NativePostTuneGraphBoundary.
Это loader/startup control, а не численный replay или история plugins.
Для достоверного source closure создан чистый Git checkout root
`325052a0802e431f45ed91619c089fbc0eef7922` со всеми семью точными gitlinks.
Исходные executable/INI hashes сверены с A2; allowlisted cache восстановлен из
сохранённых A2 flags, а не из изменившейся текущей сборки.

Артефакты: [Elder](../../../Reports/StructTrain/TimeLearner/s10-identities-elder1/README.md)
commit `c05b75aec4b8952002af3d4e91d4e07d60c8f96b` и
[M40](../../../Reports/StructTrain/TimeLearner/s10-identities-m40/README.md)
`976bdfcf71fd67593450e08f303cfa90a0df01f1`. На каждом локально проверены все
14 stored / 12 raw hashes. Научный verdict отсутствует.

Далее обязательны producer/resume roundtrip,
подключение к prepare/runner/queue и fail-closed публикации. Старые Bin fingerprints
не заменены этим модулем; TL-007 и весь этап 10 остаются открытыми.
