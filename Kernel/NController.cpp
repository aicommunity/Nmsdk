#ifndef NCONTROLLER_CPP
#define NCONTROLLER_CPP

#include <algorithm>
#include "NController.h"
#include "../Kernel/NBios.h"

namespace NMSDK {
/*
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NController::NController(void)
{
}

NController::~NController(void)
{
 UnLinkAll();
}
// --------------------------

// --------------------------
// Методы управления параметрами
// --------------------------
// Флаг разрешения обновления интерфейса
bool NController::IsEnabled(void) const
{
 return Enabled;
}

bool NController::IsEnabled(bool value)
{
 if(Enabled == value)
  return true;

 Enabled=value;
 return true;
}
// --------------------------

// --------------------------
// Методы управления данными
// --------------------------
// Возвращает число компонент к которым подключен контроллер
size_t NController::GetNumComponents(void) const
{
 return Components.size();
}

// Возвращает компонент к которому подключен контроллер по индексу
NAContainer* NController::GetComponents(size_t index)
{
 return Components[index];
}

// Возвращает индекс компонента по указателю
int NController::FindComponent(NAContainer* component) const
{
 vector<NAContainer*>::const_iterator I=find(Components.begin(),Components.end(),component);

 if(I != Components.end())
  return I-Components.begin();

 return -1;
}
// --------------------------

// --------------------------
// Методы управления интерфейсом
// --------------------------
// Связывает интерфейс с компонентом
bool NController::Link(NAContainer* component, bool forchilds)
{
 if(find(Components.begin(),Components.end(),component) != Components.end())
  return true;

 Components.push_back(component);
 component->AddController(this,forchilds);

 if(!ALink(component))
 {
  component->DelController(this,forchilds);
  Components.erase(Components.begin()+(Components.size()-1));
  return false;
 }

 return true;
}

// Отвязывает интерфейс от компонента
bool NController::UnLink(int index, bool forchilds)
{
 if(index<0 || index> int(Components.size()))
  return false;

 if(!AUnLink(index,forchilds))
  return false;

 Components[index]->DelController(this,forchilds);
 Components.erase(Components.begin()+index);
 return true;
}

bool NController::UnLink(NAContainer* component, bool forchilds)
{
 int index=FindComponent(component);

 if(index < 0)
  return true;

 return UnLink(index, forchilds);
}

bool NController::UnLinkAll(bool forchilds)
{
 bool res=true;
 while(Components.begin() != Components.end())
 {
  res &= UnLink(Components.size()-1,forchilds);
 }

 return res;
}


// Обновляет интерфейс
bool NController::Update(void)
{
 if(!Enabled)
  return true;

 return AUpdate();
}
// --------------------------
*/
}


#endif

