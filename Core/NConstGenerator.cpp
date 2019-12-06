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

#ifndef NCONST_GENERATOR_CPP
#define NCONST_GENERATOR_CPP

#include "NConstGenerator.h"



namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NConstGenerator::NConstGenerator(void)
//: NSource(name),
 : Amplitude("Amplitude",this,&NConstGenerator::SetAmplitude)
{
 UpdateOutputFlag=false;
}

NConstGenerator::~NConstGenerator(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает амплитуду импульсов
bool NConstGenerator::SetAmplitude(const double &value)
{
 if(Amplitude.v != value)
  UpdateOutputFlag=true;
 return true;
}

// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NConstGenerator* NConstGenerator::New(void)
{
 return new NConstGenerator;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NConstGenerator::ADefault(void)
{
 Amplitude=100.0;
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NConstGenerator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NConstGenerator::AReset(void)
{
 UpdateOutputFlag=true;
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NConstGenerator::ACalculate(void)
{
 if(UpdateOutputFlag)
 {
  FillOutputData(0,&Amplitude.v);
  UpdateOutputFlag=false;
 }
 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
