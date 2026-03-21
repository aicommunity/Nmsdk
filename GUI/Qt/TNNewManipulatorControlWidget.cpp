#include "TNNewManipulatorControlWidget.h"

#include "NControlSystemSettingsWidget.h"

#include <QCheckBox>
#include <QComboBox>
#include <QGroupBox>
#include <QLabel>
#include <QLineEdit>
#include <QProgressBar>
#include <QPushButton>
#include <QScrollArea>
#include <QSlider>
#include <QSpinBox>
#include <QTabWidget>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>
#include <rdk_init.h>

#include <cmath>
#include <string>

namespace {

const int kSliderMax = 100;
const char kOutputProp[] = "0";

}

TNNewManipulatorControlWidget::TNNewManipulatorControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      manipulatorNameEdit_(nullptr),
      controlSystemNameEdit_(nullptr),
      angleLabel_(nullptr),
      movementLabel_(nullptr),
      numMotionLabel_(nullptr),
      numControlLoopsLabel_(nullptr),
      controlVoltageCheckBox_(nullptr),
      momentGroup_(nullptr),
      momentSlider_(nullptr),
      momentProgressBar_(nullptr),
      extMomentEdit_(nullptr),
      movementGroup_(nullptr),
      movementSlider_(nullptr),
      movementProgressBar_(nullptr),
      movementEdit_(nullptr),
      iiAfferentGroup_(nullptr),
      iiAfferentSlider_(nullptr),
      iiAfferentEdit_(nullptr),
      iiNumAfferentSpinBox_(nullptr),
      numMotionElementsGroup_(nullptr),
      numMotionElementsSlider_(nullptr),
      numMotionElementsEdit_(nullptr),
      numControlLoopsGroup_(nullptr),
      numControlLoopsSlider_(nullptr),
      numControlLoopsEdit_(nullptr),
      manipulatorParamsGroup_(nullptr),
      voltageMulSlider_(nullptr),
      voltageMulEdit_(nullptr),
      timeDurationSlider_(nullptr),
      timeDurationEdit_(nullptr),
      vaEdit_(nullptr),
      vdEdit_(nullptr),
      sendVButton_(nullptr),
      tabWidget_(nullptr),
      controlSystemSettingsWidget_(nullptr)
{
    Name = "TNNewManipulatorControlWidget";
    ClassName = "TNNewManipulatorControlWidget";

    const QString title = tr("New manipulator control");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    auto *namesGroup = new QGroupBox(tr("Components (model only)"), this);
    auto *namesLayout = new QVBoxLayout(namesGroup);
    namesLayout->addWidget(new QLabel(tr("Manipulator name:"), this));
    manipulatorNameEdit_ = new QLineEdit(this);
    manipulatorNameEdit_->setPlaceholderText(tr("e.g. DCEngine or PendulumAndCart"));
    namesLayout->addWidget(manipulatorNameEdit_);
    namesLayout->addWidget(new QLabel(tr("Control system name:"), this));
    controlSystemNameEdit_ = new QLineEdit(this);
    controlSystemNameEdit_->setPlaceholderText(tr("e.g. N2AsfNewSimplestAfferentBranchedEngineControl"));
    namesLayout->addWidget(controlSystemNameEdit_);
    mainLayout->addWidget(namesGroup);

    tabWidget_ = new QTabWidget(this);

    auto *mainTab = new QWidget(this);
    auto *layout = new QVBoxLayout(mainTab);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *stateGroup = new QGroupBox(tr("State"), this);
    auto *stateLayout = new QVBoxLayout(stateGroup);
    angleLabel_ = new QLabel(tr("Angle: —"), this);
    movementLabel_ = new QLabel(tr("Movement: —"), this);
    numMotionLabel_ = new QLabel(tr("NumMotionElements: —"), this);
    numControlLoopsLabel_ = new QLabel(tr("NumControlLoops: —"), this);
    stateLayout->addWidget(angleLabel_);
    stateLayout->addWidget(movementLabel_);
    stateLayout->addWidget(numMotionLabel_);
    stateLayout->addWidget(numControlLoopsLabel_);
    layout->addWidget(stateGroup);

    controlVoltageCheckBox_ = new QCheckBox(tr("Control voltage (Pac → NManipulatorInput1)"), this);
    layout->addWidget(controlVoltageCheckBox_);

    momentGroup_ = new QGroupBox(tr("Moment (NManipulatorSource1.Angle)"), this);
    auto *momentLayout = new QVBoxLayout(momentGroup_);
    momentSlider_ = new QSlider(Qt::Horizontal, momentGroup_);
    momentSlider_->setRange(-kSliderMax, kSliderMax);
    momentSlider_->setValue(0);
    momentProgressBar_ = new QProgressBar(momentGroup_);
    momentProgressBar_->setRange(0, kSliderMax);
    extMomentEdit_ = new QLineEdit(momentGroup_);
    extMomentEdit_->setReadOnly(true);
    extMomentEdit_->setText("0.000");
    momentLayout->addWidget(momentSlider_);
    momentLayout->addWidget(momentProgressBar_);
    momentLayout->addWidget(extMomentEdit_);
    layout->addWidget(momentGroup_);

    movementGroup_ = new QGroupBox(tr("Movement control (OutMoment / ExtrenalMoment)"), this);
    auto *movLayout = new QVBoxLayout(movementGroup_);
    movementSlider_ = new QSlider(Qt::Horizontal, movementGroup_);
    movementSlider_->setRange(-kSliderMax, kSliderMax);
    movementSlider_->setValue(0);
    movementProgressBar_ = new QProgressBar(movementGroup_);
    movementProgressBar_->setRange(0, kSliderMax);
    movementEdit_ = new QLineEdit(movementGroup_);
    movementEdit_->setReadOnly(true);
    movementEdit_->setText("0.000");
    movLayout->addWidget(movementSlider_);
    movLayout->addWidget(movementProgressBar_);
    movLayout->addWidget(movementEdit_);
    layout->addWidget(movementGroup_);

    iiAfferentGroup_ = new QGroupBox(tr("II afferent"), this);
    auto *iiLayout = new QVBoxLayout(iiAfferentGroup_);
    iiAfferentSlider_ = new QSlider(Qt::Horizontal, iiAfferentGroup_);
    iiAfferentSlider_->setRange(-100, 100);
    iiAfferentSlider_->setValue(0);
    iiAfferentEdit_ = new QLineEdit(iiAfferentGroup_);
    iiAfferentEdit_->setReadOnly(true);
    iiAfferentEdit_->setText("0.000");
    iiLayout->addWidget(new QLabel(tr("Frequency:"), iiAfferentGroup_));
    iiLayout->addWidget(iiAfferentSlider_);
    iiLayout->addWidget(iiAfferentEdit_);
    iiLayout->addWidget(new QLabel(tr("Number of motion elements with II afferent:"), iiAfferentGroup_));
    iiNumAfferentSpinBox_ = new QSpinBox(iiAfferentGroup_);
    iiNumAfferentSpinBox_->setMinimum(0);
    iiNumAfferentSpinBox_->setMaximum(100);
    iiNumAfferentSpinBox_->setValue(0);
    iiLayout->addWidget(iiNumAfferentSpinBox_);
    layout->addWidget(iiAfferentGroup_);

    numMotionElementsGroup_ = new QGroupBox(tr("NumMotionElements"), this);
    auto *numMotionLayout = new QVBoxLayout(numMotionElementsGroup_);
    numMotionElementsSlider_ = new QSlider(Qt::Horizontal, numMotionElementsGroup_);
    numMotionElementsSlider_->setRange(1, 20);
    numMotionElementsSlider_->setValue(1);
    numMotionElementsEdit_ = new QLineEdit(numMotionElementsGroup_);
    numMotionElementsEdit_->setText("1");
    numMotionLayout->addWidget(numMotionElementsSlider_);
    numMotionLayout->addWidget(numMotionElementsEdit_);
    layout->addWidget(numMotionElementsGroup_);

    numControlLoopsGroup_ = new QGroupBox(tr("NumControlLoops"), this);
    auto *numControlLayout = new QVBoxLayout(numControlLoopsGroup_);
    numControlLoopsSlider_ = new QSlider(Qt::Horizontal, numControlLoopsGroup_);
    numControlLoopsSlider_->setRange(1, 10);
    numControlLoopsSlider_->setValue(1);
    numControlLoopsEdit_ = new QLineEdit(numControlLoopsGroup_);
    numControlLoopsEdit_->setText("1");
    numControlLayout->addWidget(numControlLoopsSlider_);
    numControlLayout->addWidget(numControlLoopsEdit_);
    layout->addWidget(numControlLoopsGroup_);

    manipulatorParamsGroup_ = new QGroupBox(tr("Manipulator parameters (requires engine API)"), this);
    auto *manipParamsLayout = new QVBoxLayout(manipulatorParamsGroup_);
    manipParamsLayout->addWidget(new QLabel(tr("Voltage multiplier:"), manipulatorParamsGroup_));
    voltageMulSlider_ = new QSlider(Qt::Horizontal, manipulatorParamsGroup_);
    voltageMulSlider_->setRange(0, 1000);
    voltageMulSlider_->setValue(100);
    voltageMulEdit_ = new QLineEdit(manipulatorParamsGroup_);
    voltageMulEdit_->setText("1.000");
    manipParamsLayout->addWidget(voltageMulSlider_);
    manipParamsLayout->addWidget(voltageMulEdit_);
    manipParamsLayout->addWidget(new QLabel(tr("Time duration:"), manipulatorParamsGroup_));
    timeDurationSlider_ = new QSlider(Qt::Horizontal, manipulatorParamsGroup_);
    timeDurationSlider_->setRange(0, 10000);
    timeDurationSlider_->setValue(0);
    timeDurationEdit_ = new QLineEdit(manipulatorParamsGroup_);
    timeDurationEdit_->setText("0.000");
    manipParamsLayout->addWidget(timeDurationSlider_);
    manipParamsLayout->addWidget(timeDurationEdit_);
    manipParamsLayout->addWidget(new QLabel(tr("Va (accumulation step):"), manipulatorParamsGroup_));
    vaEdit_ = new QLineEdit(manipulatorParamsGroup_);
    vaEdit_->setPlaceholderText("0");
    manipParamsLayout->addWidget(vaEdit_);
    manipParamsLayout->addWidget(new QLabel(tr("Vd (dissociation step):"), manipulatorParamsGroup_));
    vdEdit_ = new QLineEdit(manipulatorParamsGroup_);
    vdEdit_->setPlaceholderText("0");
    manipParamsLayout->addWidget(vdEdit_);
    sendVButton_ = new QPushButton(tr("Send V"), manipulatorParamsGroup_);
    manipParamsLayout->addWidget(sendVButton_);
    layout->addWidget(manipulatorParamsGroup_);

    layout->addStretch();
    tabWidget_->addTab(mainTab, tr("Control"));

    controlSystemSettingsWidget_ = new NControlSystemSettingsWidget(this);
    auto *settingsScroll = new QScrollArea(this);
    settingsScroll->setWidget(controlSystemSettingsWidget_);
    settingsScroll->setWidgetResizable(true);
    tabWidget_->addTab(settingsScroll, tr("Control System Settings"));

    mainLayout->addWidget(tabWidget_);
    setLayout(mainLayout);

    connect(manipulatorNameEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onManipulatorNameEdited);
    connect(controlSystemNameEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onControlSystemNameEdited);
    connect(controlVoltageCheckBox_, &QCheckBox::toggled, this, &TNNewManipulatorControlWidget::onControlVoltageCheckBoxToggled);
    connect(momentSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onMomentSliderChanged);
    connect(movementSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onMovementSliderChanged);
    connect(iiAfferentSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onIIAfferentSliderChanged);
    connect(iiNumAfferentSpinBox_, QOverload<int>::of(&QSpinBox::valueChanged), this, &TNNewManipulatorControlWidget::onIINumAfferentChanged);
    connect(numMotionElementsSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onNumMotionElementsSliderChanged);
    connect(numMotionElementsEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onNumMotionElementsEdited);
    connect(numControlLoopsSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onNumControlLoopsSliderChanged);
    connect(numControlLoopsEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onNumControlLoopsEdited);
    connect(voltageMulSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onVoltageMulSliderChanged);
    connect(voltageMulEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onVoltageMulEdited);
    connect(timeDurationSlider_, &QSlider::valueChanged, this, &TNNewManipulatorControlWidget::onTimeDurationSliderChanged);
    connect(timeDurationEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onTimeDurationEdited);
    connect(vaEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onVaEdited);
    connect(vdEdit_, &QLineEdit::editingFinished, this, &TNNewManipulatorControlWidget::onVdEdited);
    connect(sendVButton_, &QPushButton::clicked, this, &TNNewManipulatorControlWidget::onSendVClicked);
}

TNNewManipulatorControlWidget::~TNNewManipulatorControlWidget() = default;

void TNNewManipulatorControlWidget::AUpdateInterface()
{
    UpdateInterval = 100;
    readComponentData();

    angleLabel_->setText(tr("Angle: %1").arg(angle_, 0, 'f', 4));
    movementLabel_->setText(tr("Movement: %1").arg(movement_, 0, 'f', 4));
    numMotionLabel_->setText(tr("NumMotionElements: %1").arg(numMotionElements_));
    numControlLoopsLabel_->setText(tr("NumControlLoops: %1").arg(numControlLoops_));

    if (!controlSystemName_.empty())
    {
        updateControlVoltageFromModel();
        updateMomentFromModel();
        updateIIAfferentFromModel();
        updateNumMotionElementsFromModel();
        updateNumControlLoopsFromModel();
        controlSystemSettingsWidget_->setControlSystemName(controlSystemName_);
    }
    else
    {
        controlSystemSettingsWidget_->clear();
    }
    if (!manipulatorName_.empty())
    {
        updateMovementFromModel();
        updateManipulatorParamsFromModel();
    }
}

void TNNewManipulatorControlWidget::AClearInterface()
{
    manipulatorName_.clear();
    controlSystemName_.clear();
    angle_ = 0.0;
    movement_ = 0.0;
    numMotionElements_ = 0;
    numControlLoops_ = 0;
    angleLabel_->setText(tr("Angle: —"));
    movementLabel_->setText(tr("Movement: —"));
    numMotionLabel_->setText(tr("NumMotionElements: —"));
    numControlLoopsLabel_->setText(tr("NumControlLoops: —"));
    controlSystemSettingsWidget_->clear();
}

void TNNewManipulatorControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NewManipulatorControl");
    xml.WriteString("ManipulatorName", manipulatorName_);
    xml.WriteString("ControlSystemName", controlSystemName_);
    xml.SelectUp();
}

void TNNewManipulatorControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NewManipulatorControl");
    manipulatorName_ = xml.ReadString("ManipulatorName", "");
    controlSystemName_ = xml.ReadString("ControlSystemName", "");
    xml.SelectUp();
    manipulatorNameEdit_->setText(QString::fromStdString(manipulatorName_));
    controlSystemNameEdit_->setText(QString::fromStdString(controlSystemName_));
    controlSystemSettingsWidget_->setControlSystemName(controlSystemName_);
    UpdateInterval = 100;
}

void TNNewManipulatorControlWidget::onManipulatorNameEdited()
{
    manipulatorName_ = manipulatorNameEdit_->text().trimmed().toStdString();
}

void TNNewManipulatorControlWidget::onControlSystemNameEdited()
{
    controlSystemName_ = controlSystemNameEdit_->text().trimmed().toStdString();
    try
    {
        numMotionElements_ = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
        numControlLoops_ = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumControlLoops"));
    }
    catch (...)
    {
        numMotionElements_ = 0;
        numControlLoops_ = 0;
    }
    iiNumAfferentSpinBox_->setMaximum(std::max(0, numMotionElements_));
    controlSystemSettingsWidget_->setControlSystemName(controlSystemName_);
}

void TNNewManipulatorControlWidget::onControlVoltageCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyControlVoltageLinks(checked);
}

void TNNewManipulatorControlWidget::onMomentSliderChanged(int value)
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    double amplitude = double(value) / (kSliderMax / 2.0);
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_ + ".NManipulatorSource1", "Angle", amplitude);
    }
    catch (...)
    {
    }
    extMomentEdit_->setText(QString::number(amplitude, 'f', 3));
    momentProgressBar_->setValue(value > 0 ? value : -value);
}

void TNNewManipulatorControlWidget::onMovementSliderChanged(int value)
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    double amplitude = double(value) / (kSliderMax / 2.0);
    try
    {
        RDK::WriteParameterValue<double>(manipulatorName_, "OutMoment", amplitude);
    }
    catch (...)
    {
    }
    try
    {
        RDK::WriteStateValue<double>(manipulatorName_, "ExtrenalMoment", amplitude);
    }
    catch (...)
    {
    }
    movementEdit_->setText(QString::number(amplitude, 'f', 3));
    movementProgressBar_->setValue(value > 0 ? value : -value);
}

void TNNewManipulatorControlWidget::onIIAfferentSliderChanged(int value)
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    const std::string posGen = controlSystemName_ + ".IIPosAfferentGenerator";
    const std::string negGen = controlSystemName_ + ".IINegAfferentGenerator";
    if (value >= 0)
    {
        try
        {
            RDK::WriteParameterValue<double>(posGen, "Frequency", static_cast<double>(value));
            RDK::WriteParameterValue<double>(negGen, "Frequency", 0.0);
        }
        catch (...)
        {
        }
    }
    else
    {
        try
        {
            RDK::WriteParameterValue<double>(negGen, "Frequency", static_cast<double>(-value));
            RDK::WriteParameterValue<double>(posGen, "Frequency", 0.0);
        }
        catch (...)
        {
        }
    }
    iiAfferentEdit_->setText(QString::number(value >= 0 ? value : -value, 'f', 3));
    applyIIAfferentLinks(iiNumAfferentSpinBox_->value());
}

void TNNewManipulatorControlWidget::onIINumAfferentChanged(int value)
{
    if (UpdateInterfaceFlag)
        return;
    applyIIAfferentLinks(value);
}

void TNNewManipulatorControlWidget::readComponentData()
{
    if (!manipulatorName_.empty())
    {
        try
        {
            angle_ = RDK::ReadStateValue<double>(manipulatorName_, "Angle");
        }
        catch (...)
        {
        }
        try
        {
            movement_ = RDK::ReadStateValue<double>(manipulatorName_, "Movement") * 100.0;
        }
        catch (...)
        {
        }
    }
    if (!controlSystemName_.empty())
    {
        try
        {
            numMotionElements_ = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
            numControlLoops_ = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumControlLoops"));
        }
        catch (...)
        {
        }
    }
}

void TNNewManipulatorControlWidget::applyControlVoltageLinks(bool checked)
{
    const std::string prefix = controlSystemName_ + ".";
    const std::string pac = prefix + "Pac";
    const std::string input1 = prefix + "NManipulatorInput1";
    const std::string inputEmu = prefix + "NManipulatorInputEmulator1";
    if (checked)
    {
        Model_CreateLinkByName(pac.c_str(), kOutputProp, input1.c_str(), "0");
        Model_CreateLinkByName(pac.c_str(), kOutputProp, inputEmu.c_str(), "0");
    }
    else
    {
        Model_BreakLinkByName(pac.c_str(), kOutputProp, input1.c_str(), "0");
        Model_BreakLinkByName(pac.c_str(), kOutputProp, inputEmu.c_str(), "0");
    }
}

void TNNewManipulatorControlWidget::updateControlVoltageFromModel()
{
    const std::string pac = controlSystemName_ + ".Pac";
    const std::string input1 = controlSystemName_ + ".NManipulatorInput1";
    UpdateInterfaceFlag = true;
    controlVoltageCheckBox_->setChecked(Model_CheckLinkByName(pac.c_str(), kOutputProp, input1.c_str(), "0"));
    UpdateInterfaceFlag = false;
}

void TNNewManipulatorControlWidget::updateMomentFromModel()
{
    double amplitude = 0.0;
    try
    {
        amplitude = RDK::ReadParameterValue<double>(controlSystemName_ + ".NManipulatorSource1", "Angle");
    }
    catch (...)
    {
    }
    if (!UpdateInterfaceFlag)
    {
        int pos = static_cast<int>(std::round(amplitude * (kSliderMax / 2.0)));
        momentSlider_->blockSignals(true);
        momentSlider_->setValue(pos);
        momentSlider_->blockSignals(false);
        extMomentEdit_->setText(QString::number(amplitude, 'f', 3));
        momentProgressBar_->setValue(std::abs(pos));
    }
}

void TNNewManipulatorControlWidget::updateMovementFromModel()
{
    double amplitude = 0.0;
    try
    {
        amplitude = RDK::ReadParameterValue<double>(manipulatorName_, "OutMoment");
    }
    catch (...)
    {
        try
        {
            amplitude = RDK::ReadStateValue<double>(manipulatorName_, "ExtrenalMoment");
        }
        catch (...)
        {
        }
    }
    if (!UpdateInterfaceFlag)
    {
        int pos = static_cast<int>(std::round(amplitude * (kSliderMax / 2.0)));
        movementSlider_->blockSignals(true);
        movementSlider_->setValue(pos);
        movementSlider_->blockSignals(false);
        movementEdit_->setText(QString::number(amplitude, 'f', 3));
        movementProgressBar_->setValue(std::abs(pos));
    }
}

void TNNewManipulatorControlWidget::updateIIAfferentFromModel()
{
    try
    {
        double posF = RDK::ReadParameterValue<double>(controlSystemName_ + ".IIPosAfferentGenerator", "Frequency");
        double negF = RDK::ReadParameterValue<double>(controlSystemName_ + ".IINegAfferentGenerator", "Frequency");
        int pos = 0;
        if (posF > 0)
            pos = static_cast<int>(std::round(posF));
        else if (negF > 0)
            pos = -static_cast<int>(std::round(negF));
        iiAfferentSlider_->blockSignals(true);
        iiAfferentSlider_->setValue(pos);
        iiAfferentSlider_->blockSignals(false);
        iiAfferentEdit_->setText(QString::number(std::abs(pos), 'f', 3));
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::applyIIAfferentLinks(int numAfferent)
{
    if (controlSystemName_.empty())
        return;
    int numMotion = numMotionElements_;
    if (numMotion <= 0)
    {
        try
        {
            numMotion = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
        }
        catch (...)
        {
            return;
        }
    }
    const std::string prefix = controlSystemName_ + ".";
    const std::string posGen = prefix + "IIPosAfferentGenerator";
    const std::string negGen = prefix + "IINegAfferentGenerator";

    for (int i = 0; i < numMotion; ++i)
    {
        const std::string me = prefix + "MotionElement" + std::to_string(i);
        const std::string pa14 = me + ".PostAfferent14.PNeuronMembrane";
        const std::string pa24 = me + ".PostAfferent24.PNeuronMembrane";
        Model_BreakLinkByName(posGen.c_str(), kOutputProp, pa14.c_str(), "PosChannel");
        Model_BreakLinkByName(posGen.c_str(), kOutputProp, pa24.c_str(), "NegChannel");
        Model_BreakLinkByName(negGen.c_str(), kOutputProp, pa14.c_str(), "NegChannel");
        Model_BreakLinkByName(negGen.c_str(), kOutputProp, pa24.c_str(), "PosChannel");
    }

    for (int i = 0; i < numAfferent && i < numMotion; ++i)
    {
        const std::string me = prefix + "MotionElement" + std::to_string(i);
        const std::string pa14 = me + ".PostAfferent14.PNeuronMembrane";
        const std::string pa24 = me + ".PostAfferent24.PNeuronMembrane";
        Model_CreateLinkByName(posGen.c_str(), kOutputProp, pa14.c_str(), "PosChannel");
        Model_CreateLinkByName(posGen.c_str(), kOutputProp, pa24.c_str(), "NegChannel");
        Model_CreateLinkByName(negGen.c_str(), kOutputProp, pa14.c_str(), "NegChannel");
        Model_CreateLinkByName(negGen.c_str(), kOutputProp, pa24.c_str(), "PosChannel");
    }
}

void TNNewManipulatorControlWidget::onNumMotionElementsSliderChanged(int value)
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "NumMotionElements", static_cast<double>(value));
        numMotionElements_ = value;
        numMotionElementsEdit_->setText(QString::number(value));
        iiNumAfferentSpinBox_->setMaximum(std::max(0, value));
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onNumMotionElementsEdited()
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    bool ok = false;
    int value = numMotionElementsEdit_->text().trimmed().toInt(&ok);
    if (!ok || value < 1)
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "NumMotionElements", static_cast<double>(value));
        numMotionElements_ = value;
        numMotionElementsSlider_->blockSignals(true);
        numMotionElementsSlider_->setValue(value);
        numMotionElementsSlider_->blockSignals(false);
        iiNumAfferentSpinBox_->setMaximum(std::max(0, value));
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onNumControlLoopsSliderChanged(int value)
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "NumControlLoops", static_cast<double>(value));
        numControlLoops_ = value;
        numControlLoopsEdit_->setText(QString::number(value));
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onNumControlLoopsEdited()
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    bool ok = false;
    int value = numControlLoopsEdit_->text().trimmed().toInt(&ok);
    if (!ok || value < 1)
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "NumControlLoops", static_cast<double>(value));
        numControlLoops_ = value;
        numControlLoopsSlider_->blockSignals(true);
        numControlLoopsSlider_->setValue(value);
        numControlLoopsSlider_->blockSignals(false);
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onVoltageMulSliderChanged(int value)
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    double mul = double(value) / 100.0;
    voltageMulEdit_->setText(QString::number(mul, 'f', 3));
    // Requires engine API - will be implemented if engine API is available
    try
    {
        RDK::WriteParameterValue<double>(manipulatorName_, "OutputMul", mul);
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onVoltageMulEdited()
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    bool ok = false;
    double value = voltageMulEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(manipulatorName_, "OutputMul", value);
        voltageMulSlider_->blockSignals(true);
        voltageMulSlider_->setValue(static_cast<int>(std::round(value * 100.0)));
        voltageMulSlider_->blockSignals(false);
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onTimeDurationSliderChanged(int value)
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    timeDurationEdit_->setText(QString::number(value, 'f', 3));
    // Requires engine API - will be implemented if engine API is available
    try
    {
        RDK::WriteParameterValue<double>(manipulatorName_, "TimeDuration", static_cast<double>(value));
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onTimeDurationEdited()
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    bool ok = false;
    double value = timeDurationEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(manipulatorName_, "TimeDuration", value);
        timeDurationSlider_->blockSignals(true);
        timeDurationSlider_->setValue(static_cast<int>(std::round(value)));
        timeDurationSlider_->blockSignals(false);
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::onVaEdited()
{
    // Пока что просто нормализуем ввод; применение шага аккумуляции
    // выполняется в onSendVClicked (через движок, если доступен).
    if (!vaEdit_)
        return;
    bool ok = false;
    const int va = vaEdit_->text().trimmed().toInt(&ok);
    if (!ok)
        return;
    vaEdit_->setText(QString::number(va));
}

void TNNewManipulatorControlWidget::onVdEdited()
{
    if (!vdEdit_)
        return;
    bool ok = false;
    const int vd = vdEdit_->text().trimmed().toInt(&ok);
    if (!ok)
        return;
    vdEdit_->setText(QString::number(vd));
}

void TNNewManipulatorControlWidget::onSendVClicked()
{
    if (manipulatorName_.empty() || controlSystemName_.empty())
        return;
    bool okVa = false, okVd = false;
    int va = vaEdit_->text().trimmed().toInt(&okVa);
    int vd = vdEdit_->text().trimmed().toInt(&okVd);
    if (!okVa || !okVd)
        return;
    // Requires engine API - SetAccumulationStep/SetDissociationStep
    // This will be implemented when engine API is available
}

void TNNewManipulatorControlWidget::updateNumMotionElementsFromModel()
{
    try
    {
        int value = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
        numMotionElements_ = value;
        if (!UpdateInterfaceFlag)
        {
            numMotionElementsSlider_->blockSignals(true);
            numMotionElementsSlider_->setValue(value);
            numMotionElementsSlider_->blockSignals(false);
            numMotionElementsEdit_->setText(QString::number(value));
            iiNumAfferentSpinBox_->setMaximum(std::max(0, value));
        }
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::updateNumControlLoopsFromModel()
{
    try
    {
        int value = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumControlLoops"));
        numControlLoops_ = value;
        if (!UpdateInterfaceFlag)
        {
            numControlLoopsSlider_->blockSignals(true);
            numControlLoopsSlider_->setValue(value);
            numControlLoopsSlider_->blockSignals(false);
            numControlLoopsEdit_->setText(QString::number(value));
        }
    }
    catch (...)
    {
    }
}

void TNNewManipulatorControlWidget::updateManipulatorParamsFromModel()
{
    try
    {
        double mul = RDK::ReadParameterValue<double>(manipulatorName_, "OutputMul");
        if (!UpdateInterfaceFlag)
        {
            voltageMulSlider_->blockSignals(true);
            voltageMulSlider_->setValue(static_cast<int>(std::round(mul * 100.0)));
            voltageMulSlider_->blockSignals(false);
            voltageMulEdit_->setText(QString::number(mul, 'f', 3));
        }
    }
    catch (...)
    {
    }
    try
    {
        double duration = RDK::ReadParameterValue<double>(manipulatorName_, "TimeDuration");
        if (!UpdateInterfaceFlag)
        {
            timeDurationSlider_->blockSignals(true);
            timeDurationSlider_->setValue(static_cast<int>(std::round(duration)));
            timeDurationSlider_->blockSignals(false);
            timeDurationEdit_->setText(QString::number(duration, 'f', 3));
        }
    }
    catch (...)
    {
    }
    // Va/Vd require engine API - will be implemented when engine API is available
}
