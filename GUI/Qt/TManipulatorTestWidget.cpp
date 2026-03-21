#include "TManipulatorTestWidget.h"

#include <QCheckBox>
#include <QGroupBox>
#include <QLabel>
#include <QLineEdit>
#include <QPainter>
#include <QProgressBar>
#include <QPushButton>
#include <QSlider>
#include <QSpinBox>
#include <QSplitter>
#include <QVBoxLayout>

#include "qcustomplot.h"

#include <rdk_application.h>
#include <rdk_engine_support.h>
#include <rdk_init.h>

#include <cmath>
#include <string>

namespace {

const char kOutputProp[] = "0";

} // namespace

TManipulatorTestWidget::TManipulatorTestWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      namesGroup_(nullptr),
      manipulatorNameEdit_(nullptr),
      controlSystemNameEdit_(nullptr),
      momentGroup_(nullptr),
      momentSlider_(nullptr),
      momentProgressBar_(nullptr),
      extMomentEdit_(nullptr),
      iiAfferentGroup_(nullptr),
      iiAfferentSlider_(nullptr),
      iiAfferentEdit_(nullptr),
      iiNumAfferentSpinBox_(nullptr),
      receptorsGroup_(nullptr),
      iaCheckBox_(nullptr),
      ibCheckBox_(nullptr),
      iiCheckBox_(nullptr),
      controlVoltageCheckBox_(nullptr)
{
    Name = "TManipulatorTestWidget";
    ClassName = "TManipulatorTestWidget";

    const QString title = tr("Manipulator test (model-only)");
    setAccessibleName(title);
    setWindowTitle(title);

    setMinimumSize(kCanvasWidth + 300, kCanvasHeight + 200);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    auto *splitter = new QSplitter(Qt::Horizontal, this);

    // Левая панель: управление
    auto *leftWidget = new QWidget(this);
    auto *leftLayout = new QVBoxLayout(leftWidget);
    leftLayout->setContentsMargins(0, 0, 0, 0);

    namesGroup_ = new QGroupBox(tr("Components (model-only)"), leftWidget);
    auto *namesLayout = new QVBoxLayout(namesGroup_);
    namesLayout->addWidget(new QLabel(tr("Manipulator name:"), namesGroup_));
    manipulatorNameEdit_ = new QLineEdit(namesGroup_);
    manipulatorNameEdit_->setPlaceholderText(tr("e.g. DCEngine"));
    namesLayout->addWidget(manipulatorNameEdit_);
    namesLayout->addWidget(new QLabel(tr("Control system name:"), namesGroup_));
    controlSystemNameEdit_ = new QLineEdit(namesGroup_);
    controlSystemNameEdit_->setPlaceholderText(tr("e.g. N2AsfNewSimplestAfferentBranchedEngineControl"));
    namesLayout->addWidget(controlSystemNameEdit_);
    leftLayout->addWidget(namesGroup_);

    momentGroup_ = new QGroupBox(tr("Moment"), leftWidget);
    auto *momentLayout = new QVBoxLayout(momentGroup_);
    momentSlider_ = new QSlider(Qt::Horizontal, momentGroup_);
    momentSlider_->setRange(-kSliderMax, kSliderMax);
    momentProgressBar_ = new QProgressBar(momentGroup_);
    momentProgressBar_->setRange(0, kSliderMax);
    extMomentEdit_ = new QLineEdit(momentGroup_);
    extMomentEdit_->setPlaceholderText("0.0");
    momentLayout->addWidget(momentSlider_);
    momentLayout->addWidget(momentProgressBar_);
    momentLayout->addWidget(extMomentEdit_);
    leftLayout->addWidget(momentGroup_);

    iiAfferentGroup_ = new QGroupBox(tr("II Afferent"), leftWidget);
    auto *iiLayout = new QVBoxLayout(iiAfferentGroup_);
    iiAfferentSlider_ = new QSlider(Qt::Horizontal, iiAfferentGroup_);
    iiAfferentSlider_->setRange(-kSliderMax, kSliderMax);
    iiAfferentEdit_ = new QLineEdit(iiAfferentGroup_);
    iiAfferentEdit_->setPlaceholderText("0.0");
    iiLayout->addWidget(new QLabel(tr("Amplitude:"), iiAfferentGroup_));
    iiLayout->addWidget(iiAfferentSlider_);
    iiLayout->addWidget(iiAfferentEdit_);
    iiLayout->addWidget(new QLabel(tr("Number:"), iiAfferentGroup_));
    iiNumAfferentSpinBox_ = new QSpinBox(iiAfferentGroup_);
    iiNumAfferentSpinBox_->setRange(0, 10);
    iiLayout->addWidget(iiNumAfferentSpinBox_);
    leftLayout->addWidget(iiAfferentGroup_);

    receptorsGroup_ = new QGroupBox(tr("Receptors"), leftWidget);
    auto *receptorsLayout = new QVBoxLayout(receptorsGroup_);
    iaCheckBox_ = new QCheckBox(tr("Ia"), receptorsGroup_);
    ibCheckBox_ = new QCheckBox(tr("Ib"), receptorsGroup_);
    iiCheckBox_ = new QCheckBox(tr("II"), receptorsGroup_);
    controlVoltageCheckBox_ = new QCheckBox(tr("Control voltage"), receptorsGroup_);
    receptorsLayout->addWidget(iaCheckBox_);
    receptorsLayout->addWidget(ibCheckBox_);
    receptorsLayout->addWidget(iiCheckBox_);
    receptorsLayout->addWidget(controlVoltageCheckBox_);
    leftLayout->addWidget(receptorsGroup_);

    leftLayout->addStretch();
    leftWidget->setLayout(leftLayout);
    splitter->addWidget(leftWidget);

    // Правая панель: canvas + IO-графики (QCustomPlot)
    auto *rightWidget = new QWidget(this);
    auto *rightLayout = new QVBoxLayout(rightWidget);
    rightLayout->setContentsMargins(0, 0, 0, 0);

    canvasWidget_ = new QWidget(rightWidget);
    canvasWidget_->setMinimumSize(kCanvasWidth, kCanvasHeight);
    rightLayout->addWidget(canvasWidget_, 2);

    ioPlot_ = new QCustomPlot(rightWidget);
    ioPlot_->setMinimumHeight(220);
    ioPlot_->legend->setVisible(true);
    ioPlot_->xAxis->setAutoTicks(false);
    ioPlot_->xAxis->setAutoTickLabels(false);
    ioPlot_->xAxis->setRange(-0.5, 7.5);
    ioPlot_->yAxis->setRange(-1.2, 1.2);
    ioPlot_->yAxis->setLabel("IO");

    ioBars_ = new QCPBars(ioPlot_->xAxis, ioPlot_->yAxis);
    ioBars_->setName("IO");
    ioBars_->setWidth(0.25);
    ioBars_->setBrush(QColor(0, 120, 200, 70));

    sepBars_ = new QCPBars(ioPlot_->xAxis, ioPlot_->yAxis);
    sepBars_->setName("Separators");
    sepBars_->setWidth(0.25);
    sepBars_->moveAbove(ioBars_);
    sepBars_->setBrush(QColor(0, 180, 80, 70));

    engineBars_ = new QCPBars(ioPlot_->xAxis, ioPlot_->yAxis);
    engineBars_->setName("Engine");
    engineBars_->setWidth(0.25);
    engineBars_->moveAbove(sepBars_);
    engineBars_->setBrush(QColor(200, 50, 50, 70));

    rightLayout->addWidget(ioPlot_, 1);
    rightWidget->setLayout(rightLayout);
    splitter->addWidget(rightWidget);
    splitter->setStretchFactor(0, 1);
    splitter->setStretchFactor(1, 2);

    mainLayout->addWidget(splitter, 1);
    setLayout(mainLayout);

    connect(manipulatorNameEdit_, &QLineEdit::editingFinished, this, &TManipulatorTestWidget::onManipulatorNameEdited);
    connect(controlSystemNameEdit_, &QLineEdit::editingFinished, this, &TManipulatorTestWidget::onControlSystemNameEdited);
    connect(momentSlider_, &QSlider::valueChanged, this, &TManipulatorTestWidget::onMomentSliderChanged);
    connect(extMomentEdit_, &QLineEdit::editingFinished, this, &TManipulatorTestWidget::onMomentEdited);
    connect(iiAfferentSlider_, &QSlider::valueChanged, this, &TManipulatorTestWidget::onIIAfferentSliderChanged);
    connect(iiAfferentEdit_, &QLineEdit::editingFinished, this, &TManipulatorTestWidget::onIIAfferentEdited);
    connect(iiNumAfferentSpinBox_, QOverload<int>::of(&QSpinBox::valueChanged), this, &TManipulatorTestWidget::onIINumAfferentChanged);
    connect(iaCheckBox_, &QCheckBox::toggled, this, &TManipulatorTestWidget::onIaCheckBoxToggled);
    connect(ibCheckBox_, &QCheckBox::toggled, this, &TManipulatorTestWidget::onIbCheckBoxToggled);
    connect(iiCheckBox_, &QCheckBox::toggled, this, &TManipulatorTestWidget::onIICheckBoxToggled);
    connect(controlVoltageCheckBox_, &QCheckBox::toggled, this, &TManipulatorTestWidget::onControlVoltageCheckBoxToggled);
}

TManipulatorTestWidget::~TManipulatorTestWidget() = default;

void TManipulatorTestWidget::AUpdateInterface()
{
    UpdateInterval = 200;
    updateFromModel();
    updateIOPlot();
    update();
}

void TManipulatorTestWidget::AClearInterface()
{
    manipulatorName_.clear();
    controlSystemName_.clear();
    manipulatorNameEdit_->clear();
    controlSystemNameEdit_->clear();
    angle_ = 0.0;
    movement_ = 0.0;
    angleIO_ = speedIO_ = momentIO_ = 0;
    sepAngleIO_ = sepSpeedIO_ = sepMomentIO_ = 0;
    engineOutput_ = engineInput_ = 0.0;
    update();
}

void TManipulatorTestWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("ManipulatorTest");
    xml.WriteString("ManipulatorName", manipulatorName_);
    xml.WriteString("ControlSystemName", controlSystemName_);
    xml.SelectUp();
}

void TManipulatorTestWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("ManipulatorTest");
    manipulatorName_ = xml.ReadString("ManipulatorName", "");
    controlSystemName_ = xml.ReadString("ControlSystemName", "");
    xml.SelectUp();
    manipulatorNameEdit_->setText(QString::fromStdString(manipulatorName_));
    controlSystemNameEdit_->setText(QString::fromStdString(controlSystemName_));
    updateFromModel();
}

void TManipulatorTestWidget::paintEvent(QPaintEvent *event)
{
    UVisualControllerWidget::paintEvent(event);

    if (!canvasWidget_)
        return;

    const int w = canvasWidget_->width();
    const int h = canvasWidget_->height();
    if (w < 10 || h < 10)
        return;

    QPainter painter(canvasWidget_);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.fillRect(0, 0, w, h, Qt::white);

    // Рисуем манипулятор
    const double cx = w / 2.0;
    const double cy = h / 2.0;
    const double x1 = cx;
    const double y1 = cy;
    const double x2 = x1 + kLength * std::cos(angle_ - M_PI / 2.0);
    const double y2 = y1 + kLength * std::sin(angle_ - M_PI / 2.0);

    painter.setPen(QPen(QColor(0xAA, 0x00, 0xFF), 5));
    painter.drawLine(static_cast<int>(x1), static_cast<int>(y1),
                     static_cast<int>(x2), static_cast<int>(y2));
    painter.setBrush(Qt::black);
    painter.drawEllipse(QPointF(x1, y1), 10, 10);
}

void TManipulatorTestWidget::updateIOPlot()
{
    if (!ioPlot_ || !ioBars_ || !sepBars_ || !engineBars_)
        return;

    updateIOInformation();

    const auto norm = [](double v) -> double {
        if (std::isnan(v) || std::isinf(v))
            return 0.0;
        if (v > 1.0) return 1.0;
        if (v < -1.0) return -1.0;
        return v;
    };

    QVector<double> keys = {0, 1, 2, 3, 4, 5, 6, 7};
    QVector<double> ioVals = {
        norm(double(angleIO_) / kSliderMax),
        norm(double(speedIO_) / kSliderMax),
        norm(double(momentIO_) / kSliderMax),
        0, 0, 0, 0, 0
    };
    QVector<double> sepVals = {
        norm(double(sepAngleIO_) / kSliderMax),
        norm(double(sepSpeedIO_) / kSliderMax),
        norm(double(sepMomentIO_) / kSliderMax),
        0, 0, 0, 0, 0
    };
    QVector<double> engVals = {
        0, 0, 0,
        norm(engineInput_),
        norm(engineOutput_),
        0, 0, 0
    };

    ioBars_->setData(keys, ioVals);
    sepBars_->setData(keys, sepVals);
    engineBars_->setData(keys, engVals);

    ioPlot_->xAxis->setTickVector(keys);
    QVector<QString> labels;
    labels << "Angle" << "Speed" << "Moment" << "EngIn" << "EngOut" << "" << "" << "";
    ioPlot_->xAxis->setTickVectorLabels(labels);
    ioPlot_->replot();
}

void TManipulatorTestWidget::onManipulatorNameEdited()
{
    manipulatorName_ = manipulatorNameEdit_->text().trimmed().toStdString();
    updateFromModel();
}

void TManipulatorTestWidget::onControlSystemNameEdited()
{
    controlSystemName_ = controlSystemNameEdit_->text().trimmed().toStdString();
    updateFromModel();
}

void TManipulatorTestWidget::onMomentSliderChanged(int value)
{
    if (controlSystemName_.empty())
        return;

    const double moment = double(value) / double(kSliderMax / 2.0);
    extMomentEdit_->setText(QString::number(moment, 'f', 3));

    try
    {
        const std::string momentGenPath = buildComponentPath("EngineMoment");
        RDK::WriteParameterValue<double>(momentGenPath, "Amplitude", moment);
    }
    catch (...)
    {
    }

    if (value > 0)
        momentProgressBar_->setValue(value);
    else
        momentProgressBar_->setValue(-value);
}

void TManipulatorTestWidget::onMomentEdited()
{
    if (controlSystemName_.empty())
        return;

    bool ok = false;
    const double moment = extMomentEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;

    try
    {
        const std::string momentGenPath = buildComponentPath("EngineMoment");
        RDK::WriteParameterValue<double>(momentGenPath, "Amplitude", moment);
    }
    catch (...)
    {
    }

    momentSlider_->setValue(std::clamp(int(moment * kSliderMax / 2.0), -kSliderMax, kSliderMax));
}

void TManipulatorTestWidget::onIIAfferentSliderChanged(int value)
{
    if (controlSystemName_.empty())
        return;

    const double amp = double(value) / double(kSliderMax / 2.0);
    iiAfferentEdit_->setText(QString::number(amp, 'f', 3));

    // Обновляем амплитуду II афферента (упрощенно - для первого источника)
    try
    {
        const std::string iiPosPath = buildComponentPath("IIPosAfferent");
        const std::string iiNegPath = buildComponentPath("IINegAfferent");
        RDK::WriteParameterValue<double>(iiPosPath, "Amplitude", std::max(0.0, amp));
        RDK::WriteParameterValue<double>(iiNegPath, "Amplitude", std::max(0.0, -amp));
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::onIIAfferentEdited()
{
    if (controlSystemName_.empty())
        return;

    bool ok = false;
    const double amp = iiAfferentEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;

    iiAfferentSlider_->setValue(std::clamp(int(amp * kSliderMax / 2.0), -kSliderMax, kSliderMax));
    onIIAfferentSliderChanged(iiAfferentSlider_->value());
}

void TManipulatorTestWidget::onIINumAfferentChanged(int value)
{
    // В model-only режиме это может быть сложно реализовать без прямого доступа к структуре
    // Оставляем как заглушку
    Q_UNUSED(value);
}

void TManipulatorTestWidget::onIaCheckBoxToggled(bool checked)
{
    if (controlSystemName_.empty())
        return;

    // Упрощенная реализация: переключаем связи для MotionElement0
    try
    {
        const std::string motionPath = buildComponentPath("MotionElement0");
        if (checked)
        {
            // Создаем связи с сепараторами (упрощенно)
            Model_CreateLinkByName(buildComponentPath("Ia_PosSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ia2.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("Ia_NegSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ia1.Receptor").c_str(), "0");
        }
        else
        {
            // Восстанавливаем связи с AfferentSource1
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ia2.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ia1.Receptor").c_str(), "0");
        }
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::onIbCheckBoxToggled(bool checked)
{
    if (controlSystemName_.empty())
        return;

    try
    {
        const std::string motionPath = buildComponentPath("MotionElement0");
        if (checked)
        {
            Model_CreateLinkByName(buildComponentPath("Ib_PosSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ib1.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("Ib_NegSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ib2.Receptor").c_str(), "0");
        }
        else
        {
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ib2.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_Ib1.Receptor").c_str(), "0");
        }
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::onIICheckBoxToggled(bool checked)
{
    if (controlSystemName_.empty())
        return;

    try
    {
        const std::string motionPath = buildComponentPath("MotionElement0");
        if (checked)
        {
            Model_CreateLinkByName(buildComponentPath("II_PosSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_II1.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("II_NegSignumSeparator").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_II2.Receptor").c_str(), "0");
        }
        else
        {
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_II2.Receptor").c_str(), "0");
            Model_CreateLinkByName(buildComponentPath("AfferentSource1").c_str(), kOutputProp,
                                   (motionPath + ".Afferent_II1.Receptor").c_str(), "0");
        }
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::onControlVoltageCheckBoxToggled(bool checked)
{
    if (controlSystemName_.empty() || manipulatorName_.empty())
        return;

    try
    {
        const std::string pacPath = buildComponentPath("PAC");
        const std::string inputPath = manipulatorName_ + ".NManipulatorInput1";
        if (checked)
        {
            Model_CreateLinkByName(pacPath.c_str(), kOutputProp, inputPath.c_str(), "0");
        }
        else
        {
            Model_BreakLinkByName(pacPath.c_str(), kOutputProp, inputPath.c_str(), "0");
        }
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::updateFromModel()
{
    if (manipulatorName_.empty())
        return;

    try
    {
        angle_ = RDK::ReadStateValue<double>(manipulatorName_, "Angle");
        movement_ = RDK::ReadStateValue<double>(manipulatorName_, "Movement");
    }
    catch (...)
    {
    }

    // Обновляем чекбоксы на основе текущих связей
    if (!controlSystemName_.empty() && !manipulatorName_.empty())
    {
        try
        {
            const std::string pacPath = buildComponentPath("PAC");
            const std::string inputPath = manipulatorName_ + ".NManipulatorInput1";
            controlVoltageCheckBox_->setChecked(Model_CheckLinkByName(pacPath.c_str(), kOutputProp, inputPath.c_str(), "0"));
        }
        catch (...)
        {
        }
    }
}

void TManipulatorTestWidget::updateIOInformation()
{
    // Упрощенная реализация: в model-only режиме сложно получить все данные о рецепторах и сепараторах
    // Оставляем как заглушку - в реальности нужно читать данные из модели
    angleIO_ = 0;
    speedIO_ = 0;
    momentIO_ = 0;
    sepAngleIO_ = 0;
    sepSpeedIO_ = 0;
    sepMomentIO_ = 0;

    if (manipulatorName_.empty())
        return;

    try
    {
        // Пытаемся прочитать выход двигателя
        engineOutput_ = RDK::ReadStateValue<double>(manipulatorName_, "Output");
        engineInput_ = RDK::ReadStateValue<double>(manipulatorName_, "Input");
    }
    catch (...)
    {
    }
}

void TManipulatorTestWidget::writeArrow(QPainter &painter, int x, int y, int width, double direction)
{
    const int endX = x + width;
    painter.drawLine(x, y, endX, y);

    if (direction >= 0)
    {
        // Стрелка вправо
        QPointF arrow[3] = {
            QPointF(endX - 5, y - 5),
            QPointF(endX + 5, y),
            QPointF(endX - 5, y + 5)
        };
        painter.drawPolygon(arrow, 3);
    }
    else
    {
        // Стрелка влево
        QPointF arrow[3] = {
            QPointF(x + 5, y - 5),
            QPointF(x - 5, y),
            QPointF(x + 5, y + 5)
        };
        painter.drawPolygon(arrow, 3);
    }
}

std::string TManipulatorTestWidget::buildComponentPath(const std::string &componentName)
{
    if (controlSystemName_.empty())
        return componentName;
    return controlSystemName_ + "." + componentName;
}
