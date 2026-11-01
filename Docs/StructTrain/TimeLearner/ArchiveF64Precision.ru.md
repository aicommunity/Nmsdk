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

Проверки ещё не выполнены. Подэтап не принят; general archive/profile/growth
матрица, все формы векторов/матриц и полный Train→Test остаются открытыми.
Если native XML теряет значащие цифры, требуется сначала локализовать это
реальным отказом и исправить у владельца сериализации, сохраняя Rdk lifecycle.
