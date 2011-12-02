// ===========================================================
// Version:        3.0.5
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NBIOS_H
#define NBIOS_H

#include "NSupport.h"
#include "NController.h"
#include "rdk.h"

namespace NMSDK {

//using namespace MySDK;
class NStorage;
/*
class NAContainer: public RDK::UAContainer{};

class NAConnector: public RDK::UAConnector{};

class NAItem: public RDK::UAItem{};

class NADItem: public RDK::UADItem{};

class NANet: public RDK::UANet{};
  */
		  /*
class NANet: public RDK::UANet
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NANet(void);
virtual ~NANet(void);
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
public:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool Default(void);
// --------------------------
};
          */
/*
class NAContainer: public RDK::UAContainer
{
friend NStorage;
friend NController;

private: // Глобальные свойства
// Текущее время модели в секундах
static real Time;

private: // Системные свойства
// Таблица соответствий имен и Id компонент объекта
map<string,UId> CompsLookupTable;

// Таблица соответствий имен и Id параметров объекта
map<string,NVariable> ParamsLookupTable;

// Таблица соответствий имен и Id данных состояния объекта
map<string,NVariable> StateLookupTable;

// Таблица локальных указателей на дочерние компоненты
map<UId,RDK::UIPointer*> PointerLookupTable;

// Таблица компонент
vector<NAContainer*> Components;

// Таблица контроллеров интерфейса
vector<NController*> Controllers;

// Таблица соответствий <компонента в таблице Components, локальный указатель>
//map<NAContainer*,NAContainer**> ComponentPointers;

protected: // Основные свойства

public: // Общедоступные свойства
// Шаг счета в долях секунды
// Реальный шаг = 1./TimeStep
RDK::ULProperty<TimeT, NAContainer> TimeStep;

// Флаг активности объекта
// true - расчет объекта будет выполняться
// false - расчет объекта будет игнорироваться
RDK::ULProperty<bool, NAContainer>  Activity;

// Имя объекта
RDK::ULProperty<NameT, NAContainer> Name;

// Класс объекта в хранилище
UVLProperty<UId, NAContainer> Class;

// Id объекта
RDK::ULProperty<UId, NAContainer> Id;

public: // Физические свойства
// Координата компонента в пространстве сети
RDK::ULProperty<RDK::MVector<real>, NAContainer> Coord;


protected: // Временные переменные
// Если 'TimeStep' > 'Owner->TimeStep' то 'CalcCounter' является
// счетчиком текущего интервала ожидания.
// В противном случае 'CalcCounter' не ипользуется
TimeT CalcCounter;

// Хранит величину шага счета родительского
// объекта или величину шага счета этого объекта
// если родительского объекта не существует
TimeT OwnerTimeStep;

// Указатель на 0-й элемент вектора компонент
NAContainer* *PComponents;

// Количество компонент в векторе компонент
size_t NumComponents;

// Итератор, указывающий на этот объект в хранилище
//RDK::InstancesStorageIterator ObjectIterator;

public: // Открытые методы
// --------------------------
// Методы управления глобальными свойствами
// --------------------------
// Возвращает текущее время модели
static const real& GetTime(void);

// Устанавливает текущее время модели
static bool SetTime(real value);
// --------------------------

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NAContainer(void);
//NAContainer(const NameT &name);
virtual ~NAContainer(void);
// --------------------------

// --------------------------
// Методы доступа к свойствам
// --------------------------
// Проверяет, является ли объект owner
// владельцем этого объекта на каком-либо уровне иерархии
bool CheckOwner(const NAContainer *owner) const;

// Возвращает хранилище компонент этого объекта
//NStorage* const GetStorage(void) const;

// Возвращает полное имя объекта
// (включая имена всех владельцев)
NameT& GetFullName(NameT &buffer=NameTemp) const;

// Возвращает  'длинное' имя объекта
// (исключая имя владельца 'mainowner').
// Метод возвращает пустую строку, если 'mainowner' - не является
// владельцем объекта ни на каком уровне иерархии
NameT& GetLongName(const NAContainer *mainowner, NameT &buffer=NameTemp) const;

// Возвращает полный Id объекта
// (включая Id всех владельцев)
ULongId& GetFullId(ULongId &buffer=LongIdTemp) const;

// Возвращает  'длинный' Id объекта
// (исключая имя владельца 'mainowner')
// Метод возвращает пустой вектор, если 'mainowner' - не является
// владельцем объекта ни на каком уровне иерархии
ULongId& GetLongId(const NAContainer *mainowner, ULongId &buffer=LongIdTemp) const;

// Возвращает последний использованный Id компонент
//UId GetLastId(void) const;
// --------------------------

// --------------------------
// Методы управления свойствами
// --------------------------
// Удаляет владельца объекта
bool BreakOwner(void);

// Указатель устанавливается на число уровней дочерних компонент
// 'levels'. Если levels < 0 то устанавливается компонентам на всех уровнях
bool SetMainOwner(RDK::UAComponent* const mainowner);
bool SetMainOwner(RDK::UAComponent* const mainowner, int levels);

// Проверяет предлагаемое имя 'name' на уникальность в рамках данного объекта
bool CheckName(const NameT &name);

// Проверяет предлагаемый Id 'id' на уникальность в рамках данного, объекта.
bool CheckId(const UId &id);

// Генерирует имя уникальное в компонентах этого объекта
virtual NameT& GenerateName(const NameT &prefix, NameT &namebuffer);

// Генерирует уникальный Id
virtual UId GenerateId(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает величину шага интегрирования
bool SetTimeStep(TimeT timestep);

// Устанавливает флаг активности объекта
bool SetActivity(bool activity);

// Устанавливает имя объекта
bool SetName(const NameT &name);

UId GetClass(void) const;
protected:
bool SetClass(UId value);

public:
// Устанавливает Id объекта
bool SetId(const UId &id);
// --------------------------

public:
// --------------------------
// Методы доступа к таблицам соотвествий
// --------------------------
// Возвращает имя дочернего компонента по его Id
const NameT& GetComponentName(const UId &id) const;

// Возвращает Id дочернего компонента по его имени
const UId& GetComponentId(const NameT &name) const;

// Возвращает имя параметра по его Id
const NameT& GetParameterName(const UId &id) const;

// Возвращает Id параметра по его имени
const UId& GetParameterId(const NameT &name) const;

// Возвращает полное имя параметра без префикса NMSDK, и суффикса '*'
NameT GetParameterLongName(const NameT &name) const;
NameT GetParameterLongName(const UId &id) const;

// Возвращает имя переменной состояния по его Id
const NameT& GetStateName(const UId &id) const;

// Возвращает Id переменной состояния по его имени
const UId& GetStateId(const NameT &name) const;

// Возвращает полное имя переменной состояния без префикса NMSDK, и суффикса '*'
NameT GetStateLongName(const NameT &name) const;
NameT GetStateLongName(const UId &id) const;
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
//virtual NAContainer* New(const NameT &name);
virtual NAContainer* New(void)=0;

// Создает копию этого объекта с сохранением всех компонент
// и значений параметров.
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
virtual NAContainer* Alloc(const NameT &name, NStorage *stor=0, bool copystate=false);

// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;

// Осуществляет освобождение этого объекта в его хранилище
// или вызов деструктора, если Storage == 0
virtual void Free(void);
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Возвращает число дочерних компонент
size_t GetNumComponents(void) const;

// Возвращает полное число дочерних компонент
// (включая все компоненты дочерних компонент)
size_t GetNumAllComponents(void) const;

// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по короткому Id 'id'
virtual NAContainer* GetComponent(const UId &id) const;

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по короткому имени 'name'
NAContainer* GetComponent(const NameT &name) const;

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по ДЛИННОМУ Id 'id'
NAContainer* GetComponentL(const ULongId &id) const;

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по ДЛИННОМУ имени 'name'
NAContainer* GetComponentL(const NameT &name) const;

// Возвращает указатель на дочерний компонент, хранимый в этом
// объекте по порядковому индеку в списке компонент
// Метод возвращает 0, если индекс выходит за границы массива
NAContainer* GetComponentByIndex(size_t index) const;

// Добавляет дочерний компонент в этот объект
// Возвращает его Id или ForbiddenId если добавление неудачно
// Может быть передан указатель на локальную переменную
virtual UId AddComponent(NAContainer* comp, RDK::UIPointer* pointer=0);

// Удаляет дочерний компонент из этого объекта.
// Удаляемый компонент должен содержаться именно в этом объекте.
// Таким образом 'id' - должно быть коротким Id
// удаляемого объекта
// Если 'canfree' == true - предпринимается попытка вернуть объект в хранилище
// или удалить его. Иначе объект сохраняется в хранилище в состоянии занят
// либо повисает, если хранилище не установлено
virtual bool DelComponent(const UId &id, bool canfree=true);

// Удаляет дочерний компонент из этого объекта.
// Удаляемый компонент должен содержаться именно в этом объекте.
// Таким образом 'name' - должно быть коротким именем
// удаляемого объекта
// Если 'canfree' == true - предпринимается попытка вернуть объект в хранилище
// или удалить его. Иначе объект сохраняется в хранилище в состоянии занят
// либо повисает, если хранилище не установлено
bool DelComponent(const NameT &name, bool canfree=true);

// Принудительно удаляет все дочерние компоненты
void DelAllComponents(void);

// Возвращает список имен и Id компонент, содержащихся непосредственно
// в этом объекте
const map<NameT,UId>& GetComponentsList(void) const;

// Копирует все компоненты этого объекта в объект 'comp', если возможно
// Если хранилище stor != 0 то используется оно
virtual bool CopyComponents(NAContainer* comp, NStorage* stor=0) const;
// --------------------------


// ----------------------
// Методы управления коммуникационными компонентами
// ----------------------
public:
// Возвращает список длинных идентификаторов всех коннекторов сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// коннекторы будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех коннекторов включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы коннекторов только этой сети
// Предварительная очистка буфера не производится.
virtual RDK::ULongIdVector& GetConnectorsList(RDK::ULongIdVector &buffer,
						  int sublevel=-1, NAContainer *ownerlevel=0);

// Возвращает список длинных идентификаторов всех элементов сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// элементы будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех элементов включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы элементов только этой сети
// Предварительная очистка буфера не производится.
virtual RDK::ULongIdVector& GetItemsList(RDK::ULongIdVector &buffer,
							int sublevel=-1, NAContainer *ownerlevel=0);

// Возвращает список длинных идентификаторов всех подсетей сети.
// 'sublevel' опеределяет число уровней вложенности подсетей для которых
// подсети будут добавлены в список.
// если 'sublevel' == -1, то возвращает идентификаторы всех подсетей включая
// все вложенные сети.
// если 'sublevel' == 0, то возвращает идентификаторы подсетей только этой сети
// Предварительная очистка буфера не производится.
virtual RDK::ULongIdVector& GetNetsList(RDK::ULongIdVector &buffer,
							int sublevel=-1, NAContainer *ownerlevel=0);
// ----------------------

// --------------------------
// Методы доступа к параметрам
// --------------------------
// --------------------------

// --------------------------
// Методы доступа к переменным состояния
// --------------------------
// --------------------------

// --------------------------
// Методы управления текущим состоянием
// --------------------------
// Сохраняет объект в дерево
bool Save(RDK::UClassRegistry &buffer);

// Загружает объект из дерева
// Для создания компонент используется
// хранилище этого объекта или storage, если он не 0
// Если никакое хранилище не задано, то не делает ничего
// Если флаг paramsonly == true то только обновляет данные параметров
// для компонента и всех его уже существующих дочерних компонент
bool Load(RDK::UClassRegistry &buffer, NStorage *storage=0, bool paramsonly=false);

// Сохраняет состояние объекта в дерево
bool SaveState(RDK::UClassRegistry &buffer);

// Загружает состояние объекта из дерева
bool LoadState(RDK::UClassRegistry &buffer);
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool Default(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool Build(void);

// Сброс процесса счета без потери настроек
virtual bool Reset(void);

// Выполняет расчет этого объекта
virtual bool Calculate(void);
// --------------------------

// --------------------------
// Скрытые методы управления контроллерами интерфейса
// Удаление контроллеров лежит на вызывающем модуле
// --------------------------
protected:
// Добавляет новый контроллер
bool AddController(NController *controller, bool forchilds=false);

// Удаляет контроллер из списка
bool DelController(NController *controller, bool forchilds=false);

// Удаляет все контроллеры
bool DelAllControllers(bool forchilds=false);

// Инициирует отключение всех контроллеров
bool UnLinkAllControllers(bool forchilds=false);

// Проверяет, существует ли контроллер в списке
bool CheckController(NController *controller) const;

// Возвращает число контроллеров
bool GetNumControllers(void) const;

// Возвращает контроллер по индексу
NController* GetController(int index);
// --------------------------

protected:
// --------------------------
// Скрытые методы управления свойствами
// --------------------------
// Обновляет таблицу соответствий компонент заменяя 'oldname'
// имя компонента на 'newname'
bool ModifyLookupComponent(const NameT &oldname, const NameT newname);

// Обновляет таблицу соответствий компонент устанавливая Id 'id'
// для компонента с именем 'name'
void SetLookupComponent(const NameT &name, const UId &id);

// Обновляет таблицу соответствий компонент удаляя запись
// компонента с именем 'name'
void DelLookupComponent(const NameT &name);
// --------------------------

// --------------------------
// Скрытые методы управления параметрами
// --------------------------
public:
// Добавляет параметр с именем 'name' в таблицу соотвествий
// параметров и назначает ему корректный индекс
// Должна вызываться в конструкторах классов
UId AddLookupParameter(const NameT &name,UIProperty &property);

protected:
// Удаляет параметр с именем 'name' из таблицы соотвествий
// параметров
bool DelLookupParameter(const NameT &name);

// Возвращает полное имя параметра без префикса NMSDK, и суффикса '*'
NameT GetParameterLongName(const UIProperty &property) const;
// --------------------------

// --------------------------
// Скрытые методы управления состоянием
// --------------------------
public:
// Добавляет переменную состояния с именем 'name' в таблицу соотвествий
// параметров и назначает ей корректный индекс
// Должна вызываться в конструкторах классов
UId AddLookupState(const NameT &name,UIProperty &property);

protected:
// Удаляет переменную состояния с именем 'name' из таблицы соотвествий
bool DelLookupState(const NameT &name);

// Возвращает полное имя переменной состояния без префикса NMSDK, и суффикса '*'
NameT GetStateLongName(const UIProperty &property) const;
// --------------------------

// --------------------------
// Скрытые методы управления локальными указателями
// --------------------------
public:
// Добавляет указатель с именем 'name' в таблицу соотвествий
// параметров и назначает ей корректный индекс
// Должна вызываться в конструкторах классов
UId AddLookupPointer(RDK::UIPointer &pointer);

protected:
// Удаляет указатель с ID 'id' из таблицы соотвествий
bool DelLookupPointer(const UId &id);

// Возвращает полное имя указателя без префикса NMSDK, и суффикса '*'
NameT GetPointerLongName(const RDK::UIPointer &property) const;

// Осуществляет поиск в таблице указателя, соответствующего заданному источнику
map<UId,RDK::UIPointer*>::const_iterator FindLookupPointer(const NAContainer *source) const;
// --------------------------

// --------------------------
// Скрытые методы управления таблицей компонент
// --------------------------
// Добавляет компонент 'comp' в таблицу компонент
void AddComponentTable(NAContainer *comp, RDK::UIPointer* pointer=0);

// Удаляет компонент 'comp' из таблицы компонент
void DelComponentTable(NAContainer *comp);
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
protected:
// Удаляет компонент comp
// Метод предполагает, что компонент принадлежит объекту
bool DelComponent(NAContainer* comp, bool canfree);

// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
// Может быть передан указатель на локальную переменную
virtual bool AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer=0);

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
virtual bool ADelComponent(UEPtr<UAContainer> comp);
// --------------------------
};            */
							   /*
class NAConnector: public NAContainer
{
friend class NAItem;
friend class NADItem;
private: // Хранилище связей
// Список указателей на подключенные элементы сети
CItemListT CItemList;

protected: // Символические имена входов
// Список символических ссылок на входы <имя ссылки, индекс входа>
map<NameT, size_t> InputSymLinks;

public: // Общедоступные свойства
// Число доступных входов
//UVProperty<size_t, NAConnector> NumInputs;
UVLProperty<size_t, NAConnector> NumInputs;

// Признак включения/выключения режима автоматического увеличения числа входов
// при подключении нового item.
RDK::ULProperty<bool, NAContainer> AutoNumInputs;
//UProperty<bool, NAConnector> AutoNumInputs;

protected: // Переменные быстрого доступа к даннным входов. Read only!
// Число подключенных элементов item
size_t NumInputs;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NAConnector(void);
virtual ~NAConnector(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;
// --------------------------

// --------------------------
// Методы доступа к данным
// --------------------------
// Возвращает подключенный к этому коннектору объект по индексу
CItemT GetCItem(int c_index) const;

// Возвращает пару индексов <выход, вход> подключения этого item или <-1,-1>
// если такая связь отсутствует
pair<int,int> GetCItemIndexes(const NAItem *item) const;
// --------------------------

// --------------------------
// Методы управления символическими ссылками
// --------------------------
// Возвращает число символических ссылок на входы
size_t GetNumInputSymLinks(void) const;

// Возвращает индекс входа по символической ссылке
size_t GetInputSymLink(const string &name) const;

// Добавляет новую символическую ссылку на вход
// Возвращает false если такое имя уже существует
bool AddInputSymLink(const string &name, size_t index);

// Удаляет символическую ссылку на вход по имени
void DelInputSymLink(const string &name);

// Удаляет все символические ссылки на заданный вход
void DelInputSymLink(size_t index);

// Удаляет все символические ссылки
void DelInputSymLinks(void);

// Возвращает список имен ссылок
void GetInputSymLinksList(vector<NameT> &buffer) const;

// Копирует символические ссылки в объект target
bool CopyInputSymLinks(NAConnector *target) const;
// --------------------------

// ----------------------
// Коммуникационные методы
// ----------------------
protected:
// Устанавливает связь с элементом сети 'na' со входом по индексу index.
// Возвращает false если na уже подключен к этому входу.
// При успешном подключении c_index содержит реальный индекс подключенного входа
virtual bool ConnectToItem(NAItem *na, int i_index, int &c_index);

// Разрывает связь с элементом сети 'na'
virtual void DisconnectFromItem(NAItem *na);

// Разрывает связь с элементом сети подключенным ко входу 'index'
virtual void DisconnectFromIndex(int c_index);

// Выполняет действия после физически установленой связи
virtual bool AConnectToItem(NAItem *na);

// Выполняет действия после физически разорваной связи
virtual void ADisconnectFromItem(NAItem *na);

public:
// Разрывает все текущие связи
virtual void DisconnectAllItems(void);

// Разрывает все связи объекта
// исключая его внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
virtual void DisconnectByObject(const NAContainer *brklevel);

public:
// Активирует этот коннектор (посылает сообщение 'есть импульс'
// этому коннектору).
virtual void Activate(NAItem *na);

// Возвращает список подключений
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;
// ----------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
protected:
// Возвращает число подключенных элементов item
size_t GetNumInputs(void) const;

// Устанавливает число подключенных элементов item
bool SetNumInputs(size_t value);
// --------------------------

// --------------------------
// Скрытые методы управления символическими ссылками
// --------------------------
protected:
// Возвращает число символических ссылок
size_t GetNumSymLinks(const map<NameT, size_t> &symlinks) const;

// Возвращает индекс по символической ссылке
size_t GetSymLink(const string &name, const map<NameT, size_t> &symlinks) const;

// Добавляет новую символическую ссылку
// Возвращает false если такое имя уже существует
bool AddSymLink(const string &name, size_t index, map<NameT, size_t> &symlinks);

// Удаляет символическую ссылку по имени
void DelSymLink(const string &name, map<NameT, size_t> &symlinks);

// Удаляет все символические ссылки по индексу
void DelSymLink(size_t index, map<NameT, size_t> &symlinks);

// Удаляет все символические ссылки
void DelSymLinks(map<NameT, size_t> &symlinks);

// Возвращает весь список ссылок
void GetSymLinksList(vector<NameT> &buffer, const map<NameT, size_t> &symlinks) const;

// Копирует символические ссылки в объект target
bool CopySymLinks(NAConnector *target, const map<NameT, size_t> &symlinks) const;
// --------------------------

// --------------------------
// Методы управления счетом
// --------------------------
public:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool Default(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool Build(void);
// --------------------------

};

class NAItem: public NAConnector
{
private: // Основные свойства
// Список коннекторов подключенных к выходам этого объекта
vector<vector<NAConnector*> > AssociatedConnectors;

public: // Общедоступные свойства
// Число выходов
UVLProperty<size_t, NAItem> NumOutputs;
//UVProperty<size_t, NAItem> NumOutputs;


protected: // Временные переменные. Read Only!
// Указатель на первый элемент списка подключенных коннекторов
vector<NAConnector**> PAssociatedConnectors;

// Число элементов списка подключенных коннекторов
vector<size_t> NumAConnectors;

protected: // Переменные быстрого доступа к даннным выходов. Read only!
// Число выходов
size_t CNumOutputs;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NAItem(void);
virtual ~NAItem(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Возвращает число подключенных элементов item
size_t GetNumOutputs(void) const;

// Устанавливает число подключенных элементов item
bool SetNumOutputs(size_t value);
// --------------------------


public:
// ----------------------
// Коммуникационные методы
// ----------------------
// Устанавливает связь с коннектором 'c'
virtual bool Connect(NAConnector *c, int i_index, int c_index=-1);

// Разрывает связь выхода этого объекта с коннектором 'c'
virtual void Disconnect(NAConnector *c);

// Возвращает текущее число соединений для заданного выхода.
size_t GetNumAConnectors(int index) const;

// Разрывает связь выхода этого объекта с коннектором по Id 'id'.
virtual bool Disconnect(const UId &id);

// Разрывает связь выхода этого объекта со всеми
// подключенными коннекторами.
void DisconnectAll(void);

// Разрывает все связи объекта
// исключая его внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
virtual void DisconnectBy(const NAContainer *brklevel);

// Переустанавливает все связи этого item со всеми connectors которые получают
// данные от этого item
virtual void BuildLinks(void);

// Возвращает указатель на коннектор из списка подключений
// по Id 'id'.
const NAConnector* GetAConnector(const UId &id, int index) const;

// Возвращает  коннектор из списка подключений.
const NAConnector* GetAConnectorByIndex(int output, int index) const;

// Возвращает список подключений
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;

// Возвращает список подключений этого компонента и всех дочерних компонент
// к заданному компоненту comp и всем его дочерним компонентам
LinksListT& GetFullItemLinks(LinksListT &linkslist, const NAItem *comp,
							const NAContainer *netlevel) const;
// ----------------------

public:
// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool Default(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool Build(void);

// Активирует все коннекторы, подключенные к выходу этого объекта.
virtual void ActivateAll(void);
// --------------------------
};

class NADItem: public NAItem
{
friend class NIOData;
private: // Хранилище выходных данных
// Вектор выходных данных
vector<NIOData> Output;

private: // Хранилище входных связей
// Массив указателей на вектора входов
vector<const NIOData*> Input;

// Массив размеров векторов входов
vector<size_t> InputSize;

public: // Общедоступные свойства
// Размер выходных векторов
//UVProperty<vector<size_t>, NADItem> OutputSize;
UVLProperty<vector<size_t>, NADItem> OutputSize;

// Размер единичного данного вектора выходов в байтах
UVLProperty<vector<size_t>, NADItem> DataOutputSize;
//UVProperty<vector<size_t>, NADItem> DataOutputSize;

protected: // Переменные быстрого доступа к даннным входов. Read only!
// Указатель на первый элемент массива указателей на вектора входов
const NIOData** PInputData;

// Указатель на первый элемент массива размеров векторов входов
size_t* PInputDataSize;

// Размер массива векторов входов
//size_t NumInputs;

// Суммарное число всех входов
size_t FullInputSize;

// Минимальный размер вектора входов
size_t MinInputDataSize;

// Максимальный размер вектора входов
size_t MaxInputSize;

protected: // Переменные быстрого доступа к даннным выходов. Read only!
// Указатель на первый элемент массива указателей на вектора входов
const NIOData* POutputData;


public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NADItem(void);
virtual ~NADItem(void);
// --------------------------

// --------------------------
// Методы доступа к данным
// --------------------------
// Возвращает вектор выходных данных
inline const NIOData& GetOutputData(int index) const
{ return POutputData[index]; };

// Возвращает указатель на вектор входов Input по указателю на item
// Возвращает 0 если citem == 0 или не найден в списке подключений
const NIOData* GetInputData(NAItem *citem) const;

// Возвращает указатель на вектор входов Input по индексу
// Не проверяет индекс на корректность
const NIOData* GetInputData(size_t index) const;

// Возвращает размер вектора входов Input по индексу
// Не проверяет индекс на корректность
size_t GetInputSize(size_t index) const;

// Возвращает суммарный размер всех векторов входов
size_t GetFullInputSize(void) const;
// --------------------------

// ----------------------
// Методы управления выходными данными
// ----------------------
// Устанавливает размер вектора выходных данных
size_t GetOutputDataSize(int index) const;
virtual bool SetOutputDataSize(int index, size_t size, bool nobuild=false);

// Возвращает размер вектора выходных данных в байтах
inline size_t GetByteOutputSize(int index) const
{ return Output[index].ByteSize; };

// Устанавливает размер единичного данного вектора выходных данных в байтах
size_t GetDataOutputSize(int index) const
{ return Output[index].DataSize; };
bool SetDataOutputSize(int index, size_t size);

// Заполняет заданный выходной вектор данными
void FillOutputData(int index, const void *data=0);

// Заполняет все выходные вектора заданными данными
void FillOutputData(const void *data=0);
// ----------------------

// ----------------------
// Методы доступа к системным свойствам
// ----------------------
protected:
// Размер выходных векторов
vector<size_t> GetVOutputSize(void) const;
bool SetVOutputSize(const vector<size_t> value);

// Размер единичного данного вектора выходов в байтах
vector<size_t> GetVDataOutputSize(void) const;
bool SetVDataOutputSize(const vector<size_t> value);
// ----------------------

// ----------------------
// Коммуникационные методы
// ----------------------
protected:
// Устанавливает связь с элементом сети 'na' со входом по индексу index.
// Возвращает false если na уже подключен к этому входу.
// При успешном подключении c_index содержит реальный индекс подключенного входа
virtual bool ConnectToItem(NAItem *na, int i_index, int &c_index);

// Разрывает связь с элементом сети подключенным ко входу 'index'
virtual void DisconnectFromIndex(int c_index);
// ----------------------

// --------------------------
// Методы управления счетом
// --------------------------
public:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool Default(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool Build(void);

// Сброс процесса счета без потери настроек
virtual bool Reset(void);
// --------------------------

// ----------------------
// Вспомогательные методы
// ----------------------
private:
// Обновляет указатели на массивы входов и выходов
void UpdatePointers(void);

// Вычисляет минимальный и максимальный размер векторов входов
void CalcMinMaxInputsSize(void);
// ----------------------
};


class NANet: public NADItem
{
protected: // Основные свойства

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NANet(void);
virtual ~NANet(void);
// --------------------------

// --------------------------
// Методы доступа к свойствам
// --------------------------
LinksListT& GetLinks(LinksListT &linkslist, const NAContainer *netlevel) const;
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Копирует этот объект в 'target' с сохранением всех компонент
// и значений параметров
// Если 'stor' == 0, то создание объектов осуществляется
// в том же хранилище где располагается этот объект
virtual bool Copy(NAContainer *target, NStorage *stor=0, bool copystate=false) const;
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
virtual bool CheckComponentType(UEPtr<NAContainer> comp) const;
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
protected:
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
virtual bool AAddComponent(UEPtr<UAContainer> comp, RDK::UIPointer* pointer=0);

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
virtual bool ADelComponent(UEPtr<UAContainer> comp);
// --------------------------

// ----------------------
// Методы управления связями
// ----------------------
public:
// Устанавливает новую связь между выходом элемента сети
// 'item' и коннектором 'connector'
virtual bool CreateLink(const LinkSideT &itemid, const LinkSideT &connectorid);

// Устанавливает новую связь между выходом элемента сети
// 'item' и коннектором 'connector'
virtual bool CreateLink(const NameT &item, int item_index,
						const NameT &connector, int connector_index=-1);

// Устанавливает все связи из массива 'linkslist'
virtual bool CreateLinks(const LinksListT &linkslist);

// Разрывает все связи с выходом элемента сети, если
// 'id' - есть Id элемента сети.
// Иначе, если 'id' - Id коннектора, то метод разрывает
// связи этого коннектора
virtual bool BreakLink(const LinkSideT &id);

// Разрывает связь между выходом элемента сети, 'itemid'
// и коннектором 'connectorid'
virtual bool BreakLink(const LinkSideT &itemid, const LinkSideT &connectorid);

// Разрывает связь между выходом элемента сети, 'itemid'
// и коннектором 'connectorid'
virtual bool BreakLink(const NameT &itemname, int item_index,
						const NameT &connectorname, int connector_index);

// Разрывает все связи сети
// исключая ее внутренние связи и обратные связи
// brklevel - объект, относительно которого связи считаются внутренними
virtual void BreakLinks(const NAContainer* brklevel);

// Разрывает заданные связи сети
virtual bool BreakLinks(const LinksListT &linkslist);

// Разрывает все внутренние связи сети.
virtual void BreakLinks(void);
// ----------------------

// --------------------------
// Скрытые методы доступа к свойствам
// --------------------------
protected:
LinksListT& GetLinks(const NAContainer *cont, LinksListT &linkslist, const NAContainer *netlevel) const;
// --------------------------


};
*/
}
#endif

