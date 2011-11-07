/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NNeuronLifeLibraryH
#define NNeuronLifeLibraryH

#include "../../Kernel/NLibrary.h"

#include "NPulseLifeNeuron.h"
#include "NNeuronLife.h"
#include "NLifeNet.h"
#include "../MathLib/NMathLibrary.h"


namespace NMSDK {

class NNeuronLifeLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NNeuronLifeLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};    

extern NNeuronLifeLibrary NeuronLifeLibrary;

}


#endif
