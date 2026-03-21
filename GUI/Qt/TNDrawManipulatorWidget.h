#ifndef TNDRAWMANIPULATORWIDGET_H
#define TNDRAWMANIPULATORWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QLineEdit;
class QLabel;
class QPaintEvent;

// Qt-аналог NDrawManipulatorFormUnit / NDrawManipulatorFrameUnit из GUI/BCB.
// Визуализация манипулятора по данным модели: имя компонента, чтение Angle/Movement,
// отрисовка одного или двух звеньев на канвасе (только модель, без физического устройства).
class TNDrawManipulatorWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNDrawManipulatorWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNDrawManipulatorWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void onComponentNameEdited();

private:
    std::string componentName_;
    int canvasWidth_;
    int canvasHeight_;
    double x_;
    double y_;
    double angle_;
    double movement_;
    double length_;
    double zeroAngle_;
    double zeroMovement_;

    QLineEdit *componentNameEdit_;
    QLabel *hintLabel_;

    void readComponentData();
};

#endif // TNDRAWMANIPULATORWIDGET_H

