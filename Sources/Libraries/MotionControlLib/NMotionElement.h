/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.0.0

This file - part of the project: NMSDK

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */
#ifndef NMotionElementH
#define NMotionElementH

#include "../../Kernel/NBios.h"
//---------------------------------------------------------------------------
namespace NMSDK {

// Формирует СУ двигательной единицей
// Если mode == 0 - формируется полная модель
// 	    mode == 1 - модель без вставочных интернейронов
UEPtr<NANet> CreateMotionElement(NStorage *storage, const string &netclassname, int mode);

// Аналогично, но с развязкой по дендритам
UEPtr<NANet> CreateBranchedMotionElement(NStorage *storage, const string &netclassname, int mode);

bool CreateNeuronBranchLink(UEPtr<NANet> net,const string &source,
	const string &target_head, const string &target_tail);

}
//---------------------------------------------------------------------------
#endif
