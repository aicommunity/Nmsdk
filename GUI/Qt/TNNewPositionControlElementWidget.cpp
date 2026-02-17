#include "TNNewPositionControlElementWidget.h"

#include <QVBoxLayout>
#include <QLabel>

TNNewPositionControlElementWidget::TNNewPositionControlElementWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
{
    Name = "TNNewPositionControlElementWidget";
    ClassName = "TNNewPositionControlElementWidget";

    const QString title = tr("Position control element");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *label = new QLabel(tr("Position control element (Qt stub widget)."), this);
    label->setWordWrap(true);
    layout->addWidget(label);

    setLayout(layout);
}

TNNewPositionControlElementWidget::~TNNewPositionControlElementWidget() = default;

void TNNewPositionControlElementWidget::AUpdateInterface()
{
    // TODO: обновление отображения целевой/текущей позиции
}

void TNNewPositionControlElementWidget::AClearInterface()
{
    // TODO: сброс внутренних состояний/отображения
}

