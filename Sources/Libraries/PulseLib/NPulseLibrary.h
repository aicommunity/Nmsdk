/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NPulseLibraryH
#define NPulseLibraryH

#include "../../Kernel/NLibrary.h"

#include "NAfferentNeuron.h"
#include "NEyeMuscle.h"
#include "NMuscle.h"
#include "NPulseChannel.h"
#include "NPulseLTZone.h"
#include "NPulseMembrane.h"
#include "NPulseNeuron.h"
#include "NPulseSynapse.h"
#include "NPulseHebbSynapse.h"
#include "../NeuronLifeLib/NPulseLifeNeuron.h"
#include "../NeuronLifeLib/NNeuronLife.h"
#include "../NeuronLifeLib/NLifeNet.h"


namespace NMSDK {

class NPulseLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};                  

extern NPulseLibrary PulseLibrary;

}


#endif
