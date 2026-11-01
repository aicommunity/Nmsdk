# Точность физики и индивидуальных параметров ModelArchive

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

Проверки ещё не выполнены. Подэтап не принят; general archive/profile/growth
матрица, все формы векторов/матриц и полный Train→Test остаются открытыми.
Если native XML теряет значащие цифры, требуется сначала локализовать это
реальным отказом и исправить у владельца сериализации, сохраняя Rdk lifecycle.
