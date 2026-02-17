#ifndef TNDCEENGINECONTROLWIDGET_H
#define TNDCEENGINECONTROLWIDGET_H

#include "UVisualControllerWidget.h"

// Qt-аналог TNDCEngineControlFormUnit из GUI/BCB.
// Управление DC-двигателем будет перенесено сюда по мере миграции логики.
class TNDCEngineControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNDCEngineControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNDCEngineControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
};

#endif // TNDCEENGINECONTROLWIDGET_H

