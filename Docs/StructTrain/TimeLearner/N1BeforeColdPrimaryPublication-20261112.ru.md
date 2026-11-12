# Полные первичные данные исходных N1 cold probes

Пакет `Reports/StructTrain/TimeLearner/N1BeforeCold8Primary-Elder-20261112` сохраняет342 файла полного закрытого job `s11-n1-before-cold4-probes8-elder-a1`, включая все8 probe packets/CSV, исходные графы, задания, runtime/process manifests и controller/lease evidence. Raw размер6578707 bytes; XZ133872 bytes, SHA `85342b1a6f98ec7a856feafcd0cee8f1282917c0eccea5e4d9237a85777b9266`.

Исходные байты не пересериализованы. Восемь явно инвентаризированных glog aliases сохранены как обычные копии исходных байтов; при восстановлении требуется существующий явный adapter `dereferenced-glog-aliases-v1`, который проверяет дубли и оставляет реальные log targets. Это не новый формат, не реконструкция данных и не удаление уникальных логов.

Источник SDK Root5ba0a2e/Pulsec10206; Python controllerfd55a9936; приёмка [8 реальных исходных проб](ValidationPlans/ElderN1BeforeCold4Probes8A1-20261112/RESULT.ru.md). Source Git data commit `fa78fb8c14f95a8dfdbd686ea4b11e2bac9004ec`; transfer pack146949 bytes, SHA `9dbf2a92e944a7e06ee0ec9cb0a8c6427a02ee2d61e28e1aafd3420871022d77`. Данные переданы через Git; все5 извлечённых файлов сверены по ARTIFACTS до добавления в корень.

Это публикация холодных наблюдений, без обучения или классификации. Независимое восстановление342 members, audit всех8 наблюдений и отрицательный контроль отсутствующего CSV подготовлены в production reader test `N1BaselinePrimaryTest`; серверная приёмка ещё ожидается. Сохранённые сведения о закрытии процессов не становятся текущей native authority при DATA replay.
