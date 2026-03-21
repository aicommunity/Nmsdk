#include "TNDrawManipulatorWidget.h"

#include <QLabel>
#include <QLineEdit>
#include <QPaintEvent>
#include <QPainter>
#include <QPen>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>

#include <cmath>

TNDrawManipulatorWidget::TNDrawManipulatorWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      canvasWidth_(400),
      canvasHeight_(400),
      x_(canvasWidth_ / 2.0),
      y_(50.0),
      angle_(0.0),
      movement_(0.0),
      length_(100.0),
      zeroAngle_(3.14159265358979 / 2.0),
      zeroMovement_(0.0),
      componentNameEdit_(nullptr),
      hintLabel_(nullptr)
{
    Name = "TNDrawManipulatorWidget";
    ClassName = "TNDrawManipulatorWidget";

    const QString title = tr("Manipulator visualization");
    setAccessibleName(title);
    setWindowTitle(title);

    setMinimumSize(canvasWidth_, canvasHeight_ + 80);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    hintLabel_ = new QLabel(tr("Component name (model):"), this);
    layout->addWidget(hintLabel_);
    componentNameEdit_ = new QLineEdit(this);
    componentNameEdit_->setPlaceholderText(tr("e.g. Engine or PendulumAndCart"));
    layout->addWidget(componentNameEdit_);

    layout->addStretch();
    setLayout(layout);

    connect(componentNameEdit_, &QLineEdit::editingFinished, this, &TNDrawManipulatorWidget::onComponentNameEdited);
}

TNDrawManipulatorWidget::~TNDrawManipulatorWidget() = default;

void TNDrawManipulatorWidget::AUpdateInterface()
{
    readComponentData();
    update();
}

void TNDrawManipulatorWidget::AClearInterface()
{
    componentName_.clear();
    componentNameEdit_->clear();
    angle_ = 0.0;
    movement_ = 0.0;
    update();
}

void TNDrawManipulatorWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("DrawManipulator");
    xml.WriteString("ComponentName", componentName_);
    xml.SelectUp();
}

void TNDrawManipulatorWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("DrawManipulator");
    componentName_ = xml.ReadString("ComponentName", "");
    xml.SelectUp();
    componentNameEdit_->setText(QString::fromStdString(componentName_));
}

void TNDrawManipulatorWidget::paintEvent(QPaintEvent *event)
{
    UVisualControllerWidget::paintEvent(event);

    const int w = width();
    const int h = height();
    if (w < 10 || h < 10)
        return;

    const int drawH = std::min(h - 70, canvasHeight_);
    const int drawW = std::min(w, canvasWidth_);
    const double cx = drawW / 2.0;
    const double cy = 50.0;
    const double baseX = cx + zeroMovement_ + movement_;
    const double baseY = cy;
    const double endX = baseX + length_ * std::cos(zeroAngle_ + angle_);
    const double endY = baseY + length_ * std::sin(zeroAngle_ + angle_);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    painter.fillRect(0, 0, drawW, drawH, Qt::white);

    // Сетка
    painter.setPen(QPen(QColor(230, 230, 230), 1));
    const int gridStep = 20;
    for (int x = 0; x <= drawW; x += gridStep)
        painter.drawLine(x, 0, x, drawH);
    for (int y = 0; y <= drawH; y += gridStep)
        painter.drawLine(0, y, drawW, y);

    // Оси + риски (как в BCB)
    painter.setPen(QPen(Qt::red, 2));
    painter.drawLine(0, static_cast<int>(baseY), drawW, static_cast<int>(baseY));
    painter.drawLine(static_cast<int>(cx), 0, static_cast<int>(cx), drawH);
    painter.setPen(QPen(Qt::red, 1));
    for (int i = 1; i <= 20; ++i)
    {
        const int dx = i * 10;
        painter.drawLine(int(cx + dx), int(baseY - 10), int(cx + dx), int(baseY));
        painter.drawLine(int(cx - dx), int(baseY - 10), int(cx - dx), int(baseY));
    }

    painter.setPen(QPen(Qt::black, 1));
    painter.drawLine(static_cast<int>(baseX), static_cast<int>(baseY),
                     static_cast<int>(endX), static_cast<int>(endY));

    painter.setPen(QPen(Qt::blue, 4));
    painter.drawLine(static_cast<int>(baseX), static_cast<int>(baseY),
                     static_cast<int>(endX), static_cast<int>(endY));
    painter.setBrush(Qt::blue);
    painter.drawEllipse(QPointF(baseX, baseY), 10, 10);
    painter.drawEllipse(QPointF(endX, endY), 10, 10);

    // Текстовые метки
    painter.setPen(QPen(Qt::black, 1));
    QFont f = painter.font();
    f.setPointSize(std::max(8, f.pointSize()));
    painter.setFont(f);
    painter.drawText(6, 16, QString("Angle: %1").arg(angle_, 0, 'f', 4));
    painter.drawText(6, 32, QString("Movement: %1").arg(movement_, 0, 'f', 2));
    painter.drawText(6, 48, QString("End: (%1, %2)").arg(endX, 0, 'f', 1).arg(endY, 0, 'f', 1));
}

void TNDrawManipulatorWidget::onComponentNameEdited()
{
    componentName_ = componentNameEdit_->text().trimmed().toStdString();
}

void TNDrawManipulatorWidget::readComponentData()
{
    if (componentName_.empty())
        return;
    try
    {
        angle_ = RDK::ReadStateValue<double>(componentName_, "Angle");
        movement_ = RDK::ReadStateValue<double>(componentName_, "Movement") * 100.0;
    }
    catch (...)
    {
    }
}