# Точность физики и индивидуальных параметров ModelArchive

**Уточнение10.11:** ниже сохранена история ранних постановок и их тогдашние
статусы. Новый SDKf39 прошёл два literal telemetry controls при2000/20000Hz:
полные source/import soma и input arrays совпадают. [Опубликованные данные,
крупные графики и reader11/11](NativeArchiveGatePairReports.ru.md).
Это high-precision matrix+boundary subset, не весь прежний16-case corpus
и не проверка timestep convergence. Его результат не заменяет неизвестные
или отдельные исторические outcomes ниже.

Это отдельная проверка versioned ModelArchive, а не native hot XML checkpoint.
ModelIdentity кодирует double как IEEE754 bits; наличие такого fingerprint
само по себе не доказывает точность сериализации и восстановления параметров.

Существующий production fixture расширен четырьмя fresh-process случаями:
2000/20000Hz, с объявленным внешним stimulus port и без него. Проверяются
длинные десятичные значения C/Rm/RestingResistance/синаптической кинетики и
амплитуды в storage-профиле, отдельный LT C и индивидуальные learned Rs/C
несимметричного нейрона. Общая физика применяется через новый уникальный
storage recipe, а не массовыми записями в уже созданных детей.

Используется настоящий ExportModelArchive, перенос JSON в новый процесс,
ImportModelArchive, native Init/Reset и100ms отклик. Полная semantic identity
должна совпасть до и после отклика; её F64-поля требуют точного совпадения
битов параметров. Допуск1e-12 относится только к отсчётам waveform, не к
параметрам или критерию сходимости обучения. Имена артефактов отделены от
прежних коротких десятичных fixtures, чтобы исходные контроли не затирались.

В source/import artifacts дополнительно сохраняются все отсчёты физической
Soma2.SumPotential и фактически прочитанного native synapse Input. Исходный
контроль ExcChannel.Output сохранён отдельно; он не переименовывается в soma.
Fresh-process child проверяет равенство входов и отклика сомы. Это первичные
данные для временных графиков с наложенными импульсами; постановка fixture
содержит одно импульсное предъявление, а не матрицу распознавания8 паттернов.

Ещё четыре отдельных случая проверяют публичную матрицу TrainingPattern2×3
с длинными десятичными значениями. Это часть сохраняемой модели, а не
transient soma output. Их выводы отделяются от scalar/storage контроля:
точность scalar/vector сериализации не доказывает точность matrix пути.

## Фактический baseline и исправление у владельца

Elder normal a1/source61d83787dc82a04b46294ee26f742ee0614f41f5 завершил12/12
контролей, включая4 fresh-process scalar/storage precision cases. Затем
a2/source990290155c9e1f23afe9a904f7052d20b32939ba завершил16 tests с4 отказами:
все четыре новых matrix cases отвергнуты самим ExportModelArchive на этапе
rehearsal: archive_model_mismatch, TrainingPattern.data.value[0][0].
Четыре базовых и восемь scalar/boundary cases остались зелёными. Это отказ
поддержки точной матрицы, а не молчаливо успешный перенос повреждённой модели.

Причина локализована в Rdk MUXMLSerialize.h: общий MDMatrix writer создаёт
stringstream с precision6. Child feature2732a08a833596b2283c17330f33b8b692664612
использует max_digits10 для floating T и добавляет реальные native XML unit
roundtrips float/double/long double. Схема и старый parser сохраняются,
проверка ModelArchive identity не ослабляется. Исправление ещё не принято:
нужны unit+native проверки на серверах, regression и temporal evidence.

Baseline primary опубликован вbf38e748209db78d54334737bfd2a6188be5a9fc:
Reports/StructTrain/TimeLearner/s05-archive-f64-baseline-normal-a1,
82 члена/175292 bytes xz. После Git retrieval проверены внешние SHA256,
размеры и SHA256 всех членов. Оба запуска, включая отрицательный a2,
сохраняются отдельно и не заменяются результатом исправленной версии.

Исправленный normal a3 выполняется на Elder: supervisor2924884,
start_ticks311717423, source361b3a113b26aa3062671b9cddaf89fa6877f1c2.
ASan a1 на M40: supervisor850578,start_ticks262290102,
source9810425b7e5401354d0b68322a6405b1c9eac781. В обоих источниках Rdk2732a08;
последний дополнительно включает уже принятый XML coverage root3d43e6b1.
Normal проверяет unit10 и native archive16; ASan — unit10/archive16 и hot XML32
при новом matrix writer. Каждый запуск имеет отдельный runtime; источники и
build не обновляются до завершения соответствующего supervisor. Результаты
этих проверок ещё не получены, приёмка исправления остаётся открытой.

Для последующей проверяемой temporal evidence fixture получает явную schema1,
complete/window fields и массив native clock, считанный до Calculate каждого
отсчёта. Child сохраняет такой же clock и проверяет совпадение. Старые primary
a1/a2/a3 не переименовываются в эту схему: отсутствие полей остаётся известным
ограничением соответствующего producer snapshot.

Новый root module archive_transfer_reports проверяет12 transfer условий,
native16/unit10 receipts, полный состав файлов, archive/image/XML/identity
hashes, finite IEEE754 параметры, ожидаемые индивидуальные C/R и точную2×3
TrainingPattern. Проверяются все native timestamps и input samples, физическая
Soma.SumPotential и отдельный ExcChannel.Output, совпадение source/import
откликов и сводных ошибок. Графики используют production renderer с полными
отсчётами, shared amplitude и100-tick zooms; scientific verdict остаётся null.
23 tests вносят повреждения в реальные server exports; они ещё не запускались.
Новый producer/reader требуют отдельного прогона после завершения текущих jobs.

Schema1 данного fixture определяет наблюдаемую физическую сому как $.Soma2,
конечную часть двухсекционной сомы. Это один выходной ряд, а не физическая
Soma1. Адаптер renderer передаёт physical_soma_ids=[2]; заголовки, имена PNG
и metadata указывают Soma2. Для прежних loaded/warm/XML отчётов поведение
по умолчанию не меняется. Новая схема native clock уже прошла16/16 C++ и
23/23 actual-data checks на Elder; полные XML/regression и ASan ещё выполняются.

После проверки5c4e1a44cbdbc92fbab646933a1c15de606ebfda immutable code export
на Elder завершил23 archive +16 warm +16 loaded +18 XML checks. Сохранены
полные аудиты12 archive output-soma pairs и68 XML pairs; новая маркировка
выхода $.Soma2 проверяется по эффективному графу. Native normal XML32 также
прошёл; regression21 ещё выполняется. ASan source9810425b уже прошёл native
archive16 при том же Rdk2732a08, но XML32 и новая версия producer/reader там
ещё требуют завершения/проверки. Полного приёма исправления это не означает.

У очень короткого unit-процесса normal a4 зафиксирован fast-exit race чтения
/proc: runtime_provenance=incomplete_loaded_files. Этот статус не заменяется
на complete. Для a3 сохранены полные actual mappings того же unit executable
и одинаковый prelaunch runtime identity; отдельный comparison record явно
указывает, что фактические mappings a4 остаются неизвестными. Основные native
archive и XML процессы a4 имеют loaded_files_captured. Эти оси различаются
в primary receipts и не подменяют результаты численных проверок.

## Полный normal primary

Normal a4 и reader a2 завершены: unit10, archive16, hot XML32, regression21
без skips; data checks23/16/16/18. При сравнении всех24 source/import JSON
между a3 и a4 массивы waveform/actual_input/soma совпали точно. Добавление
native clock и схемы не меняло сам физический отклик.

Совместный primary2d1827febab8ec360d205163a3469f0077eba989 опубликован черезGit:
Reports/StructTrain/TimeLearner/s05-archive-f64-current-normal-a1,
441 член/645556 bytes xz. После получения локально проверены внешние SHA256,
размеры и SHA256 каждого члена. Включены оба fixed native запуска, оба reader
снимка, source/runtime/process receipts и явно сохранённое ограничение unit a4.

На M40 из этого primary строится temporal cache всех12 transfer conditions,
физический выход $.Soma2 и реальные входные импульсы, без downsampling.
Supervisor877348/start_ticks262449357; renderer использует immutable Git code
export5c4e1a44 и не меняет исходники продолжающегося ASan задания850578.
QA, выбранные изображения и прямой визуальный просмотр ещё требуются.
Исправление Rdk2732a08 по-прежнему не принято в develop: остаются ASan XML,
ASan schema1 producer/reader и визуальная приёмка. Полные этапы4/5/11 открыты.

Temporal QA завершена: все262 PNG декодированы Pillow, проверены SHA256,
1920×960, полный состав overview/100-tick views, shared/detail limits и
маркировка физического выхода Soma2. Первый набор20 selected содержал8 shared
input/peak tiles с почти плоской кривой на общем масштабе; в набор добавлены
их8 готовых detail companions. Все28 выбранных оригиналов непосредственно
просмотрены: фронт и кривизна пика разрешаются, source/import кривые совпадают
визуально. Общий масштаб сохранён рядом для контекста.

QA/selection proof23b7e17751e8db62ab12757cc9bfc90ee50ae2f8 содержит metadata
23744 bytes xz и28 selected PNG; после Git retrieval проверены все hashes.
Запись прямого просмотра: Reports/StructTrain/TimeLearner/s05-archive-f64-visual-a1/visual-review.json.
Ручной просмотр полного262-image cache не заявляется. Новая schema1 ASan
проверка выполняется отдельно; C++ XML32 предыдущего ASan уже завершены успешно.

## Адресная приёмка исправления

Предыдущие pending-записи выше сохраняют историю проверки. ASan a2/schema1
завершил unit10/archive16/reader23, затем immutable analyzer прошёл23/16/16/18.
Все24 source/import файла совпали с normal по массивам waveform, actual_input,
soma, native time_s и semantic model/image identities; все64 XML CSV совпали
побайтово. Старый ASan a1 также прошёл unit10/archive16/XML32. Все supervisors
завершены; source/runtime final guards прошли, exception отсутствует.

ASan primaryfe8e700ef0695a9a6847c4809260f4abd5819278 содержит398 членов,
497008 bytes xz. После Git retrieval локально проверены внешние SHA256,
размер и SHA256 каждого члена. Normal primary2d1827fe и262-image temporal cache
применимы по явному crossworker data-identity receipt; duplicate cache не нужен.
Все28 selected originals просмотрены, review commiteb2fb87cb0d4100555c7cd6d6ca725161937e83f.

Rdk feature принята --no-ff в develop0a1c1d05a1b12de20feabf54a25712e210865791.
Core и Tests trees равны фактически проверенному2732a08; дополнительный98055ef
меняет только документацию. Root acceptance записывает этот child merge,
PulseLib70f467d3 и Bin6304b4a2. Исправление не ослабляет строгую identity и
не меняет lifecycle или математическую цель обучения.

Приёмка ограничена floating MDMatrix XML и описанными12 asymmetric-neuron
transfer cases при2000/20000Hz, storage/scalar/matrix/individual C/R и external
stimulus absent/present. Полная физическая/growth/mode матрица, произвольные
other serializers, научная классификация и полные этапы4/5/11 остаются открытыми.
Ограничение fast-exit provenance unit a4 сохранено явно; полный actual-map
контроль идентичного unit executable имеется в a3, все ASan units mapped.

Проверки ещё не выполнены. Подэтап не принят; general archive/profile/growth
матрица, все формы векторов/матриц и полный Train→Test остаются открытыми.
Если native XML теряет значащие цифры, требуется сначала локализовать это
реальным отказом и исправить у владельца сериализации, сохраняя Rdk lifecycle.
