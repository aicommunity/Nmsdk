# Inherited properties: незавершённая native runtime проверка

Продолжение [source contracts](InheritedPropertyContracts.ru.md). В production
`Test_PulseLib_StorageComponents` добавлены16 случаев `NativeInheritedProperties`:
Classic/Branch ×N0/N1 ×2000/20000Hz ×Activity/reset и local-frequency rejection.
Они используют существующий реальный EditingRig со storage/Environment/native
model construction, а не копию функций Rdk. Контур вызывается через native
probe API; это не полная матрица configured ControllerVersion1/2 Train.

Activity cases проверяют runtime регистрацию всех девяти свойств и effective
frequency/identity. До вмешательства и после него измеряются оба входа в штатной
пачке. Между пробами штатными setters меняются диагностические пороги, debug
mask и Coord; выключение Activity должно сбросить native probe control и
выключить детей.32 глобальных ticks не должны менять физический rest baseline
выключенной модели; нулевой rest не предполагается. После включения должны
сохраниться индивидуальные параметры native графа, model revision и фактические
soma/input waveforms обоих входов. MaxCalculationDuration остаётся отрицательным:
этот тест не подтверждает режим с wall-driven пропуском детей.
Здесь проверяется явно построенное начальное состояние с неодинаковыми L,
а не результат проведённого Train. Continuation реально обученной модели
и произвольные heterogeneous Rs/C требуют собственных runtime cases.

Frequency cases изменяют локальную частоту реального генератора, сохраняя
частоту owner. Проба должна быть отклонена как multirate до первого записанного
sample; после восстановления частоты waveform и модель должны совпасть с
baseline. Цель — исключить ошибочное принятие такой конфигурации в uniform V2
контур, а не объявить поддержку multirate.

Для waveform сравнения используются весь stimulus ряд и все soma channels;
допуск потенциала1e-12 и относительного времени1e-11s проверяет повторение этого
контроля и не заменяет исходные training tolerances. Научный verdict не создаётся.
Серверная сборка/проверка, temporal reports и приёмка пока ожидаются.
Connected inherited properties, XML/Copy/reuse, изменение глобальной частоты с
пересборкой производных коэффициентов, raw Default и positive wall-limit
режимы остаются вне этого подэтапа и открыты в полном плане.

Первая серверная сборка bb3020192 на обоих workers остановилась до запуска
моделей. Тест ошибочно вызывал protected SetTimeStep напрямую; теперь используется
публичная TimeStep property со штатным setter. Отдельно компиляция native Coord
диагностики подтвердила общий дефект Rdk MUIOStream: MVector<T,3> formatter/input
ссылаются на несуществующие x/y/z вместо публичного operator()(index).
Исправление у владельца Rdk b34223ef113ca60a817589995205de06af77543a сохраняет
формат и precision caller; некорректный vector input теперь даёт failbit без
частичной подстановки координат. Добавлены шесть отдельных production-header
Math tests. Clean negative build на старом Rdk воспроизведён на обоих workers;
root proofsa7b9ffd4f7e4747a0ab364a4aca178dcaa2086d6 и
1b8c173aa8acf57ea5cade60c67baec39d9c2977: по33 verified primary members,
7284/6972 compressed bytes. Positive сборки ожидаются.
Это исправление стандартного vector stream, не MDMatrix XML writer и не
изменение физики нейрона. Первые compilation failures сохраняются как setup
ошибки, а не модельные или научные отрицательные результаты.

Для полного временного отчёта объявлен immutable fixture contract
`Scripts/StructTrain/TimeLearner/specs/inherited-properties-native-v1.json`:
16 test IDs и56 конкретных JSON/CSV пар.48 положительных проб дают72
trial-soma pairs; восемь намеренно отклонённых multirate проб не имеют
наблюдаемого контекста и не должны получать выдуманные оси/нулевые кривые.
Контракт не строится из surviving files. Generic native-test report adapter
дополнен поддержкой nonempty standalone-only набора без искусственной training
summary. Условия полного expected test/packet/CSV closure сохраняются;
полностью пустой набор остаётся ошибкой. Семь reader checks на реальных
артефактах, в том числе missing/duplicate/extra/NaN случаи, пока ожидаются.

Positive attemptA3 на обоих workers собрал targets, затем выполнил5/6 Math
cases успешно. Оставшийся test ошибочно предполагал standard token extraction
для string при using namespace RDK; штатный SDK extractor сохранил ведущий
пробел. Проверка остатка заменена явным std::getline с ожидаемым пробелом;
Rdk string semantics не меняются. Native16 не запускались после failed Math
gate. Следующая попытка должна сохранить A3 целиком и проверить6+16 заново.
