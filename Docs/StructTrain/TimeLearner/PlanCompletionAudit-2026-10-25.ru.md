# Проверка полноты выполнения принятого плана

Дополнение 26.10: исходная таблица ниже является аудитом явно указанного
снимка, а не неизменяемым описанием текущего кода. После неё приняты native
storage-профили/growth, model identity/archive/ports и исправления TL-014/015;
продолжается проверка TL-016: [контракт частот](FrequencyContract.ru.md).
Актуальная детализация: [ImplementationStatus](ImplementationStatus.ru.md),
Stage04/05/06-Progress. В частности, утверждение ниже о неизменности файлов
learner относится к старому снимку: Classic BuildStructure уже исправлен.
Все этапы 0–12 по-прежнему не выполнены полностью; ControllerVersion=2,
алгоритмы, реальный Train→Test, миграция scripts/runner, научная матрица и
семантический inventory остаются обязательной частью активной цели.

Следующий проверенный подэтап — [native executor](NativeExecution.ru.md):
пробы обоих learner, Branch solo routing, source schema 2 и финальный проход
N=2 проверены на серверах с full CTest, targeted ASan и legacy A/B. Это уточняет
текущий объём реализации, но не закрывает исходные этапы 6/7 или весь план.

Проверен снимок корня d9150b1837600df662740db4c5c6e31c11c7aeee,
PulseLib 735fea58af4b1815dc332c7d38af5bf4f68d0855,
Bin 7136679740c5aa97def6fd3700b7b781d97af8f2,
Rdk c80200bf1cd2bc8beec35546d3022da86afd35c9. Рабочие деревья до аудита чистые,
gitlinks совпадают с фактическими HEAD. Сверка охватывает полный пользовательский
план, а не только сокращённую таблицу RefactoringPlan.ru.md.

**План целиком не выполнен. Основная переработка алгоритмов двух learner ещё
не реализована.** Завершён этап начального объединения веток; реализованы части
инфраструктуры/наблюдений и проверенные подэтапы 4.1–4.5. Номера 4.1–4.5 —
внутренняя детализация этапа 4, а не закрытие пяти исходных этапов плана.

## Сверка по этапам

| Этап | Статус полного этапа | Фактическое выполнение и недостающая приёмка |
|---|---|---|
| 0. Исходные merge в develop | Выполнен | Исходные PulseLib/Bin/root объединены --no-ff; gitlinks согласованы; изменённые дочерние develop публиковались до корня. Branch hints заданы. |
| 1. Доказательства, режимы, дефекты | Частично | Есть исходные SHA, опорные исторические точки и inventory. Все 211 записей параметров имеют semantic_review=pending; 324 script candidates имеют review_required. Полного поэкспериментного реестра с августа, review всех аудитов и матрицы владельцев/defaults/setters/сохранения нет. |
| 2. Runtime и воспроизводимость | Частично | Отдельные deploy roots, explicit ini, ресурсы, build/runtime manifests и Reports реализованы и проверены на Qt5/Qt6. Нет единого runner, автоматически фиксирующего runtime перед настоящим Train, и полного published run bundle с моделью/данными для повторного научного анализа. Provenance idle-процесса не подтверждает состав библиотек всех будущих jobs. |
| 3. Наблюдения и scorer | Основной контур реализован; полная приёмка не завершена | Schema4 collector, IDs, completeness, finite checks, target labels и единый audit verdict проверены: 90 Python tests, C++ collector, синтетический CSV roundtrip. Не выполнена сквозная проверка реальных проб нового контроллера/runner; единый источник verdict ещё не распространён на все экспериментальные/аналитические пути. |
| 4. Lifecycle/storage/эффективная модель | Частично | Приняты подэтапы 4.1–4.5: частотные коэффициенты, readback связей/кэшей, explicit order, rest outputs, Copy lifecycle и opt-in image registry. Нет полной матрицы growth/load/reuse/profile/multirate; новые production storage-профили ещё не применены. Сохранность learned Rs/C при росте с legacy parent defaults не обеспечена новым контуром. |
| 5. Полный model export/import | Подготовительные проверки | Native Copy/XML fixtures и image registry не заменяют versioned ModelSpec/LearnedSoloState/RecognitionState. Нет полного экспорта определений образов, обученного состояния, inhibition, calibration/conversion provenance и semantic fingerprint проверки Train→Test. |
| 6. Общий контроллер | Не реализован | Нет нового event-driven controller и Classic/Branch adapters, ControllerVersion=2 и compatibility A/B. Существующие общие helpers не являются выполнением этого этапа. |
| 7. Исправление алгоритмов | Не реализовано по принятой спецификации | Не внедрены revision-bound measurements, signed/valid peak policy, новые bounded L/N/R searches, certificates/fresh all-input verification и полный optional C-trim контракт. Исправления физической динамики меняют условия работы learner, но не заменяют переработку его управляющего алгоритма. |
| 8. Conversion/PostTune/calibration | Не реализовано по принятой спецификации | Нет immutable Solo→Recognition conversion, сохраняемого происхождения преобразования, транзакционного PostTune с полным rollback и нового frozen/calibration контура. Старые реализации остаются действующими. |
| 9. Пакет экспериментов и миграция | Частично, начальная основа | В корневом пакете только __init__, __main__, inventory, runtime. Общий entry point поддерживает только inventory; runtime имеет отдельный module CLI. Нет остальных production-команд, config adapter и законченного migration manifest. Старые скрипты Bin/Docs не удалены. |
| 10. Очереди/provenance/publisher | Частично только runtime provenance | Нет production ConditionSpec, канонического serializer условий, lease/lock/PID runner и fail-closed publisher. В старом publisher остаются rsync и git push check=False. |
| 11. Контрольные эксперименты | Не выполнен | Новые артефакты содержат implementation tests. Не выполнены исторический replay августа, cold retrain, legacy/v2 A/B, настоящие перестановки стимулов/ITI и полная матрица физических режимов. Перестановка строк CSV проверяет scorer, а не robustness нейрона. |
| 12. Вся документация и завершение | Частично | Обновлены профильные документы root/PulseLib/Rdk и analyzer ClDesc, старая controller spec помечена исторической. Полная актуализация learner/config/analysis docs и проверка отсутствия конкурирующих актуальных спецификаций не завершены. |

## Прямая проверка кода

Сравнение PulseLib HEAD с исходным фактическим checkout
652e0942f82029af388e432c004fc4a477387cb3 не показывает изменений в четырёх файлах:
NNeuronTimeLearner.cpp/.h и NNeuronTimeLearnerBranch.cpp/.h. Поиск новых сущностей
ControllerVersion, TrainingCertificate, LearnedSoloState, RecognitionState,
ConditionSpec и ModelSpec в production C++/Python проверенного контура не нашёл
их реализации. Это подтверждает отсутствие основных этапов 5–8 и 10, а не
только недостаток отчётных документов.

Конкретные открытые места:

- Branch AllSynapsesNormalized всё ещё пропускает входы, отличные от
  ActivePulseIndex: Core/NNeuronTimeLearnerBranch.cpp:6033. Независимая свежая
  финальная проверка всех входов из плана не добавлена.
- RebuildCableForPostTuneProbes использует parent MembraneCapacity либо 1e-9:
  тот же файл, :6565. Единый полный import вместо специальной реконструкции
  пока не реализован.
- Mutable ParallelResistanceScaled остаётся механизмом legacy conversion.
- Bin/Configs/SpikeSamples/StructTrain/scripts/commit_timelearner_matrix_wave.py
  содержит rsync_from_17 и push с check=False. Новый publisher отсутствует.
- source_inventory.json — исходный inventory с пометками pending, не полный
  семантически проверенный реестр и не завершённый manifest удаления скриптов.

## Что подтверждают имеющиеся проверки

Серверные журналы и manifests подтверждают проверки конкретных компонентов:
scorer/collector, native коэффициентов, графа/связей, Copy/XML/Reset и registry.
В последнем наборе на обоих серверах прошли 15 targeted cases и четыре maintained
Rdk/PulseLib CTest suites. Проверки выполнены через jump host на .11/.17.
Полный обязательный набор вариантов из раздела 4 пользовательского плана этим
не закрывается. Новых научных результатов обучения или признанного Controller v2
на основании этих тестов нет.

Августовские визуальные 4/8–6/8 остаются наблюдениями своего исходного протокола.
Без replay/cold/order/ITI серии нельзя ни отменять их, ни переносить на новый
протокол. Получение 8/8 не требуется для завершения рефакторинга; требуются
реализация контрактов и достоверные проверки, включая отрицательные исходы.

## Дополнительно обнаруженная проблема упаковки

Проверены 130 файлов, перечисленных в имеющихся SHA256SUMS.json: отсутствующих
файлов нет, все Git blobs совпадают с опубликованными SHA256. Однако Windows
checkout с core.autocrlf=true преобразовал окончания строк у 90 текстовых файлов,
и их рабочие копии не совпали с manifest. Все 90 расхождений объясняются CRLF→LF;
серверные результаты в Git не повреждены.

В рамках аудита добавлено -text для Reports/StructTrain/TimeLearner/** и
восстановлены точные байты tracked артефактов из Git. Исходные hashes и данные не
пересчитываются под изменённое представление. Эта правка закрывает конкретный
дефект cross-platform упаковки, а не весь этап runtime/publication.
После правки повторно проверены 130/130 рабочих файлов и 130/130 файлов нового
checkout в отдельный временный каталог: несовпадений SHA256 нет. Код обучения
и исходные измерения в этом аудите не изменялись; новые эксперименты не запускались.

## Условия объявления плана выполненным

Нельзя считать весь план выполненным по числу merge или количеству unit-тестов.
Остаются обязательными полный evidence/property review, production storage/growth,
versioned export/import, общий контроллер и алгоритмы, conversion/PostTune,
единый пакет и удаление старых scripts, scheduler/publisher, научные контроли
и итоговая сквозная проверка документации. Каждый закрываемый этап должен иметь
код, соответствующие документы, адресные серверные проверки, артефакты и
согласованные merge commits — без подмены pending на PASS.
