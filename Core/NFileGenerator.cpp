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

#ifndef NFILE_GENERATOR_CPP
#define NFILE_GENERATOR_CPP

#include "NFileGenerator.h"
#include <strstream>

namespace NMSDK {

// Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NFileGenerator::NFileGenerator(void)
//: NSource(name),
 : FileName("FileName",this,&NFileGenerator::SetFileName)
{
 DataStartTime=0;
}

NFileGenerator::~NFileGenerator(void)
{
}
// --------------------------

// --------------------------
// Методы управления общедоступными свойствами
// --------------------------
// Устанавливает имя файла с данными
bool NFileGenerator::SetFileName(const string &value)
{
 FileName.v=value;
 return Reset();
}
// --------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NFileGenerator* NFileGenerator::New(void)
{
 return new NFileGenerator;
}
// --------------------------

// --------------------------
// Методы доступа к компонентам
// --------------------------
// Метод проверяет на допустимость объекта данного типа
// в качестве компоненты данного объекта
// Метод возвращает 'true' в случае допустимости
// и 'false' в случае некорректного типа
bool NFileGenerator::CheckComponentType(UEPtr<UContainer> comp) const
{
 return false;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NFileGenerator::ADefault(void)
{
 FileName="FileGenerator.ini";
 return NSource::ADefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NFileGenerator::ABuild(void)
{
 return true;
}

// Сброс процесса счета.
bool NFileGenerator::AReset(void)
{
 Ini.Delete();
 Ini.LoadFromFile(FileName);
 Data.clear();

 // Заполняем массив данных
 vector<string> sections,variables;
 vector<double> value;
 string svalue;

 Ini.GetSectionList(sections);

 for(size_t i=0;i<sections.size();i++)
 {
  vector<RDK::UItemData> &data=Data[RDK::atof(sections[i])];
  Ini.GetVariableList(sections[i],variables);
  data.resize(variables.size());
  for(size_t j=0;j<variables.size();j++)
  {
   svalue=Ini(sections[i],variables[j],"");
   if(svalue.size()>0)
   {
	strstream stream(&svalue[0],svalue.size());
	RDK::operator >> (stream,value);
	//stream>>value;
	data[j].Resize(1,value.size());
	for(size_t k=0;k<value.size();k++)
	 data[j].Double[k]=value[k];
   }
   else
    data[j].Resize(0,0);
  }
 }
 CurrentIndex=Data.begin();
 DataStartTime=0;
 return NSource::AReset();
}

// Выполняет расчет этого объекта
bool NFileGenerator::ACalculate(void)
{
 if(CurrentIndex == Data.end())
 {
  FillOutputData();
  return true;
 }

 DataStartTime+=1.0/TimeStep;
 if(DataStartTime >= CurrentIndex->first)
 {
  int size=(NumOutputs<int(CurrentIndex->second.size()))?NumOutputs:CurrentIndex->second.size();

  for(int i=0;i<size;i++)
   for(int j=0;j<CurrentIndex->second[i].GetSize();j++)
    POutputData[i].Double[j]=CurrentIndex->second[i].Double[j];

  ++CurrentIndex;
  if(CurrentIndex == Data.end())
  {
   CurrentIndex=Data.begin();
   DataStartTime=0;
  }
 }

 return true;//NSource::ACalculate();
}
// --------------------------
}
#endif
