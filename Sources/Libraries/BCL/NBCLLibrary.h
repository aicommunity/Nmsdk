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

#ifndef NBCLLibraryH
#define NBCLLibraryH

#include "../../Kernel/NLibrary.h"

#include "NItem.h"
#include "NConnector.h"
#include "NNet.h"
#include "NModel.h"
#include "NNeuron.h"
#include "NReceiver.h"
#include "NSource.h"

namespace NMSDK {

class NBCLLibrary: public NLibrary
{
public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NBCLLibrary(void);
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};          

extern NBCLLibrary BCLLibrary;

}


#endif
