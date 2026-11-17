# Исследование N1 около измеренной timing-ready длины

Реализован кандидат изменения порядка поиска. Серверные C++/native проверки
этого кандидата ещё не проведены, merge в develop не выполнен.
Текущие M40 cap16 и Elder single-sweep cold опыты используют прежние runtimes.

Основание — [полная траектория cold Classic](LongColdSearchInspection-20261117.ru.md):
L241 дала временную готовность, но исходная амплитуда не восстановилась при
проверенных Rs вплоть до Rmin. После этого исследовались L4…50, а ближайшие
к241 длины не получили измерений. Это ограничение порядка поиска в конечном
бюджете, не доказательство невозможности нормализации или глобальной физической
недостижимости. Сохраняются CapturedPerInput и все исходные допуски.

`ProposeMeasuredLength` оставлен без изменений: он не должен придумывать новую
временную ошибку, когда наблюдается timing-ready точка. В `PrioritizeMeasuredLength`
добавлен отдельный finite exploration fallback для native N1. После такой точки
с amplitude miss он ставит ближайшую непроверенную легальную длину следующей
после текущего конечного Rs turn. Меньшая длина выигрывает равное расстояние.
Branch по-прежнему проходит shared-bank legality и displacement guards.
Предложение не переносит measurement/domain/certificate на новый граф.

Для каждого кандидата обязательны действующий per-input Rs domain, native
edit/readback, новые anchor/input observation и сравнение обоих residuals.
Резерв бюджетов не пополняется, N0 не меняется. Исчерпание локального порядка
не превращается в PhysicalInfeasible. Полное terminal best-state восстановление
остаётся самостоятельным открытым исправлением.

Добавлены три production C++ cases: nearest bounds/ties/INT_MAX без обхода
всего домена; Classic/Branch controller с контролируемыми ответами, где после
timing-ready amplitude miss только соседняя геометрия удовлетворяет обоим
допускам; неизменный N0 порядок. Они используют настоящий recorder/session,
но управляемые физические ответы: это state-machine тесты, не физические опыты.
Настоящий нейронный cold A/B необходим отдельно.

Приёмка после освобождения server slot: собрать immutable SDK из exact gitlinks,
выполнить весь затронутый controller/length/source-reader cohort без skips,
проверить старые bounded-search/capacitance/Branch случаи; затем повторить
single-sweep control с прежними physics, допусками и budgets. Оценить полноту
all-input gate, measured timing/amplitude residuals и реальный frozen8 Test
с временными графиками Soma и входов. Не выдавать успех controlled fixture
за сходимость нейронной модели. До этого статус «реализовано, не проверено».

На M40 уже доставлены через Git exact Root3743979b00a53c10a8dc39e7a72bc16bcc729fa7
и Pulse025576540b18455489ef7a1c8292fc146b39aea4, отдельный каталог
source-timing-neighbourhood-sdk-a1. Подготовлен cohort216 literal production
TEST случаев: controller/length/Rs/C/recovery/source reader. Controls commit
9f638781715cf99b0dcb6a25cbf3d8c0ed22657f. Legacy TEST_F physical fixtures явно
вне этого dialect/cohort, не подсчитываются как пройденные и остаются частью
отдельной физической матрицы. Сборка/выполнение216 не запускались: единственный
M40 slot принадлежит текущему cold Branch. Подготовка исходников и декларации
не подменяет проверку и не изменяет работающий runtime.

Последующее отдельное исправление candidate admission учитывает нечётный
остаток probe budget: одна проба не финансирует новую пару anchor/input,
поэтому domain/edit не выдаются. Новый production TEST включает восемь
Classic/Branch × N0/N1 × allowance1/3 сценариев; уточнена диагностическая
причина allowance1 в существующем termination case. Начатые N0 repeats и
final verification сохраняют свой учёт. Проверка не восстанавливает best
и не предсказывает затраты wall time. Подготовленный выше immutable SDK216
этого дополнения не содержит: его нельзя выдавать за проверку нового кода.
До серверного исполнения оба изменения остаются непроверенными.
