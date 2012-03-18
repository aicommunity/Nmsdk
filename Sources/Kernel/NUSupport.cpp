/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:		alexab@ailab.ru
url:        http://ailab.ru
Version:    1.0.0

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#include "NUSupport.h"

namespace NMSDK {

// Записывает изображение в bitmap
RDK::UBitmap& operator << (RDK::UBitmap &bmp, const RDK::UItemData &data)
{
 if(data.GetByteSize()<int(sizeof(int)*3))
  return bmp;

 bmp.SetRes(data.Int[0],data.Int[1],static_cast<RDK::UBMColorModel>(data.Int[1]));

 if(size_t(bmp.GetByteLength()) != (data.GetByteSize()-sizeof(int)*3))
  return bmp;

 bmp.SetImage(data.UChar+sizeof(int)*3);
 return bmp;
}

// Записывает изображение в data
// data.DataSize устанавливается = 1
// Формал записи: Width,Height,ColorModel,<данные>
RDK::UItemData& operator >> (const RDK::UBitmap &bmp, RDK::UItemData &data)
{
 data.Assign(bmp.GetLength(),1,bmp.GetData(),sizeof(int)*3);
 data.Int[0]=bmp.GetWidth();
 data.Int[1]=bmp.GetWidth();
 data.Int[2]=bmp.GetColorModel();
 return data;
}


// Записывает изображение в data
// Предполагает, что память уже выделена
// Формал записи: Width,Height,ColorModel,<данные>
const RDK::UItemData& operator >> (const RDK::UBitmap &bmp, const RDK::UItemData &data)
{
 data.Assign(bmp.GetLength(),bmp.GetData(),sizeof(int)*3);
 data.Int[0]=bmp.GetWidth();
 data.Int[1]=bmp.GetWidth();
 data.Int[2]=bmp.GetColorModel();
 return data;
}

}
