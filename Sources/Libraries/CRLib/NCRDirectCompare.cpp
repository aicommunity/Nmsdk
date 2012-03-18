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

#include "NCRDirectCompare.h"
#include <algorithm>
#include <fstream>

namespace NMSDK {

using namespace std;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRDirectCompare::NCRDirectCompare(void)
//: NACRClassifier(name),
 // NumInputs(this,&NCRDirectCompare::SetNumInputs),
: MinRecThreshold("MinRecThreshold",this),
  MaxRecThreshold("MaxRecThreshold",this,&NCRDirectCompare::SetMaxRecThreshold),
  MiddleRecThreshold("MiddleRecThreshold",this),
  AbsoluteRecThreshold("AbsoluteRecThreshold",this),
  RecognitionType("RecognitionType",this),
  ReliabilityDistance("ReliabilityDistance",this),
  ReliabilityValue("ReliabilityValue",this)
{
// AddLookupParameter("RecognitionType",RecognitionType);

// AddLookupParameter("MinRecThreshold",MinRecThreshold);
// AddLookupParameter("MaxRecThreshold",MaxRecThreshold);
// AddLookupParameter("MiddleRecThreshold",MiddleRecThreshold);
// AddLookupParameter("AbsoluteRecThreshold",AbsoluteRecThreshold);
}

NCRDirectCompare::~NCRDirectCompare(void)
{
}
// --------------------------

// -----------------------------
// Методы управления параметрами
// -----------------------------
// Устанавливает число входов всех скрытых слоев
/*bool NCRDirectCompare::SetNumInputs(size_t numinputs)
{
// NumInputs=numinputs;
 Ready=false;

 ModifiedFlag=true;
 return true;
}     */

// Порог распознавания по максимуму суммы превышения
bool NCRDirectCompare::SetMaxRecThreshold(real value)
{
 ModifiedFlag=true;
 return true;
}
// -----------------------------

// -----------------------------
// Методы доступа к данным модели
// -----------------------------
// Вектор выборки
real NCRDirectCompare::GetSamples(int i, int j, int k) const
{
 return Samples[i][j][k];
}

// Вектор оригинальных выходов слоев сети
const vector<real>& NCRDirectCompare::GetNativeOutput(void) const
{
 return NativeOutput;
}

// Вектор входов
/*const vector<real>& NCRDirectCompare::GetInputs(void) const
{
 return Inputs;
} */
// -----------------------------

// ------------------------
// Методы счета
// ------------------------
// Загружает настройки из файла
bool NCRDirectCompare::AFileLoad(fstream &file)
{
 int i,j,k;
 size_t numclasses,numtrainsamples;
 int rectype;
 size_t numinputs;
 size_t temp;
 real value;

 file.read((char*)&numclasses,sizeof(numclasses));
 file.read((char*)&numinputs,sizeof(numinputs));

 if(numclasses <2 || numinputs ==0)
  return false;

 SetOutputDataSize(0,numclasses);

// PInputDataSize[0]=PInputDataSize[0];
 Build();

 file.read((char*)&numtrainsamples,sizeof(numtrainsamples));
 NumTrainSamples=numtrainsamples;

 file.read((char*)&rectype,sizeof(rectype));
 RecognitionType=rectype;

// Порог распознавания по максимуму суммы превышения
// в процентах от максимума входов (0,1)
 file.read((char*)&value,sizeof(value));
 MaxRecThreshold=value;

 file.read((char*)&value,sizeof(value));
 MinRecThreshold=value;

 file.read((char*)&value,sizeof(value));
 MiddleRecThreshold=value;

 file.read((char*)&value,sizeof(value));
 AbsoluteRecThreshold=value;

 file.read((char*)&temp,sizeof(temp));
 Samples.resize(temp);
 for(i=0;i<(int)Samples.size();i++)
 {
  file.read((char*)&temp,sizeof(temp));
  Samples[i].resize(temp);
  for(j=0;j<(int)Samples[i].size();j++)
  {
   file.read((char*)&temp,sizeof(temp));
   Samples[i][j].resize(temp);
   for(k=0;k<(int)Samples[i][j].size();k++)
	file.read((char*)&(Samples[i][j][k]),sizeof(Samples[i][j][k]));
  }
 }

 return true;
}

// Сохраняет настройки в файл
bool NCRDirectCompare::AFileSave(fstream &file)
{
 size_t i,j,k;
 int rectype;
 real value;

 size_t temp;
 temp=GetOutputDataSize(0);
 file.write((char*)&temp,sizeof(temp));
 temp=GetInputDataSize(0);
 file.write((char*)&temp,sizeof(temp));

 temp=NumTrainSamples;
 file.write((char*)&temp,sizeof(temp));

 rectype=RecognitionType;
 file.write((char*)&rectype,sizeof(rectype));

 // Порог распознавания по максимуму суммы превышения
 // в процентах от максимума входов (0,1)
 value=MaxRecThreshold;
 file.write((char*)&value,sizeof(value));

 value=MinRecThreshold;
 file.write((char*)&value,sizeof(value));

 value=MiddleRecThreshold;
 file.write((char*)&value,sizeof(value));

 value=AbsoluteRecThreshold;
 file.write((char*)&value,sizeof(value));

 temp=Samples.size();
 file.write((char*)&temp,sizeof(temp));

 for(i=0;i<Samples.size();i++)
 {
  temp=Samples[i].size();
  file.write((char*)&temp,sizeof(temp));
  for(j=0;j<Samples[i].size();j++)
  {
   temp=Samples[i][j].size();
   file.write((char*)&temp,sizeof(temp));
   for(k=0;k<Samples[i][j].size();k++)
	file.write((char*)&(Samples[i][j][k]),sizeof(Samples[i][j][k]));
  }
 }

 return true;
}
// ------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
RDK::UAContainer* NCRDirectCompare::New(void)
{
 return new NCRDirectCompare;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NCRDirectCompare::ACRDefault(void)
{
 SetOutputDataSize(0,2);
 if(!Build())
  return false;
// PInputDataSize[0]=100;   // Заглушка!!! Что это

 Real minrate,maxrate;
 minrate.assign(GetOutputDataSize(0),10);
 maxrate.assign(GetOutputDataSize(0),90);

 MinQualityRate=minrate;
 MaxQualityRate=maxrate;

// AutoQualityRate=true;
 AutoQualityRate=false;
// AutoAlignmentOutput=false;
 AutoAlignmentOutput=false;
 /*
 RecognitionType=3;
 MinRecThreshold=0.96;
 MaxRecThreshold=0.96;
 MaxInputValue=1;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=10;
   */
/*
 RecognitionType=1;
 MinRecThreshold=0.85;
 MaxRecThreshold=0.95;
 MaxInputValue=1;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=0.5;
  */
/* RecognitionType=1;
 MinRecThreshold=0.95;
 MaxRecThreshold=0.95;
 MaxInputValue=1;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=0.5;
*/
 RecognitionType=6;
 AbsoluteRecThreshold=0.988;
 MaxRecThreshold=0.975;
 MiddleRecThreshold=0.95;
 MinRecThreshold=0.9;
 MaxInputValue=1;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=1;

 ReliabilityDistance=0.03;

 ReliabilityValue=4.2;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NCRDirectCompare::ACRBuild(void)
{
 return true;
}


// Сброс процесса счета.
bool NCRDirectCompare::ACRReset(void)
{
 return true;
}

bool NCRDirectCompare::ACRCalculate(void)
{
 int classindex;

 real mininput,maxinput;
 int resclassindex=-1;
 real maxoutput=0;
 int nummethods=0;
 size_t outputsize=GetOutputDataSize(0);

 pair<real,int> max_out[2];

 if(NumTrainSamples<=0)
  return true;

 NativeOutput.resize(outputsize);
 vector<vector<real> > sortinput;

 switch(RecognitionType)
 {
 case 0:
  memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
  for(size_t i=outputsize;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(NativeOutput[classindex]<GetInputData(0)->Double[i])
	NativeOutput[classindex]=GetInputData(0)->Double[i];
  }

  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;

 case 1:
  memset(&NativeOutput[0],0,outputsize*sizeof(real));

  mininput=GetInputData(0)->Double[0];
  maxinput=GetInputData(0)->Double[0];
  for(size_t i=1;i<GetInputDataSize(0);i++)
  {
   if(mininput>GetInputData(0)->Double[i])
	mininput=GetInputData(0)->Double[i];
   if(maxinput<GetInputData(0)->Double[i])
	maxinput=GetInputData(0)->Double[i];
  }

  if(maxinput<(MaxInputValue()-MinInputValue())*MinRecThreshold)
  {
   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];
   break;
  }

  for(size_t i=0;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(GetInputData(0)->Double[i]>maxinput*MaxRecThreshold)
	NativeOutput[classindex]+=GetInputData(0)->Double[i]-maxinput*MaxRecThreshold;
  }
  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;

 case 2:
  memset(&NativeOutput[0],0,outputsize*sizeof(real));

  mininput=GetInputData(0)->Double[0];
  maxinput=GetInputData(0)->Double[0];
  for(size_t i=1;i<GetInputDataSize(0);i++)
  {
   if(mininput>GetInputData(0)->Double[i])
	mininput=GetInputData(0)->Double[i];
   if(maxinput<GetInputData(0)->Double[i])
	maxinput=GetInputData(0)->Double[i];
  }

  if(maxinput<(MaxInputValue()-MinInputValue())*MinRecThreshold)
  {
   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];
   break;
  }

  maxinput=(MaxInputValue()-MinInputValue());
  for(size_t i=0;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(GetInputData(0)->Double[i]>maxinput*MaxRecThreshold)
	NativeOutput[classindex]+=GetInputData(0)->Double[i]-maxinput*MaxRecThreshold;
  }
  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;

 case 3:
  memset(&NativeOutput[0],0,outputsize*sizeof(real));

  mininput=GetInputData(0)->Double[0];
  maxinput=GetInputData(0)->Double[0];
  for(size_t i=1;i<GetInputDataSize(0);i++)
  {
   if(mininput>GetInputData(0)->Double[i])
	mininput=GetInputData(0)->Double[i];
   if(maxinput<GetInputData(0)->Double[i])
	maxinput=GetInputData(0)->Double[i];
  }

  if(maxinput<(MaxInputValue()-MinInputValue())*MinRecThreshold)
  {
   for(size_t k=0;k<outputsize;k++)
    POutputData[0].Double[k]=NativeOutput[k];
   break;
  }

  for(size_t i=0;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(GetInputData(0)->Double[i]>(MaxInputValue()-MinInputValue())*MaxRecThreshold)
	++NativeOutput[classindex];//=PInputs[0]->Double[i]-maxinput*MaxRecThresholdCoeff;
  }
  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;

 case 4:
  memset(&NativeOutput[0],0,outputsize*sizeof(real));

  mininput=GetInputData(0)->Double[0];
  maxinput=GetInputData(0)->Double[0];
  for(size_t i=1;i<GetInputDataSize(0);i++)
  {
   if(mininput>GetInputData(0)->Double[i])
	mininput=GetInputData(0)->Double[i];
   if(maxinput<GetInputData(0)->Double[i])
	maxinput=GetInputData(0)->Double[i];
  }

  if(maxinput<MinRecThreshold*(MaxInputValue()-MinInputValue()))
  {
   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];
   break;
  }

  // Ищем абсолютный максимум
  if(maxinput>AbsoluteRecThreshold*(MaxInputValue()-MinInputValue()))
  {
   memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
   for(size_t i=outputsize;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(NativeOutput[classindex]<GetInputData(0)->Double[i])
	 NativeOutput[classindex]=GetInputData(0)->Double[i];
   }


   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(resclassindex == int(k))
	 POutputData[0].Double[k]=MaxOutputValue;
	else
	 POutputData[0].Double[k]=0;
  }
  else
  // Если выше максимального порога то вычисляем результат по числу максимумов
  if(maxinput>MaxRecThreshold*(MaxInputValue()-MinInputValue()))
  {
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>(MaxInputValue()-MinInputValue())*MaxRecThreshold)
	 ++NativeOutput[classindex];
   }

   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]=0;
  }
  else
  if(maxinput>MiddleRecThreshold*(MaxInputValue()-MinInputValue()))
  {
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>MiddleRecThreshold*(MaxInputValue()-MinInputValue()))
	 NativeOutput[classindex]+=GetInputData(0)->Double[i]-MiddleRecThreshold*(MaxInputValue()-MinInputValue());
   }
/*
   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];*/

   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]=0;
  }
  else
  {
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>MinRecThreshold)
	 NativeOutput[classindex]+=GetInputData(0)->Double[i]-MinRecThreshold;
   }

/*   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];*/
   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]=0;
  }


 break;

 case 5:
  memset(&NativeOutput[0],0,outputsize*sizeof(real));

  mininput=GetInputData(0)->Double[0];
  maxinput=GetInputData(0)->Double[0];
  for(size_t i=1;i<GetInputDataSize(0);i++)
  {
   if(mininput>GetInputData(0)->Double[i])
	mininput=GetInputData(0)->Double[i];
   if(maxinput<GetInputData(0)->Double[i])
	maxinput=GetInputData(0)->Double[i];
  }

  if(maxinput<MinRecThreshold*(MaxInputValue()-MinInputValue()))
  {
   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];
   break;
  }

  // Ищем абсолютный максимум
  memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
  for(size_t i=outputsize;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(NativeOutput[classindex]<GetInputData(0)->Double[i])
	NativeOutput[classindex]=GetInputData(0)->Double[i];
  }
  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];

  // Масштабируем
   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]=0;

  nummethods++;

  if(maxinput>(MaxInputValue()-MinInputValue())*MaxRecThreshold)
  {
   memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>(MaxInputValue()-MinInputValue())*MaxRecThreshold)
	 ++NativeOutput[classindex];
   }

   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
		maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]+=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]+=0;

   nummethods++;
  }

  if(maxinput>(MaxInputValue()-MinInputValue())*MiddleRecThreshold)
  {
  memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>maxinput*MiddleRecThreshold)
	 NativeOutput[classindex]+=GetInputData(0)->Double[i]-maxinput*MiddleRecThreshold;
   }

   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]+=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]+=0;

   nummethods++;
  }

  memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
   for(size_t i=0;i<GetInputDataSize(0);i++)
   {
	classindex=i/outputsize;
	classindex*=outputsize;
	classindex=i-classindex;
	if(GetInputData(0)->Double[i]>maxinput*MinRecThreshold)
	 NativeOutput[classindex]+=GetInputData(0)->Double[i]-mininput;//PInputs[0]->Double[i]-maxinput*MinRecThreshold;
   }
   nummethods++;
/*   for(size_t k=0;k<outputsize;k++)
	POutputData[0].Double[k]=NativeOutput[k];*/
   maxoutput=0;
   for(size_t k=0;k<outputsize;k++)
   {
	if(maxoutput<NativeOutput[k])
	{
	 maxoutput=NativeOutput[k];
	 resclassindex=k;
	}
   }
   for(size_t k=0;k<outputsize;k++)
	if(maxoutput)
	 POutputData[0].Double[k]+=NativeOutput[k]/maxoutput;
	else
	 POutputData[0].Double[k]+=0;

   for(size_t k=0;k<outputsize;k++)
	 POutputData[0].Double[k]/=nummethods;

 break;

 case 6:
  sortinput.resize(outputsize);

  for(size_t i=0;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   sortinput[classindex].push_back(GetInputData(0)->Double[i]);
  }

  for(size_t i=0;i<outputsize;i++)
  {
   sort(sortinput[i].begin(),sortinput[i].end());
  }

  for(size_t k=0;k<outputsize;k++)
  {
   POutputData[0].Double[k]=0;
   for(int j=int(sortinput[k].size())-1;j>=int(sortinput[k].size())-5;j--)
   {
	POutputData[0].Double[k]+=sortinput[k][j];
   }
   NativeOutput[k]=POutputData[0].Double[k];
  }


  for(size_t k=0;k<2;k++)
   max_out[k].first=0;
  for(size_t k=0;k<outputsize;k++)
  {
   if(max_out[0].first<POutputData[0].Double[k])
   {
	max_out[1].first=max_out[0].first;
	max_out[1].second=max_out[0].second;
	max_out[0].first=POutputData[0].Double[k];
	max_out[0].second=k;
   }
  }

  if((max_out[0].first-max_out[1].first)<ReliabilityDistance ||
	 (max_out[0].first<ReliabilityValue))
  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=0;
  for(size_t k=0;k<outputsize;k++)
   NativeOutput[k]=POutputData[0].Double[k];

 break;

 case 10:
  memcpy(&NativeOutput[0],&GetInputData(0)->Double[0],outputsize*sizeof(real));
  for(size_t i=outputsize;i<GetInputDataSize(0);i++)
  {
   classindex=i/outputsize;
   classindex*=outputsize;
   classindex=i-classindex;
   if(NativeOutput[classindex]<GetInputData(0)->Double[i])
	NativeOutput[classindex]=GetInputData(0)->Double[i];
  }

  for(size_t k=0;k<outputsize;k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;
 }

 return true;
}
// --------------------------


// --------------------------
// Скрытые методы обучения сети
// --------------------------
// Сброс настроек обучение в исходное состояние
void NCRDirectCompare::AResetTraining(void)
{
 Samples.resize(GetOutputDataSize(0));
// GetInputData(0)->Double.resize(GetInputDataSize(0));

 for(size_t j=0;j<Samples.size();j++)
 {
  Samples[j].clear();
 }
}

// Однократное обучение на заданном примере
real NCRDirectCompare::ATrain(size_t exp_class)
{
 real E=0;

// Samples[exp_class].push_back();
 Samples[exp_class].resize(Samples[exp_class].size()+1);
 Samples[exp_class].back().resize(GetInputDataSize(0));
 for(size_t i=0;i<GetInputDataSize(0);i++)
  Samples[exp_class].back()[i]=GetInputData(0)->Double[i];


 return E;
}
// --------------------------


// ------------------------
// Скрытые методы счета
// ------------------------
// Устанавливает значения входного вектора для распознавания
/*bool NCRDirectCompare::SetInput(const Real &input)
{
 size_t i;

// PInputs[0]->Double.resize(NumPInputs[0]->Double);

 size_t mmin=(GetInputDataSize(0)<input.size())?GetInputDataSize(0):input.size();
 for(i=0;i<mmin;i++)
  {
   PInputs[0]->Double[i]=input[i];
  }

 return true;
}  */
// ------------------------


}

//---------------------------------------------------------------------------

