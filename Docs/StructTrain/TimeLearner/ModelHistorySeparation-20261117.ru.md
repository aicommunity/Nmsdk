# Разделение модели и истории: уточнение этапа5

Наблюдение по коду: NativeRecognitionState.cpp сохраняет весь `source_solo`
в recognition package, затем PrepareRecognitionPackage снова вычисляет
conversion из этого полного источника. Python stopped/recognition auditors
также проверяют историю. Физика небольшой модели и сотни измерений повторно
передаются вместе при каждой frozen серии. Baseline старой модели содержит
stopped source271032927 байт; фактический recognition candidate —317475838 байт.
Загрузка и анализ занимают значительно больше времени, чем native Test.
Точные доли времени отдельных функций пока не профилированы.

Отдельное несогласование входов видно в PulseLib891259ea:
ParseNativeLearnedState ограничен128MiB, ParseNativeRecognitionState —256MiB.
Сохранённые крупные документы превышают эти пределы. Уже принятые large
roundtrips вызывают Prepare с QJsonObject;317-МБ control проверяет hash.
Они **не подтверждают** эти публичные string-parser пути. Пока это проверка
по коду и фактическому размеру, а не отдельный runtime-reproducer parser.

Продолжение исходного этапа5:

1. Проверить реальные entry points на сохранённых больших документах и
   записать точную причину отказа. Сопоставить пределы codec с объявленными
   бюджетами; не расширять все лимиты произвольным числом и не выдавать
   успех hash за успешный Load.
2. Выделить небольшой физический модельный payload через существующий
   ModelArchive: storage definitions, весь граф, связи, индивидуальные Rs/C,
   частота, dataset/target, итоговый threshold и solo/recognition marker.
   История и controller checkpoint — отдельные связанные artifacts. Сохранить
   исходные форматы через явные compatibility adapters и исходную историю.
3. Связывать полный training evidence и его качество с **конкретным** model
   hash. Frozen import и измерения проверяют действительный граф и динамику.
   Полная история остаётся доступной для независимого аудита; она не должна
   автоматически становиться controller checkpoint или сертификатом Exact.
   Нельзя заменять проверку источника доверяемым JSON-флагом либо опускать
   зависимости, повреждение которых меняет заявленный verdict.

Нужны реальные non-symmetric roundtrip и waveform tests обеих топологий,
solo/conversion save-load без повторного scaling, повреждение связей/класса/
индивидуального параметра и отсутствие evidence dependency. Rest-state,
native Build/Init/Reset и storage ownership остаются штатными. Новая архитектура
не должна задерживать уже запущенные опыты и подменять цель обучения.
