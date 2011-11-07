//---------------------------------------------------------------------------


#pragma hdrstop

#include "CRFeatureSelectorNone.h"
#include <fstream>
#include <iomanip>

//---------------------------------------------------------------------------

// ---------------------
// Методы счета
// ---------------------
// Метод задания входного вектора
bool CRFeatureSelectorNone::SetInputImage(const UBitmap &input)
{
 if(!CRFeatureSelector::SetInputImage(input))
  return false;

 SetNumOutputs(InputImage.GetLength());

 return true;
}
// ---------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool CRFeatureSelectorNone::ADefault(void)
{

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool CRFeatureSelectorNone::ABuild(void)
{
// Output.resize(NumOutputs);

 return true;
}

// Сброс процесса счета.
bool CRFeatureSelectorNone::AReset(void)
{
 real data=-0.5;
 FillOutputData(&data);
// Output.assign(NumOutputs,-0.5);

 return true;
}

// Выполняет расчет этого объекта
bool CRFeatureSelectorNone::ACalculate(void)
{
// Output=Input;
 if(!InputImage.GetLength())
  return false;

 InputImage.SetColorModel(ubmY8);

 for(size_t i=0;i<GetOutputDataSize(0);i++)
  POutputData->Double[i]=double(InputImage.GetData()[i])/255.0-0.5;
 /*
 int k=0;

 for(int i=0;i<Input->width;i++)
  for(int j=0;j<Input->height;j++)
  {
   Output[k]=double((*pbmp)(i,j).b)/255.0-0.5;
   k++;
  }*/

 return true;
}
// --------------------------

// ---------------------
// Методы сериализации
// ---------------------
bool CRFeatureSelectorNone::SaveToFile(const std::string &filename)
{
 std::fstream file(filename.c_str(), ios::out);

 if(!file)
  return false;

 // Тут сохранение
 file<<NumOutputs<<std::endl;

 file.close();

 return true;
}

bool CRFeatureSelectorNone::LoadToFile(const std::string &filename)
{
 std::fstream file(filename.c_str(), ios::in);

 if(!file)
  return false;

 // Тут загрузка
 size_t value;
 file>>value;
 if(!SetNumOutputs(value))
  return false;

 file.close();

 return true;
}
// ---------------------


//---------------------------------------------------------------------------

#pragma package(smart_init)
