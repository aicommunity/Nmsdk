#ifndef TNMANIPULATORCONTROLWIDGET_H
#define TNMANIPULATORCONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QCheckBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QProgressBar;
class QSlider;

// Qt-аналог TNManipulatorControlForm из GUI/BCB.
// Только работа с моделью: выбор компонентов по имени, чтение Angle/Movement,
// переключение афферентов и момента через Model_* и Read/WriteParameterValue.
// Без доступа к физическому манипулятору (COM/DLL).
class TNManipulatorControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNManipulatorControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNManipulatorControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onManipulatorNameEdited();
    void onControlSystemNameEdited();
    void onMomentSliderChanged(int value);
    void onMovementControlSliderChanged(int value);
    void onIaCheckBoxToggled(bool checked);
    void onIbCheckBoxToggled(bool checked);
    void onIICheckBoxToggled(bool checked);
    void onControlVoltageCheckBoxToggled(bool checked);

private:
    std::string manipulatorName_;
    std::string controlSystemName_;

    int canvasWidth_;
    int canvasHeight_;
    double x_;
    double y_;
    double angle_;
    double movement_;
    double length_;
    double zeroAngle_;
    double zeroMovement_;
    std::string readComponentName_;

    QLineEdit *manipulatorNameEdit_;
    QLineEdit *controlSystemNameEdit_;
    QLabel *angleLabel_;
    QLabel *movementLabel_;
    QGroupBox *afferentGroup_;
    QCheckBox *iaCheckBox_;
    QCheckBox *ibCheckBox_;
    QCheckBox *iiCheckBox_;
    QCheckBox *controlVoltageCheckBox_;
    QGroupBox *momentGroup_;
    QSlider *momentSlider_;
    QProgressBar *momentProgressBar_;
    QLineEdit *extMomentEdit_;
    QGroupBox *movementControlGroup_;
    QSlider *movementControlSlider_;
    QProgressBar *movementControlProgressBar_;
    QLineEdit *movementControlEdit_;

    void loadInterfaceInfoFromNet();
    void readComponentData();
    void applyIaLinks(bool checked);
    void applyIbLinks(bool checked);
    void applyIILinks(bool checked);
    void applyControlVoltageLinks(bool checked);
    void updateCheckboxesFromModel();
    void updateMomentFromModel();
    void updateMovementControlFromModel();
};

#endif // TNMANIPULATORCONTROLWIDGET_H

