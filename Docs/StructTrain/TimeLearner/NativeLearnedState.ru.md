# Native learned state: перенос завершённой границы обучения

Рабочая ветка stage05/native-trained-state. Реализация подготовлена; серверная
проверка и полная приёмка ещё не завершены. Этот документ не закрывает этап 5.

## Подтверждённое дополнение A6 и межсерверный перенос

Root `7186788be098a58091a14025d664647e5d9eb2cd`, PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`: на каждом сервере пять новых
проверок и 43 регрессионных прошли; в каждом наборе один служебный role-helper
skip. Родительские tests отдельно запускают этот helper в свежем процессе.
Проверены Classic/Branch × N0/N1 и отдельный Exact-control с SyncTolerance=0.2.
Same-process и fresh-process frozen CSV совпадают побайтно.

Через Git выполнены оба направления межсерверного переноса: пять пакетов
M40 → Elder-1 и пять Elder-1 → M40. Во всех случаях совпали model hash,
сертификат и весь frozen CSV, без числового ослабления сравнения.
Независимый Python-сериализатор совпал с C++ по трём SHA для каждого из пяти
пакетов на каждом сервере: envelope, physical archive и semantic model.

Все A1–A6, включая compile failures и неудачные fresh-process попытки,
опубликованы с stored/raw SHA256 в разделах
`Reports/StructTrain/TimeLearner/s05-native-learned-elder1` и `s05-native-learned-m40`.
Межсерверные supplements опубликованы commits
`fe7b21f0b557e668c3e2dde4db472b5fc6ee0763` и
`94d0ce7410e0a793f3dbab0cd4f5eb8020f02509` соответствующих evidence branches.
Они объединены в рабочую ветку merge commits; develop ещё не обновлён.

В A5 исправлено общее разрешение executable и соседнего runtime ini независимо
от CWD. A4 не мог запустить дочерние процессы; A5 выявил неинициализированный
корневой NModel в новом helper; A6 исправляет его через штатные Init/Reset.
Прежние ad-hoc проверки могли использовать defaults вместо заявленного ini;
это ограничение прежней runtime доказательности сохранено в отчётах.

Расширенная matrix A7 (20 кГц, configured sources, N=1/4/6), ASan, полный
maintained CTest после shared harness изменения и независимый полный аудит
сертификатов по исходным CSV ещё не приняты. Последний реализован в root-модуле
`Scripts/StructTrain/TimeLearner/learned_evidence.py`, серверные tests ожидаются.
Поэтому последующие строки «подготовлены» описывают исходную постановку и не
отменяют приведённые выше уже завершённые адресные проверки.

Пакет timelearner_completed_state schema 1 разделяет физический архив, полную
декларацию dataset/генератора, индивидуальные параметры и доказательство обучения.
Он хранит исходные immutable storage definitions, актуальный Neuron граф и связи,
Dataset snapshot, ModelSpec, protocol/цель, L/Ns/Rs, фактическую child physics,
model epoch, references и все пробы последней независимой final verification.
Порог сохраняется как фактический параметр LTZone; текущий протокол калибровки fixed.

Сертификат при импорте не десериализуется доверенным объектом: CapturedReferences
заново строятся из реальных reference packets, а FinalVerificationSession повторно
обрабатывает финальные пакеты в исходном порядке, включая допустимые повторы.
Заново вычисленные residuals/Exact должны совпасть с сохранённым сертификатом и
hash фактического импортированного нейрона. Данные bound к protocol/модели/epoch;
подмена stored Exact, потеря пробы или графа запрещает приёмку.

Образы регистрируются штатно, без замены существующих prototypes. Dataset и Neuron
импортируются отдельными готовыми объектами с native Load/Init и связями. До замены
проверяются реальные банки, частота и численная допустимость. Внешние listeners
старых дочерних объектов запрещают замену; ошибка attach/readback возвращает
старые объекты и их порядок. Public lifecycle bool не используются как канал ошибок.

Получатель входит в frozen состояние с IsNeedToTrain=false; повторный Build/Reset
сохраняет физическую модель и goal. Это не mid-probe checkpoint: физическая динамика
сбрасывается штатно, поиск продолжается новым запуском с завершённой границы.
Bare XML/Copy с initialized marker не является заменой полного пакета, также для
native API с ControllerVersion=1. Исторические V1 конфигурации без marker сохраняют
прежний dispatch.

Начальная реализация принимает certified completed boundaries Exact и
SearchUnresolved; diagnostic/budget/external-stop без финального сертификата,
RecognitionState/conversion и calibrated/PostTune состояния требуют расширения.
Полный experiment run bundle, первичные CSV и provenance остаются отдельными
артефактами pipeline; модельный пакет не объявляет научный verdict и не является
самостоятельным доказательством независимого Test.

Подготовлены Classic/Branch × N0/N1 roundtrips с heterogeneous child C, проверкой
references/certificate/readback, сохранением после Reset и отказом повреждённого
пакета без изменения старой модели. Отдельный Exact-control использует явно
заданный SyncTolerance=0.2; он не подтверждает сходимость при default 0.02.
Fresh-process/cross-host перенос и сравнение настоящих frozen response traces
подтверждены дополнением A6 выше. Расширенная corruption/rollback матрица,
все статусы и перечисленные оставшиеся проверки остаются условиями приёмки.
