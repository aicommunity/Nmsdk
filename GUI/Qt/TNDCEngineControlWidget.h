#ifndef TNDCEENGINECONTROLWIDGET_H
#define TNDCEENGINECONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QCheckBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QProgressBar;
class QSlider;

// Qt-аналог TNDCEngineControlFormUnit из GUI/BCB.
// Управление DC-двигателем только через модель (без физического манипулятора).
class TNDCEngineControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNDCEngineControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNDCEngineControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;

private slots:
    void onMomentSliderChanged(int value);
    void onIaCheckBoxToggled(bool checked);
    void onIbCheckBoxToggled(bool checked);
    void onIICheckBoxToggled(bool checked);
    void onControlVoltageCheckBoxToggled(bool checked);

private:
    std::string motionControlName_;
    std::string componentName_;

    int canvasWidth_;
    int canvasHeight_;
    double x_;
    double y_;
    double angle_;
    double length_;

    QGroupBox *afferentGroup_;
    QCheckBox *iaCheckBox_;
    QCheckBox *ibCheckBox_;
    QCheckBox *iiCheckBox_;
    QCheckBox *controlVoltageCheckBox_;
    QGroupBox *momentGroup_;
    QSlider *momentSlider_;
    QProgressBar *momentProgressBar_;
    QLineEdit *extMomentEdit_;

    void readComponentData();
    void applyIaLinks(bool checked);
    void applyIbLinks(bool checked);
    void applyIILinks(bool checked);
    void applyControlVoltageLinks(bool checked);
    void updateCheckboxesFromModel();
};

#endif // TNDCEENGINECONTROLWIDGET_H

