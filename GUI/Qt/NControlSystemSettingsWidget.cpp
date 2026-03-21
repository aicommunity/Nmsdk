#include "NControlSystemSettingsWidget.h"

#include <QCheckBox>
#include <QComboBox>
#include <QGroupBox>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QSlider>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>

#include <cmath>

namespace {

const int kPacGainSliderMax = 500;
const int kTimeSliderMax = 1000;

}

NControlSystemSettingsWidget::NControlSystemSettingsWidget(QWidget *parent)
    : QWidget(parent),
      pacGroup_(nullptr),
      pacGainSlider_(nullptr),
      pacGainEdit_(nullptr),
      pacActivatorTimeSlider_(nullptr),
      pacActivatorTimeEdit_(nullptr),
      pacDeactivatorTimeSlider_(nullptr),
      pacDeactivatorTimeEdit_(nullptr),
      contoursGroup_(nullptr),
      activeContoursList_(nullptr),
      modesGroup_(nullptr),
      branchModeCheckBox_(nullptr),
      renshowModeCheckBox_(nullptr),
      afferentRangeModeComboBox_(nullptr),
      useSimpleAfferentsCheckBox_(nullptr),
      useNewNeuronsCheckBox_(nullptr),
      contourGroup_(nullptr),
      currentContourAmplitudeEdit_(nullptr),
      currentContourAverageEdit_(nullptr),
      transientTimeEdit_(nullptr),
      currentTransientStateCheckBox_(nullptr),
      instantAvgSpeedEdit_(nullptr),
      structuralAdaptationGroup_(nullptr),
      enableStructuralAdaptationCheckBox_(nullptr),
      maxAmpEdit_(nullptr),
      minAmpEdit_(nullptr),
      updateInProgress_(false)
{
    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    pacGroup_ = new QGroupBox(tr("PAC parameters"), this);
    auto *pacLayout = new QVBoxLayout(pacGroup_);
    pacLayout->addWidget(new QLabel(tr("Gain:"), pacGroup_));
    pacGainSlider_ = new QSlider(Qt::Horizontal, pacGroup_);
    pacGainSlider_->setRange(0, kPacGainSliderMax);
    pacGainSlider_->setValue(100);
    pacGainEdit_ = new QLineEdit(pacGroup_);
    pacGainEdit_->setReadOnly(true);
    pacGainEdit_->setText("100.000");
    pacLayout->addWidget(pacGainSlider_);
    pacLayout->addWidget(pacGainEdit_);
    pacLayout->addWidget(new QLabel(tr("Secretion TC (activator time):"), pacGroup_));
    pacActivatorTimeSlider_ = new QSlider(Qt::Horizontal, pacGroup_);
    pacActivatorTimeSlider_->setRange(0, kTimeSliderMax);
    pacActivatorTimeEdit_ = new QLineEdit(pacGroup_);
    pacActivatorTimeEdit_->setReadOnly(true);
    pacActivatorTimeEdit_->setText("0.000");
    pacLayout->addWidget(pacActivatorTimeSlider_);
    pacLayout->addWidget(pacActivatorTimeEdit_);
    pacLayout->addWidget(new QLabel(tr("Dissociation TC (deactivator time):"), pacGroup_));
    pacDeactivatorTimeSlider_ = new QSlider(Qt::Horizontal, pacGroup_);
    pacDeactivatorTimeSlider_->setRange(0, kTimeSliderMax);
    pacDeactivatorTimeEdit_ = new QLineEdit(pacGroup_);
    pacDeactivatorTimeEdit_->setReadOnly(true);
    pacDeactivatorTimeEdit_->setText("0.000");
    pacLayout->addWidget(pacDeactivatorTimeSlider_);
    pacLayout->addWidget(pacDeactivatorTimeEdit_);
    layout->addWidget(pacGroup_);

    contoursGroup_ = new QGroupBox(tr("Active contours"), this);
    auto *contoursLayout = new QVBoxLayout(contoursGroup_);
    activeContoursList_ = new QListWidget(contoursGroup_);
    activeContoursList_->setSelectionMode(QAbstractItemView::NoSelection);
    contoursLayout->addWidget(activeContoursList_);
    layout->addWidget(contoursGroup_);

    modesGroup_ = new QGroupBox(tr("Modes"), this);
    auto *modesLayout = new QVBoxLayout(modesGroup_);
    branchModeCheckBox_ = new QCheckBox(tr("Motoneuron branch mode"), modesGroup_);
    renshowModeCheckBox_ = new QCheckBox(tr("Renshow mode"), modesGroup_);
    useSimpleAfferentsCheckBox_ = new QCheckBox(tr("Use simple afferents"), modesGroup_);
    useNewNeuronsCheckBox_ = new QCheckBox(tr("Use new neurons"), modesGroup_);
    modesLayout->addWidget(branchModeCheckBox_);
    modesLayout->addWidget(renshowModeCheckBox_);
    modesLayout->addWidget(useSimpleAfferentsCheckBox_);
    modesLayout->addWidget(useNewNeuronsCheckBox_);
    modesLayout->addWidget(new QLabel(tr("Afferent range mode:"), modesGroup_));
    afferentRangeModeComboBox_ = new QComboBox(modesGroup_);
    afferentRangeModeComboBox_->addItems({tr("0"), tr("1"), tr("2"), tr("3")});
    modesLayout->addWidget(afferentRangeModeComboBox_);
    layout->addWidget(modesGroup_);

    contourGroup_ = new QGroupBox(tr("Current contour"), this);
    auto *contourLayout = new QVBoxLayout(contourGroup_);
    contourLayout->addWidget(new QLabel(tr("Amplitude:"), contourGroup_));
    currentContourAmplitudeEdit_ = new QLineEdit(contourGroup_);
    currentContourAmplitudeEdit_->setReadOnly(true);
    currentContourAmplitudeEdit_->setPlaceholderText("0.0");
    contourLayout->addWidget(currentContourAmplitudeEdit_);
    contourLayout->addWidget(new QLabel(tr("Average:"), contourGroup_));
    currentContourAverageEdit_ = new QLineEdit(contourGroup_);
    currentContourAverageEdit_->setReadOnly(true);
    currentContourAverageEdit_->setPlaceholderText("0.0");
    contourLayout->addWidget(currentContourAverageEdit_);
    contourLayout->addWidget(new QLabel(tr("Transient time:"), contourGroup_));
    transientTimeEdit_ = new QLineEdit(contourGroup_);
    transientTimeEdit_->setReadOnly(true);
    transientTimeEdit_->setPlaceholderText("0.0");
    contourLayout->addWidget(transientTimeEdit_);
    currentTransientStateCheckBox_ = new QCheckBox(tr("Current transient state"), contourGroup_);
    currentTransientStateCheckBox_->setEnabled(false);
    contourLayout->addWidget(currentTransientStateCheckBox_);
    contourLayout->addWidget(new QLabel(tr("Instant avg speed:"), contourGroup_));
    instantAvgSpeedEdit_ = new QLineEdit(contourGroup_);
    instantAvgSpeedEdit_->setReadOnly(true);
    instantAvgSpeedEdit_->setPlaceholderText("0.0");
    contourLayout->addWidget(instantAvgSpeedEdit_);
    layout->addWidget(contourGroup_);

    structuralAdaptationGroup_ = new QGroupBox(tr("Structural adaptation"), this);
    auto *structLayout = new QVBoxLayout(structuralAdaptationGroup_);
    enableStructuralAdaptationCheckBox_ = new QCheckBox(tr("Enable structural adaptation"), structuralAdaptationGroup_);
    structLayout->addWidget(enableStructuralAdaptationCheckBox_);
    structLayout->addWidget(new QLabel(tr("Max amplitude:"), structuralAdaptationGroup_));
    maxAmpEdit_ = new QLineEdit(structuralAdaptationGroup_);
    maxAmpEdit_->setPlaceholderText("0.0");
    structLayout->addWidget(maxAmpEdit_);
    structLayout->addWidget(new QLabel(tr("Min amplitude:"), structuralAdaptationGroup_));
    minAmpEdit_ = new QLineEdit(structuralAdaptationGroup_);
    minAmpEdit_->setPlaceholderText("0.0");
    structLayout->addWidget(minAmpEdit_);
    layout->addWidget(structuralAdaptationGroup_);

    layout->addStretch();
    setLayout(layout);

    connect(pacGainSlider_, &QSlider::valueChanged, this, &NControlSystemSettingsWidget::onPacGainSliderChanged);
    connect(pacActivatorTimeSlider_, &QSlider::valueChanged, this, &NControlSystemSettingsWidget::onPacActivatorTimeSliderChanged);
    connect(pacDeactivatorTimeSlider_, &QSlider::valueChanged, this, &NControlSystemSettingsWidget::onPacDeactivatorTimeSliderChanged);
    connect(activeContoursList_, &QListWidget::itemChanged, this, &NControlSystemSettingsWidget::onActiveContourItemChanged);
    connect(branchModeCheckBox_, &QCheckBox::toggled, this, &NControlSystemSettingsWidget::onBranchModeCheckBoxToggled);
    connect(renshowModeCheckBox_, &QCheckBox::toggled, this, &NControlSystemSettingsWidget::onRenshowModeCheckBoxToggled);
    connect(afferentRangeModeComboBox_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &NControlSystemSettingsWidget::onAfferentRangeModeChanged);
    connect(useSimpleAfferentsCheckBox_, &QCheckBox::toggled, this, &NControlSystemSettingsWidget::onUseSimpleAfferentsCheckBoxToggled);
    connect(useNewNeuronsCheckBox_, &QCheckBox::toggled, this, &NControlSystemSettingsWidget::onUseNewNeuronsCheckBoxToggled);
    connect(transientTimeEdit_, &QLineEdit::editingFinished, this, &NControlSystemSettingsWidget::onTransientTimeEdited);
    connect(enableStructuralAdaptationCheckBox_, &QCheckBox::toggled, this, &NControlSystemSettingsWidget::onEnableStructuralAdaptationCheckBoxToggled);
    connect(maxAmpEdit_, &QLineEdit::editingFinished, this, &NControlSystemSettingsWidget::onMaxAmpEdited);
    connect(minAmpEdit_, &QLineEdit::editingFinished, this, &NControlSystemSettingsWidget::onMinAmpEdited);
}

NControlSystemSettingsWidget::~NControlSystemSettingsWidget() = default;

void NControlSystemSettingsWidget::setControlSystemName(const std::string &name)
{
    controlSystemName_ = name;
    updateFromModel();
}

void NControlSystemSettingsWidget::updateFromModel()
{
    if (controlSystemName_.empty())
        return;
    updateInProgress_ = true;
    updatePACFromModel();
    updateActiveContoursFromModel();
    updateModesFromModel();
    updateContourFromModel();
    updateStructuralAdaptationFromModel();
    updateInProgress_ = false;
}

void NControlSystemSettingsWidget::clear()
{
    controlSystemName_.clear();
    numControlLoops_ = 0;
    activeContoursList_->clear();
}

void NControlSystemSettingsWidget::onPacGainSliderChanged(int value)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "PacGain", static_cast<double>(value));
    }
    catch (...)
    {
    }
    pacGainEdit_->setText(QString::number(value, 'f', 3));
}

void NControlSystemSettingsWidget::onPacActivatorTimeSliderChanged(int value)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    double tc = double(value) / kTimeSliderMax;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "PacSecretionTC", tc);
    }
    catch (...)
    {
    }
    pacActivatorTimeEdit_->setText(QString::number(tc, 'f', 4));
}

void NControlSystemSettingsWidget::onPacDeactivatorTimeSliderChanged(int value)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    double tc = double(value) / kTimeSliderMax;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "PacDissociationTC", tc);
    }
    catch (...)
    {
    }
    pacDeactivatorTimeEdit_->setText(QString::number(tc, 'f', 4));
}

void NControlSystemSettingsWidget::onActiveContourItemChanged()
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    std::vector<bool> contours;
    contours.resize(activeContoursList_->count());
    for (int i = 0; i < activeContoursList_->count(); ++i)
        contours[i] = activeContoursList_->item(i)->checkState() == Qt::Checked;
    try
    {
        std::string valueStr;
        for (size_t i = 0; i < contours.size(); ++i)
        {
            if (i > 0)
                valueStr += ",";
            valueStr += contours[i] ? "true" : "false";
        }
        RDK::WriteParameterValue<std::string>(controlSystemName_, "ActiveContours", valueStr);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onBranchModeCheckBoxToggled(bool checked)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<int>(controlSystemName_, "MotoneuronBranchMode", checked ? 1 : 0);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onRenshowModeCheckBoxToggled(bool checked)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<int>(controlSystemName_, "RenshowMode", checked ? 1 : 0);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onAfferentRangeModeChanged(int index)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        RDK::WriteParameterValue<int>(controlSystemName_, "AfferentRangeMode", index);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::updatePACFromModel()
{
    try
    {
        double gain = RDK::ReadParameterValue<double>(controlSystemName_, "PacGain");
        pacGainSlider_->blockSignals(true);
        pacGainSlider_->setValue(static_cast<int>(std::round(gain)));
        pacGainSlider_->blockSignals(false);
        pacGainEdit_->setText(QString::number(gain, 'f', 3));
    }
    catch (...)
    {
    }
    try
    {
        double tc = RDK::ReadParameterValue<double>(controlSystemName_, "PacSecretionTC");
        pacActivatorTimeSlider_->blockSignals(true);
        pacActivatorTimeSlider_->setValue(static_cast<int>(std::round(tc * kTimeSliderMax)));
        pacActivatorTimeSlider_->blockSignals(false);
        pacActivatorTimeEdit_->setText(QString::number(tc, 'f', 4));
    }
    catch (...)
    {
    }
    try
    {
        double tc = RDK::ReadParameterValue<double>(controlSystemName_, "PacDissociationTC");
        pacDeactivatorTimeSlider_->blockSignals(true);
        pacDeactivatorTimeSlider_->setValue(static_cast<int>(std::round(tc * kTimeSliderMax)));
        pacDeactivatorTimeSlider_->blockSignals(false);
        pacDeactivatorTimeEdit_->setText(QString::number(tc, 'f', 4));
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::updateActiveContoursFromModel()
{
    try
    {
        std::string contoursStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "ActiveContours");
        std::vector<bool> contours;
        QStringList parts = QString::fromStdString(contoursStr).split(',', Qt::SkipEmptyParts);
        for (const QString &part : parts)
        {
            QString trimmed = part.trimmed().toLower();
            contours.push_back(trimmed == "true" || trimmed == "1");
        }
        try
        {
            numControlLoops_ = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumControlLoops"));
        }
        catch (...)
        {
            numControlLoops_ = static_cast<int>(contours.size());
        }
        activeContoursList_->blockSignals(true);
        activeContoursList_->clear();
        for (int i = 0; i < numControlLoops_; ++i)
        {
            QString label = tr("Afferent%1").arg(i + 1);
            if (i == 0)
                label += tr(" (II)");
            else if (i == 1)
                label += tr(" (Ia)");
            else if (i == 2)
                label += tr(" (Ib)");
            else if (i == 3)
                label += tr(" (Ic)");
            QListWidgetItem *item = new QListWidgetItem(label, activeContoursList_);
            item->setFlags(item->flags() | Qt::ItemIsUserCheckable);
            item->setCheckState(i < static_cast<int>(contours.size()) && contours[i] ? Qt::Checked : Qt::Unchecked);
        }
        activeContoursList_->blockSignals(false);
    }
    catch (...)
    {
        activeContoursList_->clear();
    }
}

void NControlSystemSettingsWidget::updateModesFromModel()
{
    try
    {
        int branchMode = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "MotoneuronBranchMode"));
        branchModeCheckBox_->blockSignals(true);
        branchModeCheckBox_->setChecked(branchMode != 0);
        branchModeCheckBox_->blockSignals(false);
    }
    catch (...)
    {
    }
    try
    {
        int renshowMode = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "RenshowMode"));
        renshowModeCheckBox_->blockSignals(true);
        renshowModeCheckBox_->setChecked(renshowMode != 0);
        renshowModeCheckBox_->blockSignals(false);
    }
    catch (...)
    {
    }
    try
    {
        int rangeMode = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "AfferentRangeMode"));
        afferentRangeModeComboBox_->blockSignals(true);
        afferentRangeModeComboBox_->setCurrentIndex(rangeMode);
        afferentRangeModeComboBox_->blockSignals(false);
    }
    catch (...)
    {
    }
    try
    {
        std::string afferentName = RDK::ReadParameterValue<std::string>(controlSystemName_, "MCAfferentObjectName");
        useSimpleAfferentsCheckBox_->blockSignals(true);
        useSimpleAfferentsCheckBox_->setChecked(afferentName == "NSimpleAfferentNeuron");
        useSimpleAfferentsCheckBox_->blockSignals(false);
    }
    catch (...)
    {
    }
    try
    {
        std::string neuronName = RDK::ReadParameterValue<std::string>(controlSystemName_, "MCNeuroObjectName");
        useNewNeuronsCheckBox_->blockSignals(true);
        useNewNeuronsCheckBox_->setChecked(neuronName == "NNewSynSPNeuron");
        useNewNeuronsCheckBox_->blockSignals(false);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::updateContourFromModel()
{
    try
    {
        std::string ampStr = RDK::ReadStateValue<std::string>(controlSystemName_, "CurrentContourAmplitude");
        currentContourAmplitudeEdit_->setText(QString::fromStdString(ampStr));
    }
    catch (...)
    {
        currentContourAmplitudeEdit_->clear();
    }
    try
    {
        std::string avgStr = RDK::ReadStateValue<std::string>(controlSystemName_, "CurrentContourAverage");
        currentContourAverageEdit_->setText(QString::fromStdString(avgStr));
    }
    catch (...)
    {
        currentContourAverageEdit_->clear();
    }
    try
    {
        double transientTime = RDK::ReadStateValue<double>(controlSystemName_, "CurrentTransientTime");
        transientTimeEdit_->setText(QString::number(transientTime, 'f', 3));
    }
    catch (...)
    {
        transientTimeEdit_->clear();
    }
    try
    {
        bool transientState = RDK::ReadStateValue<bool>(controlSystemName_, "CurrentTransientState");
        currentTransientStateCheckBox_->setChecked(transientState);
    }
    catch (...)
    {
        currentTransientStateCheckBox_->setChecked(false);
    }
    try
    {
        double speed = RDK::ReadStateValue<double>(controlSystemName_, "InstantAvgSpeed");
        instantAvgSpeedEdit_->setText(QString::number(speed, 'f', 3));
    }
    catch (...)
    {
        instantAvgSpeedEdit_->clear();
    }
}

void NControlSystemSettingsWidget::updateStructuralAdaptationFromModel()
{
    try
    {
        std::string useContourStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "UseContourData");
        QStringList parts = QString::fromStdString(useContourStr).split(',', Qt::SkipEmptyParts);
        bool enabled = !parts.isEmpty() && (parts[0].trimmed().toLower() == "true" || parts[0].trimmed() == "1");
        enableStructuralAdaptationCheckBox_->blockSignals(true);
        enableStructuralAdaptationCheckBox_->setChecked(enabled);
        enableStructuralAdaptationCheckBox_->blockSignals(false);
        maxAmpEdit_->setEnabled(!enabled);
        minAmpEdit_->setEnabled(!enabled);
    }
    catch (...)
    {
        enableStructuralAdaptationCheckBox_->setChecked(false);
        maxAmpEdit_->setEnabled(true);
        minAmpEdit_->setEnabled(true);
    }
    try
    {
        std::string maxAmpStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "DestContourMaxAmplitude");
        QStringList parts = QString::fromStdString(maxAmpStr).split(',', Qt::SkipEmptyParts);
        if (!parts.isEmpty())
            maxAmpEdit_->setText(parts[0].trimmed());
    }
    catch (...)
    {
        maxAmpEdit_->clear();
    }
    try
    {
        std::string minAmpStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "DestContourMinAmplitude");
        QStringList parts = QString::fromStdString(minAmpStr).split(',', Qt::SkipEmptyParts);
        if (!parts.isEmpty())
            minAmpEdit_->setText(parts[0].trimmed());
    }
    catch (...)
    {
        minAmpEdit_->clear();
    }
}

void NControlSystemSettingsWidget::onUseSimpleAfferentsCheckBoxToggled(bool checked)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        std::string value = checked ? "NSimpleAfferentNeuron" : "NAfferentNeuron";
        RDK::WriteParameterValue<std::string>(controlSystemName_, "MCAfferentObjectName", value);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onUseNewNeuronsCheckBoxToggled(bool checked)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        std::string value = checked ? "NNewSynSPNeuron" : "NSynSPNeuron";
        RDK::WriteParameterValue<std::string>(controlSystemName_, "MCNeuroObjectName", value);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onTransientTimeEdited()
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    bool ok = false;
    double value = transientTimeEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        RDK::WriteParameterValue<double>(controlSystemName_, "DestTransientTime", value);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onEnableStructuralAdaptationCheckBoxToggled(bool checked)
{
    if (updateInProgress_ || controlSystemName_.empty())
        return;
    try
    {
        int numLoops = numControlLoops_;
        if (numLoops <= 0)
        {
            numLoops = static_cast<int>(RDK::ReadParameterValue<double>(controlSystemName_, "NumControlLoops"));
        }
        std::string valueStr;
        for (int i = 0; i < numLoops; ++i)
        {
            if (i > 0)
                valueStr += ",";
            valueStr += checked ? "true" : "false";
        }
        RDK::WriteParameterValue<std::string>(controlSystemName_, "UseContourData", valueStr);
        maxAmpEdit_->setEnabled(!checked);
        minAmpEdit_->setEnabled(!checked);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onMaxAmpEdited()
{
    if (updateInProgress_ || controlSystemName_.empty() || enableStructuralAdaptationCheckBox_->isChecked())
        return;
    bool ok = false;
    double value = maxAmpEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        std::string currentStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "DestContourMaxAmplitude");
        QStringList parts = QString::fromStdString(currentStr).split(',', Qt::SkipEmptyParts);
        if (parts.isEmpty())
            parts.append("0.0");
        parts[0] = QString::number(value, 'f', 3);
        std::string newStr = parts.join(",").toStdString();
        RDK::WriteParameterValue<std::string>(controlSystemName_, "DestContourMaxAmplitude", newStr);
    }
    catch (...)
    {
    }
}

void NControlSystemSettingsWidget::onMinAmpEdited()
{
    if (updateInProgress_ || controlSystemName_.empty() || enableStructuralAdaptationCheckBox_->isChecked())
        return;
    bool ok = false;
    double value = minAmpEdit_->text().trimmed().toDouble(&ok);
    if (!ok)
        return;
    try
    {
        std::string currentStr = RDK::ReadParameterValue<std::string>(controlSystemName_, "DestContourMinAmplitude");
        QStringList parts = QString::fromStdString(currentStr).split(',', Qt::SkipEmptyParts);
        if (parts.isEmpty())
            parts.append("0.0");
        parts[0] = QString::number(value, 'f', 3);
        std::string newStr = parts.join(",").toStdString();
        RDK::WriteParameterValue<std::string>(controlSystemName_, "DestContourMinAmplitude", newStr);
    }
    catch (...)
    {
    }
}

