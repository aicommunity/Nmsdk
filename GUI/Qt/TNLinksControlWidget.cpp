#include "TNLinksControlWidget.h"

#include <QComboBox>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>

#include <rdk_application.h>

#include "UComponentLinksWidget.h"

TNLinksControlWidget::TNLinksControlWidget(QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app),
      topGroup_(nullptr),
      modeCombo_(nullptr),
      firstEdit_(nullptr),
      secondEdit_(nullptr),
      openButton_(nullptr),
      linksWidget_(nullptr)
{
    Name = "TNLinksControlWidget";
    ClassName = "TNLinksControlWidget";

    const QString title = tr("Links (UComponentLinksWidget)");
    setAccessibleName(title);
    setWindowTitle(title);

    auto *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(4, 4, 4, 4);

    topGroup_ = new QGroupBox(tr("Setup"), this);
    auto *topLayout = new QHBoxLayout(topGroup_);
    topLayout->addWidget(new QLabel(tr("Mode:"), topGroup_));
    modeCombo_ = new QComboBox(topGroup_);
    modeCombo_->addItems({tr("Single component"), tr("Two components")});
    topLayout->addWidget(modeCombo_);
    topLayout->addWidget(new QLabel(tr("First:"), topGroup_));
    firstEdit_ = new QLineEdit(topGroup_);
    firstEdit_->setPlaceholderText(tr("component name"));
    topLayout->addWidget(firstEdit_, 1);
    topLayout->addWidget(new QLabel(tr("Second:"), topGroup_));
    secondEdit_ = new QLineEdit(topGroup_);
    secondEdit_->setPlaceholderText(tr("component name"));
    topLayout->addWidget(secondEdit_, 1);
    openButton_ = new QPushButton(tr("Open/Refresh"), topGroup_);
    topLayout->addWidget(openButton_);
    mainLayout->addWidget(topGroup_);

    linksWidget_ = new UComponentLinksWidget(this, app);
    mainLayout->addWidget(linksWidget_, 1);

    setLayout(mainLayout);

    connect(modeCombo_, QOverload<int>::of(&QComboBox::currentIndexChanged), this, &TNLinksControlWidget::onModeChanged);
    connect(openButton_, &QPushButton::clicked, this, &TNLinksControlWidget::onOpenClicked);

    applyModeUi();
}

TNLinksControlWidget::~TNLinksControlWidget() = default;

void TNLinksControlWidget::AUpdateInterface()
{
    // Обновляет только вложенный виджет связей (если он инициализирован).
    linksWidget_->UpdateInterface(false);
}

void TNLinksControlWidget::AClearInterface()
{
    firstName_.clear();
    secondName_.clear();
    firstEdit_->clear();
    secondEdit_->clear();
    linksWidget_->unInit();
}

void TNLinksControlWidget::ASaveParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("LinksControl");
    xml.WriteString("Mode", std::to_string(mode_));
    xml.WriteString("First", firstName_);
    xml.WriteString("Second", secondName_);
    xml.SelectUp();
}

void TNLinksControlWidget::ALoadParameters(RDK::USerStorageXML &xml)
{
    xml.SelectNodeForce("LinksControl");
    try
    {
        mode_ = std::stoi(xml.ReadString("Mode", "0"));
    }
    catch (...)
    {
        mode_ = 0;
    }
    firstName_ = xml.ReadString("First", "");
    secondName_ = xml.ReadString("Second", "");
    xml.SelectUp();

    modeCombo_->setCurrentIndex(mode_);
    firstEdit_->setText(QString::fromStdString(firstName_));
    secondEdit_->setText(QString::fromStdString(secondName_));
    applyModeUi();
    initLinksWidget();
}

void TNLinksControlWidget::onModeChanged(int index)
{
    mode_ = index;
    applyModeUi();
}

void TNLinksControlWidget::onOpenClicked()
{
    firstName_ = firstEdit_->text().trimmed().toStdString();
    secondName_ = secondEdit_->text().trimmed().toStdString();
    initLinksWidget();
}

void TNLinksControlWidget::applyModeUi()
{
    const bool two = (mode_ == 1);
    secondEdit_->setEnabled(two);
}

void TNLinksControlWidget::initLinksWidget()
{
    if (mode_ == 0)
    {
        if (firstName_.empty())
        {
            linksWidget_->unInit();
            return;
        }
        linksWidget_->initWidget(QString::fromStdString(firstName_));
        return;
    }

    // two components
    if (firstName_.empty() || secondName_.empty())
    {
        linksWidget_->unInit();
        return;
    }
    linksWidget_->initWidget(QString::fromStdString(firstName_), QString::fromStdString(secondName_));
}

