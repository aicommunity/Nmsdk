# Configured native controller: версия 2

Рабочая ветка `stage06/configured-native-controller`. Реализация подготовлена;
серверная проверка и приёмка этой редакции ещё не завершены. Этот документ не
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

Подготовлены Classic/Branch × N0/N1 configured searches, строгий codec roundtrip,
corruption controls, защита от незаметного cold reset и сохранность после Build/Reset.
Проверки не должны вызывать BeginNativeTraining для запуска configured поиска.
Научный PASS и полная mode/physics matrix этим подэтапом не обещаются.
