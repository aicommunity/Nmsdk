# Native-допуск отказа composite search: фундамент

Статус: код реализован, серверная компиляция и runtime-проверки ещё не выполнены.
Это подэтап реализации typed composite recovery, не готовая настройка обучения.

`RejectedCompositeMeasurement` — закрытый C++ тип. Его создаёт только native
attempt по завершённой Search-группе protocol5 при Missing/Ambiguous назначении.
Он содержит Prepared identity, неизменяемые all-input references, вид отказа,
канонический content ID и проверку актуальной группы. Скалярного peak/residual,
reference или certificate этот тип не создаёт. Публичный JSON/content hash не
восстанавливает native lease; default/aggregate/public construction запрещены.

`NativeCompositeTrainingAttempt::EnableRejectedSearchAdmission()` вызывается
явно до первой группы. Это разрешение factory создавать допуск, а не политика
перехода поиска. По умолчанию выключено: прежние callers не пересчитывают
rejected content и сохраняют существующее поведение RetrySameCandidate.
Reference и Final, cancelled/incomplete/nonfinite/clock/budget ошибки не получают
допуск. Перед выдачей проверяются boundary, actual native instances, исходный
профиль, подготовленное окно, all-input references и model/wall budgets.

`RequireCurrent()` повторно проверяет lease, owner/control, native instances,
revision и окно; затем требует тот же завершённый текущий group identity.
Следующая группа, Cancel, уничтожение attempt, learner Reset, external stop
или пересоздание графа должны отзывать ранее скопированный допуск. Снятие
запроса управления не означает сходимости. Физический расчёт остаётся у native
scheduler; новых Calculate/Reset/Build вызовов контроллеру не добавлено.

Content ID отдельного вида включает method/proposal/logical/source/candidate
binding, native packets и hashes фактических CSV, а также свежую selection.
Это идентификатор условий и данных отказа, а не разрешение, читаемое из файла.
Consumed/elapsed timestamps в него не входят: сроки отдельно проверяются
живыми monotonic clocks. Валидные measurement-v2 content ID сохраняют прежнее
содержимое; их совместимость должна проверяться старым сохранённым package6.

Добавлено 22 integration cases на реальных storage/Environment компонентах:
Classic/Branch Missing и Ambiguous, Missing при 20000 Гц, default Off, partial,
Reference/Final, group budget и отзыв после смены жизненного состояния. Для
сервера к ним добавить прежние valid factory cases при 2000/20000 Гц, два native
package roundtrip и чтение старого package6. Наличие теста в исходнике пока не
является его прохождением; полная mode/scientific matrix этим набором не закрыта.

Следующий кодовый шаг — private typed reject/consume в BoundedTrainingSession,
доставка из NativeTrainingService, ordered recovery evidence и новая явно
версионированная policy в codecs/readers. Runtime2 по-прежнему принимает только
retry_same_candidate. Не обходить этот запрет и не запускать дорогой Train с
несуществующей настройкой. CapturedPerInput, tolerance и assigned maximum не
меняются; весь исходный план 0–12 остаётся открытым за пределами принятых частей.

Серверная приёмка: [исходный subject и исправленный повтор](ThreeWorkerRejectedSearch-20261111.ru.md).
Исходные Linux попытки завершены19PASS/10FAIL на каждом worker, не приняты.
NaN mutation выявила выход private MatchedOmission Failure из публичных
content-ID API; Pulseaf612ba переводит его в std::invalid_argument с исходной
причиной. Содержимое valid content ID не меняется. Исправлены также envelope
Ambiguous fixture и проверка отдельного group budget; тесты не ослабляются
до произвольного отказа. B1 выполняет те же29cases в отдельных leaves на
новых Linux SDK. Windows отдельно проверяет переносимость19 ранее прошедших
случаев старого subject. Полная runtime-приёмка новой функции остаётся открытой.
