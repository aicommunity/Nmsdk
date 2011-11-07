// ===========================================================
// Version:        3.0.3
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

#ifndef NNET_H
#define NNET_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NNet: public NANet
{
public: // Типы данных
typedef vector<vector<vector<vector<vector<UId> > > > > NNetStructure;
// Расстояние организации связей
RDK::ULProperty<real, NANet> LinkDistance;

public: // Общедоступные свойства
// Класс компонента по умолчанию в хранилище
RDK::ULProperty<UId,NNet> DefaultComponentClassId;

// Структура сети
// 0 - Произвольная структура
// 1 - многослойная сеть
// 2 - рецептивная многослойная сеть
RDK::ULProperty<int,NNet> NetType;

// Число слоев
RDK::ULProperty<size_t,NNet> NumLayers;

// Ширина слоя
RDK::ULProperty<size_t,NNet> LayerWidth;

// Глубина слоя
RDK::ULProperty<size_t,NNet> LayerHeight;

// Ширина рецептивного поля
RDK::ULProperty<size_t,NNet> ReceptorFieldWidth;

// Глубина рецептивного поля
RDK::ULProperty<size_t,NNet> ReceptorFieldHeight;

// Способ организации связей сети
// 0 - нет
// 1 - межслойные - все со всеми между слоями с расстоянием 'LinkDistance'
// 2 - межслойные - рецептивные поля между соседними слоями
// 3 - все со всеми в заданном радиусе 'LinkDistance'
RDK::ULProperty<size_t, NNet> LinksOrganizationMode;

protected: // Данные
// Структура сети
RDK::UCLStateProperty<NNetStructure,NNet> NetStructure;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNet(void);
virtual ~NNet(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NNet* New(void);
// --------------------------

// --------------------------
// Методы управления структурой сети
// --------------------------
// Создает новый экземпляр компонента по умолчанию и добавляет его в сеть
NAContainer* InsertComponent(void);
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

// Сброс процесса счета без потери настроек
virtual bool Reset(void);
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Собирает структуру сети
virtual bool BuildNetStructure(void);

// Собирает структуру слоя 'layer'
virtual bool BuildLayerStructure(size_t layer);

// Собирает структуру рецептивного поля слоя 'layer', с координатами
// 'i' по ширине, 'j' по глубине
virtual bool BuildReceptorField(size_t layer, size_t i, size_t j);

// Организует связи сети
virtual bool BuildLinksStructure(void);

// Организует связи компонента слоя 'layer', с координатами
// 'i' по ширине, 'j' по глубине
virtual bool BuildLinksStructure(size_t layer, size_t i, size_t j);

// Способ организации связей сети, определяемый LinksOrganizationMode
// 0 - нет
virtual bool BuildLinksStructureNone(size_t layer, size_t i, size_t j);

// Способ организации связей сети, определяемый LinksOrganizationMode
// 1 - межслойные - все со всеми между слоями с расстоянием 'LinkDistance'
virtual bool BuildLinksStructureMultilayer(size_t layer, size_t i, size_t j);

// Способ организации связей сети, определяемый LinksOrganizationMode
// 2 - межслойные - рецептивные поля между соседними слоями
virtual bool BuildLinksStructureReceptor(size_t layer, size_t i, size_t j);

// Способ организации связей сети, определяемый LinksOrganizationMode
// 3 - все со всеми в заданном радиусе 'LinkDistance'
virtual bool BuildLinksStructureFullRadius(size_t layer, size_t i, size_t j);
// --------------------------
};

}
#endif


