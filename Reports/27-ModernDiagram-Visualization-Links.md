# Modern Diagram — визуализация и связи (декабрь 2025)

## Что сделано
- Новый виджет `UModernDiagramWidget` (QGraphicsView/QGraphicsScene), отдельная вкладка рядом с классическим.
- Узлы: `NodeItem` с портами, перемещаемые, выделяемые; линии `LinkItem` привязаны к узлам.
- Координаты: читаются из ядра (`Coord`) с fallback на plain `x y z`; лог `load coord (plain)`/`load coord`; автонормализация сцены (min->0,0), авторамка `fitInView` с паддингом.
- Сохранение: при движении узла лог `save coord`, запись `Model_SetComponentParameterValue` в ядровых координатах (неотрицательные).
- Масштаб/прокрутка: `fitInView`+sceneRect, скроллы активны; мини-карта есть.

## Диагностика связей
- Парсинг `Model_GetComponentInternalLinks` в `buildLinks`.
- Логи: размер XML, сэмпл (до 2000 символов), `links parsed count`, `link raw srcName/srcId/dstName/dstId`, `link add`, `link skip` (srcOk/dstOk), итоговая сводка added/skipped.
- Резолв узлов:
  - Сначала по `Name` (`link.Item.Name`/`Connector.Name`) через `m_nodeByName`.
  - Если не найдено — по `Id`: берётся `Id`, отрезается префикс после первой точки (верхний компонент), убирается префикс модели при наличии, ищется в `m_nodeByName`.
- Показанные в логе примеры: `srcId=PGenerator`, `dstId=PNeuronS1D0Syn1.Soma1.ExcSynapse1` теперь мапятся на узлы `PGenerator` и `PNeuronS1D0Syn1`.

## Наблюдения/особенности
- Внутри `UStringLinksList` `Id` содержит полное имя компонента/подкомпонента; `Name` — имя порта (`Output`, `Input`, `ChannelInputs`, `SynapticInputs` и др.).
- При отсутствии узла по `Id` связь пропускается; лог `link skip ... srcOk/dstOk` помогает увидеть, что именно не найдено.
- Начальные координаты могут быть как XML `<Coord>`, так и plain `x y z`; последняя форма идёт от старого виджета — теперь поддерживается.

## Использование логов
- Канал: `RDK_GLOB_MESSAGE`, уровень `RDK_EX_DEBUG`.
- Ключевые метки: `[ModernDiagram] load coord`, `(plain)`, `save coord`, `links xml bytes/sample`, `links parsed count`, `link raw`, `link add`, `link skip`, `links summary`.

## Оставшиеся риски
- Если в `Id` верхний компонент не совпадает с именем узла в сцене, связь всё ещё будет пропущена.
- Нет визуализации связей на уровне подкомпонентных портов — линии ведутся между верхними узлами.

## Где правки
- `Rdk/GUI/Qt/UModernDiagramWidget.{h,cpp}`

