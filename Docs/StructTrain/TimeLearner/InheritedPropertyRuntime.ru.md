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
сохраниться индивидуальные learned parameters, model revision и фактические
soma/input waveforms обоих входов. MaxCalculationDuration остаётся отрицательным:
этот тест не подтверждает режим с wall-driven пропуском детей.

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
