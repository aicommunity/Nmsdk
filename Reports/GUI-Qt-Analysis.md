# Повторный анализ GUI (Qt)

## Контекст и цели

- Согласно `Reports/00-Project-Overview.md`, Neuro Modeler SDK (Nmsdk) — это компонентная среда для конструирования и исполнения нейросетевых и робототехнических моделей. GUI служит единственным визуальным фронтендом NeuroModeler и должен быстро отображать состояние `UNet`, предоставляя средства настройки компонентов и анализа сигналов.
- Требования повтора: учитывать только Qt-реализацию (`Rdk/GUI/Qt`), сохранить привязку к ядру `Rdk/Core`, сфокусироваться на производительности (включая взаимодействие с ядром) и удобстве конфигурации/графов.

## Архитектура Qt-GUI

### Слой визуальных контроллеров

- Базовый класс `UVisualControllerWidget` наследует одновременно `QWidget` и `RDK::UIVisualController`, автоматически регистрируя каждый виджет в `UIVisualControllerStorage`. Он инкапсулирует логику жизненного цикла (AfterLoad/BeforeClose/BeforeCalculate/UpdateInterface и пр.), управление интервалом обновления и флагами расчёта.
```12:151:Rdk/GUI/Qt/UVisualControllerWidget.h
class UVisualControllerWidget:public QWidget, public RDK::UIVisualController
{
    ...
    bool UpdateInterfaceFlag;
    bool AlwaysUpdateFlag;
    RDK::UELockVar<long> UpdateInterval;
    static RDK::UELockVar<bool> CalculationModeFlag;
    ...
    virtual void UpdateInterface(bool force_update=false);
}
```
- Главное окно `UVisualControllerMainWidget` расширяет QMainWindow, управляет таймингами обновления (`UpdateInterval`, `LastUpdateTime`), проверяет состояние модели и каналов, держа GUI в соответствии с тиком ядра.
```8:281:Rdk/GUI/Qt/UVisualControllerMainWidget.cpp
UVisualControllerMainWidget::UVisualControllerMainWidget(...){
    application = app;
    UpdateInterval=1000;
    RDK::UIVisualControllerStorage::AddInterface(this);
}
...
void UVisualControllerMainWidget::UpdateInterface(bool force_update){
    if(UpdateInterval>0 && CalculationModeFlag){
        ...
        if(GetCalculationStepUpdatedFlag() == true)
            return;
        else
            SetCalculationStepUpdatedFlag();
    }
    if(!Core_IsChannelInit() || (CheckModelFlag && !Model_Check()))
        return;
    AUpdateInterface();
}
```

### Модули графов и мониторинга

- Стек `UGraphWidget` → `UGraphPaintWidget` (на `QCustomPlot`) организует выбор компонент/свойств, регистрацию источников данных и визуализацию графов. `UGraphWidget::AUpdateInterface` на каждом тике блокирует модель (`RDK::GetModelLock`), читает свойство через `AccessPropertyData`, формирует точки и инициирует `replot`.
```145:201:Rdk/GUI/Qt/UGraphWidget.cpp
void UGraphWidget::AUpdateInterface(){
    int n=graphPainter->getSize();
    for(int i=0; i<n; i++){
        RDK::UELockPtr<RDK::UNet> model=RDK::GetModelLock<RDK::UNet>();
        auto component=model->GetComponentL(current_graph.nameComponent,true);
        auto *m=component->AccessPropertyData<RDK::MDMatrix<double>>(current_graph.nameProperty);
        double y=(*m)(current_graph.Jy,current_graph.Jx);
        double x=Model_GetDoubleRealTime();
        addDataToGraph(i,x,y);
        if (flagUpdateBordersX>0) { ... }
    }
    graphPainter->redrawGraph();
}
```
- `UGraphPaintWidget` хранит описание каждого графика в `vector<TSingleGraph>` и при любом изменении полностью обновляет QCustomPlot (через `setData`, `replot`). Нет стратификации данных или буферизации.
```18:219:Rdk/GUI/Qt/UGraphPaintWidget.cpp
ui->widget->clearGraphs();
vectorGraph.push_back(newTSingleGraph);
ui->widget->graph(id)->setData(X,Y);
ui->widget->replot();
```

### Конфигурационные инструменты

- `UComponentPropertySelectionWidget` отображает `UComponentsListWidget` внутри диалога, что используется, например, в `UGraphWidget::slotActionSelectOutput` для выбора источника данных.
- `UComponentsListWidget` строит представление дерева компонентов, вкладки параметров/состояний/входов/выходов, избранное, список каналов. `AUpdateInterface` очищает и пересоздаёт дерево полностью, а `reloadPropertys` повторно перечисляет все свойства выбранного компонента, выполняя `GetModelLock` и `GetPropertiesList`.
```142:389:Rdk/GUI/Qt/UComponentsListWidget.cpp
void UComponentsListWidget::AUpdateInterface(){
    componentsTree->clear();
    QTreeWidgetItem *rootItem = new QTreeWidgetItem(componentsTree);
    rootItem->setText(0, "Model");
    addComponentSons("", rootItem, oldRootItem, oldSelectedItem);
}
...
void UComponentsListWidget::reloadPropertys(bool forceReload){
    auto model = RDK::GetModelLock(getWorkChannelIndex());
    auto cont = model->GetComponentL(currentDrawPropertyComponentName.toLocal8Bit().constData(), true);
    auto varMap = cont->GetPropertiesList();
    for(...){
        if (i->second.CheckMask(ptPubInput)) ...
    }
}
```

## Проблемы производительности и взаимодействия с ядром

1. **Синхронная отрисовка графов поверх блокирующих вызовов ядра.**  
   - Каждый граф в `AUpdateInterface` запрашивает блокировку модели, находит компонент по длинному имени, извлекает матрицу и читает отдельный элемент. Все операции выполняются в UI-потоке без кэширования указателей на свойства и без контроля времени выполнения. Нагрузка растёт линейно с числом графов, а любое ожидание `GetModelLock` стопорит весь интерфейс.
   - *Решения:*  
     - Буферизовать `RDK::UEPtr` компонента и `MDMatrix` в структуре `TSingleGraph` с проверкой версий/валидности.  
     - Перенести выборку данных в фоновые задания (Qt Concurrent / `std::future`) и публиковать батчи точек в GUI через `QMetaObject::invokeMethod`.  
     - Добавить слой подписки на каналы ядра (observer/события), чтобы графы получали готовые значения без полного обхода модели.

2. **Перерисовка QCustomPlot полными массивами.**  
   - `addDataToGraph` хранит растущие `std::vector<double>` и при каждом обновлении вызывает `setData` с копией всего набора точек + `replot`, что даёт O(n²) копирования при длинных сериях.  
   - *Решения:* использовать `QCPGraph::addData`/`replaceData` с `QSharedPointer<QCPGraphDataContainer>`, ограничивать историю скользящим окном (ring buffer), а `replot` вызывать раз в кадр с `QCustomPlot::replot(QCustomPlot::rpQueuedReplot)` или через `QTimer`.

3. **Полная перестройка дерева компонентов и списков свойств.**  
   - `UComponentsListWidget::AUpdateInterface` и `reloadPropertys` всегда очищают `QTreeWidget`, пересоздают каждую ветку и заново считывают все свойства из ядра. Это тяжело для сетей с тысячами компонент и ведёт к множеству аллокаций/строковых преобразований.  
   - *Решения:* внедрить модель на `QAbstractItemModel` с ленивой загрузкой (populate on expand), кешировать `UComponent` → список дочерних идентификаторов, дифференциально обновлять дерево при событии изменения модели. Для вкладок параметров — хранить последнее значение и обновлять только изменённые узлы.

4. **Отсутствие разделения потоков GUI и расчёта.**  
   - Базовый `UVisualControllerWidget::UpdateInterface` лишь пропускает обновление, если `CalculationModeFlag` активен и ещё не прошёл интервал, но не выполняет долгие операции вне GUI. Любая длительная загрузка параметров или сериализация (`SaveParameters`) блокирует интерфейс.  
   - *Решения:* ввести очередь событий от ядра (например, `UIVisualControllerStorage` → `QThread` воркер), где трудоёмкие вызовы (`GetPropertiesList`, `SaveParameters`) выполняются за пределами основного потока, а GUI получает уже подготовленные DTO.

5. **Состояния графов и конфигурации хранятся в INI/XML с частыми синхронными вызовами IO.**  
   - `ASaveParameters` / `ALoadParameters` (`UGraphWidget`, `UComponentsListWidget`) обращаются к `QSettings` напрямую. Для больших проектов запись/чтение на каждый закрываемый диалог замедляет UX.  
   - *Решения:* буферизовать настройки в памяти и записывать пачкой (например, при закрытии приложения), использовать неблокирующую загрузку в отдельном потоке.

## Рекомендации по улучшению UX графов и конфигурации

### Графы

1. **Мастера подключения сигналов.**  
   - Расширить `UComponentPropertySelectionWidget` фильтрами по типу компонента/подсети, быстрым поиском по имени и предпросмотром структуры данных (матрица, скаляр).  
2. **Шаблоны и профили графов.**  
   - В `UGraphControlDialog` добавить сохранение набора графов (цвет, компонент, свойство) как пресета; загрузка пресета на новый проект ускорит работу.  
3. **Множественные оси и режим “heatmap”.**  
   - Для параметров типа матриц позволить отображать тепловые карты (на `QCPColorMap`) или множественные оси для разных масштабов.  
4. **Синхронизация с конфигурацией.**  
   - Клик по графику должен подсвечивать соответствующий компонент в `UComponentsListWidget`, обеспечивая двустороннюю навигацию.  
5. **Интерактивные окна времени.**  
   - Введение панелей “History window” и “Live window” (скользящий диапазон) управляемых колесом мыши/жестами; хранить длинную историю в отдельном буфере, а на экране показывать лишь часть.

### Конфигурация/схемы

1. **Виртуализированное дерево компонентов.**  
   - Перенести дерево на `QTreeView + QAbstractItemModel`, поддерживающий lazy loading, фильтры, сохранение состояния раскрытых веток.  
2. **Расширенный поиск и закладки.**  
   - Добавить глобальный поиск по имени/классу/типу, сохранение пользовательских “избранных” узлов/свойств в отдельной панели.  
3. **Массовые действия и сравнение.**  
   - UI для массового изменения параметров (multi-select + batch edit), сравнение свойств двух компонентов бок о бок.  
4. **Контекстная помощь и предварительные проверки.**  
   - Интеграция описаний классов (`UClassDescriptionDisplay`) напрямую в информационную панель, подсветка несовместимых связей ещё при выборе.  
5. **Интерактивное редактирование связей.**  
   - В `UComponentLinksWidget` внедрить drag-and-drop между выходами и входами, отображение веса/задержек, фильтры по каналу.

## Предлагаемая дорожная карта оптимизации

1. **Сбор телеметрии.**  
   - Добавить профайлер времени для `AUpdateInterface` каждого виджета (например, RAII-таймер). Это позволит количественно подтвердить узкие места.
2. **Фоновая синхронизация данных.**  
   - Создать сервис `GuiModelSnapshot`, который по событиям ядра подтягивает актуальные данные, а GUI читает только из snapshot (lock-free).  
3. **Инкрементальные обновления графов.**  
   - Реализовать кольцевые буферы и `QCPGraph::addData`. Ограничить обновление осей по расписанию (`QTimer` 30–60 Гц).  
4. **Новый компонентный браузер.**  
   - Построить модель на `QAbstractItemModel`, подключить `QSortFilterProxyModel` для поиска, добавить lazy fetch.  
5. **UX-улучшения** (по п. “Графы” и “Конфигурация”), начиная с наиболее востребованных: пресеты графов, фильтр компонентов, двусторонняя синхронизация выбора.

## Следующие шаги

- Утвердить приоритеты (например, начать с графов, т.к. они критичны для анализа данных).  
- Спроектировать API для snapshot/observer между ядром и GUI.  
- Подготовить PoC оптимизированного `UGraphWidget`, замерить снижение нагрузки.  
- После подтверждения — распространить подход на остальные визуальные контроллеры.

