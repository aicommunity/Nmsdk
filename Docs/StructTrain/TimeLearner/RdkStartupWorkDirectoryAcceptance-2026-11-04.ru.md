# Приёмка явного рабочего каталога Rdk —04.11.2026

Rdk develop merge `10e9d05aa658dd2203c89bc84ba9166595b50014` сохраняет
заданный до Init рабочий каталог UApplication. При пустом значении остаётся
каталог executable. SystemDir и штатный путь WorkDirectory/EventsLog сохранены.
Core tree `c4965d0db1875763ce2226b97fc1db04a771035b` совпадает с проверенным
Rdk `0e70cf07ddc52f6af81ac0b291e299434925319c`; после проверки изменена только
документация. Поля/ABI и контракты компонентов Build/Calculate/Reset не менялись.

Реальные проверки выполнены через jump host на Elder normal и M40 ASan.
Source root `b3bfe86e913bc1f7aeb5a340a72698eacb060f00`, PulseLib
`541bf89b9966f63ca5131fa57a31a9ae3f5820ea`, Rdk0e70cf07. Все7 exact children
этого source доступны в origin. Инженерные модели используют двухвходовый LT
профиль и historical same-matrix calibration, не исходный stock Phase A.

На каждом worker подтверждены:

* 4 native preflight без тиков обучения;
* 4 fresh frozen imports по4 полных trial с точным совпадением всех сохранённых
  наблюдений и calibrated packages;
* 4 настоящие калибровки с совпадением всей transaction и итогового model;
* 3 отказа до Init: output внутри runtime, существующий output и INI override;
* concurrent duplicate: один0 и один2, файловые логи только победившего PID;
* неизменность старого и нового runtime directories;
* отдельный обычный запуск того же binary без native flags: прежний default
  executable-directory/EventsLog, ожидаемый отказ отсутствующего project;
* 9 проверок архиватора: штатный alias, чужой PID, escape, dangling link,
  цепочка, другая severity, primary/directory symlink и portable regular copy.

ASan loaded-files действительно содержит libasan, detect_leaks=0; отсутствие
утечек этим не проверено. Это scoped startup/transport gate, не полный CTest.
Первые Console-only и alias-packaging отказы сохранены в primary архиве.
Логи записываются штатным Rdk в частный каталог операции. Реальные log files
входят в evidence; severity alias отдельно проверяется и не дублируется.

Исходные evidence commits опубликованы:
normal `f6004c6f0d3208005c3a14648929735174526f39`,
ASan `948b7f2da761c87b8cb2b09e6bef1cddc7ff6d07`.
Артефакты доступны в Reports/StructTrain/TimeLearner:
`s02-native-event-log-{normal,asan}-a3`,
`s02-rdk-default-startup-{normal,asan}-a1`,
`s02-native-event-calibration-{normal,asan}-a1`.
Каждый пакет содержит primary.tar.xz, bundle и SHA256SUMS. На worker1011
members и315 source hashes независимо сверены с точными Git blobs;
normal archives суммарно9462440 bytes, ASan9043364 bytes.
NativeEventLogNormalVerification.json, NativeEventLogAsanVerification.json
и NativeEventLogRemoteClosure.json фиксируют статическую сверку.

Эта корневая приёмка записывает Rdk gitlink и проверенные артефакты.
Console/ModelSpec2/общий перенос новой feature проходят свою отдельную
приёмку. Научный verdict не выдаётся; исходные этапы1–12 остаются частичными,
полностью завершён только этап0.
