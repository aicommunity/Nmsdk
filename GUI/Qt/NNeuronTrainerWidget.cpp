#include "NNeuronTrainerWidget.h"

#include <QVBoxLayout>
#include <QLabel>

NNeuronTrainerWidget::NNeuronTrainerWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
{
    Name = "NNeuronTrainerWidget";
    ClassName = "NNeuronTrainerWidget";

    const QString title = tr("Neuron trainer");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *label = new QLabel(tr("Neuron trainer (Qt stub widget)."), this);
    label->setWordWrap(true);
    layout->addWidget(label);

    setLayout(layout);
}

NNeuronTrainerWidget::~NNeuronTrainerWidget() = default;

void NNeuronTrainerWidget::AUpdateInterface()
{
    // TODO: обновление прогресса и метрик обучения
}

void NNeuronTrainerWidget::AClearInterface()
{
    // TODO: очистка интерфейса при закрытии проекта/сбросе
}

