# Actual A4: приняты семь проверок независимого reader на шести архивах

На M40 **7/7 PASS,0FAIL/error/skip**,36.3656s. Использован неизменённый production auditor source `cec33f2fcceb8c8f815e3494173bf48dcd39ed6c`, пакет441Python files, fingerprint `629bd6fe86318b5e38251ab4f822a07d01debf4c8a9ab3d88a8896c0636de20d`. Это численная проверка существующих native exports, не новое обучение.

Вход — только шесть actual exports из [A4](CompositeFull250A4Acceptance-20261109.ru.md), commit `b4feb38aeed9940c4292b532b3de0e3ab853685e`:157 исходных JSON/CSV файлов,74,969,578bytes. Для reader выделена новая immutable projection; source/config/runtime-plan/index/model/CSV bytes совпали с Git. Данные не реконструировались из ожидаемых assertions. Seventh/final-sweep bundle не создавался.

| Case | Records /complete /measurement в native index | Назначение проверки |
| --- | --- | --- |
| classic-service |6 /6 /6|Все исходные primary, closure/geometry/counters|
| branch-service |6 /6 /6|То же для общего кабеля|
| branch-C0 |6 /6 /6|Реальный сохранённый C0 witness/history|
| classic-warm |6 /6 /6|Две попытки, сохранённая история и учёт|
| classic-partial |1 /0 /0|Неполная группа не становится измерением|
| branch-ambiguous |1 /1 /0|Закрытое неоднозначное наблюдение не становится измерением|

Числа таблицы прочитаны из native index; существующие семь tests независимо потребляют исходные данные и recompute geometry/closure для измеренных records. Проверены также sidecars, внешние CSV mirrors, missing/corrupt mirror refusal, перенос CSV без подмены semantic proof и rehashed partial/counter tamper. Список exact7 IDs сохранён в [постановке](CompositeNativeA4Semantic7Preparation-20261109.suite.json). Это не проверка полного training certificate, native import или научной классификации: соответствующие поля auditor остаются false/null.

Единственный запуск: unit `timelearner-2ef634c6-93ac-424b-87c0-44d81167c32e.service`, invocation `549b79f1c0e849128639083aecb5a575`, PID1046103/start328064253, binding `b00a7c34b18db6f308ac8c8cd2e1b07fce2bab0707bd9d2552ca427c252d055c`. Группа закрыта, lease освобождён; source632Git files и fixture157 до/после совпали.

Evidence `1f1e8a5ef47abd4d7d644748ddc5a8624f3f0e75`, origin `codex/timelearner-composite-native-a4-semantic7-m40-a1-evidence`. [Compact archive](../../../Reports/StructTrain/TimeLearner/s10-composite-native-a4-semantic7-m40-a1/primary.tar.xz) содержит69metadata files/86268compressed bytes, SHA256 `df6a1cec36af442865ad1666a6788eea7160fcfc40b3b581eb38922f916275c4`. Исходные75MB повторно не публиковались: authoritative payload остаётся в b4feb, включая полный context/model/native CSV.

Root независимо повторил metadata reader `c5f1cb2b90f19b0dd2c46b64f8b5cc5a7f65036fed6482be6cdffb8e94b548be`. [Квитанция](../../../Reports/StructTrain/TimeLearner/s10-composite-native-a4-semantic7-root-verification/independent-verification.json) SHA256 `7bf79275eec4e154099ec50ac8b7379602c8af7c857ba5886d18dc77b6c83a2f` проверяет7actual log/AST/derived-JUnit IDs, Git input/source bytes, runtime identity и точную связь request/binding/worker lease/recovery. Локально не повторялись tests, CSV numeric analysis, модели или графики.

Первый fixture-prep остановился **до lease/data writes**: sparse donor не содержал `.gitignore` blob, необходимый `git status`. В тот же новый plan Git ODB добавлены служебные Git objects, затем preparation завершена; SourceCEC и scientific data не исправлялись. Отдельная ошибка локального чтения результата исправлена повторным чтением уже сохранённого stdout; preparation не повторялась. [Полная подготовка и ограничения](CompositeNativeA4Semantic7Prepared-20261109.ru.md), negative/append records сохранены в evidence.

Подэтап actual-six archive1 принят. Archive2/candidate-window DATA, полный C++ cold decoder на этих exact six files, package/App execution и научная матрица остаются отдельными требованиями. Только исходный этап0 полного плана принят целиком; этот результат не закрывает этапы3/5/6 целиком.
