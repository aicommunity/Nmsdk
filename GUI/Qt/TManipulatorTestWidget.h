#ifndef TMANIPULATORTESTWIDGET_H
#define TMANIPULATORTESTWIDGET_H

#include "UVisualControllerWidget.h"

#include <string>

class QCheckBox;
class QGroupBox;
class QLabel;
class QLineEdit;
class QProgressBar;
class QPushButton;
class QSlider;
class QSpinBox;
class QWidget;
class QCustomPlot;
class QCPBars;

// Qt-аналог ManipulatorTestUnit (GUI/BCB), model-only версия.
// В BCB использовались:
// - UGraphics/UBitmap для рисования манипулятора
// - TChart/TBarSeries для IO-графиков (angle, speed, moment, separators)
// - Прямой доступ к NManipulatorSource, NConstGenerator, NANet
// - NWPhysicalManipulator для физического устройства (OnDevice/OffDevice, ComPort)
//
// Здесь создаем model-only версию:
// - QPainter для рисования манипулятора и бар-графиков
// - Управление параметрами через модель (Moment, II Afferent, чекбоксы Ia/Ib/II, Control Voltage)
// - Исключаем физическое устройство (OnDevice/OffDevice, ComPort, InitManipulator)
class TManipulatorTestWidget : public UVisualControllerWidget
{
    Q_OBJECT

public:
    explicit TManipulatorTestWidget(QWidget *parent = nullptr, RDK::UApplication *app = nullptr);
    ~TManipulatorTestWidget() override;

    void AUpdateInterface() override;
    void AClearInterface() override;
    void ASaveParameters(RDK::USerStorageXML &xml) override;
    void ALoadParameters(RDK::USerStorageXML &xml) override;

protected:
    void paintEvent(QPaintEvent *event) override;

private slots:
    void onManipulatorNameEdited();
    void onControlSystemNameEdited();
    void onMomentSliderChanged(int value);
    void onMomentEdited();
    void onIIAfferentSliderChanged(int value);
    void onIIAfferentEdited();
    void onIINumAfferentChanged(int value);
    void onIaCheckBoxToggled(bool checked);
    void onIbCheckBoxToggled(bool checked);
    void onIICheckBoxToggled(bool checked);
    void onControlVoltageCheckBoxToggled(bool checked);

private:
    std::string manipulatorName_;
    std::string controlSystemName_;

    // UI элементы
    QGroupBox *namesGroup_;
    QLineEdit *manipulatorNameEdit_;
    QLineEdit *controlSystemNameEdit_;

    QGroupBox *momentGroup_;
    QSlider *momentSlider_;
    QProgressBar *momentProgressBar_;
    QLineEdit *extMomentEdit_;

    QGroupBox *iiAfferentGroup_;
    QSlider *iiAfferentSlider_;
    QLineEdit *iiAfferentEdit_;
    QSpinBox *iiNumAfferentSpinBox_;

    QGroupBox *receptorsGroup_;
    QCheckBox *iaCheckBox_;
    QCheckBox *ibCheckBox_;
    QCheckBox *iiCheckBox_;
    QCheckBox *controlVoltageCheckBox_;

    QWidget *canvasWidget_ = nullptr;
    QCustomPlot *ioPlot_ = nullptr;
    QCPBars *ioBars_ = nullptr;
    QCPBars *sepBars_ = nullptr;
    QCPBars *engineBars_ = nullptr;

    // Данные для визуализации
    double angle_ = 0.0;
    double movement_ = 0.0;
    int angleIO_ = 0;
    int speedIO_ = 0;
    int momentIO_ = 0;
    int sepAngleIO_ = 0;
    int sepSpeedIO_ = 0;
    int sepMomentIO_ = 0;
    double engineOutput_ = 0.0;
    double engineInput_ = 0.0;

    static constexpr int kCanvasWidth = 640;
    static constexpr int kCanvasHeight = 480;
    static constexpr double kLength = 100.0;
    static constexpr int kSliderMax = 100;

    void updateFromModel();
    void updateIOInformation();
    void updateIOPlot();
    void writeArrow(QPainter &painter, int x, int y, int width, double direction);
    std::string buildComponentPath(const std::string &componentName);
};

#endif // TMANIPULATORTESTWIDGET_H
