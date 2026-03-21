#include "NNeuronTrainerWidget.h"

#include <QGroupBox>
#include <QLabel>
#include <QLineEdit>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>

NNeuronTrainerWidget::NNeuronTrainerWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      trainerName_("NeuronTrainer"),
      trainerNameEdit_(nullptr),
      paramsGroup_(nullptr),
      numInputDendriteLabel_(nullptr),
      delayLabel_(nullptr),
      spikesFrequencyLabel_(nullptr),
      maxDendriteLengthLabel_(nullptr),
      ltzThresholdLabel_(nullptr),
      useFixedLTZLabel_(nullptr),
      isTrainingLabel_(nullptr)
{
    Name = "NNeuronTrainerWidget";
    ClassName = "NNeuronTrainerWidget";

    const QString title = tr("Neuron trainer");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    layout->addWidget(new QLabel(tr("Component name (NNeuronTrainer):"), this));
    trainerNameEdit_ = new QLineEdit(this);
    trainerNameEdit_->setText(QString::fromStdString(trainerName_));
    trainerNameEdit_->setPlaceholderText(tr("e.g. NeuronTrainer"));
    layout->addWidget(trainerNameEdit_);

    paramsGroup_ = new QGroupBox(tr("Parameters (from model)"), this);
    auto *paramsLayout = new QVBoxLayout(paramsGroup_);
    numInputDendriteLabel_ = new QLabel(tr("NumInputDendrite: —"), paramsGroup_);
    delayLabel_ = new QLabel(tr("Delay: —"), paramsGroup_);
    spikesFrequencyLabel_ = new QLabel(tr("SpikesFrequency: —"), paramsGroup_);
    maxDendriteLengthLabel_ = new QLabel(tr("MaxDendriteLength: —"), paramsGroup_);
    ltzThresholdLabel_ = new QLabel(tr("LTZThreshold: —"), paramsGroup_);
    useFixedLTZLabel_ = new QLabel(tr("UseFixedLTZThreshold: —"), paramsGroup_);
    isTrainingLabel_ = new QLabel(tr("IsNeedToTrain: —"), paramsGroup_);
    paramsLayout->addWidget(numInputDendriteLabel_);
    paramsLayout->addWidget(delayLabel_);
    paramsLayout->addWidget(spikesFrequencyLabel_);
    paramsLayout->addWidget(maxDendriteLengthLabel_);
    paramsLayout->addWidget(ltzThresholdLabel_);
    paramsLayout->addWidget(useFixedLTZLabel_);
    paramsLayout->addWidget(isTrainingLabel_);
    layout->addWidget(paramsGroup_);

    layout->addStretch();
    setLayout(layout);

    connect(trainerNameEdit_, &QLineEdit::editingFinished, this, &NNeuronTrainerWidget::onTrainerNameEdited);
}

NNeuronTrainerWidget::~NNeuronTrainerWidget() = default;

void NNeuronTrainerWidget::AAfterLoadProject()
{
    UpdateInterface(true);
}

void NNeuronTrainerWidget::AUpdateInterface()
{
    if (trainerName_.empty())
        return;

    try
    {
        numInputDendrite_    = RDK::ReadParameterValue<int>(trainerName_, "NumInputDendrite");
        delay_               = RDK::ReadParameterValue<double>(trainerName_, "Delay");
        spikesFrequency_     = RDK::ReadParameterValue<double>(trainerName_, "SpikesFrequency");
        maxDendriteLength_   = RDK::ReadParameterValue<int>(trainerName_, "MaxDendriteLength");
        ltzThreshold_        = RDK::ReadParameterValue<double>(trainerName_, "LTZThreshold");
        useFixedLTZThreshold_ =
            RDK::ReadParameterValue<bool>(trainerName_, "UseFixedLTZThreshold");
        isTraining_          = RDK::ReadParameterValue<bool>(trainerName_, "IsNeedToTrain");
    }
    catch (...)
    {
    }
    updateLabels();
}

void NNeuronTrainerWidget::AClearInterface()
{
    numInputDendrite_ = 0;
    delay_ = 0.0;
    spikesFrequency_ = 0.0;
    maxDendriteLength_ = 0;
    ltzThreshold_ = 0.0;
    useFixedLTZThreshold_ = false;
    isTraining_ = false;
    updateLabels();
}

void NNeuronTrainerWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NeuronTrainer");
    xml.WriteString("TrainerName", trainerName_);
    xml.SelectUp();
}

void NNeuronTrainerWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("NeuronTrainer");
    trainerName_ = xml.ReadString("TrainerName", "NeuronTrainer");
    xml.SelectUp();
    trainerNameEdit_->setText(QString::fromStdString(trainerName_));
}

void NNeuronTrainerWidget::onTrainerNameEdited()
{
    trainerName_ = trainerNameEdit_->text().trimmed().toStdString();
    if (trainerName_.empty())
        trainerName_ = "NeuronTrainer";
}

void NNeuronTrainerWidget::updateLabels()
{
    numInputDendriteLabel_->setText(tr("NumInputDendrite: %1").arg(numInputDendrite_));
    delayLabel_->setText(tr("Delay: %1").arg(delay_, 0, 'f', 4));
    spikesFrequencyLabel_->setText(tr("SpikesFrequency: %1").arg(spikesFrequency_, 0, 'f', 4));
    maxDendriteLengthLabel_->setText(tr("MaxDendriteLength: %1").arg(maxDendriteLength_));
    ltzThresholdLabel_->setText(tr("LTZThreshold: %1").arg(ltzThreshold_, 0, 'f', 4));
    useFixedLTZLabel_->setText(tr("UseFixedLTZThreshold: %1").arg(useFixedLTZThreshold_ ? tr("true") : tr("false")));
    isTrainingLabel_->setText(tr("IsNeedToTrain: %1").arg(isTraining_ ? tr("true") : tr("false")));
}