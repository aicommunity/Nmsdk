# Состояние общего среза06.11.2026

Подтверждённый develop `fec986d785a7dfb473b4ad1821db4a6b9d03f390` принял
два узких исправления: native gate создаёт собственный output/native перед
изолированным тестом; portable primary restoration явно проверяет и исключает
из производной копии dereferenced glog aliases. Для первого есть прежние
normal/ASan native binaries и оригинальный BranchAliasing test; для второго —
по14/14 адресных production проверок на обоих workers. Полный план ими не закрыт.

Проверяемый C++ SDK2e/Pulse12d остаётся кандидатом. Обычный304 прошёл;
ASan lifecycle A3 выполнил все133 cases с132 passed и1 failed из-за отсутствующего
выходного каталога в runner. [Все исходные primary и source hashes](SharedControllerNovember6Verification.json)
сохранены в Git, отрицательный verdict не исправлен задним числом.

После исправления каталога прежний точный native тест прошёл на обоих workers,
без пересборки и изменения его тела. Попытка полного A4 остановилась до C++:
в отдельном accepted tool snapshot отсутствовал pending native_partition.
A5 использует согласованный tool root `bb288399bdb66aaadb3db7ec5f01c76cd9bd57ae`,
где partition runner присутствует, а native_gate побайтно равен проверенному642a9c875.
Оба предшествующих отказа сохранены. Последний kernel просмотр A5 подтвердил
case0032, PID887808/start303259399, R, start совпадает с owned-process.json.
Это наблюдение живого задания, не полный ASan PASS.

[Полный coordinator контроль](PipelineConditionFullMatrixAcceptance.ru.md):
16/16 tests,40 actual native phases,1456 CSV проверены попарно; схема1/2
не меняет измеренный результат на объявленных8 случаях. Это не полная
factor attestation или все режимы learner. Численных прогонов локально не было.

[Готовый инженерный визуальный отчёт](PipelineConditionPilotVisualReport.ru.md)
содержит46 оригиналов; full cache всех214 trial/soma и2620 views — на M40.
Данные/модели в Git, повторного Train ради рисунков не было. Результат двух
N2 LT same-matrix controls остаётся TP2/FP0/FN0/TN2 каждого; он не переносится
на stock4-input/8-pattern и не является independent scientific evaluation.

Пять старых AsymRm XML patch/overlay tools удалены в отдельной feature Bin
`4123c177848f159dd52de41dffe923085d14d633`, root
`e38260b47f718cb6dc5695ca2e36e0ab9dc12b1f`. Retrieval manifest220 и source
review подготовлены; metadata gates и children-first merge этого подэтапа
ещё не выполнены. Accepted Bin остаётся f12f09ae. Остаются24 Python AsymRm
и прочая миграция, расширенная lifecycle/storage/algorithm/mode/physics matrix,
stock measurement recovery, frozen order/ITI/reset science и сквозная документация.
Только исходный этап0 полностью принят; этапы1–12 частичны.
