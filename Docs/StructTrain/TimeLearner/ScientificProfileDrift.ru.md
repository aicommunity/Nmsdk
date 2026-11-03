# Научная модель и интеграционный fixture: обнаруженное различие

В исходном stock `NSPNeuronGen` отдельная LT-мембрана отключена:
`NPulseLibrary::CreateClassSamples` устанавливает `LTMembraneClassName=""`
перед Build/UploadClass. В августовском графе есть LTZone, но нет LTMembrane.

Отдельная мембрана добавлена в созданный при рефакторинге `EditingRig`:
root commit `4585a3b3fac7e7a5c0f0dcd39eb92ca485992f74`,
`Tests/Integration/Libraries/Test_PulseLib_NativeModelEditor.cpp`:

```cpp
profile.initialThreshold=1.;
profile.ltMembrane=profile.body;
profile.ltMembrane->excChannel.capacity=.3e-9;
```

Это integration-профиль для проверки неоднородной физики, редактирования и
сохранности LT-ёмкости. `RegisterStorageProfile` создаёт отдельные образы;
общий `NSPNeuronGen` не менялся. Позднее этот archive использован при подготовке
двухвходовых cold N1 jobs. Base class не доказывает тождество stock-физике.

## Подтверждённая физика

Сопоставлены оригинальный Bin commit
`1c1464e248f8744e858bd66df0be99e39969fd65`,
`Configs/SpikeSamples/StructTrain/SelectivityPhaseA/EXP00_baseline/Train/Parameters_00.xml`,
и actual Solo graph из normal N1 calibration proof
`27c5120e06d61be2244fd92111a4b062774880a8`.
Прочитаны дочерние компоненты, а не только parent defaults.

| Свойство | Августовский граф | Новая N1-модель |
|---|---|---|
| Отдельная LTMembrane | Нет | Есть, ExcChannel 0.3 nF |
| Synapse DissociationTC | 0.005 s | 0.001 s |
| InhChannel RestingResistance | 10 MΩ | 100 MΩ |
| Body channel Capacity | 1 nF | 1 nF |
| Число входов | 4 | 2 |

Одновременно отличаются несколько факторов. Ни молчание при пороге1, ни5/8
нельзя причинно объяснять только LTMembrane. Возможное уменьшение пика,
задержка и изменение ширины реакции — гипотезы. Влияние на вероятность спайка
может зависеть от суммирования, порога и обратного действия спайка; монотонный
эффект не установлен.

## Исправление постановки

Использование этого fixture как основного научного продолжения исходной модели
было ошибкой постановки. Наблюдения валидны для сохранённого изменённого профиля.
Инженерные heterogeneous storage/transport tests также сохраняют силу.

1. Основной научный контур — stock `NSPNeuronGen` без LTMembrane. Сначала
   native preflight и readback полного графа/дочерней физики. Исходный target
   [0.01,0.08,0.16,0.24] и max length100 берутся из августовского снимка.
   Новый V2 training protocol объявляется отдельно, не как replay старого кода.
2. Общая физика задаётся storage-образами; не менять общий prototype или
   исправлять C/кинетику/наличие LT записями learner на каждом тике.
3. LT Off/On сравнивается парно при одинаковой остальной физике, morphology/Rs,
   частоте и protocol. Модели имеют разные fingerprints; старый Exact
   certificate не переносится автоматически после изменения графа.
4. Отделить probes при одном фиксированном пороге от новой реальной калибровки
   каждого варианта. Подбор другого порога не должен скрывать эффект LT.
   Cold Train с LT Off/On — отдельная проверка влияния на обучение.
5. Выполняющаяся серия528 предъявлений остаётся diagnostic study изменённого
   двухвходового профиля; основной stock-контур и матрицу физики она не заменяет.

На первой странице будущего научного отчёта должны быть фактические body/LT
параметры, размерность, профиль и полный model archive. Хэш доказывает конкретную
модель, но не её соответствие научному замыслу. До дорогого Train требуется
explicit profile readback. Все исходные этапы1–12 остаются в полном scope.
