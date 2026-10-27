# Семантическая проверка новых свойств configured controller

Проверены исходники PulseLib `025d809f7b86cc79e18ddd711c6adc40e2396bf8`
двух классов: `NNeuronTimeLearner` и `NNeuronTimeLearnerBranch`. Этот обзор
касается трёх свойств каждого класса. Он не закрывает review 211 записей
первоначального inventory и не заменяет их отдельную проверку. Code review
16 исходных записей теперь зафиксирован отдельно в
[LegacyControlPropertyContracts](LegacyControlPropertyContracts.ru.md) и
[PropertyReview.json](PropertyReview.json); 195 остаются непроверенными.

| Свойство обоих классов | Тип, единицы, Default | Владелец и setter | Build/Calculate/Reset | Сохранение и ограничения |
|---|---|---|---|---|
| ControllerVersion | int, идентификатор версии, 1 | Декларация контроллера. Setter принимает только 1/2; после native ownership запрещает смену значения; допустимое присваивание делает компонент unready | V2 Build подготавливает native declaration, BeforeCalculate запускает службу только при Need и Idle; V1 без native ownership сохраняет legacy dispatch. Reset версию не переключает | ptPubParameter: XML/Copy и full learned-state package. Отсутствие поля оставляет default 1; V1 также допускает явный native C++ API, поэтому номер версии не равен признаку отсутствия native модели |
| ControllerConfiguration | string, strict JSON schema 1, пустая строка | Декларация ModelSpec/protocol/search. Setter запрещает изменение при активном Train и изменение уже принятой декларации; допустимое присваивание делает компонент unready | V2 Build разбирает и проверяет конфигурацию, строит cold модель только при отсутствии process-local declaration и marker=false. BeforeCalculate не заменяет Build. Reset сохраняет декларацию и исходную цель | ptPubParameter: XML/Copy и full package. Не трактовать как controller checkpoint; сохранённый граф нельзя восстановить только этой cold декларацией. Configured retarget/reconfiguration ещё не реализованы; строку нельзя считать действующим фактором, если setter её отклонил |
| ConfiguredModelInitialized | bool, marker, false | Внутренний сохраняемый признак принятого cold/import состояния. Отдельного setter нет; production native пути задают его SetDataDirect | Marker=true при отсутствии process-local declaration блокирует cold реконструкцию и выставляет diagnostic; Build возвращает управление без скрытой перезаписи обученной модели. Reset не возвращает marker в false | ptPubParameter \| ptPubState: параметр необходим, поскольку Rdk Copy(false) вызывает Build до копирования state. XML/Copy без полного импорта намеренно остаются удержанными. Это не флаг сходимости, valid Train или научного PASS |

В обоих классах используются одинаковые validators и native service; различие
топологий задаётся явным branch аргументом. Ошибки V2 Build попадают в
`NativeModelEditFailure`/typed outcome; lifecycle bool не является протоколом ошибок.
Legacy hooks и вся матрица режимов ещё требуют завершения общего этапа 4/6.

## Проверки и доказательность

Принятый configured подэтап: root
`cb9e035b390390746ada5caa2c500917b8884612`, по 14/14 configured tests на обоих
серверах. Источники и первичные артефакты:
[ConfiguredNativeController](ConfiguredNativeController.ru.md).

Адресные test names в `Test_PulseLib_NativeModelEditor.cpp`:

- `ConfiguredNativeTraining.ClassicN0/BranchN0/ClassicN1/BranchN1` — реальный запуск V2 через scheduler.
- `ClassicColdXmlStartsTheController` и `BranchColdXmlStartsTheController` — cold XML Load.
- `StrictCodecRejectsDuplicateUnknownAndCorruptFields` — strict schema.
- `MissingConfigurationAndLoadedMarkerFailWithoutColdReset` — отсутствие декларации/сохранённый marker.
- `ClassicXmlLoadDoesNotColdReset` и `BranchXmlLoadDoesNotColdReset`.
- `ClassicCopyWithoutStateDoesNotColdReset` и `BranchCopyWithoutStateDoesNotColdReset`.
- `ClassicCopyWithStateDoesNotColdReset` и `BranchCopyWithStateDoesNotColdReset`.

A7 root `4cc548656857bd97d927c16fdd070c7608e091f0` добавляет фактический full
learned-state перенос configured source (Classic N1, Branch N0). Это адресная
проверка сохранения декларации и frozen модели, а не полная matrix всех параметров.

Остаются обязательными отдельные проверки configured reconfiguration/retarget,
всех режимов Calculate/StructureBuild, optional C/PostTune/calibration и всех
физических profiles. Marker загружаем ради совместимости, но не разрешаем
использовать его как независимый научный фактор эксперимента.
