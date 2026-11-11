# Полный первичный архив нового Classic N4/N1 Train

M40, исходный job s07-n1-after-stock-classic-train-m40-a1. Исходное выполнение completed/0, обучение invalid_observation, certificate=null; калибровка/Test не выполнялись. Это диагностическое остановленное состояние, а не обученная модель для публикации классификации.

SDK subject root fcfd8bdff149c14cbe67149e996945d122bf954d / Pulse5f1a4ac6f9aff208ada7f8bcf62645c9d79a6615. [Временные графики и разбор](ClassicWindowTemporal-20261111.ru.md).

[Полный bundle](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/bundle.json) и [primary.tar.xz](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/primary.tar.xz):463 regular archive members (461 исходный файл +2 явные glog-алиас копии). Распакованный размер259370887B; XZ10194852B. SHA256 e541de403a9b9600f35a3d926599529d499110c3ae4e127e66acc52c9fc9e4d7. Хранятся весь model package, summary, initial/final graphs, native observations, фактические CSV, configuration, process/kernel/runtime evidence и журналы. Исходный job не менялся.

Штатный closed-primary-bundle проверил полный namespace, хеши и закрытие3 исходных kernel groups до и после сбора. Собственный collector также завершён, его lease released. [Proof](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/collection-proof.json), [collector terminal](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/collection-terminal.json). Передача результатов — Git pack с проверкой SHA256, без rsync/scp. Числа Python filesystem identity в исходных proof сохранены как байты, без JSON roundtrip через JavaScript.

Восстановление на сервере из корневого checkout:

    python -B -m Scripts.StructTrain.TimeLearner.portable_primary Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/bundle.json NEW_RESTORE --compatibility dereferenced-glog-aliases-v1

NEW_RESTORE должен быть новым каталогом. Внутри original-train/ находится исходное задание; model package и summary — original-train/worker/native-stock-cold7/Classic-stock-cold7-N1/runs/train/native/. Адаптер сначала проверяет463 members, затем удаляет только2 подтверждённые избыточные alias-копии из новой derived tree; исходный архив не изменяется.

Независимое восстановление этого нового архива на Elder выполнено:1/1 адресная проверка,63.09 с,463/463 members,461 retained regular files после alias adapter. Повторно проверены package6/summary,18 logical groups/108 native probes/388908 samples, effective stock physics и L=[54,1,1,1]. Повреждение CSV в новой распакованной копии отклонено; исходный архив и его6 файлов не изменились. Outcome остаётся invalid_observation, certificate=null. [Фактический audit](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/independent-elder/restoration.json), [результат теста](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/independent-elder/validation-result.json), [closure и lease](../../../Reports/StructTrain/TimeLearner/N1ClassicTrainPrimary-20261111/independent-elder/closure-and-reservation.json). Это DATA-восстановление без расчёта модели; live authority, сходимость и classification не создаются.

Сохранены два отказа подготовки: A1 не имел полного alias record; A2 округлил nanosecond integers при JSON.parse/stringify в JavaScript. Оба остановлены до создания архива. A3 использовал исходный Python JSON как точный UTF-8 текст; Git blob hash проверен до доставки. [Все manifests и readbacks](ValidationPlans/M40N1ClassicPrimaryBundleA1-20261111).
