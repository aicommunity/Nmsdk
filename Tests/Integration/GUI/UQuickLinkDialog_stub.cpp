// Stub implementation for UQuickLinkDialog for unit tests
// This avoids pulling in all dependencies

#include "UQuickLinkDialog.h"
#include <QWidget>
#include <QString>
#include <rdk_application.h>

UQuickLinkDialog::UQuickLinkDialog(QWidget *parent, const QString& componentName, RDK::UApplication *app)
    : QDialog(parent)
    , m_componentName(componentName)
    , m_application(app)
    , m_outputTree(nullptr)
    , m_inputTree(nullptr)
    , m_outputFilter(nullptr)
    , m_inputFilter(nullptr)
    , m_createButton(nullptr)
    , m_cancelButton(nullptr)
    , m_selectedSourceComponent()
    , m_selectedSourceProperty()
    , m_selectedTargetComponent()
    , m_selectedTargetProperty()
{
    // Stub implementation - not used in movement tests
}

UQuickLinkDialog::~UQuickLinkDialog()
{
    // Stub implementation
}

QString UQuickLinkDialog::getSelectedOutput() const
{
    return QString(); // Stub
}

QString UQuickLinkDialog::getSourceComponent() const
{
    return m_selectedSourceComponent; // Stub - return member
}

QString UQuickLinkDialog::getSourceProperty() const
{
    return m_selectedSourceProperty; // Stub - return member
}

QString UQuickLinkDialog::getSelectedInput() const
{
    return QString(); // Stub
}

QString UQuickLinkDialog::getTargetComponent() const
{
    return m_selectedTargetComponent; // Stub - return member
}

QString UQuickLinkDialog::getTargetProperty() const
{
    return m_selectedTargetProperty; // Stub - return member
}

void UQuickLinkDialog::onFilterChanged(const QString& text)
{
    // Stub
}

void UQuickLinkDialog::onOutputSelected(QTreeWidgetItem* item, int column)
{
    // Stub
}

void UQuickLinkDialog::onInputSelected(QTreeWidgetItem* item, int column)
{
    // Stub
}

void UQuickLinkDialog::validateSelection()
{
    // Stub
}

void UQuickLinkDialog::populateOutputs()
{
    // Stub
}

void UQuickLinkDialog::populateInputs()
{
    // Stub
}

void UQuickLinkDialog::filterTree(QTreeWidget* tree, const QString& filter)
{
    // Stub
}

QTreeWidgetItem* UQuickLinkDialog::createPropertyItem(const QString& componentName,
                                                       const QString& propertyName,
                                                       const QString& aliasName,
                                                       unsigned int propertyType,
                                                       bool isConnected)
{
    return nullptr; // Stub
}

bool UQuickLinkDialog::areTypesCompatible(unsigned int outputType, unsigned int inputType)
{
    return false; // Stub
}
