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

#include "NCRDistance.h"
#include <algorithm>
#include <fstream>


namespace NMSDK {

using namespace std;

int elemsort(const void *v1,const void *v2)
{
 real vv1,vv2;

 memcpy(&vv1,v1,sizeof(real));
 memcpy(&vv2,v2,sizeof(real));
 if(vv1<vv2)
  return -1;

 if(vv1>vv2)
  return 1;

 return 0;
}

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRDistance::NCRDistance(void)
//: NACRClassifier(name),
 : NumInputs("NumInputs",this,&NCRDistance::SetNumInputs),
  NumMaxElements("NumMaxElements",this),
  MinElementsDistance("MinElementsDistance",this),
  DispersionCroppingFlag("DispersionCroppingFlag",this),
  MaxDispersionValue("MaxDispersionValue",this),
  RecognitionType("RecognitionType",this),
  MinRecThreshold("MinRecThreshold",this),
  MaxRecThreshold("MaxRecThreshold",this,&NCRDistance::SetMaxRecThreshold)
{
/* AddLookupParameter("NumInputs",NumInputs);

 AddLookupParameter("NumMaxElements",NumMaxElements);
 AddLookupParameter("MinElementsDistance",MinElementsDistance);
 AddLookupParameter("DispersionCroppingFlag",DispersionCroppingFlag);
 AddLookupParameter("MaxDispersionValue",MaxDispersionValue);
 AddLookupParameter("RecognitionType",RecognitionType);

 AddLookupParameter("MinRecThreshold",MinRecThreshold);
 AddLookupParameter("MaxRecThreshold",MaxRecThreshold);
 */
}

NCRDistance::~NCRDistance(void)
{
}
// --------------------------

// -----------------------------
// Методы управления параметрами
// -----------------------------
// Устанавливает число входов всех скрытых слоев
bool NCRDistance::SetNumInputs(size_t numinputs)
{
// NumInputs=numinputs;
 Ready=false;

 return true;
}

// Устанавливает скорость обучения сети
bool NCRDistance::SetTrainingRate(real tr)
{
 if(tr <= 0)
  return false;

 return true;
}

// Порог распознавания по максимуму суммы превышения
bool NCRDistance::SetMaxRecThreshold(real value)
{
// MaxOutputValue=(0.5-MinRecThreshold-value*(0.5-MinRecThreshold))*OutputSize;
// MinOutputValue=0;

 return true;
}
// -----------------------------

// -----------------------------
// Методы доступа к данным модели
// -----------------------------
// Вектор математического ожидания
real NCRDistance::GetMiddleSamples(int i, int j) const
{
 return MiddleSamples[i][j];
}

// Вектор выборки
real NCRDistance::GetSamples(int i, int j, int k) const
{
 return Samples[i][j][k];
}

// Вектор исходных данных выборки
real NCRDistance::GetPreSamples(int i, int j, int k) const
{
 return PreSamples[i][j][k];
}

// Вектор оригинальных выходов слоев сети
const vector<real>& NCRDistance::GetNativeOutput(void) const
{
 return NativeOutput;
}

// Вектор входов
const vector<real>& NCRDistance::GetInputs(void) const
{
 return Inputs;
}

// Дисперсия отклонений
real NCRDistance::GetDispersion(int i, int j) const
{
 return Dispersion[i][j];
}

// Стандартное отклонение
real NCRDistance::GetSDeviation(int i, int j) const
{
 if(fabs(MiddleSamples[i][j])>1e-5)
  return sqrt(Dispersion[i][j])*100.0/fabs(MiddleSamples[i][j]);
 else
  return 1e6;
}


// -----------------------------

// ------------------------
// Методы счета
// ------------------------
// Загружает настройки из файла
bool NCRDistance::AFileLoad(fstream &file)
{
 int i,j,k;
 size_t numclasses,numtrainsamples;
 int rectype;
 size_t numinputs;
 size_t temp;

 file.read((char*)&numclasses,sizeof(numclasses));
 file.read((char*)&numinputs,sizeof(numinputs));

 if(numclasses <2 || numinputs ==0)
  return false;

 SetOutputDataSize(0,numclasses);

 SetNumInputs(numinputs);
 Build();

 file.read((char*)&numtrainsamples,sizeof(numtrainsamples));
 NumTrainSamples=numtrainsamples;

 file.read((char*)&rectype,sizeof(rectype));
 RecognitionType=rectype;


 file.read((char*)&temp,sizeof(temp));
 PreSamples.resize(temp);
 for(i=0;i<(int)PreSamples.size();i++)
 {
  file.read((char*)&temp,sizeof(temp));
  PreSamples[i].resize(temp);
  for(j=0;j<(int)PreSamples[i].size();j++)
  {
   file.read((char*)&temp,sizeof(temp));
   PreSamples[i][j].resize(temp);
   for(k=0;k<(int)PreSamples[i][j].size();k++)
	file.read((char*)&(PreSamples[i][j][k]),sizeof(PreSamples[i][j][k]));
  }
 }

 CalcMiddleSamples();
 CalcMaxElements();

 return true;
}

// Сохраняет настройки в файл
bool NCRDistance::AFileSave(fstream &file)
{
 size_t i,j,k;
 int rectype;

 size_t temp;
 temp=GetOutputDataSize(0);
 file.write((char*)&temp,sizeof(temp));
 temp=NumInputs;
 file.write((char*)&temp,sizeof(temp));

 temp=NumTrainSamples;
 file.write((char*)&temp,sizeof(temp));

 rectype=RecognitionType;
 file.write((char*)&rectype,sizeof(rectype));

 temp=PreSamples.size();
 file.write((char*)&temp,sizeof(temp));

 for(i=0;i<PreSamples.size();i++)
 {
  temp=PreSamples[i].size();
  file.write((char*)&temp,sizeof(temp));
  for(j=0;j<PreSamples[i].size();j++)
  {
   temp=PreSamples[i][j].size();
   file.write((char*)&temp,sizeof(temp));
   for(k=0;k<PreSamples[i][j].size();k++)
	file.write((char*)&(PreSamples[i][j][k]),sizeof(PreSamples[i][j][k]));
  }
 }

 return true;
}
// ------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NAContainer* NCRDistance::New(void)
{
 return new NCRDistance;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NCRDistance::ACRDefault(void)
{
 SetOutputDataSize(0,2);
 SetNumInputs(100);
// MinOutputValue=0;//-0.5;
// MaxOutputValue=10000;//0.5;

 Real minrate,maxrate;
 minrate.assign(GetOutputDataSize(0),10);
 maxrate.assign(GetOutputDataSize(0),90);

 MinQualityRate=minrate;
 MaxQualityRate=maxrate;

 AutoQualityRate=true;
 AutoAlignmentOutput=false;

// NumMaxElements=20;
 MinElementsDistance=1000;

 DispersionCroppingFlag=1;
 MaxDispersionValue=50;

 RecognitionType=5;

 MinRecThreshold=0.7;
 MaxRecThreshold=0.98;
 MaxInputValue=0.5;
 MinInputValue=0;
 MinOutputValue=0;
 MaxOutputValue=0.001;//((MaxInputValue-MinInputValue)-MaxRecThreshold*(MaxInputValue-MinInputValue))*NumInputs;

 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NCRDistance::ACRBuild(void)
{
 return true;
}


// Сброс процесса счета.
bool NCRDistance::ACRReset(void)
{
 return true;
}

bool NCRDistance::ACRCalculate(void)
{
 int classindex;

 if(NumTrainSamples<=0)
  return true;

 NativeOutput.resize(GetOutputDataSize(0));

 switch(RecognitionType)
 {
 case 0:
  memcpy(&NativeOutput[0],&Inputs[0],GetOutputDataSize(0)*sizeof(real));
  for(size_t i=GetOutputDataSize(0);i<NumInputs;i++)
  {
   classindex=i/GetOutputDataSize(0);
   classindex*=GetOutputDataSize(0);
   classindex=i-classindex;
   if(NativeOutput[classindex]<Inputs[i])
	NativeOutput[classindex]=Inputs[i];
  }
  for(size_t k=0;k<GetOutputDataSize(0);k++)
   POutputData[0].Double[k]=NativeOutput[k];
 break;

 case 1:
 for(size_t j=0;j<GetOutputDataSize(0);j++)
 {
  NativeOutput[j]=-1;
  for(size_t k=0;k<Samples[j].size();k++)
  {
   real omin=0;
   for(size_t i=0;i<NumInputs;i++)
	omin+=(Samples[j][k][i]-Inputs[i])*(Samples[j][k][i]-Inputs[i]);
   omin=sqrt(omin);

   if(NativeOutput[j] < 0 || NativeOutput[j] > omin)
	NativeOutput[j]=omin;
  }
 }
 break;

 case 2:
 for(size_t j=0;j<MiddleSamples.size();j++)
 {
  NativeOutput[j]=-1;
  real omin=0;
  for(size_t k=0;k<MiddleSamples[j].size();k++)
   omin+=(MiddleSamples[j][k]-Inputs[k])*(MiddleSamples[j][k]-Inputs[k]);
//  for(size_t k=0;k<NumMaxElements;k++)
//   omin+=(MiddleSamples[j][MaxElementsIndex[k]]-Inputs[MaxElementsIndex[k]])*(MiddleSamples[j][MaxElementsIndex[k]]-Inputs[MaxElementsIndex[k]]);
//  for(size_t k=0;k<MiddleSamples[j].size();k++)
//   omin+=ElementWeights[MaxElementsIndex[k]]*(MiddleSamples[j][k]-Inputs[k])*(MiddleSamples[j][k]-Inputs[k]);

//  for(size_t k=0;k<NumMaxElements;k++)
//   if(find(DispersionBanIndexes.begin(),DispersionBanIndexes.end(),MaxClassElementsIndex[j][k]) == DispersionBanIndexes.end())
//   omin+=Weights[j][MaxClassElementsIndex[j][k]]*(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]])*
//		 (MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]]);

//  for(size_t k=0;k<NumMaxElements;k++)
//   omin+=Weights[j][MaxClassElementsIndex[j][k]]*
//		(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]])*
//		(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]]);

  omin=sqrt(omin);
  NativeOutput[j]=omin;
 }
 for(size_t k=0;k<GetOutputDataSize(0);k++)
  POutputData[0].Double[k]=-NativeOutput[k];
 break;

 case 3:
 for(size_t j=0;j<MiddleSamples.size();j++)
 {
  NativeOutput[j]=-1;
  real omin=0;
//  for(size_t k=0;k<NumMaxElements;k++)
//   omin+=(MiddleSamples[j][MaxElementsIndex[k]]-Inputs[MaxElementsIndex[k]])*(MiddleSamples[j][MaxElementsIndex[k]]-Inputs[MaxElementsIndex[k]]);
//  for(size_t k=0;k<MiddleSamples[j].size();k++)
//   omin+=ElementWeights[MaxElementsIndex[k]]*(MiddleSamples[j][k]-Inputs[k])*(MiddleSamples[j][k]-Inputs[k]);

  for(size_t k=0;k<MiddleSamples.size();k++)
   if(find(DispersionBanIndexes.begin(),DispersionBanIndexes.end(),MaxClassElementsIndex[j][k]) == DispersionBanIndexes.end())
   omin+=/*Weights[j][MaxClassElementsIndex[j][k]]**/(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]])*
		 (MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]]);

//  for(size_t k=0;k<NumMaxElements;k++)
//   omin+=Weights[j][MaxClassElementsIndex[j][k]]*
//		(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]])*
//		(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]]);

  omin=sqrt(omin);
  NativeOutput[j]=omin;
 }
 for(size_t k=0;k<GetOutputDataSize(0);k++)
  POutputData[0].Double[k]=-NativeOutput[k];

 break;

 case 4:
 for(size_t j=0;j<MiddleSamples.size();j++)
 {
  NativeOutput[j]=-1;
  real omin=0;
  for(size_t k=0;k<MiddleSamples.size();k++)
   if(find(DispersionBanIndexes.begin(),DispersionBanIndexes.end(),MaxClassElementsIndex[j][k]) == DispersionBanIndexes.end())
   omin+=Weights[j][MaxClassElementsIndex[j][k]]*(MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]])*
		 (MiddleSamples[j][MaxClassElementsIndex[j][k]]-Inputs[MaxClassElementsIndex[j][k]]);

  omin=sqrt(omin);
  NativeOutput[j]=omin;
 }
 for(size_t k=0;k<GetOutputDataSize(0);k++)
  POutputData[0].Double[k]=-NativeOutput[k];

 break;
 }

 return true;
}
// --------------------------


// --------------------------
// Скрытые методы обучения сети
// --------------------------
// Сброс настроек обучение в исходное состояние
void NCRDistance::AResetTraining(void)
{
// Samples.resize(GetOutputDataSize(0));
 PreSamples.resize(GetOutputDataSize(0));
// Inputs.resize(NumInputs);

 for(size_t j=0;j<Samples.size();j++)
 {
  Samples[j].clear();
  PreSamples[j].clear();
 }
}

// Однократное обучение на заданном примере
real NCRDistance::ATrain(size_t exp_class)
{
 real E=0;

 PreSamples[exp_class].push_back(Inputs);

 // Расчет максимальных элементов вектора
 if(exp_class == GetOutputDataSize(0)-1)
 {
  CalcMiddleSamples();
  CalcMaxElements();
 }

 return E;
}

// Расчет средних ожидаемых векторов
void NCRDistance::CalcMiddleSamples(void)
{
 // Считаем среднее
 MiddleSamples.resize(PreSamples.size());

 for(size_t i=0;i<PreSamples.size();i++)
 {
  MiddleSamples[i].assign(PreSamples[i][0].size(),0);
  for(size_t k=0;k<PreSamples[i][0].size();k++)
  {
   for(size_t j=0;j<PreSamples[i].size();j++)
   {
	MiddleSamples[i][k]+=PreSamples[i][j][k];
   }
   MiddleSamples[i][k]/=PreSamples[i].size();
  }
 }

 // Считаем дисперсию
 Dispersion.resize(PreSamples.size());
 DispersionBanIndexes.clear();

 for(size_t i=0;i<PreSamples.size();i++)
 {
  Dispersion[i].assign(PreSamples[i][0].size(),0);
  for(size_t k=0;k<PreSamples[i][0].size();k++)
  {
   for(size_t j=0;j<PreSamples[i].size();j++)
   {
	Dispersion[i][k]+=(MiddleSamples[i][k]-PreSamples[i][j][k])*
					  (MiddleSamples[i][k]-PreSamples[i][j][k]);
   }
   Dispersion[i][k]/=PreSamples[i].size();
//   Dispersion[i][k]=sqrt(Dispersion[i][k]);
//   Dispersion[i][k]/=MiddleSamples[i][k];
//   Dispersion[i][k]*=100;

   // Считаем запрещенные индексы
   if(GetSDeviation(i,k)>MaxDispersionValue)
    DispersionBanIndexes.push_back(k);
  }
 }

// CalcDispersionCropping();
 Samples=PreSamples;
// CalcMiddleSamples();
}

// Расчет максимальных элементов вектора
void NCRDistance::CalcMaxElements(void)
{
 if(MiddleSamples.size() == 0 ||
	MiddleSamples[0].size() == 0)
  return;

 // Считаем максимальные компоненты выборочно для класса
 NumMaxElements->resize(MiddleSamples.size());
 MaxClassElements.resize(MiddleSamples.size());
 MaxClassElementsIndex.resize(MiddleSamples.size());

 for(size_t k=0;k<MiddleSamples.size();k++)
 {
  MaxClassElements[k].assign(MiddleSamples[k].size(),1e6);
  MaxClassElementsIndex[k].assign(MiddleSamples[k].size(),0);

  for(size_t j=0;j<MiddleSamples[k].size();j++)
  {
   for(size_t i=0;i<MiddleSamples.size();i++)
   {
	if(i != k && MaxClassElements[k][j]>fabs(MiddleSamples[k][j]-MiddleSamples[i][j]))
	{
	 MaxClassElements[k][j]=fabs(MiddleSamples[k][j]-MiddleSamples[i][j]);
	}
   }
  }
 }

 for(size_t k=0;k<MaxClassElements.size();k++)
 {
  vector<real> temp=MaxClassElements[k];
  qsort(&temp[0],temp.size(),sizeof(real),elemsort);
  reverse(temp.begin(),temp.end());
  vector<real> orig=MaxClassElements[k];

  // Расчет индексов максимальных компонент
  for(size_t j=0;j<MiddleSamples[0].size();j++)
   for(size_t i=0;i<MiddleSamples[0].size();i++)
   if(temp[j] != -1 && orig[i] == temp[j])
   {
	MaxClassElementsIndex[k][j]=i;
	orig[i]=-1;
	break;
   }

 }

 // Расчет весов компонент выборочно для класса
 Weights.resize(MaxClassElements.size());
 for(size_t k=0;k<Weights.size();k++)
 {
  Weights[k].assign(MaxClassElements[k].size(),1);
  real emax,emin;
  emax=emin=MaxClassElements[k][0];
  for(size_t i=1;i<MaxClassElements[k].size();i++)
  {
   if(MaxClassElements[k][i]<emin)
	emin=MaxClassElements[k][i];
   if(MaxClassElements[k][i]>emax)
	emax=MaxClassElements[k][i];
  }

  if(emax-emin>0)
   for(size_t i=0;i<MaxClassElements[k].size();i++)
   {
//	 Weights[k][i]=fabs((MaxClassElements[k][i]-emin)/(emax-emin));
//	if(Dispersion[k][i]>0)
//	 Weights[k][i]=fabs(((MaxClassElements[k][i]-emin)/(emax-emin))/(GetSDeviation(k,i)/MaxDispersionValue));
//	else
	 Weights[k][i]=fabs((MaxClassElements[k][i]-emin)/(emax-emin));
   }

 }


// NumMaxElements=NumInputs/3;//MiddleSamples.size();//NumInputs;
}


// Отсечение выбросов в обучающей выборке по дисперсии
void NCRDistance::CalcDispersionCropping(void)
{
 Samples=PreSamples;
 switch(DispersionCroppingFlag)
 {
 case 1:
  for(size_t i=0;i<Dispersion.size();i++)
  {
   for(size_t j=0;j<Dispersion[i].size();j++)
   {
	if(GetSDeviation(i,j)>MaxDispersionValue)
	{
	 for(size_t n=0;n<Samples.size();n++)
	  for(size_t m=0;m<Samples[n].size();m++)
	   Samples[n][m][j]=0;
	}
   }
  }

 break;

 case 2:
  for(size_t i=0;i<Dispersion.size();i++)
  {
   for(size_t j=0;j<Dispersion[i].size();j++)
   {
	if(Dispersion[i][j]>MaxDispersionValue)
	{

	}
   }
  }

 break;
 }

}
// --------------------------


// ------------------------
// Скрытые методы счета
// ------------------------
// Устанавливает значения входного вектора для распознавания
bool NCRDistance::SetInput(const Real &input)
{
 size_t i;

 Inputs.resize(NumInputs);

 size_t mmin=(Inputs.size()<input.size())?Inputs.size():input.size();
 for(i=0;i<mmin;i++)
  {
   Inputs[i]=input[i];
  }

 return true;
}
// ------------------------


}

