#include "TNDCEngineControlWidget.h"

#include <QVBoxLayout>
#include <QLabel>

TNDCEngineControlWidget::TNDCEngineControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
{
    Name = "TNDCEngineControlWidget";
    ClassName = "TNDCEngineControlWidget";

    const QString title = tr("DC engine control");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *label = new QLabel(tr("DC engine control (Qt stub widget)."), this);
    label->setWordWrap(true);
    layout->addWidget(label);

    setLayout(layout);
}

TNDCEngineControlWidget::~TNDCEngineControlWidget() = default;

void TNDCEngineControlWidget::AUpdateInterface()
{
    // TODO: обновлять состояние управления DC-двигателем
}

void TNDCEngineControlWidget::AClearInterface()
{
    // TODO: очистка интерфейса при закрытии проекта/сбросе
}

