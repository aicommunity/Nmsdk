/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.2.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NPulseNeuronLibraryH
#define NPulseNeuronLibraryH

#include "../../Kernel/NLibrary.h"
#include "../PulseLib/NAfferentNeuron.h"
#include "../PulseLib/NPulseNeuron.h"
#include "../PulseLib/NEyeMuscle.h"
#include "../PulseLib/NMuscle.h"
#include "../PulseLib/NPulseChannel.h"
#include "../PulseLib/NPulseLTZone.h"
#include "../PulseLib/NPulseMembrane.h"
#include "../PulseLib/NPulseSynapse.h"
#include "../PulseLib/NPulseHebbSynapse.h"
#include "../NeuronLifeLib/NNeuronLifeLibrary.h"

namespace NMSDK {

class NPulseNeuronLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseNeuronLibrary(void);
// --------------------------

// --------------------------
// Методы создания составных моделей
// --------------------------
// Метод формирования модели простого импульсного нейрона
NPulseNeuron* CreateSimplePulseNeuron(NStorage *storage, const string &neuronclass, const string &membraneclass, int num_membranes,
                    int num_stimulates, int num_arresting, int dendrite_length=1);

// Метод формирования модели простого импульсного нейрона с синапсами хебба
NPulseNeuron* CreateSimplePulseHebbNeuron(NStorage *storage, const string &neuronclass, int num_membranes,
                    int num_stimulates, int num_arresting, int dendrite_length=1);

// Метод формирования модели афферентного нейрона
NAfferentNeuron* CreateAfferentNeuron(NStorage *storage, int num_membranes);
// --------------------------


// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};    

extern NPulseNeuronLibrary PulseNeuronLibrary;

}


#endif
