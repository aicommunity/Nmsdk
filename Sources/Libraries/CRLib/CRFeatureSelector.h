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
public: // ���������
// ����� ���������� ����������
// 0 - �� ���������
// 1 - �� ��������
RDK::ULProperty<int,CRFeatureSelector> StatisticMode;

protected: // ������
// ������� �����������
UBitmap InputImage;

public:
map<string,vector<UBitmap> > *BmpTrainSample;

public:
// ---------------------
// ������������ � �����������
// ---------------------
CRFeatureSelector(const string &name);
virtual ~CRFeatureSelector(void);
// ---------------------

// ---------------------
// ������ ���������� �����������
// ---------------------
protected:
// ����� ���������� ����������
bool SetStatisticMode(int value);
// ---------------------

// ---------------------
// ������ ������� � ������
// ---------------------
public:
// ������ ������
const UBitmap& GetInputImage(void) const;
// ---------------------

// ---------------------
// ������ �����
// ---------------------
// ����� ������� �������� �������
virtual bool SetInputImage(const UBitmap &input);

// �������������
virtual void Init(void)=0;

// ���������������
virtual void UnInit(void)=0;
// ---------------------

// ---------------------
// ������ ������������
// ---------------------
virtual bool SaveToFile(const std::string &filename)=0;
virtual bool LoadFromFile(const std::string &filename)=0;
// ---------------------

};
//---------------------------------------------------------------------------
#endif
