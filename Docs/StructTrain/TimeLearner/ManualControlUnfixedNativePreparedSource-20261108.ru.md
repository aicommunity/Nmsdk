# Исходная production-версия для manual-authority A/B

Статус: локальная source preparation, без сборки и runtime. Неисправленная production Pulse сохраняется **800f92ae1f9e0133cefc0ccfe36abc3d8c99727f**. Исходный Rootf74 не изменён. Новый code root `bb1d24ea950ff068c25f7db7186517b55eef3dbd`, ветка `codex/timelearner-manual-control-unfixed-native-preparation`.

Обычный merge `668bb6f8848bb4ee2d9694cc7b165d461df21dab` объединяет f74 с17db: те же проверенные deadline fixtures и два явно исключаемых diagnostic-only случая. Следующий обычный merge bb1d объединяет его сdb2: та же полная worker/helper ancestry. Production gitlinks в обоих объединениях сохраняются; App/Tests/CMake относительно первого merge не меняются.

Сравнение с corrected code root `e11bbd403a5f93790a7ad6c5a245c1964797d63d` подтверждает одинаковые App, Scripts, Rdk, Bin, .gitmodules, корневой CMakeLists и cmake. Оба maintained worker/preparer blobs byte-identical db2. Исправленный Pulseb287 сюда не подставлялся. [Manifest](ManualControlUnfixedNativePreparedSource-20261108.json) хранит parents, все изменённые пути и hashes. В TU321 literal tests, четыре targeted source controls; actual compiled inventory ещё отсутствует.

Два OwnNextGroups являются положительными контролями. Два ForeignBegin ожидаются отрицательными только после подтверждения достигнутой runtime-границы: ошибка настройки, исчезнувший пик, timeout или падение до old Consume не доказывают выявленный дефект. Существующий worker принимает только all-pass и останавливается на первой failed leaf, поэтому future execution разделяется на POS2, NEG1, NEG1. Отрицательные jobs должны честно сохранять terminal failure; отдельный collector проверяет и сохраняет их реальные primary, даже если worker не дошёл до своего успешного artifact-loop.

До выполнения нужны закрытая приёмка baseline248, свежие source/physical/runtime preflight и canonical specs, реальное конфигурирование профиля CMake, ресурсы и независимая process/data closure. Никакие результаты этих четырёх controls здесь не получены; source A/B не заменяет compiled/native A/B. Серверные источники, работающий M40 runtime, физика, defaults и пользовательские копии не менялись.
