# Readback фактической модели

Новый Console режим:

```text
NeuroModelerConsole --app-ini /runtime/NeuroModelerConsole.ini \
  --config /work/Test/Project.ini --inspect-model /results/readback.json
```

Режим выполняет штатную загрузку проекта и ModelInit, снимает фактический граф
и завершает процесс без Calculate. Его нельзя совмещать с расчётом, SaveProject,
check-config или генерацией ClDesc. Существующий output не перезаписывается.

Inspector сам не выполняет Build/Reset и не исправляет параметры перед чтением.
Нативная инициализация в CLI соответствует подготовке к исполнению; её Reset
не означает возврат модели к необученной структуре. Именно поэтому source
configuration и effective graph учитываются раздельно.

JSON schema 1 содержит именованное дерево компонентов и классы, actual child
order, frequency, flags Init/Ready/Activity, параметры/состояния через штатный
serializer Rdk, connected flags, прямые property bindings с индексами входов, effective
C/R/TC/PSI и соответствие cached membrane/channel/LTZone pointers именованному графу.
NaN/Inf не заменяются нулём: выдаются null с diagnostics и valid=false. Ссылка
кэша/источника за пределы полного графа также делает readback невалидным.

Источники читаются через read-only API UIPropertyInput::GetDataSources, а не
реестр UItem connectors: прямой SetPointer не обязан создавать UItem. UVProperty
отражает приоритет ExternalDataSource над ConnectedOutputs, как native GetData;
порядок vector slots сохраняется. Неизвестная реализация connected property,
пустой или неразрешённый источник запрещает valid=true. API не вызывает GetData
и не заполняет lazy cache; общий serializer параметров может штатно читать данные.
Снимок выполняется при остановленном расчёте и без параллельного изменения графа.
Изменение виртуального интерфейса требует согласованной пересборки Rdk и модулей.

Это readback, а не model export или checkpoint. Generic rdk_value сохраняет
нативное представление Rdk, которое может быть текстом скаляра или XML массива.
Его нельзя интерпретировать как унифицированный JSON numeric type. Поля physics
содержат отдельные численные значения. Распознаваемые credential properties
не включаются; такой документ не считается полным valid snapshot.

Следующий этап сопоставляет этот граф с ModelSpec и обученным состоянием. Одного
valid=true недостаточно, чтобы доказать совпадение Train/Test, frozen model,
правильный фактор эксперимента либо научный результат.
