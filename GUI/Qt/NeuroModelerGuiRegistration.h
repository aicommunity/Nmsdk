#ifndef NEUROMODELERGUIREGISTRATION_H
#define NEUROMODELERGUIREGISTRATION_H

#include "UGEngineControlWidget.h"

// Регистрация доменных Qt-виджетов NeuroModeler в UGEngineControlWidget.
// Реализация будет использовать универсальный механизм регистрации
// пользовательских виджетов, добавленный в UGEngineControlWidget.
void RegisterNeuroModelerWidgets(UGEngineControlWidget &mainWindow, RDK::UApplication &app);

#endif // NEUROMODELERGUIREGISTRATION_H

