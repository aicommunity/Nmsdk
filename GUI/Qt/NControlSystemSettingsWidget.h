#ifndef NCONTROLSYSTEMSETTINGSWIDGET_H
#define NCONTROLSYSTEMSETTINGSWIDGET_H

#include <QWidget>

#include <string>

class QCheckBox;
class QComboBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QListWidget;
class QSlider;
class QSpinBox;
class QPushButton;

// Виджет для управления параметрами системы управления (NEngineMotionControl):
// PAC (Gain, SecretionTC, DissociationTC), ActiveContours, BranchMode, RenshowMode и др.
// Только модель: ReadParameterValue/WriteParameterValue.
class NControlSystemSettingsWidget : public QWidget
{
    Q_OBJECT

public:
    explicit NControlSystemSettingsWidget(QWidget *parent = nullptr);
    ~NControlSystemSettingsWidget() override;

    void setControlSystemName(const std::string &name);
    std::string controlSystemName() const { return controlSystemName_; }

    void updateFromModel();
    void clear();

signals:
    void controlSystemNameChanged(const std::string &name);

private slots:
    void onPacGainSliderChanged(int value);
    void onPacActivatorTimeSliderChanged(int value);
    void onPacDeactivatorTimeSliderChanged(int value);
    void onActiveContourItemChanged();
    void onBranchModeCheckBoxToggled(bool checked);
    void onRenshowModeCheckBoxToggled(bool checked);
    void onAfferentRangeModeChanged(int index);
    void onUseSimpleAfferentsCheckBoxToggled(bool checked);
    void onUseNewNeuronsCheckBoxToggled(bool checked);
    void onTransientTimeEdited();
    void onEnableStructuralAdaptationCheckBoxToggled(bool checked);
    void onMaxAmpEdited();
    void onMinAmpEdited();

private:
    std::string controlSystemName_;
    int numControlLoops_ = 0;

    QGroupBox *pacGroup_;
    QSlider *pacGainSlider_;
    QLineEdit *pacGainEdit_;
    QSlider *pacActivatorTimeSlider_;
    QLineEdit *pacActivatorTimeEdit_;
    QSlider *pacDeactivatorTimeSlider_;
    QLineEdit *pacDeactivatorTimeEdit_;

    QGroupBox *contoursGroup_;
    QListWidget *activeContoursList_;

    QGroupBox *modesGroup_;
    QCheckBox *branchModeCheckBox_;
    QCheckBox *renshowModeCheckBox_;
    QComboBox *afferentRangeModeComboBox_;
    QCheckBox *useSimpleAfferentsCheckBox_;
    QCheckBox *useNewNeuronsCheckBox_;

    QGroupBox *contourGroup_;
    QLineEdit *currentContourAmplitudeEdit_;
    QLineEdit *currentContourAverageEdit_;
    QLineEdit *transientTimeEdit_;
    QCheckBox *currentTransientStateCheckBox_;
    QLineEdit *instantAvgSpeedEdit_;

    QGroupBox *structuralAdaptationGroup_;
    QCheckBox *enableStructuralAdaptationCheckBox_;
    QLineEdit *maxAmpEdit_;
    QLineEdit *minAmpEdit_;

    bool updateInProgress_ = false;

    void updatePACFromModel();
    void updateActiveContoursFromModel();
    void updateModesFromModel();
    void updateContourFromModel();
    void updateStructuralAdaptationFromModel();
};

#endif // NCONTROLSYSTEMSETTINGSWIDGET_H
