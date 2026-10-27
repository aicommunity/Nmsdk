# Native learned state: перенос завершённой границы обучения

Рабочая ветка stage05/native-trained-state. Реализация подготовлена; серверная
проверка и полная приёмка ещё не завершены. Этот документ не закрывает этап 5.

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
Fresh-process/cross-host перенос, сравнение настоящих frozen response traces,
расширенная corruption/rollback матрица и все статусы остаются условиями приёмки.
