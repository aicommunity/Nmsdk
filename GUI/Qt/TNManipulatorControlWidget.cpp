#include "TNManipulatorControlWidget.h"

#include <QCheckBox>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QProgressBar>
#include <QSlider>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>
#include <rdk_init.h>

#include <cmath>
#include <string>

namespace {

const int kMomentSliderMax = 100;
const char kOutputProp[] = "0";

std::string motionElementPath(const std::string &controlSystemName, int index)
{
    return controlSystemName + ".MotionElement" + std::to_string(index);
}

} // namespace

TNManipulatorControlWidget::TNManipulatorControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      canvasWidth_(640),
      canvasHeight_(480),
      x_(canvasWidth_ / 2.0),
      y_(canvasHeight_ / 2.0),
      angle_(0.0),
      movement_(0.0),
      length_(100.0),
      zeroAngle_(0.0),
      zeroMovement_(0.0),
      manipulatorNameEdit_(nullptr),
      controlSystemNameEdit_(nullptr),
      angleLabel_(nullptr),
      movementLabel_(nullptr),
      afferentGroup_(nullptr),
      iaCheckBox_(nullptr),
      ibCheckBox_(nullptr),
      iiCheckBox_(nullptr),
      controlVoltageCheckBox_(nullptr),
      momentGroup_(nullptr),
      momentSlider_(nullptr),
      momentProgressBar_(nullptr),
      extMomentEdit_(nullptr),
      movementControlGroup_(nullptr),
      movementControlSlider_(nullptr),
      movementControlProgressBar_(nullptr),
      movementControlEdit_(nullptr)
{
    Name = "TNManipulatorControlWidget";
    ClassName = "TNManipulatorControlWidget";

    const QString title = tr("Manipulator control");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *namesGroup = new QGroupBox(tr("Components (model only)"), this);
    auto *namesLayout = new QVBoxLayout(namesGroup);
    namesLayout->addWidget(new QLabel(tr("Manipulator name:"), this));
    manipulatorNameEdit_ = new QLineEdit(this);
    manipulatorNameEdit_->setPlaceholderText(tr("e.g. Engine or PendulumAndCart"));
    namesLayout->addWidget(manipulatorNameEdit_);
    namesLayout->addWidget(new QLabel(tr("Control system name:"), this));
    controlSystemNameEdit_ = new QLineEdit(this);
    controlSystemNameEdit_->setPlaceholderText(tr("e.g. EngineControlRangeAfferent"));
    namesLayout->addWidget(controlSystemNameEdit_);
    layout->addWidget(namesGroup);

    auto *stateGroup = new QGroupBox(tr("State"), this);
    auto *stateLayout = new QVBoxLayout(stateGroup);
    angleLabel_ = new QLabel(tr("Angle: —"), this);
    movementLabel_ = new QLabel(tr("Movement: —"), this);
    stateLayout->addWidget(angleLabel_);
    stateLayout->addWidget(movementLabel_);
    layout->addWidget(stateGroup);

    afferentGroup_ = new QGroupBox(tr("Afferents"), this);
    auto *affLayout = new QVBoxLayout(afferentGroup_);
    iaCheckBox_ = new QCheckBox(tr("Ia"), afferentGroup_);
    ibCheckBox_ = new QCheckBox(tr("Ib"), afferentGroup_);
    iiCheckBox_ = new QCheckBox(tr("II"), afferentGroup_);
    controlVoltageCheckBox_ = new QCheckBox(tr("Control voltage"), afferentGroup_);
    affLayout->addWidget(iaCheckBox_);
    affLayout->addWidget(ibCheckBox_);
    affLayout->addWidget(iiCheckBox_);
    affLayout->addWidget(controlVoltageCheckBox_);
    layout->addWidget(afferentGroup_);

    momentGroup_ = new QGroupBox(tr("Moment"), this);
    auto *momentLayout = new QVBoxLayout(momentGroup_);
    momentSlider_ = new QSlider(Qt::Horizontal, momentGroup_);
    momentSlider_->setRange(-kMomentSliderMax, kMomentSliderMax);
    momentSlider_->setValue(0);
    momentProgressBar_ = new QProgressBar(momentGroup_);
    momentProgressBar_->setRange(0, kMomentSliderMax);
    momentProgressBar_->setValue(0);
    extMomentEdit_ = new QLineEdit(momentGroup_);
    extMomentEdit_->setReadOnly(true);
    extMomentEdit_->setText("0.000");
    momentLayout->addWidget(new QLabel(tr("Amplitude (NManipulatorSource1.Angle):"), momentGroup_));
    momentLayout->addWidget(momentSlider_);
    momentLayout->addWidget(momentProgressBar_);
    momentLayout->addWidget(extMomentEdit_);
    layout->addWidget(momentGroup_);

    movementControlGroup_ = new QGroupBox(tr("Movement control"), this);
    auto *movementLayout = new QVBoxLayout(movementControlGroup_);
    movementControlSlider_ = new QSlider(Qt::Horizontal, movementControlGroup_);
    movementControlSlider_->setRange(-kMomentSliderMax, kMomentSliderMax);
    movementControlSlider_->setValue(0);
    movementControlProgressBar_ = new QProgressBar(movementControlGroup_);
    movementControlProgressBar_->setRange(0, kMomentSliderMax);
    movementControlProgressBar_->setValue(0);
    movementControlEdit_ = new QLineEdit(movementControlGroup_);
    movementControlEdit_->setReadOnly(true);
    movementControlEdit_->setText("0.000");
    movementLayout->addWidget(new QLabel(tr("OutMoment / ExtrenalMoment:"), movementControlGroup_));
    movementLayout->addWidget(movementControlSlider_);
    movementLayout->addWidget(movementControlProgressBar_);
    movementLayout->addWidget(movementControlEdit_);
    layout->addWidget(movementControlGroup_);

    layout->addStretch();
    setLayout(layout);

    connect(manipulatorNameEdit_, &QLineEdit::editingFinished, this, &TNManipulatorControlWidget::onManipulatorNameEdited);
    connect(controlSystemNameEdit_, &QLineEdit::editingFinished, this, &TNManipulatorControlWidget::onControlSystemNameEdited);
    connect(momentSlider_, &QSlider::valueChanged, this, &TNManipulatorControlWidget::onMomentSliderChanged);
    connect(iaCheckBox_, &QCheckBox::toggled, this, &TNManipulatorControlWidget::onIaCheckBoxToggled);
    connect(ibCheckBox_, &QCheckBox::toggled, this, &TNManipulatorControlWidget::onIbCheckBoxToggled);
    connect(iiCheckBox_, &QCheckBox::toggled, this, &TNManipulatorControlWidget::onIICheckBoxToggled);
    connect(controlVoltageCheckBox_, &QCheckBox::toggled, this, &TNManipulatorControlWidget::onControlVoltageCheckBoxToggled);
    connect(movementControlSlider_, &QSlider::valueChanged, this, &TNManipulatorControlWidget::onMovementControlSliderChanged);
}

TNManipulatorControlWidget::~TNManipulatorControlWidget() = default;

void TNManipulatorControlWidget::AUpdateInterface()
{
    UpdateInterval = 100;

    loadInterfaceInfoFromNet();
    readComponentData();

    angleLabel_->setText(tr("Angle: %1").arg(angle_, 0, 'f', 4));
    movementLabel_->setText(tr("Movement: %1").arg(movement_, 0, 'f', 4));

    if (!controlSystemName_.empty())
    {
        updateCheckboxesFromModel();
        updateMomentFromModel();
    }
    if (!manipulatorName_.empty())
    {
        updateMovementControlFromModel();
    }
}

void TNManipulatorControlWidget::AClearInterface()
{
    manipulatorName_.clear();
    controlSystemName_.clear();
    manipulatorNameEdit_->clear();
    controlSystemNameEdit_->clear();
    canvasWidth_ = 0;
    canvasHeight_ = 0;
    x_ = 0.0;
    y_ = 0.0;
    angle_ = 0.0;
    movement_ = 0.0;
    length_ = 0.0;
    zeroAngle_ = 0.0;
    zeroMovement_ = 0.0;
    readComponentName_.clear();
    angleLabel_->setText(tr("Angle: —"));
    movementLabel_->setText(tr("Movement: —"));
}

void TNManipulatorControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("Control");
    xml.WriteString("ManipulatorName", manipulatorName_);
    xml.WriteString("ControlSystemName", controlSystemName_);
    xml.SelectUp();
}

void TNManipulatorControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    manipulatorName_.clear();
    controlSystemName_.clear();
    zeroAngle_ = 0.0;
    zeroMovement_ = 0.0;
    movement_ = 0.0;

    xml.SelectNodeForce("Control");
    manipulatorName_ = xml.ReadString("ManipulatorName", "");
    controlSystemName_ = xml.ReadString("ControlSystemName", "");
    xml.SelectUp();

    manipulatorNameEdit_->setText(QString::fromStdString(manipulatorName_));
    controlSystemNameEdit_->setText(QString::fromStdString(controlSystemName_));
    loadInterfaceInfoFromNet();
    UpdateInterval = 100;
}

void TNManipulatorControlWidget::onManipulatorNameEdited()
{
    manipulatorName_ = manipulatorNameEdit_->text().trimmed().toStdString();
}

void TNManipulatorControlWidget::onControlSystemNameEdited()
{
    controlSystemName_ = controlSystemNameEdit_->text().trimmed().toStdString();
}

void TNManipulatorControlWidget::onMomentSliderChanged(int value)
{
    if (UpdateInterfaceFlag || controlSystemName_.empty())
        return;
    double amplitude = double(value) / (kMomentSliderMax / 2.0);
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

void TNManipulatorControlWidget::onIaCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIaLinks(checked);
}

void TNManipulatorControlWidget::onIbCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIbLinks(checked);
}

void TNManipulatorControlWidget::onIICheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIILinks(checked);
}

void TNManipulatorControlWidget::onControlVoltageCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyControlVoltageLinks(checked);
}

void TNManipulatorControlWidget::loadInterfaceInfoFromNet()
{
    // Обновление из модели при необходимости можно расширить (параметры PAC и т.д.)
}

void TNManipulatorControlWidget::readComponentData()
{
    if (manipulatorName_.empty())
        return;
    readComponentName_ = manipulatorName_;
    try
    {
        angle_ = RDK::ReadStateValue<double>(readComponentName_, "Angle");
        movement_ = RDK::ReadStateValue<double>(readComponentName_, "Movement") * 100.0;
    }
    catch (...)
    {
    }
}

void TNManipulatorControlWidget::applyIaLinks(bool checked)
{
    const std::string prefix = controlSystemName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(controlSystemName_, i);
        const std::string posSep = prefix + "Ia_PosIntervalSeparator" + std::to_string(i + 1);
        const std::string negSep = prefix + "Ia_NegIntervalSeparator" + std::to_string(i + 1);
        const std::string ia2 = motion + ".Afferent_Ia2";
        const std::string ia1 = motion + ".Afferent_Ia1";
        if (checked)
        {
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ia2.c_str(), "Receptor");
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ia1.c_str(), "Receptor");
            Model_CreateLinkByName(posSep.c_str(), kOutputProp, ia2.c_str(), "Receptor");
            Model_CreateLinkByName(negSep.c_str(), kOutputProp, ia1.c_str(), "Receptor");
        }
        else
        {
            Model_BreakLinkByName(posSep.c_str(), kOutputProp, ia2.c_str(), "Receptor");
            Model_BreakLinkByName(negSep.c_str(), kOutputProp, ia1.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ia2.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ia1.c_str(), "Receptor");
        }
    }
}

void TNManipulatorControlWidget::applyIbLinks(bool checked)
{
    const std::string prefix = controlSystemName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(controlSystemName_, i);
        const std::string posSep = prefix + "Ib_PosIntervalSeparator" + std::to_string(i + 1);
        const std::string negSep = prefix + "Ib_NegIntervalSeparator" + std::to_string(i + 1);
        const std::string ib1 = motion + ".Afferent_Ib1";
        const std::string ib2 = motion + ".Afferent_Ib2";
        if (checked)
        {
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ib2.c_str(), "Receptor");
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ib1.c_str(), "Receptor");
            Model_CreateLinkByName(posSep.c_str(), kOutputProp, ib1.c_str(), "Receptor");
            Model_CreateLinkByName(negSep.c_str(), kOutputProp, ib2.c_str(), "Receptor");
        }
        else
        {
            Model_BreakLinkByName(posSep.c_str(), kOutputProp, ib1.c_str(), "Receptor");
            Model_BreakLinkByName(negSep.c_str(), kOutputProp, ib2.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ib1.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ib2.c_str(), "Receptor");
        }
    }
}

void TNManipulatorControlWidget::applyIILinks(bool checked)
{
    const std::string prefix = controlSystemName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(controlSystemName_, i);
        const std::string posSep = prefix + "II_PosIntervalSeparator" + std::to_string(i + 1);
        const std::string negSep = prefix + "II_NegIntervalSeparator" + std::to_string(i + 1);
        const std::string ii1 = motion + ".Afferent_II1";
        const std::string ii2 = motion + ".Afferent_II2";
        if (checked)
        {
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ii2.c_str(), "Receptor");
            Model_BreakLinkByName(afferentSource.c_str(), kOutputProp, ii1.c_str(), "Receptor");
            Model_CreateLinkByName(posSep.c_str(), kOutputProp, ii1.c_str(), "Receptor");
            Model_CreateLinkByName(negSep.c_str(), kOutputProp, ii2.c_str(), "Receptor");
        }
        else
        {
            Model_BreakLinkByName(posSep.c_str(), kOutputProp, ii1.c_str(), "Receptor");
            Model_BreakLinkByName(negSep.c_str(), kOutputProp, ii2.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ii2.c_str(), "Receptor");
            Model_CreateLinkByName(afferentSource.c_str(), kOutputProp, ii1.c_str(), "Receptor");
        }
    }
}

void TNManipulatorControlWidget::applyControlVoltageLinks(bool checked)
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

void TNManipulatorControlWidget::updateCheckboxesFromModel()
{
    if (controlSystemName_.empty())
        return;
    const std::string motion0 = controlSystemName_ + ".MotionElement0";
    const std::string ia2 = motion0 + ".Afferent_Ia2";
    const std::string ib1 = motion0 + ".Afferent_Ib1";
    const std::string ii1 = motion0 + ".Afferent_II1";
    const std::string posIa = controlSystemName_ + ".Ia_PosIntervalSeparator1";
    const std::string posIb = controlSystemName_ + ".Ib_PosIntervalSeparator1";
    const std::string posII = controlSystemName_ + ".II_PosIntervalSeparator1";
    const std::string pac = controlSystemName_ + ".Pac";
    const std::string input1 = controlSystemName_ + ".NManipulatorInput1";

    UpdateInterfaceFlag = true;
    iaCheckBox_->setChecked(Model_CheckLinkByName(posIa.c_str(), kOutputProp, ia2.c_str(), "Receptor"));
    ibCheckBox_->setChecked(Model_CheckLinkByName(posIb.c_str(), kOutputProp, ib1.c_str(), "Receptor"));
    iiCheckBox_->setChecked(Model_CheckLinkByName(posII.c_str(), kOutputProp, ii1.c_str(), "Receptor"));
    controlVoltageCheckBox_->setChecked(Model_CheckLinkByName(pac.c_str(), kOutputProp, input1.c_str(), "0"));
    UpdateInterfaceFlag = false;
}

void TNManipulatorControlWidget::updateMomentFromModel()
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
        int pos = static_cast<int>(std::round(amplitude * (kMomentSliderMax / 2.0)));
        momentSlider_->blockSignals(true);
        momentSlider_->setValue(pos);
        momentSlider_->blockSignals(false);
        extMomentEdit_->setText(QString::number(amplitude, 'f', 3));
        momentProgressBar_->setValue(std::abs(pos));
    }
}

void TNManipulatorControlWidget::onMovementControlSliderChanged(int value)
{
    if (UpdateInterfaceFlag || manipulatorName_.empty())
        return;
    double amplitude = double(value) / (kMomentSliderMax / 2.0);
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
    movementControlEdit_->setText(QString::number(amplitude, 'f', 3));
    movementControlProgressBar_->setValue(value > 0 ? value : -value);
}

void TNManipulatorControlWidget::updateMovementControlFromModel()
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
        int pos = static_cast<int>(std::round(amplitude * (kMomentSliderMax / 2.0)));
        movementControlSlider_->blockSignals(true);
        movementControlSlider_->setValue(pos);
        movementControlSlider_->blockSignals(false);
        movementControlEdit_->setText(QString::number(amplitude, 'f', 3));
        movementControlProgressBar_->setValue(std::abs(pos));
    }
}