#ifndef NControllerH
#define NControllerH

#include "rdk.h"

namespace NMSDK {

//class NAContainer;
typedef RDK::UAContainer NAContainer;
typedef RDK::UController NController;

/*
class NController: public RDK::UModule
{
protected: // Параметры
// Флаг разрешения обновления интерфейса
bool Enabled;

protected: // Данные
// Указатель на компоненты
std::vector<NAContainer*> Components;

public:
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NController(void);
virtual ~NController(void);
// --------------------------

// --------------------------
// Методы управления параметрами
// --------------------------
// Флаг разрешения обновления интерфейса
bool IsEnabled(void) const;
bool IsEnabled(bool value);
// --------------------------

// --------------------------
// Методы управления данными
// --------------------------
// Возвращает число компонент к которым подключен контроллер
size_t GetNumComponents(void) const;

// Возвращает компонент к которому подключен контроллер по индексу
NAContainer* GetComponents(size_t index);

// Возвращает индекс компонента по указателю
int FindComponent(NAContainer* component) const;
// --------------------------

// --------------------------
// Методы управления интерфейсом
// --------------------------
public:
// Связывает интерфейс с компонентом
virtual bool Link(NAContainer* component, bool forchilds=false);

// Отвязывает интерфейс от компонента
virtual bool UnLink(int index, bool forchilds=false);
virtual bool UnLink(NAContainer* component, bool forchilds=false);
virtual bool UnLinkAll(bool forchilds=false);

// Обновляет интерфейс
virtual bool Update(void);
// --------------------------

// --------------------------
// Скрытые методы управления интерфейсом
// --------------------------
protected:
// Связывает интерфейс с компонентом
virtual bool ALink(NAContainer* component, bool forchilds=false)=0;

// Отвязывает интерфейс от компонента
virtual bool AUnLink(int index, bool forchilds=false)=0;

// Обновляет интерфейс
virtual bool AUpdate(void)=0;
// --------------------------
};
      */
}

#endif
