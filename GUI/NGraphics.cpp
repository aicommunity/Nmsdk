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
#ifndef N_GRAPHICS_CPP
#define N_GRAPHICS_CPP

#include "NGraphics.h"

namespace NMSDK {

	// ------------------------
	// Конструкторы и деструкторы
	// ------------------------
	NVDescription::NVDescription(void) {
		// ------------------------
		// Геометрические параметры
		// ------------------------
		// Координаты элемента в пикселях
		X = -1;
		Y = -1;

		// Радиус элемента
		Radius = 30;

		// Цвет контура элемента
		ContourColor = UColorT(255, 0, 0, 0);

		// Толщина контура элемента в пикселях
		ContourWidth = 3;

		// Цвет заливки элемента
		FillColor = UColorT(0, 255, 255, 0);

		LinkColor = UColorT(0, 0, 255, 0);

		// Толщина контура связи
		LinkWidth = 2;
		// ------------------------

		// ------------------------
		// Идентификационные параметры
		// ------------------------
		// Одномерный индекс i
		Index = 0;

		// 3D индекс (i,j,k)
		I = 0;
		J = 0;
		K = 0;

		// Id нейрона (если -1 - Id не определен)
		Id = ForbiddenId;

		// Тип элемента
		// 0 - не определено
		// 1 - конечный элемент NAItem
		// 2 - элемент-сеть NANet
		Type = 0;
		// ------------------------

		// ------------------------
		// Индикаторы
		// ------------------------
		// Заполнение индикаторов в %
		// (если -1, то отключен)
		TopIndicator = 10;
		BottomIndicator = 20;
		LeftIndicator = 30;
		RightIndicator = 40;
		// ------------------------

	}

	NVDescription::~NVDescription(void) {
	}
	// ------------------------
	/* ******************************************************************* */

	/* ******************************************************************* */
	// ---------------------------
	// Конструкторы и деструкторы
	// ---------------------------
	NGraphics::NGraphics(void) {
		Net = 0;
		GEngine = 0;

		// Цвет фона
		FoneColor = UColorT(255, 255, 255, 255);

		CanvasWidth = 0;
		CanvasHeight = 0;

		// Цвет пустых индикаторов
		IndicatorEmptyColorTop = UColorT(255, 255, 255, 255);
		IndicatorEmptyColorBottom = UColorT(255, 255, 255, 255);
		IndicatorEmptyColorLeft = UColorT(255, 255, 255, 255);
		IndicatorEmptyColorRight = UColorT(255, 255, 255, 255);

		// Цвет полных индикаторов
		IndicatorFullColorTop = UColorT(255, 0, 0);
		IndicatorFullColorBottom = UColorT(0, 255, 0);
		IndicatorFullColorLeft = UColorT(0, 0, 255);
		IndicatorFullColorRight = UColorT(0, 255, 255);
	}

	NGraphics::~NGraphics(void) {
	}
	// ---------------------------

	// ---------------------------
	// Методы доступа к данным
	// ---------------------------
	// Возвращает указатель на НС
	UANet* NGraphics::GetNet(void) {
		return Net;
	}

	// Возвращает элемент таблицы соответствий
	NVDescription& NGraphics::GetDescription(const UId &id) {
		return Descriptions[id];
	}

	// Возвращает всю таблицу соответсвий
	const map<UId, NVDescription>& NGraphics::GetDescriptions(void) {
		return Descriptions;
	}

	// Возвращает указатель на движок отображения
	UAGraphics* NGraphics::GetGEngine(void) {
		return GEngine;
	}

	// Связывает класс с новой НС
	// Если net == 0 то отключает класс от текущей НС и возвращает true
	bool NGraphics::SetNet(UANet *net) {
		if (Net == net)
			return true;

		Net = net;
		BuildDestinations();
		return true;
	}

	// Связывает класс с новой НС
	// Если engine == 0 то возвращает false и не делеает ничего
	bool NGraphics::SetEngine(UAGraphics* engine) {
		if (GEngine == engine)
			return true;

		GEngine = engine;
		CanvasWidth = GEngine->GetCWidth();
		CanvasHeight = GEngine->GetCHeight();

		Draw();
		return true;
	}

	// Обновляет таблицу соответствий
	void NGraphics::UpdateDescriptions(void) {
	}
	// ---------------------------

	// ---------------------------
	// Методы размещения элементов по графическому полю
	// ---------------------------
	// Метод автоматического распределения существующих элементов по полю
	void NGraphics::BuildDestinations(void) {
		Descriptions.clear();
		UpdateDestinations();
	}

	// Метод автоматического распределения нераспределенных элементов
	// (нераспределенные элементы имеют координаты -1,-1)
	void NGraphics::UpdateDestinations(void) {
		if (!Net)
			return;
		/*
		size_t numcomps=Net->GetComponentsList().size();
		map<string,UId>::const_iterator I,J;
		map<UId,NVDescription>::iterator dI;
		I=Net->GetComponentsList().begin();
		J=Net->GetComponentsList().end();

		// Вычисляем допустимое число элементов по горизонтали и вертикали.
		// Пытаемся разместить все объекты квадратом
		int xres=static_cast<int>(ceil(sqrt(float(numcomps))));
		if(xres<=0)
		xres=1;
		ElementsXRes=xres;
		ElementsYRes=numcomps/xres;
		if(ElementsXRes*ElementsYRes<int(numcomps))
		++ElementsXRes;

		int i=0,j=0,l=0;
		while(I != J)
		{
		dI=Descriptions.find(I->second);
		if(dI == Descriptions.end())
		{
		Descriptions[I->second].Index=l;
		Descriptions[I->second].I=i;
		Descriptions[I->second].J=j;
		Descriptions[I->second].X=(CanvasWidth/ElementsXRes)*i+(CanvasWidth/ElementsXRes)/2;
		Descriptions[I->second].Y=(CanvasHeight/ElementsYRes)*j+(CanvasHeight/ElementsYRes)/2;
		if(dynamic_cast<NAItem*>(Net->GetComponent(I->second)))
		{
		Descriptions[I->second].Radius=10;
		Descriptions[I->second].Type=1;
		}
		else
		if(dynamic_cast<UANet*>(Net->GetComponent(I->second)))
		{
		Descriptions[I->second].Radius=15;
		Descriptions[I->second].Type=2;
		}

		Descriptions[I->second].Name=Net->GetComponent(I->second)->Name;


		++l; ++i;
		if(i >= ElementsXRes)
		{
		i=0;
		++j;
		}
		}
		++I;
		} */
	}

	// Устанавливает координаты размещения элемента id
	// Возвращает false если элемент не найден или координаты некорректны
	// Метод не проверяет свободна-ли занимаемая область
	bool NGraphics::SetDestination(const UId &id, int x, int y) {

		return true;
	}
	// ---------------------------

	// ---------------------------
	// Основные методы отображения
	// ---------------------------
	// Метод перерисовки всех элементов
	void NGraphics::Draw(void) {
		GEngine->SetPenColor(FoneColor);
		GEngine->SetPenWidth(1);

		GEngine->Rect(0, 0, CanvasWidth, CanvasHeight, true);
		map<UId, NVDescription>::iterator I, J;
		I = Descriptions.begin();
		J = Descriptions.end();

		while (I != J) {
			if (!Draw(I->first))
				return;

			if (!DrawLinks(I->first))
				return;
			++I;
		}
	}

	// Метод обновления изображения отдельного элемента сети
	// Возвращает false если элемент не найден
	bool NGraphics::Draw(const UId &id) {
		map<UId, NVDescription>::iterator I = Descriptions.find(id);

		if (I == Descriptions.end())
			return false;

		Paint(I->second);

		return true;
	}

	// Метод отображения связей элемента сети
	// (показывает с какими элементами связан этот элемент)
	// links==true - отображает схему связей линиями
	// highlight==true - подсвечивает все нейроны связанные с этим
	// (сам нейрон подсвечивается в случае, если на него есть обратные связи)
	// contour==true - окружает контуром нейроны связанные с этим
	// (в контур могут попасть и не связанные нейроны)
	bool NGraphics::DrawLinks(const UId &id, bool links, bool highlight,
		bool contour) {
		NVDescription out, in;

		RDK::ULinksList linkslist;

		UEPtr<UAItem>item = dynamic_pointer_cast<UAItem>(Net->GetComponent(id));
		out = Descriptions[id];

		for (int i = 0; i < Net->GetNumComponents(); i++) {
			linkslist.Clear();
			if (item != Net->GetComponentByIndex(i)) {
				item->GetFullItemLinks(linkslist,
					dynamic_pointer_cast<UAItem>(Net->GetComponentByIndex(i)),
					Net);
				if (linkslist.GetSize() > 0) {
					in = Descriptions[Net->GetComponentByIndex(i)->GetId()];
					PaintLink(out, in, links, highlight, contour);
				}

			}
		}

		/*
		NAItem* item=dynamic_cast<NAItem*>(Net->GetComponent(id));
		if(item)
		{
		for(size_t i=0;i<item->NumOutputs;i++)
		{
		for(size_t j=0;j<item->GetNumAConnectors(i);j++)
		{
		in=Descriptions[item->GetAConnector(int(i),j)->Id];
		PaintLink(out, in, links, highlight, contour);
		}
		}
		}
		 */
		return true;
	}
	// ---------------------------

	// ---------------------------
	// Вспомогательные методы отображения
	// ---------------------------
	// Отрисовывает элемент в заданной позиции
	void NGraphics::Paint(NVDescription &ndescr, bool highlight) {
		if (!GEngine)
			return;

		switch(ndescr.Type) {
		case 1:
			PaintItem(ndescr, highlight);
			break;

		case 2:
			PaintNet(ndescr, highlight);
			break;
		}

		// Отрисовываем индикаторы
		PaintIndicator(ndescr.X - ndescr.Radius,
			ndescr.Y + ndescr.Radius + ndescr.ContourWidth, ndescr.Radius * 2,
			ndescr.Radius / 2, ndescr.TopIndicator, 1, IndicatorFullColorTop,
			IndicatorEmptyColorTop);
		PaintIndicator(ndescr.X - ndescr.Radius,
			ndescr.Y - ndescr.Radius - ndescr.ContourWidth * 3,
			ndescr.Radius * 2, ndescr.Radius / 2, ndescr.BottomIndicator, 1,
			IndicatorFullColorBottom, IndicatorEmptyColorBottom);
		PaintIndicator(ndescr.X - ndescr.Radius - ndescr.Radius / 2 -
			ndescr.ContourWidth, ndescr.Y - ndescr.Radius, ndescr.Radius / 2,
			ndescr.Radius * 2, ndescr.LeftIndicator, 3, IndicatorFullColorLeft,
			IndicatorEmptyColorLeft);
		PaintIndicator(ndescr.X + ndescr.Radius + ndescr.ContourWidth,
			ndescr.Y - ndescr.Radius, ndescr.Radius / 2, ndescr.Radius * 2,
			ndescr.RightIndicator, 3, IndicatorFullColorRight,
			IndicatorEmptyColorRight);

		// Отрисовываем имя
		GEngine->SetPenColor(ndescr.ContourColor);
		// GEngine->Text(ndescr.Name,ndescr.X-ndescr.Radius*3,static_cast<int>(ndescr.Y-ndescr.Radius*3.5));
	}

	// Отрисовывает конечный элемент (NAItem*) с центром в заданной позиции
	void NGraphics::PaintItem(NVDescription &ndescr, bool highlight) {
		GEngine->SetPenWidth(ndescr.ContourWidth);
		if (ndescr.ContourColor == ndescr.FillColor) {
			GEngine->SetPenColor(ndescr.ContourColor);
			GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, true);
		}
		else {
			if (highlight) {
				GEngine->SetPenColor(ndescr.FillColor);
				GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, false);

				GEngine->SetPenColor(ndescr.ContourColor);
				GEngine->Circle(ndescr.X, ndescr.Y,
					ndescr.Radius -
					(ndescr.ContourWidth + ndescr.ContourWidth /
						2 - 2), true);
			}
			else {
				GEngine->SetPenColor(ndescr.ContourColor);
				GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, false);

				GEngine->SetPenColor(ndescr.FillColor);
				GEngine->Circle(ndescr.X, ndescr.Y,
					ndescr.Radius -
					(ndescr.ContourWidth + ndescr.ContourWidth /
						2 - 2), true);
			}
		}
	}

	// Отрисовывает элемент-сеть (UANet*) с центром в заданной позиции
	void NGraphics::PaintNet(NVDescription &ndescr, bool highlight) {
		GEngine->SetPenWidth(ndescr.ContourWidth);
		if (ndescr.ContourColor == ndescr.FillColor) {
			GEngine->SetPenColor(ndescr.ContourColor);
			GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, true);
		}
		else {
			if (highlight) {
				GEngine->SetPenColor(ndescr.ContourColor);
				GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, false);

				GEngine->SetPenColor(ndescr.FillColor);
				GEngine->Circle(ndescr.X, ndescr.Y,
					ndescr.Radius - ndescr.ContourWidth, true);
			}
			else {
				GEngine->SetPenColor(ndescr.FillColor);
				GEngine->Circle(ndescr.X, ndescr.Y, ndescr.Radius, false);

				GEngine->SetPenColor(ndescr.ContourColor);
				GEngine->Circle(ndescr.X, ndescr.Y,
					ndescr.Radius - ndescr.ContourWidth, true);
			}
		}
	}

	// Отрисовывает индикатор с заданными параметрами
	// Направление direction задается следующим образом
	// 1 - индикатор заполняется слева направо
	// 2 - индикатор заполняется справа налево
	// 3 - индикатор заполняется сверху вниз
	// 4 - индикатор заполняется снизу вверх
	void NGraphics::PaintIndicator(int x, int y, int width, int height,
		double precent, int direction, UColorT full, UColorT empty) {
		if (precent < 0)
			return;

		GEngine->SetPenWidth(1);
		GEngine->SetPenColor(empty);
		GEngine->Rect(x, y, x + width, y + height, true);
		GEngine->SetPenColor(full);
		GEngine->Rect(x, y, x + width, y + height, false);

		switch(direction) {
		case 1:
			GEngine->Rect(x, y, x +static_cast<int>((width * precent) / 100.0),
				y + height, true);
			break;

		case 2:
			GEngine->Rect
				(x +static_cast<int>((width - (width * precent) / 100.0)),
				y, x + width, y + height, true);
			break;

		case 3:
			GEngine->Rect(x, y, x + width,
				y +static_cast<int>((height * precent) / 100.0), true);
			break;

		case 4:
			GEngine->Rect(x,
				y +static_cast<int>((height - (height * precent) / 100.0)),
				x + width, y + height, true);
			break;
		}
	}

	// Отрисовывает связь
	void NGraphics::PaintLink(NVDescription &out, NVDescription &in,
		bool links, bool highlight, bool contour) {
		if (!GEngine)
			return;

		if (links) {
			GEngine->SetPenColor(out.LinkColor);
			GEngine->SetPenWidth(out.LinkWidth);
			GEngine->Line(out.X + out.Radius, out.Y, in.X - in.Radius, in.Y);
			GEngine->Rect(in.X - in.Radius - out.LinkWidth,
				in.Y - out.LinkWidth,
				in.X - in.Radius + out.LinkWidth, in.Y + out.LinkWidth, true);
		}

		if (highlight) {
			PaintItem(out, true);
			PaintItem(in, true);
		}

		if (contour) {
		}

	}
	// Отрисовывает окружность
	// ---------------------------

}
#endif

