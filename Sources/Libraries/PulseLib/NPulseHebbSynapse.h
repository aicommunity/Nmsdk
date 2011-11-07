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

#ifndef NPULSE_HEBB_SYNAPSE_H
#define NPULSE_HEBB_SYNAPSE_H

#include "../../Kernel/NBios.h"
#include "NPulseSynapse.h"


namespace NMSDK {

class NPulseHebbSynapse: public NPulseSynapse
{
public: // Общедоступные свойства
RDK::ULProperty<real,NPulseHebbSynapse> Min;
RDK::ULProperty<real,NPulseHebbSynapse> Mout;
RDK::ULProperty<real,NPulseHebbSynapse> Md;
RDK::UCLProperty<vector<real>,NPulseHebbSynapse> ActiveMs;
RDK::UCLProperty<vector<real>,NPulseHebbSynapse> PassiveMs;
RDK::UCLProperty<vector<real>,NPulseHebbSynapse> Kmot;
RDK::ULProperty<real,NPulseHebbSynapse> Kin;
RDK::ULProperty<real,NPulseHebbSynapse> Kout;

// К-т усиления динамической связи
RDK::ULProperty<real,NPulseHebbSynapse> GdGain;

// К-т усиления статической связи
RDK::ULProperty<real,NPulseHebbSynapse> GsGain;


protected: // Основные свойства

protected: // Временные переменные
RDK::ULStateProperty<real,NPulseHebbSynapse> G;
RDK::ULStateProperty<real,NPulseHebbSynapse> Gd;
RDK::UCLStateProperty<vector<real>,NPulseHebbSynapse> Gs;
RDK::ULStateProperty<real,NPulseHebbSynapse> Win;
RDK::ULStateProperty<real,NPulseHebbSynapse> Wout;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NPulseHebbSynapse(void);
virtual ~NPulseHebbSynapse(void);
// --------------------------

protected:
// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
//bool SetPulseAmplitude(real value);

// Постоянная времени выделения медиатора
//bool SetSecretionTC(real value);

// Постоянная времени распада медиатора
//bool SetDissociationTC(real value);

// Коэффициент пресинаптического торможения
//bool SetInhibitionCoeff(real value);

// Вес (эффективность синапса) синапса
//bool SetResistance(real value);
// --------------------------

public:
// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
virtual NPulseHebbSynapse* New(void);
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
protected:
// Восстановление настроек по умолчанию и сброс процесса счета
virtual bool ADefault(void);

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
virtual bool ABuild(void);

// Сброс процесса счета.
virtual bool AReset(void);

// Выполняет расчет этого объекта
virtual bool ACalculate(void);
// --------------------------
};

}
#endif
