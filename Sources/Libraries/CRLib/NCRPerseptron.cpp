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

#ifndef NCRPERSEPTRON_CPP
#define NCRPERSEPTRON_CPP

#include "NCRPerseptron.h"
#include <fstream>

namespace NMSDK {

real alpha=1;

real Sigmoid(real x)
{
 if(alpha*x>1.0e3)
  return 0.5;

 if(alpha*x<-1.0e3)
  return -0.5;

 return 1./(1.+expl(-alpha*x))-0.5;
}


// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRPerseptron::NCRPerseptron(void)
//: NACRClassifier(name),
 : NumLayers("NumLayers",this,&NCRPerseptron::SetNumLayers),
  NumInputs("NumInputs",this,&NCRPerseptron::SetNumInputs),
  TrainingRate("TrainingRate",this,&NCRPerseptron::SetTrainingRate),
  Moment("Moment",this,&NCRPerseptron::SetTrainingRate),
  AutoSetLayerInputs("AutoSetLayerInputs",this,&NCRPerseptron::SetAutoSetLayerInputs)
{
/* AddLookupParameter("NumLayers",NumLayers);
 AddLookupParameter("NumInputs",NumInputs);
 AddLookupParameter("TrainingRate",TrainingRate);
 AddLookupParameter("Moment",Moment);
 AddLookupParameter("AutoSetLayerInputs",AutoSetLayerInputs);
 */
}

NCRPerseptron::~NCRPerseptron(void)
{
}
// --------------------------

// -----------------------------
// Методы доступа к данным
// -----------------------------
real NCRPerseptron::GetWeight(size_t layer, size_t col, size_t row)
{
 return Weights[layer][col][row];
}

real NCRPerseptron::GetInputs(size_t row)
{
 return Inputs[row];
}

real NCRPerseptron::GetOutputs(size_t layer, size_t row)
{
 return Outputs[layer][row];
}
// -----------------------------

// -----------------------------
// Методы управления параметрами
// -----------------------------
// Устанавливает число слоев сети
bool NCRPerseptron::SetNumLayers(size_t num)
{
 Ready=false;

 if(num < 2)
  return false;

// NumLayers=num;
 NumInputs->resize(num);
 return true;
}

// Устанавливает число входов всех скрытых слоев
bool NCRPerseptron::SetNumInputs(const vector<size_t> &numinputs)
{
 size_t i;
 bool key;

 if(NumInputs->size() == numinputs.size())
  {
   key=true;
   for(i=0;i<NumInputs->size();i++)
	if(NumInputs[i] != numinputs[i])
	 { key=false; break; }
   if(key)
	return true;
  }

 Ready=false;


 return true;
}

// Устанавливает скорость обучения сети
bool NCRPerseptron::SetTrainingRate(real tr)
{
 if(tr <= 0)
  return false;

// TrainingRate=tr;
 return true;
}

// Устанавливает момент сети
bool NCRPerseptron::SetMoment(real m)
{
 if(Moment.v < 0 || Moment.v > 1.0)
  return false;

// Moment=m;
 return true;
}

// Автоопределение размера слоев
bool NCRPerseptron::SetAutoSetLayerInputs(bool value)
{
 if(AutoSetLayerInputs == false)
 {
  Ready=false;
 }

 return true;
}
// -----------------------------

// ------------------------
// Методы счета
// ------------------------
// Загружает настройки из файла 'name'
bool NCRPerseptron::AFileLoad(fstream &file)
{
 int i,j,k;
 size_t numlayers,numclasses;
 vector<size_t> numinputs;

 file.read((char*)&numlayers,sizeof(numlayers));
 file.read((char*)&numclasses,sizeof(numclasses));
 numinputs.resize(numlayers);
 
 for(i=0;i<(int)numlayers;i++)
  file.read((char*)&(numinputs[i]),sizeof(numinputs[i]));

 if(numlayers <=0 || numclasses <2 || numinputs.size() ==0)
  return false;


 NumLayers=numlayers;
 SetOutputDataSize(0,numclasses);


 SetNumInputs(numinputs);
 Build();

 for(k=0;k<(int)NumLayers();k++)
  {
   for(i=0;i<(int)Weights[k].size();i++)
	for(j=0;j<(int)Weights[k][i].size();j++)
	 file.read((char*)&(Weights[k][i][j]),sizeof(Weights[k][i][j]));
  }

 return true;
}

// Сохраняет настройки в файл 'name'
bool NCRPerseptron::AFileSave(fstream &file)
{
 int i,j,k;

 size_t temp;
 temp=NumLayers();
 file.write((char*)&temp,sizeof(temp));
 temp=GetOutputDataSize(0);
 file.write((char*)&temp,sizeof(temp));
 for(i=0;i<(int)NumLayers;i++)
  file.write((char*)&(NumInputs[i]),sizeof(NumInputs[i]));

 for(k=0;k<(int)NumLayers();k++)
  {
   for(i=0;i<(int)Weights[k].size();i++)
	for(j=0;j<(int)Weights[k][i].size();j++)
	 file.write((char*)&(Weights[k][i][j]),sizeof(Weights[k][i][j]));
  }

 return true;
}
// ------------------------

// --------------------------
// Системные методы управления объектом
// --------------------------
// Выделяет память для новой чистой копии объекта этого класса
NAContainer* NCRPerseptron::New(void)
{
 return new NCRPerseptron;
}
// --------------------------

// --------------------------
// Скрытые методы управления счетом
// --------------------------
// Восстановление настроек по умолчанию и сброс процесса счета
bool NCRPerseptron::ACRDefault(void)
{
 vector<size_t> numinputs;


 numinputs.resize(2);
 numinputs[0]=200;
 numinputs[1]=900;

 NumLayers=2;
 SetOutputDataSize(0,2);
 SetNumInputs(numinputs);
 TrainingRate=0.1;
 Moment=0.5;
// MinOutputValue=0;
// MaxOutputValue=100;
 MinOutputValue=-0.5;
 MaxOutputValue=0.5;

 Real minrate,maxrate;
 minrate.assign(GetOutputDataSize(0),10);
 maxrate.assign(GetOutputDataSize(0),90);

 MinQualityRate=minrate;
 MaxQualityRate=maxrate;

 AutoQualityRate=true;
 AutoAlignmentOutput=true;

// AutoAlignmentOutput=false;

 AutoSetLayerInputs=true;
 return true;
}

// Обеспечивает сборку внутренней структуры объекта
// после настройки параметров
// Автоматически вызывает метод Reset() и выставляет Ready в true
// в случае успешной сборки
bool NCRPerseptron::ACRBuild(void)
{
 size_t i,j;

 Weights.resize(NumLayers);
 dWeights.resize(NumLayers);
 Outputs.resize(NumLayers);
 NumInputs->resize(NumLayers);

 if(AutoSetLayerInputs())
 {
  vector<size_t> numinputs=NumInputs();
  for(size_t i=1;i<NumLayers;i++)
   numinputs[i]=(NumInputs[0]+GetOutputDataSize(0))/(i+1);

  SetNumInputs(numinputs);
 }

 if(NumLayers)
  Inputs.resize(NumInputs[0]);
 else
  Inputs.resize(0);

 for(i=0;i<NumLayers;i++)
  {
   if(i == NumLayers-1)
	Outputs[i].resize(GetOutputDataSize(0));
   else
	Outputs[i].resize(NumInputs[i+1]);
   }

 for(i=0;i<NumLayers;i++)
  {
   if(i == NumLayers-1)
	{
	 Weights[i].resize(GetOutputDataSize(0));
	 dWeights[i].resize(GetOutputDataSize(0));
	}
   else
	{
	 Weights[i].resize(NumInputs[i+1]);
	 dWeights[i].resize(NumInputs[i+1]);
	}

   // Изменяем длины строк матрицы весов
   for(j=0;j<Weights[i].size();j++)
	{
	 Weights[i][j].resize(NumInputs[i]+1);
	 dWeights[i][j].resize(NumInputs[i]+1);
	}
  }

 Ready=true;
 ResetTraining();
 return true;
}


// Сброс процесса счета.
bool NCRPerseptron::ACRReset(void)
{
 return true;
}

// Выполняет расчет этого объекта на текущем шаге.
bool NCRPerseptron::ACRCalculate(void)
{
 Inputs.resize(PInputDataSize[0]);
 for(size_t i=0;i<PInputDataSize[0];i++)
  Inputs[i]=PInputData[0]->Double[i];

 CalcNetwork(Inputs);
 if(GetOutputDataSize(0) > 0 && Outputs.size()>0 && Outputs[Outputs.size()-1].size()>=GetOutputDataSize(0))
  memcpy(POutputData[0].Void, &Outputs[Outputs.size()-1][0],GetOutputDataSize(0)*sizeof(real));

 return true;
}
// --------------------------


// --------------------------
// Скрытые методы обучения сети
// --------------------------
// Сброс настроек обучение в исходное состояние
void NCRPerseptron::AResetTraining(void)
{
 size_t i,j,k;

 if(!Ready)
  return;

 time_t tm;
 time(&tm);
 srand(static_cast<unsigned>(tm));
 for(k=0;k<NumLayers;k++)
  {
   for(i=0;i<Weights[k].size();i++)
    for(j=0;j<Weights[k][i].size();j++)
     {
       Weights[k][i][j]=((real)((rand()*100.0)/real(RAND_MAX))/100.0-0.5)*0.1;
     }
  }

 for(k=0;k<NumLayers;k++)
  {
   for(i=0;i<Weights[k].size();i++)
    for(j=0;j<Weights[k][i].size();j++)
     {
      dWeights[k][i][j]=0;
     }

  }

}

// Однократное обучение на заданном примере
real NCRPerseptron::ATrain(size_t exp_class)
{
 int i,j,l;
 real E;
 real corr;
 vector<real> delta;
 vector<real> delta_prev;
 vector<vector<real> > weights_prev;
 vector<vector<real> > *pweights;
 vector<vector<real> > *pdweights;

 if(!Ready)
  return 0;
 
 // Проводим распознавание примера
 Inputs.resize(PInputDataSize[0]);
 for(size_t i=0;i<PInputDataSize[0];i++)
  Inputs[i]=PInputData[0]->Double[i];
// for(size_t i=0;i<PInputDataSize[0];i++)
//  Inputs[i]=(PInputData[0]->Double[i]-0.9)*5;
// for(size_t i=0;i<PInputDataSize[0];i++)
//  Inputs[i]=(PInputData[0]->Double[i]-0.8)*2.5;


 CalcNetwork(Inputs);

 // Рассчитываем поправки выходному слою
 delta.assign(Weights[NumLayers-1].size(),0);
 for(j=0;j<(int)Weights[NumLayers-1].size();j++)
  {
   if(j == (int)exp_class)
    delta[j]=Outputs[NumLayers-1][j]-0.5;
   else
    delta[j]=Outputs[NumLayers-1][j]+0.5;
  }

 // Корректируем веса всем слоям
 for(l=NumLayers-1;l>=0;l--)
  {
   pweights=&(Weights[l]);
   pdweights=&(dWeights[l]);

   if(l<(int)NumLayers()-1)
    {
     delta.assign(pweights->size(),0);
     for(i=0;i<(int)Outputs[l].size();i++)
      {
       for(j=0;j<(int)Outputs[l+1].size();j++)
        delta[i]+=delta_prev[j]*weights_prev[j][i];

       delta[i]*=Outputs[l][i]*(1.0-Outputs[l][i]); // Проверить почему это за суммой!!!!
      }
    }

   if(l > 0)
    {
     weights_prev.resize(pweights->size());
     for(i=0;i<(int)pweights->size();i++)
      {
       weights_prev[i].resize((*pweights)[0].size());
       for(j=0;j<(int)(*pweights)[0].size();j++)
        weights_prev[i][j]=(*pweights)[i][j];
      }
    }


   for(i=0;i<(int)pweights->size();i++)
    {
     corr=alpha*delta[i];
     for(j=0;j<(int)(*pweights)[0].size()-1;j++)
      {
       if(l>0)
		(*pdweights)[i][j]=-TrainingRate*corr*Outputs[l-1][j]+Moment*(*pdweights)[i][j];
       else
        (*pdweights)[i][j]=-TrainingRate*corr*Inputs[j]+Moment*(*pdweights)[i][j];

       (*pweights)[i][j]+=(*pdweights)[i][j];
      }

     (*pdweights)[i][(*pdweights)[0].size()-1]=TrainingRate*corr*0.5+ // почему не считается разность с предыдущим шагом??
                              Moment*(*pdweights)[i][(*pdweights)[0].size()-1];
     (*pweights)[i][(*pweights)[0].size()-1]+=(*pdweights)[i][(*pdweights)[0].size()-1];

    }

   delta_prev.resize(delta.size());
   for(i=0;i<(int)delta.size();i++)
    delta_prev[i]=delta[i];
  }

 // Вычисляем ошибку
 E=0;
 for(i=0;i<(int)Outputs[NumLayers-1].size();i++)
  {
   if(i == (int)exp_class)
    E+=(Outputs[NumLayers-1][i]-0.5)*(Outputs[NumLayers-1][i]-0.5);
   else
    E+=(Outputs[NumLayers-1][i]+0.5)*(Outputs[NumLayers-1][i]+0.5);
  }
 return 0.5*E;
}
// --------------------------


// ------------------------
// Скрытые методы счета
// ------------------------
// Устанавливает значения входного вектора для распознавания
bool NCRPerseptron::SetInput(const Real &input)
{
 size_t i;

 size_t mmin=(Inputs.size()<input.size())?Inputs.size():input.size();
 for(i=0;i<mmin;i++)
  {
   Inputs[i]=input[i];
  }

 return true;
}

// Производит расчет заданного слоя
void NCRPerseptron::CalcLayer(vector<real> &in_x, vector<real> &out_q,
						vector<vector<real> > &weights,
						real(*ActiveFunc)(real x))
{
 int i,j;
 real sum;

 if(!Ready)
  return;

 int out_q_size=int(out_q.size());
 int weights_size_1=int(weights[0].size())-1;
 real* wp,*xp=&(in_x[0]);
 for(i=0;i<out_q_size;++i)
  {
   sum=0;
   wp=&(weights[i][0]);
   xp=&(in_x[0]);
   for(j=0;j<weights_size_1;wp++,xp++,j++)
	sum+=(*wp)*(*xp);
   out_q[i]=ActiveFunc(sum-(*wp)*0.5);
  }
}


// Производит расчет всей сети
void NCRPerseptron::CalcNetwork(vector<real> &inputs)
{
 size_t i;
 vector<real> *p_inputs;

 if(!Ready)
  return;


 // Аналогично проводим расчет на всех слоях кроме последнего
 // вплоть до предпоследнего включительно
 p_inputs=&inputs;
 for(i=0;i<NumLayers;i++)
  {
   CalcLayer(*p_inputs,Outputs[i],Weights[i],Sigmoid);
   p_inputs=&(Outputs[i]);
  }

}
// ------------------------


}
#endif

