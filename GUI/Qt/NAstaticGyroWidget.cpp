#include "NAstaticGyroWidget.h"

#include <QLabel>
#include <QLineEdit>
#include <QVBoxLayout>

#include <rdk_application.h>
#include <rdk_engine_support.h>

#include <cmath>

namespace {
const double pi = 3.14159265358979;
}

NAstaticGyroWidget::NAstaticGyroWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      componentNameEdit_(nullptr),
      radiansLabel_(nullptr),
      degreesLabel_(nullptr)
{
    Name = "NAstaticGyroWidget";
    ClassName = "NAstaticGyroWidget";

    const QString title = tr("Astatic gyro");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *layout = new QVBoxLayout(this);
    layout->setContentsMargins(4, 4, 4, 4);

    layout->addWidget(new QLabel(tr("Component name (NAstaticGyro):"), this));
    componentNameEdit_ = new QLineEdit(this);
    componentNameEdit_->setPlaceholderText(tr("e.g. NAstaticGyro"));
    layout->addWidget(componentNameEdit_);

    radiansLabel_ = new QLabel(tr("radians:\nalpha = —\nbetta = —\ngamma = —"), this);
    radiansLabel_->setWordWrap(false);
    layout->addWidget(radiansLabel_);

    degreesLabel_ = new QLabel(tr("degrees:\nalpha = —\nbetta = —\ngamma = —"), this);
    degreesLabel_->setWordWrap(false);
    layout->addWidget(degreesLabel_);

    layout->addStretch();
    setLayout(layout);

    connect(componentNameEdit_, &QLineEdit::editingFinished, this, &NAstaticGyroWidget::onComponentNameEdited);
}

NAstaticGyroWidget::~NAstaticGyroWidget() = default;

void NAstaticGyroWidget::AUpdateInterface()
{
    readComponentData();
    radiansLabel_->setText(tr("radians:\nalpha = %1\nbetta = %2\ngamma = %3")
                               .arg(alpha_, 0, 'f', 6)
                               .arg(betta_, 0, 'f', 6)
                               .arg(gamma_, 0, 'f', 6));
    degreesLabel_->setText(tr("degrees:\nalpha = %1\nbetta = %2\ngamma = %3")
                               .arg(180.0 * alpha_ / pi, 0, 'f', 4)
                               .arg(180.0 * betta_ / pi, 0, 'f', 4)
                               .arg(180.0 * gamma_ / pi, 0, 'f', 4));
}

void NAstaticGyroWidget::AClearInterface()
{
    componentName_.clear();
    componentNameEdit_->clear();
    alpha_ = 0.0;
    betta_ = 0.0;
    gamma_ = 0.0;
    radiansLabel_->setText(tr("radians:\nalpha = —\nbetta = —\ngamma = —"));
    degreesLabel_->setText(tr("degrees:\nalpha = —\nbetta = —\ngamma = —"));
}

void NAstaticGyroWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("AstaticGyro");
    xml.WriteString("ComponentName", componentName_);
    xml.SelectUp();
}

void NAstaticGyroWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("AstaticGyro");
    componentName_ = xml.ReadString("ComponentName", "");
    xml.SelectUp();
    componentNameEdit_->setText(QString::fromStdString(componentName_));
}

void NAstaticGyroWidget::onComponentNameEdited()
{
    componentName_ = componentNameEdit_->text().trimmed().toStdString();
}

void NAstaticGyroWidget::readComponentData()
{
    if (componentName_.empty())
        return;
    try
    {
        alpha_ = RDK::ReadStateValue<double>(componentName_, "alpha");
        betta_ = RDK::ReadStateValue<double>(componentName_, "betta");
        gamma_ = RDK::ReadStateValue<double>(componentName_, "gamma");
    }
    catch (...)
    {
    }
}
