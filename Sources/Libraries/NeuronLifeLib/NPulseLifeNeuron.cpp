// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NPULSE_LIFE_NEURON_CPP
#define NPULSE_LIFE_NEURON_CPP

#include "NPulseLifeNeuron.h"

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseLifeNeuron::NPulseLifeNeuron(void)
//: NPulseNeuron(name),
 : SummaryPosGd("SummaryPosGd",this),
  SummaryPosGs("SummaryPosGs",this),
  SummaryPosG("SummaryPosG",this),
  SummaryNegGd("SummaryNegGd",this),
  SummaryNegGs("SummaryNegGs",this),
  SummaryNegG("SummaryNegG",this)
{
 NeuronLife=0;

  fstream stream;
}

NPulseLifeNeuron::~NPulseLifeNeuron(void)
{
}
// --------------------------

// --------------------------
// Методы доступа к временным переменным
// --------------------------
// Возвращает указатель на модель жизнеобеспечения
NNeuronLife* NPulseLifeNeuron::GetNeuronLife(void)
{
 return NeuronLife;
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NPulseLifeNeuron* NPulseLifeNeuron::New(void)
{
 return new NPulseLifeNeuron;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NPulseLifeNeuron::CheckComponentType(UEPtr<NAContainer> comp) const
{
 if(NPulseNeuron::CheckComponentType(comp) || dynamic_pointer_cast<NNeuronLife>(comp))
  return true;

 return false;
}
// --------------------------

// --------------------------
// Скрытые методы управления компонентами
// --------------------------
// Выполняет завершающие пользовательские действия
// при добавлении дочернего компонента в этот объект
// Метод будет вызван только если comp был
// успешно добавлен в список компонент
bool NPulseLifeNeuron::AAddComponent(UEPtr<UAContainer> comp, UEPtr<UIPointer> pointer)
{
 UEPtr<NNeuronLife> temp=dynamic_pointer_cast<NNeuronLife>(comp);

 if(temp && NeuronLife)
  return false;

 if(!NPulseNeuron::AAddComponent(comp,pointer))
  return false;

 if(temp)
  NeuronLife=temp;

 return true;
}

// Выполняет предварительные пользовательские действия
// при удалении дочернего компонента из этого объекта
// Метод будет вызван только если comp
// существует в списке компонент
bool NPulseLifeNeuron::ADelComponent(UEPtr<UAContainer> comp)
{
 if(comp == NeuronLife)
  NeuronLife=0;

 return NPulseNeuron::ADelComponent(comp);
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NPulseLifeNeuron::ADefault(void)
{
 if(!NPulseNeuron::ADefault())
  return false;

 SetNumOutputs(NumOutputs+12);
 for(int i=NumOutputs-12;i<NumOutputs;i++)
  SetOutputDataSize(i,1);

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NPulseLifeNeuron::ABuild(void)
{
 if(!NPulseNeuron::ABuild())
  return false;

 return true;
}

// Сброс процесса счета.
bool NPulseLifeNeuron::AReset(void)
{
 if(!NPulseNeuron::AReset())
  return false;

 // Суммарный динамический вес
 SummaryPosGd=0;
 SummaryNegGd=0;

 // Суммарный статический вес
 SummaryPosGs=0;
 SummaryNegGs=0;

 // Суммарный результирующий вес
 SummaryPosG=0;
 SummaryNegG=0;


 return true;
}

// Выполняет расчет этого объекта
bool NPulseLifeNeuron::ACalculate(void)
{
 if(/*!LTZone ||*/ !NeuronLife)
  return false;

 if(!NPulseNeuron::ACalculate())
  return false;

 LTZone->Threshold=NeuronLife->GetOutputData(0).Double[3];

 // Суммарный динамический вес возбуждающей связи
 POutputData[3].Double[0]=SummaryPosGd;
 if(POutputData[1].Double[0] != 0)
  POutputData[4].Double[0]=SummaryPosGd/POutputData[1].Double[0];
 else
  POutputData[4].Double[0]=0;
 SummaryPosGd=0;

 // Суммарный статический вес возбуждающей связи
 POutputData[5].Double[0]=SummaryPosGs;
 if(POutputData[1].Double[0] != 0)
  POutputData[6].Double[0]=SummaryPosGs/POutputData[1].Double[0];
 else
  POutputData[6].Double[0]=0;
 SummaryPosGs=0;

 // Суммарный результирующий вес возбуждающей связи
 POutputData[7].Double[0]=SummaryPosG;
 if(POutputData[1].Double[0] != 0)
  POutputData[8].Double[0]=SummaryPosG/POutputData[1].Double[0];
 else
  POutputData[8].Double[0]=0;
 SummaryPosG=0;

 // Суммарный динамический вес тормозной связи
 POutputData[9].Double[0]=SummaryNegGd;
 if(POutputData[2].Double[0] != 0)
  POutputData[10].Double[0]=SummaryNegGd/POutputData[2].Double[0];
 else
  POutputData[10].Double[0]=0;
 SummaryNegGd=0;

 // Суммарный статический вес тормозной связи
 POutputData[11].Double[0]=SummaryNegGs;
 if(POutputData[2].Double[0] != 0)
  POutputData[12].Double[0]=SummaryNegGs/POutputData[2].Double[0];
 else
  POutputData[12].Double[0]=0;
 SummaryNegGs=0;

 // Суммарный результирующий вес тормозной связи
 POutputData[13].Double[0]=SummaryNegG;
 if(POutputData[2].Double[0] != 0)
  POutputData[14].Double[0]=SummaryNegG/POutputData[2].Double[0];
 else
  POutputData[14].Double[0]=0;
 SummaryNegG=0;

 return true;
}
// --------------------------

}
#endif
