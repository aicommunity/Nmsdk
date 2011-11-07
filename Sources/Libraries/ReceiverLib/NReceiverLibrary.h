/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2010.
E-mail:            alexab@ailab.ru
url:            http://ailab.ru
Version:        1.0.0

This file - part of the project: NMSDK

File License:        BSD License
Project License:    GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NReceiverLibraryH
#define NReceiverLibraryH

#include "../../Kernel/NLibrary.h"

#include "NFrequencyReceiver.h"
#include "NReceptor.h"
#include "NManipulatorInput.h"
#include "NManipulatorInputEmulator.h"
#include "NSimpleStatistic.h"
#include "NNetworkLinksStatistic.h"

namespace NMSDK {

class NReceiverLibrary: public NLibrary
{
public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NReceiverLibrary(void);
// --------------------------

// --------------------------
// ������ ����������� �����������
// --------------------------
// ��������� ������ ClassSamples �������� ������������ �������� � �� �������.
// �� ��������� ��������������� ������� ������� � ������ ������.
virtual void ACreateClassSamples(NStorage *storage);
// --------------------------
};    

extern NReceiverLibrary ReceiverLibrary;

}


#endif
