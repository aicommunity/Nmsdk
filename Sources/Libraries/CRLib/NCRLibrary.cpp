/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#include "NCRLibrary.h"


#include "NACRClassifier.cpp"
#include "NCRDirectCompare.cpp"
#include "NCRDistance.cpp"
#include "NCRFusion.cpp"
#include "NCRPerseptron.cpp"
#include "NCRSample.cpp"



namespace NMSDK {   

NCRLibrary CRLibrary;

// --------------------------
// Конструкторы и деструкторы
// --------------------------
NCRLibrary::NCRLibrary(void)
 : NLibrary("CRLibrary","1.0")
{
}
// --------------------------

// --------------------------
// Методы заполенения бибилиотеки
// --------------------------
// Заполняет массив ClassSamples готовыми экземплярами образцов и их именами.
// Не требуется предварительная очистка массива и уборка памяти.
void NCRLibrary::ACreateClassSamples(NStorage *storage)
{
 NAContainer *cont;

 cont=new NCRPerseptron;
 cont->SetName("Perseptron");
 cont->Default();
 UploadClass("NCRPerseptron",cont);

 cont=new NCRDirectCompare;
 cont->SetName("DirectCompare");
 cont->Default();
 UploadClass("NDirectCompare",cont);

 cont=new NCRDistance;
 cont->SetName("Distance");
 cont->Default();
 UploadClass("NCRDistance",cont);

 cont=new NCRFusion;
 cont->SetName("Fusion");
 cont->Default();
 UploadClass("NCRFusion",cont);
}
// --------------------------


}
