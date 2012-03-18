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

#ifndef NACRCLASSIFIER_CPP
#define NACRCLASSIFIER_CPP


#include "NACRClassifier.h"
//#include "USupport.h"
#include <algorithm>


namespace NMSDK {
/*
        class NACRClassifier
*/

NACRClassifier::NACRClassifier(void)
// : NADItem(name),
 : TrainEpsilon("TrainEpsilon",this,&NACRClassifier::SetTrainEpsilon),
   TrainMaxStepsNum("TrainMaxStepsNum",this,&NACRClassifier::SetTrainMaxStepsNum),
   MinOutputValue("MinOutputValue",this,&NACRClassifier::SetMinOutputValue),
   MaxOutputValue("MaxOutputValue",this,&NACRClassifier::SetMaxOutputValue),
   DesiredMinOutputValue("DesiredMinOutputValue",this),
   DesiredMaxOutputValue("DesiredMaxOutputValue",this),
   MinInputValue("MinInputValue",this,&NACRClassifier::SetMinInputValue),
   MaxInputValue("MaxInputValue",this,&NACRClassifier::SetMaxInputValue),

   MinQualityRate("MinQualityRate",this,&NACRClassifier::SetMinQualityRate),
   MaxQualityRate("MaxQualityRate",this,&NACRClassifier::SetMaxQualityRate),
   TrainFileName("TrainFileName",this,&NACRClassifier::SetTrainFileName),
   AutoQualityRate("AutoQualityRate",this),
   AutoAlignmentOutput("AutoAlignmentOutput",this),

   NumTrainSamples("NumTrainSamples",this),
   TrainingError("TrainingError",this),
   QualityRate("QualityRate",this),
   ScaledResult("ScaledResult",this),
   IsSuccessed("IsSuccessed",this),
   ModifiedFlag("ModifiedFlag",this)
{
 Ready=false;
}

NACRClassifier::~NACRClassifier(void)
{
}

// -----------------------------
// Методы управления параметрами
// -----------------------------
// Устанавливает максимально допустимую ошибку обучения
bool NACRClassifier::SetTrainEpsilon(real eps)
{
 if(eps <= 0)
  return false;

// TrainEpsilon=eps;
 return true;
}

// Устанавливает предельное число шагов обучения
bool NACRClassifier::SetTrainMaxStepsNum(size_t lmaxsteps)
{
 ModifiedFlag=true;
 return true;
}

// Устанавливает граничные величины входных значений классификатора
bool NACRClassifier::SetMinInputValue(real value)
{
 ModifiedFlag=true;
 return true;
}

bool NACRClassifier::SetMaxInputValue(real value)
{
 ModifiedFlag=true;
 return true;
}

// Устанавливает граничные величины выходных значений классификатора
bool NACRClassifier::SetMinOutputValue(real value)
{
 ModifiedFlag=true;
 return true;
}

bool NACRClassifier::SetMaxOutputValue(real value)
{
 ModifiedFlag=true;
 return true;
}

// Устанавливает граничные величины допустимого показателя качества
bool NACRClassifier::SetMinQualityRate(const Real& value)
{
 size_t sz=(value.size()<MaxQualityRate->size())?value.size():MaxQualityRate->size();
 for(size_t i=0;i<sz;i++)
  if(value[i]>=MaxQualityRate[i] || value[i] <0 || value[i] >100)
   return false;

 ModifiedFlag=true;
 return true;
}

bool NACRClassifier::SetMaxQualityRate(const Real& value)
{
 size_t sz=(value.size()<MinQualityRate->size())?value.size():MinQualityRate->size();
 for(size_t i=0;i<sz;i++)
  if(value[i]<=MinQualityRate[i] || value[i] <0 || value[i] >100)
   return false;

 ModifiedFlag=true;
 return true;
}

// Имя файла загрузки/сохранения состояния обучения
bool NACRClassifier::SetTrainFileName(string name)
{
 if(name == "")
  return false;

 ModifiedFlag=true;
 return true;
}
// -----------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NACRClassifier::ADefault(void)
{
 SetNumOutputs(2);
 SetOutputDataSize(0,10);


 TrainEpsilon=0.01;

 TrainMaxStepsNum=1;
 MinInputValue=-0.5;
 MaxInputValue=0.5;

 MinOutputValue=-0.5;
 MaxOutputValue=0.5;

 DesiredMinOutputValue=-0.5;
 DesiredMaxOutputValue=0.5;

 Real minrate,maxrate;
 minrate.assign(GetOutputDataSize(0),DesiredMinOutputValue*0.1);
 maxrate.assign(GetOutputDataSize(0),DesiredMaxOutputValue*0.9);

 MinQualityRate=minrate;
 MaxQualityRate=maxrate;

 AutoQualityRate=false;
 AutoAlignmentOutput=false;

 return ACRDefault();
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NACRClassifier::ABuild(void)
{
 ScaledResult->resize(GetOutputDataSize(0));

 size_t sz=MinQualityRate->size();
 MinQualityRate->resize(GetOutputDataSize(0));
 if(sz<GetOutputDataSize(0) && sz>0)
 {
  for(size_t i=sz;i<GetOutputDataSize(0);i++)
   MinQualityRate[i]=MinQualityRate[0];
 }

 sz=MaxQualityRate->size();
 MaxQualityRate->resize(GetOutputDataSize(0));
 if(sz<GetOutputDataSize(0) && sz>0)
 {
  for(size_t i=sz;i<GetOutputDataSize(0);i++)
   MaxQualityRate[i]=MaxQualityRate[0];
 }

 if(GetOutputDataSize(0) != GetOutputDataSize(1))
  SetOutputDataSize(1,GetOutputDataSize(0));

 return ACRBuild();
}


// Сброс процесса счета.
bool NACRClassifier::AReset(void)
{
 QualityRate=pair<float,int>(0.0f,0);
 IsSuccessed=false;
 return ACRReset();
}

// Выполняет расчет этого объекта на текущем шаге.
bool NACRClassifier::ACalculate(void)
{
 if(!ACRCalculate())
  return false;

 // Если разрешено автовырванивание выхода, то проводим его
 if(AutoAlignmentOutput && GetOutputDataSize(0)>0)
 {
  real maxoutput=POutputData[0].Double[0];
  real minoutput=POutputData[0].Double[0];
  for(size_t k=1;k<GetOutputDataSize(0);k++)
  {
   if(maxoutput<POutputData[0].Double[k])
	maxoutput=POutputData[0].Double[k];
   if(minoutput>POutputData[0].Double[k])
	minoutput=POutputData[0].Double[k];
  }

  if(maxoutput && fabs(maxoutput-minoutput)>0)
   for(size_t k=0;k<GetOutputDataSize(0);k++)
	POutputData[0].Double[k]=
	 (POutputData[0].Double[k]-minoutput)*(MaxOutputValue()-MinOutputValue)/(maxoutput-minoutput)+MinOutputValue;
 }

 // Вычисляем маштабированный выход [0;100]
 ScaledResult->resize(GetOutputDataSize(0));
 size_t o1size=GetOutputDataSize(1);
 size_t o0size=GetOutputDataSize(0);

 if(o1size != o0size)
  SetOutputDataSize(1,GetOutputDataSize(0));
 if(NumOutputs>1)
  for(size_t k=0;k<GetOutputDataSize(0);k++)
   POutputData[1].Double[k]=ScaledResult[k]=(POutputData[0].Double[k]-MinOutputValue)*((DesiredMaxOutputValue()-DesiredMinOutputValue)/(MaxOutputValue()-MinOutputValue))+DesiredMinOutputValue;
 else
  for(size_t k=0;k<GetOutputDataSize(0);k++)
   ScaledResult[k]=(POutputData[0].Double[k]-MinOutputValue)*((DesiredMaxOutputValue()-DesiredMinOutputValue)/(MaxOutputValue()-MinOutputValue))+DesiredMinOutputValue;

 // Вычисляем показатель качества
 real qual;
 size_t res;
 vector<real>::iterator I,J;

 I = max_element(ScaledResult->begin(),ScaledResult->end());
 J=ScaledResult->begin();
 for(res=0;res<GetOutputDataSize(0);res++)
  if(J+res == I)
   break;

 // Вычисление показателей качества
 qual=100;
 for(size_t k=0;k<GetOutputDataSize(0);k++)
  if(k != res && qual>(ScaledResult[res]-ScaledResult[k]))
   qual=ScaledResult[res]-ScaledResult[k];

 QualityRate->first=qual;
 QualityRate->second=res;

 if(MinQualityRate[QualityRate->second] >= qual || MinQualityRate[QualityRate->second] <= 0)
  IsSuccessed=false;
 else
  IsSuccessed=true;

 return true;
}
// --------------------------


// Сброс настроек обучение в исходное состояние
void NACRClassifier::ResetTraining(void)
{
 if(!Ready)
  Build();

 if(AutoQualityRate)
 {
  MaxQualityRate->assign(GetOutputDataSize(0),0);
 }


 NumTrainSamples=0;

 TrainingError=0;
 ModifiedFlag=true;
 AResetTraining();
}

// Однократное обучение на заданном примере номера
// exp_class - номер правильного класса
bool NACRClassifier::Train(size_t exp_class)
{
 size_t step;

 if(!Build())
  return false;

 if(exp_class >= GetOutputDataSize(0))
  return false;

 // Проводим итеративную процедуру обучения
 for(step=0;step<TrainMaxStepsNum;step++)
  {
   TrainingError=ATrain(exp_class);
   if(TrainingError < TrainEpsilon)
	break;
  }

 if(exp_class == 0)
  ++NumTrainSamples.v;

 if(AutoQualityRate)
 {
  Calculate();
  if(MaxQualityRate[exp_class]<QualityRate->first && exp_class == size_t(QualityRate->second))
   MaxQualityRate[exp_class]=QualityRate->first;
 }

 ModifiedFlag=true;
 return true;
}
// --------------------------

// ------------------------
// Методы счета
// ------------------------
// Загружает настройки из файла 'name'
bool NACRClassifier::FileLoad(const string &name)
{
 fstream file((name).c_str(), ios_base::in | ios_base::binary);
 if(!file.is_open())
  return false;

 real temp;
 size_t itemp;
 string stemp;

 // Максимально допустимая ошибка обучения
 file.read((char*)&temp,sizeof(temp));
 TrainEpsilon=temp;

 if(file.eof())
  return false;

 // Предельное число шагов обучения
 file.read((char*)&itemp,sizeof(itemp));
 TrainMaxStepsNum=itemp;

 // Граничные величины выходных значений классификатора
 file.read((char*)&temp,sizeof(temp));
 MinOutputValue=temp;
 file.read((char*)&temp,sizeof(temp));
 MaxOutputValue=temp;

 file.read((char*)&temp,sizeof(temp));
 MinInputValue=temp;
 file.read((char*)&temp,sizeof(temp));
 MaxInputValue=temp;


 // Граничные величины допустимого показателя качества
 file.read((char*)&itemp,sizeof(itemp));
 MinQualityRate->resize(itemp);
 for(size_t i=0;i<itemp;i++)
 {
  file.read((char*)&temp,sizeof(temp));
  MinQualityRate[i]=temp;
 }
 file.read((char*)&itemp,sizeof(itemp));
 MaxQualityRate->resize(itemp);
 for(size_t i=0;i<itemp;i++)
 {
  file.read((char*)&temp,sizeof(temp));
  MaxQualityRate[i]=temp;
 }

 // Имя файла загрузки/сохранения состояния обучения
 file.read((char*)&itemp,sizeof(itemp));
 stemp.resize(itemp);
 file.read((char*)&stemp[0],itemp);
 TrainFileName=stemp;

 // Признак разрешения автоматической настройки показателя качества
 // по результатам обучения
 file.read((char*)&itemp,sizeof(itemp));
 AutoQualityRate=itemp;

 file.read((char*)&itemp,sizeof(itemp));
 AutoAlignmentOutput=itemp;

 // Число примеров в обучающей выборке
 file.read((char*)&itemp,sizeof(itemp));
 NumTrainSamples=itemp;

 file.read((char*)&itemp,sizeof(itemp));
 Activity=itemp;

 if(file.eof())
  return false;

 if(!AFileLoad(file))
  return false;

 ModifiedFlag=false;
 return true;
}

// Сохраняет настройки в файл 'name'
bool NACRClassifier::FileSave(const string &name)
{
 if(!ModifiedFlag)
  return true;

 if(!Ready)
  return false;

 fstream file((name).c_str(), ios_base::out | ios_base::trunc | ios_base::binary);

 if(!file.is_open())
  return false;

 real temp;
 size_t itemp;
 string stemp;

 // Максимально допустимая ошибка обучения
 temp=TrainEpsilon;
 file.write((char*)&temp,sizeof(temp));

 // Предельное число шагов обучения
 itemp=TrainMaxStepsNum;
 file.write((char*)&itemp,sizeof(itemp));

 // Граничные величины выходных значений классификатора
 temp=MinOutputValue;
 file.write((char*)&temp,sizeof(temp));
 temp=MaxOutputValue;
 file.write((char*)&temp,sizeof(temp));

 temp=MinInputValue;
 file.write((char*)&temp,sizeof(temp));
 temp=MaxInputValue;
 file.write((char*)&temp,sizeof(temp));

 // Граничные величины допустимого показателя качества
 itemp=MinQualityRate->size();
 file.write((char*)&itemp,sizeof(itemp));
 for(size_t i=0;i<itemp;i++)
 {
  temp=MinQualityRate[i];
  file.write((char*)&temp,sizeof(temp));
 }
 itemp=MaxQualityRate->size();
 file.write((char*)&itemp,sizeof(itemp));
 for(size_t i=0;i<itemp;i++)
 {
  temp=MaxQualityRate[i];
  file.write((char*)&temp,sizeof(temp));
 }

 // Имя файла загрузки/сохранения состояния обучения
 itemp=TrainFileName->size();
 file.write((char*)&itemp,sizeof(itemp));
 stemp=TrainFileName;
 file.write((char*)&stemp[0],itemp);

 // Признак разрешения автоматической настройки показателя качества
 // по результатам обучения
 itemp=AutoQualityRate;
 file.write((char*)&itemp,sizeof(itemp));

 itemp=AutoAlignmentOutput;
 file.write((char*)&itemp,sizeof(itemp));

 // Число примеров в обучающей выборке
 itemp=NumTrainSamples;
 file.write((char*)&itemp,sizeof(itemp));

 itemp=Activity;
 file.write((char*)&itemp,sizeof(itemp));

 if(!AFileSave(file))
  return false;

 ModifiedFlag=false;
 return true;
}


}
#endif

