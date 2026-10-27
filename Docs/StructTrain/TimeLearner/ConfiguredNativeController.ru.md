# Configured native controller: версия 2

Подэтап `stage06/configured-native-controller` прошёл адресную серверную проверку.
Он подключает V2 cold configuration через штатные параметры и XML Load, но не
меняет классификацию целых этапов плана и не объявляет готовым trained-state import.

`ControllerVersion` по умолчанию 1: существующие конфигурации сохраняют legacy
dispatch. Значение 2 включает explicit native cold configuration из строкового
параметра `ControllerConfiguration`. Это JSON schema 1, kind
`timelearner_native_cold_configuration`, с ModelSpec, фактическим профилем
генератора, начальными ISI, окнами, допусками и конечными бюджетами поиска.

Build разбирает декларацию и выполняет storage-owned cold builder только один
раз. Последующие Build сохраняют граф и проверяют actual readback. Перед первым
Calculate дочерних компонентов native Before hook запускает общий training
service. Ручных Calculate и перехода к legacy между пробами нет. CalculateMode
0 автоматически снимает Need по окончании; mode 1 сохраняет внешнее управление.
Внешнее снятие Need останавливает управление без Exact; новый фронт Need после
остановки сбрасывает временный контроль, сохраняя goal до явного retarget.

Parser запрещает неизвестные/отсутствующие поля, неверные типы, дробные counters,
нечисловые/nonfinite значения и дублирующиеся JSON keys, включая Unicode-escaped
написания одного ключа. Отдельные model/search/probe поля валидируются до проб.
Pattern hash и canonical input/stimulus IDs выводятся из объявленного порядка
ISI, а не задаются несогласованными копиями. Actual source physics проверяется
против декларации; storage profile должен быть зарегистрирован штатным способом.

Callbacks и наблюдения не являются частью конфигурации. Read-only evidence sinks
подключаются отдельно; ошибки sink отклоняют наблюдение. Общая физика принадлежит
storage images, индивидуальные начальные Ns/Rs — ModelSpec. Неиспользуемые legacy
optional C-trim/PostTune/calibration пока отклоняются явно и остаются обязательной
незавершённой частью полного рефакторинга.

`ConfiguredModelInitialized` — сохраняемый guard холодного построения. Если после
Load/Copy имеется этот marker, но отсутствует process-local native declaration,
Build отклоняет состояние с `configured_trained_model_requires_explicit_state_import`.
Это предотвращает молчаливую замену обученного графа исходным. Поддержка полного
versioned trained-state import/export остаётся следующим обязательным шагом;
marker не является checkpoint и не доказывает обученность.

Guard помечен и Parameter, и State: Rdk Copy(false) вызывает Build после
копирования параметров, до копирования состояния. State-only marker оказался бы
слишком поздним. При восстановлении нового экземпляра property setter допускает
загрузку самой декларации независимо от порядка полей, но Build удерживает
диагностику до полного trained-state import. Пройдены реальные XML Load,
Copy(false) и Copy(true) controls для обеих топологий с heterogeneous child C.

Пройдены Classic/Branch × N0/N1 configured searches, строгий codec roundtrip,
corruption controls, защита от незаметного cold reset и сохранность после Build/Reset.
Проверки не должны вызывать BeginNativeTraining для запуска configured поиска.
Научный PASS и полная mode/physics matrix этим подэтапом не обещаются.

## Проверки и артефакты

| Снимок root | Проверки на каждом сервере |
|---|---|
| `17eff7e4d01dd7b542342302524c23637f1f8f6d` (A1) | 6/6 configured и 97/97 builder/service/editor/lifecycle/bounded/final/assigned regressions |
| `e6b576d2a36a309a84f49e33ef359b216f8154bf` (A2) | 12/12 configured, 97/97 regressions; M40 ASan 12/12 |
| `cb9e035b390390746ada5caa2c500917b8884612` (A3) | 14/14 configured (включая два настоящих cold XML starts), 21/21 addressed native builder/service regressions; M40 ASan 9/9 XML/Copy/codec |

A3 PulseLib: `971c6a7b5c08aa674b72a46c798c7392d9e1acec`;
Bin: `5727448ba5c543e10bb96a96f1fef4d34a2be954` (ClDesc трёх новых свойств и
уточнения CalculateMode/AdditionalInputPattern). ASan: detect_leaks=0; отсутствие
всех утечек не доказано. После единственной A3 owner-guard строки не повторялась
вся A2 матрица 97: финальные 14 configured и 21 native regressions покрывают
затронутое поведение; полного CTest на A3 не заявляется.

Первый A2 Python-аудит сохранил два failures: corruption tests предполагали
isolated baseline, а assigned-пакету записывали уже установленную политику.
Production auditor не ослаблялся. Исправлены сами мутации: explicit isolated
semantics для whole-burst окна и переключение фактической политики на другую.
На каждом сервере все 18 tests прошли на configured assigned data и отдельно
все 18 — на настоящих legacy isolated data, без skips.

Независимо проверены 308 service CSV/packets и 22 negative certificate summaries
A2/A3, в том числе 28 проб из cold XML; также 16 builder packets и четыре
assigned/isolated diagnostics. Серии перекрываются и проверяют реализацию:
их нельзя считать независимыми научными обучениями. Все search outcomes —
честные SearchUnresolved; научного verdict пакет не производит.

Git-пакеты со всеми попытками и первичными данными:
[Elder-1](../../../Reports/StructTrain/TimeLearner/s06-configured-controller-elder1/README.md),
[M40](../../../Reports/StructTrain/TimeLearner/s06-configured-controller-m40/README.md).
Локально после Git-получения проверены 4682 stored hashes и 4678 raw gzip
payloads без ошибок: [машинная сводка](ConfiguredNativeController.validation.json).
Опубликованные merge commits develop: PulseLib
`c1d5b177278f1eb347c1ebc725555837c36642bb`, Bin
`f5e1d0200127223981daa71da22cf5ee02fdbc60`. Root фиксирует именно эти gitlinks.

## Открытые требования

Полный trained-state export/import и Train→Test, reconfiguration/retarget с новым
протоколом, geometry-dependent Rs domains, production длительности окон/recovery,
C-trim, conversion/PostTune/calibration, вся physics/mode matrix и scientific
controls остаются обязательными. Зарегистрированные storage recipes должны быть
доступны принимающему runtime; один JSON с именами образов не переносит их
определения. Новый controller пока не рекомендуется как завершённая замена всех
существующих научных конфигураций. Ошибки конфигурации удерживаются typed
диагностикой; public Build/Reset/Calculate bool не используются как error channel.
