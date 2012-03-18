//---------------------------------------------------------------------------

#ifndef CRFeatureSelectorH
#define CRFeatureSelectorH
#include <vector>
#include <map>
#include <string>
#include <string>
#include <memory>
#include <vector>
#include <UBitmap.h>
#include <CVUBitmap.h>
//#include "UModule.h"
#include "NBios.h"


using namespace std;
using namespace MySDK;

#include "cxcore.h"

//typedef float real;

using namespace NMSDK;
//---------------------------------------------------------------------------
class CRFeatureSelectorpublic NANet//UModule
{
public: // Параметры
// Режим накопления статистики
// 0 - по максимуму
// 1 - по среднему
RDK::ULProperty<int,CRFeatureSelector> StatisticMode;

protected: // Данные
// Входное изображение
UBitmap InputImage;

public:
map<string,vector<UBitmap> > *BmpTrainSample;

public:
// ---------------------
// Конструкторы и деструкторы
// ---------------------
CRFeatureSelector(const string &name);
virtual ~CRFeatureSelector(void);
// ---------------------

// ---------------------
// Методы управления параметрами
// ---------------------
protected:
// Режим накопления статистики
bool SetStatisticMode(int value);
// ---------------------

// ---------------------
// Методы доступа к данным
// ---------------------
public:
// Вектор входов
const UBitmap& GetInputImage(void) const;
// ---------------------

// ---------------------
// Методы счета
// ---------------------
// Метод задания входного вектора
virtual bool SetInputImage(const UBitmap &input);

// Инициализация
virtual void Init(void)=0;

// Деинициализация
virtual void UnInit(void)=0;
// ---------------------

// ---------------------
// Методы сериализации
// ---------------------
virtual bool SaveToFile(const std::string &filename)=0;
virtual bool LoadFromFile(const std::string &filename)=0;
// ---------------------

};
//---------------------------------------------------------------------------
#endif
