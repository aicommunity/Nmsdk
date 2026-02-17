#include "TNDrawManipulatorWidget.h"

#include <QVBoxLayout>
#include <QLabel>

TNDrawManipulatorWidget::TNDrawManipulatorWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
{
    Name = "TNDrawManipulatorWidget";
    ClassName = "TNDrawManipulatorWidget";

    const QString title = tr("Manipulator visualization");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *label = new QLabel(tr("Manipulator visualization (Qt stub widget)."), this);
    label->setWordWrap(true);
    layout->addWidget(label);

    setLayout(layout);
}

TNDrawManipulatorWidget::~TNDrawManipulatorWidget() = default;

void TNDrawManipulatorWidget::AUpdateInterface()
{
    // TODO: обновлять изображение/состояние манипулятора
}

void TNDrawManipulatorWidget::AClearInterface()
{
    // TODO: очистить визуализацию при закрытии проекта/сбросе
}

