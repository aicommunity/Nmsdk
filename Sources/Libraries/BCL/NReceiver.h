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

#ifndef NRECEIVER_H
#define NRECEIVER_H

#include "../../Kernel/NBios.h"

namespace NMSDK {

class NReceiver: public NADItem//NAConnector
{
protected: // Основные свойства

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NReceiver(void);
virtual ~NReceiver(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NReceiver* New(void);
// --------------------------
};

}

#endif



