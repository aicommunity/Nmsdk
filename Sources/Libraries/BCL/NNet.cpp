// ===========================================================
// Version:        3.0.2
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

#ifndef NNET_CPP
#define NNET_CPP

#include "NNet.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNet::NNet(void)
//: NANet(name),
 : DefaultComponentClassId("DefaultComponentClassId",this),
  NetType("NetType",this),
  NumLayers("NumLayers",this),
  LayerWidth("LayerWidth",this),
  LayerHeight("LayerHeight",this),
  ReceptorFieldWidth("ReceptorFieldWidth",this),
  ReceptorFieldHeight("ReceptorFieldHeight",this),
  LinksOrganizationMode("LinkOrganizationMode",this),
  LinkDistance("LinkDistance",this),

  NetStructure("NetStructure",this)

{
}

NNet::~NNet(void)
{
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NNet* NNet::New(void)
{
 return new NNet;
}
// --------------------------

// --------------------------
// Методы управления структурой сети
// --------------------------
// Создает новый экземпляр компонента по умолчанию и добавляет его в сеть
NAContainer* NNet::InsertComponent(void)
{
 if(!Storage || DefaultComponentClassId == ForbiddenId)
  return 0;

 NAContainer *comp=static_cast<NAContainer*>(Storage->TakeObject(DefaultComponentClassId));
 if(!comp)
  return 0;

 if(AddComponent(comp) == ForbiddenId)
 {
  Storage->ReturnObject(comp);
  return 0;
 }

 return comp;
}
// --------------------------



// --------------------------
// Методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NNet::Default(void)
{
 if(!NANet::Default())
  return false;

 DefaultComponentClassId=ForbiddenId;
 NetType=0;
 NumLayers=1;
 LayerWidth=1;
 LayerHeight=1;
 ReceptorFieldWidth=1;
 ReceptorFieldHeight=1;
 LinksOrganizationMode=0;
 LinkDistance=1;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NNet::Build(void)
{
 if(!BuildNetStructure())
  return false;

 if(!BuildLinksStructure())
  return false;

 return NANet::Build();
}

// Сброс процесса счета без потери настроек
bool NNet::Reset(void)
{
 return NANet::Reset();
}
// --------------------------


// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Собирает структуру сети
bool NNet::BuildNetStructure(void)
{
/* switch(NetType.v)
 {
 case 0:
 break;

 case 1:
 case 2:
  if(DefaultComponentClassId == ForbiddenId)
   return true;

  NetStructure.v.resize(NumLayers.v);
  for(size_t i=0;i<NumLayers.v;i++)
  {
   NetStructure[i].resize(LayerWidth.v);
   for(size_t j=0;j<LayerWidth.v;j++)
   {
	NetStructure[i][j].resize(LayerHeight.v);
	for(size_t k=0;k<LayerHeight.v;k++)
	{
	 NetStructure[i][j][k].resize(ReceptorFieldWidth.v);
	 for(size_t n=0;n<ReceptorFieldWidth.v;n++)
	 {
	  NetStructure[i][j][k][n].resize(ReceptorFieldHeight.v);
	 }
	}
   }
  }

  for(size_t i=0;i<NumLayers.v;i++)
   if(!BuildLayerStructure(i))
    return false;
 break;
 }          */
 return true;
}

// Собирает структуру слоя 'layer'
bool NNet::BuildLayerStructure(size_t layer)
{
 for(size_t i=0;i<LayerWidth.v;i++)
  for(size_t j=0;j<LayerHeight.v;j++)
   if(!BuildReceptorField(layer,i,j))
    return false;

 return true;
}

// Собирает структуру рецептивного поля слоя 'layer', с координатами
// 'i' по ширине, 'j' по глубине
bool NNet::BuildReceptorField(size_t layer, size_t i, size_t j)
{
/* for(size_t n=0;n<ReceptorFieldWidth.v;n++)
  for(size_t m=0;m<ReceptorFieldHeight.v;m++)
  {
   if(!GetComponent(NetStructure[layer][i][j][n][m]))
   {
	NAContainer* comp=InsertComponent();
	if(!comp)
	 return false;

	NetStructure[layer][i][j][n][m]=comp->Id;
   }
  }*/
 return true;
}

// Организует связи сети
bool NNet::BuildLinksStructure(void)
{
 for(size_t k=0;k<NumLayers.v;k++)
 {
  for(size_t i=0;i<LayerWidth.v;i++)
   for(size_t j=0;j<LayerHeight.v;j++)
	if(!BuildLinksStructure(k, i, j))
	 return false;
 }
 return true;
}

// Организует связи компонента слоя 'layer', с координатами
// 'i' по ширине, 'j' по глубине
bool NNet::BuildLinksStructure(size_t layer, size_t i, size_t j)
{
 switch(LinksOrganizationMode)
 {
 case 0:
  return BuildLinksStructureNone(layer,i,j);
 case 1:
  return BuildLinksStructureMultilayer(layer,i,j);
 case 2:
  return BuildLinksStructureReceptor(layer,i,j);
 case 3:
  return BuildLinksStructureFullRadius(layer,i,j);
 }
 return false;
}

// Способ организации связей сети, определяемый LinksOrganizationMode
// 0 - нет
bool NNet::BuildLinksStructureNone(size_t layer, size_t i, size_t j)
{
 return true;
}

// Способ организации связей сети, определяемый LinksOrganizationMode
// 1 - межслойные - все со всеми между слоями с расстоянием 'LinkDistance'
bool NNet::BuildLinksStructureMultilayer(size_t layer, size_t i, size_t j)
{
 return false;
}

// Способ организации связей сети, определяемый LinksOrganizationMode
// 2 - межслойные - рецептивные поля между соседними слоями
bool NNet::BuildLinksStructureReceptor(size_t layer, size_t i, size_t j)
{
 return false;
}

// Способ организации связей сети, определяемый LinksOrganizationMode
// 3 - все со всеми в заданном радиусе 'LinkDistance'
bool NNet::BuildLinksStructureFullRadius(size_t layer, size_t i, size_t j)
{
 return false;
}
// --------------------------

}
#endif

