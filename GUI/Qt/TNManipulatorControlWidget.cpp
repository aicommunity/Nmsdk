#include "TNManipulatorControlWidget.h"

#include <QVBoxLayout>
#include <QLabel>

TNManipulatorControlWidget::TNManipulatorControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
{
    // Имена для системы UIVisualController
    Name = "TNManipulatorControlWidget";
    ClassName = "TNManipulatorControlWidget";

    const QString title = tr("Manipulator control");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    auto *label = new QLabel(tr("Manipulator control (Qt stub widget)."), this);
    label->setWordWrap(true);
    layout->addWidget(label);

    setLayout(layout);
}

TNManipulatorControlWidget::~TNManipulatorControlWidget() = default;

void TNManipulatorControlWidget::AUpdateInterface()
{
    // TODO: перенести обновление состояния манипулятора из BCB-формы
}

void TNManipulatorControlWidget::AClearInterface()
{
    // TODO: очистка UI при закрытии проекта/сбросе
}

void TNManipulatorControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    Q_UNUSED(xml);
    // TODO: сохранить пользовательские настройки/положение элементов
}

void TNManipulatorControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    Q_UNUSED(xml);
    // TODO: загрузить пользовательские настройки/положение элементов
}

