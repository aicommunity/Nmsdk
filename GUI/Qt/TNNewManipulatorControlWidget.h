#ifndef TNNEWMANIPULATORCONTROLWIDGET_H
#define TNNEWMANIPULATORCONTROLWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QCheckBox;
class QComboBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QProgressBar;
class QPushButton;
class QSlider;
class QSpinBox;
class QTabWidget;

class NControlSystemSettingsWidget;

// Qt-аналог TNewManipulatorControlForm из GUI/BCB.
// Управление манипулятором и системой управления только через модель (без физического устройства).
// Отличия от TNManipulatorControlWidget: нет Ia/Ib/II чекбоксов, есть II Afferent (частота + число),
// момент и движение, Control voltage, отображение Angle/Movement и NumMotionElements/NumControlLoops.
class TNNewManipulatorControlWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TNNewManipulatorControlWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TNNewManipulatorControlWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

private slots:
    void onManipulatorNameEdited();
    void onControlSystemNameEdited();
    void onControlVoltageCheckBoxToggled(bool checked);
    void onMomentSliderChanged(int value);
    void onMovementSliderChanged(int value);
    void onIIAfferentSliderChanged(int value);
    void onIINumAfferentChanged(int value);
    void onNumMotionElementsSliderChanged(int value);
    void onNumMotionElementsEdited();
    void onNumControlLoopsSliderChanged(int value);
    void onNumControlLoopsEdited();
    void onVoltageMulSliderChanged(int value);
    void onVoltageMulEdited();
    void onTimeDurationSliderChanged(int value);
    void onTimeDurationEdited();
    void onVaEdited();
    void onVdEdited();
    void onSendVClicked();

private:
    std::string manipulatorName_;
    std::string controlSystemName_;

    double angle_ = 0.0;
    double movement_ = 0.0;
    int numMotionElements_ = 0;
    int numControlLoops_ = 0;

    QLineEdit *manipulatorNameEdit_;
    QLineEdit *controlSystemNameEdit_;
    QLabel *angleLabel_;
    QLabel *movementLabel_;
    QLabel *numMotionLabel_;
    QLabel *numControlLoopsLabel_;
    QCheckBox *controlVoltageCheckBox_;
    QGroupBox *momentGroup_;
    QSlider *momentSlider_;
    QProgressBar *momentProgressBar_;
    QLineEdit *extMomentEdit_;
    QGroupBox *movementGroup_;
    QSlider *movementSlider_;
    QProgressBar *movementProgressBar_;
    QLineEdit *movementEdit_;
    QGroupBox *iiAfferentGroup_;
    QSlider *iiAfferentSlider_;
    QLineEdit *iiAfferentEdit_;
    QSpinBox *iiNumAfferentSpinBox_;
    QGroupBox *numMotionElementsGroup_;
    QSlider *numMotionElementsSlider_;
    QLineEdit *numMotionElementsEdit_;
    QGroupBox *numControlLoopsGroup_;
    QSlider *numControlLoopsSlider_;
    QLineEdit *numControlLoopsEdit_;
    QGroupBox *manipulatorParamsGroup_;
    QSlider *voltageMulSlider_;
    QLineEdit *voltageMulEdit_;
    QSlider *timeDurationSlider_;
    QLineEdit *timeDurationEdit_;
    QLineEdit *vaEdit_;
    QLineEdit *vdEdit_;
    QPushButton *sendVButton_;
    QTabWidget *tabWidget_;
    NControlSystemSettingsWidget *controlSystemSettingsWidget_;

    void readComponentData();
    void applyControlVoltageLinks(bool checked);
    void updateControlVoltageFromModel();
    void updateMomentFromModel();
    void updateMovementFromModel();
    void updateIIAfferentFromModel();
    void applyIIAfferentLinks(int numAfferent);
    void updateNumMotionElementsFromModel();
    void updateNumControlLoopsFromModel();
    void updateManipulatorParamsFromModel();
};

#endif // TNNEWMANIPULATORCONTROLWIDGET_H
