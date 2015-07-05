// ===========================================================
// Version:        1.0.0
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2009.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */
#ifndef N_GRAPHICS_H
#define N_GRAPHICS_H

#include "../Libraries/Nmsdk-BasicLib/Core/NSupport.h"
#include "rdk.h"

namespace NMSDK {

//using namespace RDK;
using RDK::UColorT;
using RDK::UBColor;
using RDK::UBitmap;
using RDK::UAGraphics;
using RDK::UGraphics;
using RDK::UBitmapFont;


/*
	���������, ����������� ������ NAContainer* ��� ���������� �������
*/
struct NVDescription
{
// ------------------------
// ����������������� ���������
// ------------------------
// ���������� ������ i
int Index;

// 3D ������ (i,j,k)
// I,J - ���������� ������ � ��������� K
int I, J, K;

// ��� ��������
string Name;

// Id �������� (���� -1 - Id �� ���������)
UId Id;

// ��� ��������
// 0 - �� ����������
// 1 - �������� ������� NAItem
// 2 - �������-���� NANet
int Type;
// ------------------------

// ------------------------
// �������������� ���������
// ------------------------
// ���������� �������� � ��������
int X,Y;

// ������ �������� � ��������
int Radius;

// ���� ������� ��������
UColorT ContourColor;

// ������� ������� �������� � ��������
int ContourWidth;

// ���� ������� ��������
UColorT FillColor;

// ���� ��������� ������
UColorT LinkColor;

// ������� ������� �����
int LinkWidth;
// ------------------------

// ------------------------
// ����������
// ------------------------
// ���������� ����������� � %
// (���� -1, �� ��������)
double TopIndicator,BottomIndicator,LeftIndicator,RightIndicator;
// ------------------------

// ------------------------
// ������������ � �����������
// ------------------------
NVDescription(void);
~NVDescription(void);
// ------------------------
};

/*
	����� ������������ ����������� ��
*/
class NGraphics
{
protected: // ������
// ��������� �� ��
UNet *Net;

// ������� ������������ ����� ��������� ���� � �������� ���������� ���������
map<UId,NVDescription> Descriptions;

// ������ ��� ����������� ����
UAGraphics* GEngine;

protected: // ���������
// ---------------------------
// ��������� �����������
// ---------------------------
// �������� ������ � ������ �����������
int CanvasWidth, CanvasHeight;

// ����� ��������� � ������
int ElementsXRes;

// ����� ����� ���������
int ElementsYRes;

// ���� ������ �����������
UColorT IndicatorEmptyColorTop;
UColorT IndicatorEmptyColorBottom;
UColorT IndicatorEmptyColorLeft;
UColorT IndicatorEmptyColorRight;

// ���� ������ �����������
UColorT IndicatorFullColorTop;
UColorT IndicatorFullColorBottom;
UColorT IndicatorFullColorLeft;
UColorT IndicatorFullColorRight;

// ���� ����
UColorT FoneColor;
// ---------------------------


public: // ������
// ---------------------------
// ������������ � �����������
// ---------------------------
NGraphics(void);
~NGraphics(void);
// ---------------------------

// ---------------------------
// ������ ������� � ������
// ---------------------------
// ���������� ��������� �� ��
UNet* GetNet(void);

// ���������� ������� ������� ������������
NVDescription& GetDescription(const UId &id);

// ���������� ��� ������� �����������
const map<UId,NVDescription>& GetDescriptions(void);

// ���������� ��������� �� ������ �����������
UAGraphics* GetGEngine(void);

// ��������� ����� � ����� ��
// ���� net == 0 �� ��������� ����� �� ������� �� � ���������� true
bool SetNet(UNet *net);

// ��������� ����� � ����� ��
// ���� engine == 0 �� ���������� false � �� ������� ������
bool SetEngine(UAGraphics* engine);

// ��������� ������� ������������
void UpdateDescriptions(void);
// ---------------------------

// ---------------------------
// ������ ���������� ��������� �� ������������ ����
// ---------------------------
// ����� ��������������� ������������� ������������ ��������� �� ����
void BuildDestinations(void);

// ����� ��������������� ������������� ���������������� ���������
// (���������������� �������� ����� ���������� -1,-1)
void UpdateDestinations(void);

// ������������� ���������� ���������� �������� id
// ���������� false ���� ������� �� ������ ��� ���������� �����������
// ����� �� ��������� ��������-�� ���������� �������
bool SetDestination(const UId &id, int x, int y);
// ---------------------------

// ---------------------------
// �������� ������ �����������
// ---------------------------
// ����� ����������� ���� ���������
void Draw(void);

// ����� ���������� ����������� ���������� �������� ����
// ���������� false ���� ������� �� ������
bool Draw(const UId &id);

// ����� ����������� ������ �������� ����
// (���������� � ������ ���������� ������ ���� �������)
// links==true - ���������� ����� ������ �������
// highlight==true - ������������ ��� ������� ��������� � ����
// (��� ������ �������������� � ������, ���� �� ���� ���� �������� �����)
// contour==true - �������� �������� ������� ��������� � ����
// (� ������ ����� ������� � �� ��������� �������)
bool DrawLinks(const UId &id,
			   bool links=true, bool highlight=false, bool contour=false);
// ---------------------------

// ---------------------------
// ��������������� ������ �����������
// ---------------------------
// ������������ ������� � �������� �������
void Paint(NVDescription &ndescr, bool highlight=false);

// ������������ �������� ������� (NAItem*) � ������� � �������� �������
void PaintItem(NVDescription &ndescr, bool highlight=false);

// ������������ �������-���� (NANet*) � ������� � �������� �������
void PaintNet(NVDescription &ndescr, bool highlight=false);

// ������������ �����
void PaintLink(NVDescription &out, NVDescription &in,
			   bool links=true, bool highlight=true, bool contour=true);


// ������������ ��������� � ��������� �����������
// ����������� direction �������� ��������� �������
// 1 - ��������� ����������� ����� �������
// 2 - ��������� ����������� ������ ������
// 3 - ��������� ����������� ������ ����
// 4 - ��������� ����������� ����� �����
void PaintIndicator(int x,int y, int width, int height,
				   double precent, int direction, UColorT full, UColorT empty);

// ������������ ����������
// ---------------------------
};

}
#endif


