# Причины остановки ограниченного поиска

Открытый подэтап этапов6/7/5/12. Исходный PulseLib
`a18bf543007c52a3ac7a6fbb148a48cb2c351de3` объединяет исчерпание
maximumSweeps после OutsideTolerance и отсутствие измеренного допустимого
кандидата в SearchUnresolved. Это разные причины остановки.

Контракт исправления: Exact имеет приоритет при свежем успешном all-input
проходе, даже если использован последний разрешённый sweep. Если допуски
не выполнены и следующую итерацию запрещает maximumSweeps — BudgetExhausted
с конкретной причиной. Отсутствие measured legal candidate остаётся
SearchUnresolved. Неполные/повреждённые измерения не превращаются в эти исходы.
Не менять CapturedPerInput, ranking, выбор кандидатов, допуски и физику.

Первый commit содержит только6 новых controller tests (позднее уточнены до7), ещё без исправления.
Они используют production BoundedTrainingSession/ProbeRecorder и явно заданные
observations; это не доказательство native physics или классификации.
Четыре cases проверяют Classic/Branch × N0/N1 при maximumSweeps1/2;
три положительных контроля — Exact на последнем sweep, InvalidObservation
после missing-peak retries и SearchUnresolved при отсутствии регулируемых входов.
Сначала требуется реальный failing baseline на сервере, затем correction,
все старые affected decision tests, native controls, export/load и строгие
readers на обоих workers. Исторические результаты не переклассифицируются.

Quantized/BestEffort и прочие причины ограничений поиска остаются частью
полного плана. Данный подэтап не объявляет глобальную физическую недостижимость
и не закрывает весь этап7. Сборки — только серверные, в отдельных runtimes.


Первый ASan baseline root234f84b0d:6 tests, четыре ожидаемых budget failures
и один ошибочный fixture expectation. Missing peak не продвигает поиск
к следующему кандидату: штатно повторяет пробу до declared invalid-observation
budget, возвращая InvalidObservation. Исправлено только ожидание этого теста;
добавлен независимый N=1/no-adjustable-input control, который действительно
должен остаться SearchUnresolved при свежем OutsideTolerance.
Повторный baseline должен иметь7 tests /4 expected failures /3 controls.


Исправленный baseline91a9524b5 на M40:7 tests, четыре ожидаемых failures
и три controls passed. Реализованная Pulse feature
`63fd7a9fecbc567fb8e5c690ae58fc73a896de65` различает sweep/probe/edit/epoch/
adapter limits и передаёт Reason через native service в существующие
summary/stopped-package поля. FinalVerification rejection не подменяется
старой search rejection. Exact на последнем sweep сохраняется.

В pure session свежий negative certificate остаётся измерительным свидетельством.
Native service при BudgetExhausted сохраняет модель, references, final/observed
packets в штатном diagnostic stopped state, без completed-Train сертификата.
Import должен сохранять outcome/reason/graph; ConvertNativeSoloToRecognition
не должен автоматически принимать такой stopped package. Отдельный diagnostic
Test path остаётся обязательным открытым пунктом плана, а не скрытым обходом.

Подготовлено46 cases:33 прежних controller tests (у девяти reviewed ожиданий
max-sweep сменён терминальный статус),9 termination checks и4 настоящих native
Classic/Branch×N0/N1 budget/export/import controls. Native controls фиксируют
законную исходную геометрию и Rs/Ns, sync tolerance0 только как контролируемое
условие несинхронности,8 полных observations на case. Это не научная оценка
при default0.02. Все32 packet/CSV и48 soma pairs подлежат строгому анализу
и полным временным отчётам. Приёмка ещё не выполнена, в develop изменений нет.


## Проверенный промежуточный результат

На обоих workers46/46 C++ (42 controller и4 native boundary cases),
4 production stopped-state audits и32 полных probe/CSV (48 soma pairs).
Normal primary `348f15e866f36769b29a20678c6ef0e0897a2961`, ASan
`f3061e974e3e134ba0900e80e53a1c02dc14015d`: по114 verified members,
95560/98336 bytes. ASan loaded-files snapshot содержит реальную libasan.
Baseline initial `fc8b8a2b0b0616866aa5a94f9028e81f6f47e1a6` (29 members),
corrected `a2bc9dadba6fb651cc52a5e7918b0125d0eeb25a` (38 members): также
проверены все archive/member/bundle hashes. Сохранились исходные setup errors.

Feature НЕ принята в develop. Важно: смена max-sweep статуса влияет на свежие
ранее nonexact completed-boundary/recognition fixtures. Их регрессии нельзя
заменить четырьмя успешными singleton-domain controls. Требуются actual
configured/positive/transfer проверки и явный diagnostic evaluation путь,
без автоматического обхода guard-а и без переоценки исторических архивов.
Native32 temporal reports и scoped direct visual review ещё открыты.
Точное состояние и следующие обязательные действия в progress JSON.
Все текущие numeric jobs завершились; их immutable source/runtime snapshots
не переименовываются под более поздний metadata HEAD.

## Продолжение проверки 2026-11-02

Предыдущий абзац описывает закрытые 46-case gates, а не более поздние задания.
В develop принят только независимый `native-gate` runner, root merge
`44334e272de8429f29775512a860584c60350899`; алгоритмическая Pulse feature
`63fd7a9fecbc567fb8e5c690ae58fc73a896de65` по-прежнему НЕ принята.

На Elder численный root `24d1beba2bb58982931a62668a3019dd053e20f8` прошёл
30/34 дополнительных случаев: native service, configured/XML/Copy, repeated N0.
Четыре прежних `NativeLearnedState` fixtures требуют сертификат сразу после
`maximum_sweeps_exhausted` и падают до проверки переноса. Первичные данные,
включая failed JUnit: `946fbb10ec11d19d1677547501023db29d7634b8`, 643 verified
members / 1,693,314 bytes. Это отрицательный результат gate, без PASS.
Такой же полный ASan gate продолжает работать; повторно он не запускался.

Root `575046be521cdc26507bd52f5b85ceb29f46d3bd` явно разделил ожидания helper-а:
четыре default0.02 случая должны сохранить BudgetExhausted и stopped package,
а существующий named explicit0.2 контроль должен сохранить Exact/completed
package. Оба пути проверяют настоящий import, frozen input/soma samples,
отдельный процесс и rollback. Допуски, модель и алгоритм не изменены.
Пять случаев были выполнены на Elder: 5 failed из-за двух новых ошибочных
ожиданий helper-а ПОСЛЕ явного learner Reset. Данные сохранены в
`dfbe623c510c5b2ab831e4584bc73d2e626e8e4f`, 230 verified members / 846,577 bytes.
Это не положительная приёмка и не доказательство изменения физического графа.

В root `5e299dedfd10985cce3bca8da04b70acbe3a4432` исправлены именно эти
ожидания: Reset переводит управление в Idle/Searching; остановленный attempt
после этого нельзя повторно export как терминальную границу. Ранее полученный
immutable stopped package сохраняется, граф/индивидуальные параметры/refs
проверяются отдельно. После rejected import проверяется состояние именно
перед этой операцией, включая status/reason/state, а не до Reset.
Нужна повторная серверная проверка; по коду она не считается завершённой.

Diagnostic frozen probes не являются completed-Train recognition. Conversion
проверяется с реальными storage/environment и точной причиной
`recognition_requires_completed_solo`; отсутствие сертификата не маскируется.
Runner обязан export на закрытой границе ДО явного Reset контроллера.
Самостоятельный model export после Reset и публичный diagnostic-evaluation
протокол остаются отдельными обязательными пунктами общего плана.
Старые сохранённые nonexact completed packages не переименовываются в stopped;
их фактический replay/import требует отдельного compatibility контроля.

`specs/native-search-termination-v1.json` содержит 46 source-declared TEST IDs
и ровно 32 ожидаемых packet/CSV. Полнота не выводится из существующих файлов.
Для этих закрытых исходных gates строится temporal cache на M40 Data:
48 trial/soma pairs с реальными входными импульсами, overview и sample-scale
увеличениями. Попытка системным Python завершилась до rendering из-за
отсутствия matplotlib; сохранена как temporal-asan-a1. Повтор использует
существующий plot-venv-a1 и отдельный readback temporal-asan-a2. Полный кэш не
публикуется в Git; нужны его manifest, проверенные hashes и выбранные рисунки.
До завершения rendering/direct review визуальная приёмка остаётся открытой.

### Последующий подтверждённый результат и совместный кандидат

ASan34 закрыт:30 passed/4 прежних certificate-expectation failures, как на
Elder. Primary `e6a42403fabe970db55130dae35de4aa4cd6da4c`:642 verified members,
1,703,899 bytes. Gate отрицательный. Исправленные transport fixtures на Elder,
численный root5e299dedf:5/5 passed (diagnostic Budget4 и explicitly0.2
Exact/completed1). Для всех5 независимо сверены frozen/fresh-process CSV.
Primary `f80a5f3f71fdaabbe38a1d2bb12d67ac8318d6d0`:248 verified members,
901,164 bytes. Его ASan5 пока выполняется, успех не заявляется.

Temporal cache32 закрыт:48 trial/soma pairs,288 PNG на M40 Data,
`report-cache/s07-search-termination-asan-a1`. Git содержит metadata и24
selected PNG: `cc0c6c6d6abfdb1583b2aa4f14503698f6049ce6`,40 verified members,
3,578,781 bytes. Все24 просмотрены непосредственно в1920×960: видны импульсы
и форма сомы, zoom не менее14.208 pixels/native tick. Полная ручная проверка288
не заявляется; exact hashes/границы в SearchTerminationVisualQA.json.
Shared Y относится к каждой группе, отдельные standalone groups имеют свои
подписанные шкалы. Нельзя сравнивать амплитуду только по высоте кривой в пикселях.

Normal/ASan32 CSV побайтно одинаковы, все32 JSON одинаковы после строгого разбора
и canonical serialization. Raw JSON bytes различны и hashes сохранены.
Ledger `fbed495970d5fdce1f279c613425bcbf01ac73b1` позволяет normal ссылаться на
тот же кэш без дублирования рисунков. Кэш явно связан с ASan primary, runtime
идентичности остаются разными. Это training diagnostics, не classification.
Воспроизведение: maintained CLI `report --format native-test-run` с
native-search-termination-v1.json, --artifacts (native.xml/native), новым
--output и plot-venv. Alias native.xml есть точная копия original gtest.xml.

Объединение только feature branches: Pulse merge
`fca7141178a854c5a2f579e4a195b3a3165340f9`, root merge
`481a9f76d927a7947db308e3c3f0a8ba12e160cf`. Конфликты gitlink и append-секций
аудита разрешены сохранением combined Pulse и обеих записей с уточнением статуса.
Математические допуски не менялись. Develop алгоритмов ещё не обновлялся.

Новый численный кандидат `07167d55125ced4eeff72703a718203e8c90bfc7` также
усиливает precise Reset-export reason и сохраняет прежний missing-final
completed-state rejection дополнительно к duplicate-final control. Эти новые
проверки на кандидате ещё не выполнены. Spec integrated-wall-search-native-v1
объявляет163 уникальных IDs:46 bounded/termination,34 configured/service/
transfer +1 named Exact transport,66 wall-policy,16 inherited/frequency.
Начата отдельная Elder-сборка. Источники M40 до окончания текущего ASan5 не
меняются. После сборки нужны реальные163 и Console/report regressions на обоих
workers. Old source closures не переименовываются под новый metadata HEAD.
Saved legacy replay, public diagnostic evaluation, остальные режимы/physics,
legacy A/B и другие требования исходного плана остаются открытыми.

ASan five-case follow-up завершён:5/5 passed, с настоящей loaded libasan,
diagnostic Budget4 и named Exact/completed1; все5 frozen/fresh-process CSV
побайтно равны внутри worker. Primary
`461cc58deda8f8d1b026fa3564591d1bd2882926`:248 verified members/904,964 bytes.
Этим закрыт scoped transport gate численного root5e299dedf на обоих workers.
Усиленные проверки и combined Pulse нового root07167d551 этим не принимаются.
Его Elder build завершён и163-case gate запущен; на M40 начат build той же
точной closure. Owned PID/start ticks и пути обновлены в progress JSON.
