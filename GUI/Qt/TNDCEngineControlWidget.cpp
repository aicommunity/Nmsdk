#include "TNDCEngineControlWidget.h"

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

std::string motionElementPath(const std::string &motionControlName, int index)
{
    return motionControlName + ".MotionElement" + std::to_string(index);
}

} // namespace

TNDCEngineControlWidget::TNDCEngineControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      canvasWidth_(640),
      canvasHeight_(480),
      x_(canvasWidth_ / 2.0),
      y_(canvasHeight_ / 2.0),
      angle_(0.0),
      length_(100.0),
      afferentGroup_(nullptr),
      iaCheckBox_(nullptr),
      ibCheckBox_(nullptr),
      iiCheckBox_(nullptr),
      controlVoltageCheckBox_(nullptr),
      momentGroup_(nullptr),
      momentSlider_(nullptr),
      momentProgressBar_(nullptr),
      extMomentEdit_(nullptr)
{
    Name = "TNDCEngineControlWidget";
    ClassName = "TNDCEngineControlWidget";

    const QString title = tr("DC engine control");
    setAccessibleName(title);
    setWindowTitle(title);

    motionControlName_ = "EngineControlRangeAfferent";
    componentName_ = motionControlName_ + ".Engine";

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

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
    momentLayout->addWidget(new QLabel(tr("Amplitude:"), momentGroup_));
    momentLayout->addWidget(momentSlider_);
    momentLayout->addWidget(momentProgressBar_);
    momentLayout->addWidget(extMomentEdit_);
    layout->addWidget(momentGroup_);

    layout->addStretch();
    setLayout(layout);

    connect(momentSlider_, &QSlider::valueChanged, this, &TNDCEngineControlWidget::onMomentSliderChanged);
    connect(iaCheckBox_, &QCheckBox::toggled, this, &TNDCEngineControlWidget::onIaCheckBoxToggled);
    connect(ibCheckBox_, &QCheckBox::toggled, this, &TNDCEngineControlWidget::onIbCheckBoxToggled);
    connect(iiCheckBox_, &QCheckBox::toggled, this, &TNDCEngineControlWidget::onIICheckBoxToggled);
    connect(controlVoltageCheckBox_, &QCheckBox::toggled, this, &TNDCEngineControlWidget::onControlVoltageCheckBoxToggled);
}

TNDCEngineControlWidget::~TNDCEngineControlWidget() = default;

void TNDCEngineControlWidget::AUpdateInterface()
{
    readComponentData();
    updateCheckboxesFromModel();

    double amplitude = 0.0;
    try
    {
        amplitude = RDK::ReadParameterValue<double>(motionControlName_ + ".EngineMoment", "Amplitude");
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

void TNDCEngineControlWidget::AClearInterface()
{
    motionControlName_.clear();
    componentName_.clear();
    angle_ = 0.0;
}

void TNDCEngineControlWidget::onMomentSliderChanged(int value)
{
    if (UpdateInterfaceFlag)
        return;
    double amplitude = double(value) / (kMomentSliderMax / 2.0);
    try
    {
        RDK::WriteParameterValue<double>(motionControlName_ + ".EngineMoment", "Amplitude", amplitude);
    }
    catch (...)
    {
    }
    extMomentEdit_->setText(QString::number(amplitude, 'f', 3));
    momentProgressBar_->setValue(value > 0 ? value : -value);
}

void TNDCEngineControlWidget::onIaCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIaLinks(checked);
}

void TNDCEngineControlWidget::onIbCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIbLinks(checked);
}

void TNDCEngineControlWidget::onIICheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyIILinks(checked);
}

void TNDCEngineControlWidget::onControlVoltageCheckBoxToggled(bool checked)
{
    if (UpdateInterfaceFlag)
        return;
    applyControlVoltageLinks(checked);
}

void TNDCEngineControlWidget::readComponentData()
{
    try
    {
        angle_ = RDK::ReadStateValue<double>(componentName_, "Angle");
    }
    catch (...)
    {
    }
}

void TNDCEngineControlWidget::applyIaLinks(bool checked)
{
    const std::string prefix = motionControlName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(motionControlName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(motionControlName_, i);
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

void TNDCEngineControlWidget::applyIbLinks(bool checked)
{
    const std::string prefix = motionControlName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(motionControlName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(motionControlName_, i);
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

void TNDCEngineControlWidget::applyIILinks(bool checked)
{
    const std::string prefix = motionControlName_ + ".";
    const std::string afferentSource = prefix + "AfferentSource1";
    int numMotions = 0;
    try
    {
        numMotions = static_cast<int>(RDK::ReadParameterValue<double>(motionControlName_, "NumMotionElements"));
    }
    catch (...)
    {
        return;
    }
    for (int i = 0; i < numMotions; ++i)
    {
        const std::string motion = motionElementPath(motionControlName_, i);
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

void TNDCEngineControlWidget::applyControlVoltageLinks(bool checked)
{
    const std::string prefix = motionControlName_ + ".";
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

void TNDCEngineControlWidget::updateCheckboxesFromModel()
{
    if (motionControlName_.empty())
        return;
    const std::string motion0 = motionControlName_ + ".MotionElement0";
    const std::string ia2 = motion0 + ".Afferent_Ia2";
    const std::string ib1 = motion0 + ".Afferent_Ib1";
    const std::string ii1 = motion0 + ".Afferent_II1";
    const std::string posIa = motionControlName_ + ".Ia_PosIntervalSeparator1";
    const std::string posIb = motionControlName_ + ".Ib_PosIntervalSeparator1";
    const std::string posII = motionControlName_ + ".II_PosIntervalSeparator1";
    const std::string pac = motionControlName_ + ".Pac";
    const std::string input1 = motionControlName_ + ".NManipulatorInput1";

    UpdateInterfaceFlag = true;
    iaCheckBox_->setChecked(Model_CheckLinkByName(posIa.c_str(), kOutputProp, ia2.c_str(), "Receptor"));
    ibCheckBox_->setChecked(Model_CheckLinkByName(posIb.c_str(), kOutputProp, ib1.c_str(), "Receptor"));
    iiCheckBox_->setChecked(Model_CheckLinkByName(posII.c_str(), kOutputProp, ii1.c_str(), "Receptor"));
    controlVoltageCheckBox_->setChecked(Model_CheckLinkByName(pac.c_str(), kOutputProp, input1.c_str(), "0"));
    UpdateInterfaceFlag = false;
}