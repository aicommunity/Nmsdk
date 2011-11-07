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

#ifndef NNEURON_H
#define NNEURON_H

#include "NNet.h"

namespace NMSDK {

class NNeuron: public NNet
{
protected: // Основные свойства

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNeuron(void);
virtual ~NNeuron(void);
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NNeuron* New(void);
// --------------------------
};

}

#endif



