//---------------------------------------------------------------------------

#ifndef CRFeatureSelectorNoneH
#define CRFeatureSelectorNoneH

#include "CRFeatureSelector.h"

class CRFeatureSelectorNone: public CRFeatureSelector
{
// ---------------------
// Методы счета
// ---------------------
// Метод задания входного вектора
virtual bool SetInputImage(const UBitmap &input);
// ---------------------


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


// ---------------------
// Методы сериализации
// ---------------------
virtual bool SaveToFile(const std::string &filename);
virtual bool LoadToFile(const std::string &filename);
// ---------------------

};
//---------------------------------------------------------------------------
#endif
