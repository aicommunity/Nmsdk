// Stub implementation for UClassFavoritesEditor for unit tests
// This avoids pulling in all dependencies

#include "UClassFavoritesEditor.h"
#include <QWidget>
#include <QString>
#include <string>
#include <rdk_application.h>

UClassFavoritesEditor::UClassFavoritesEditor(std::string class_name, QWidget *parent, RDK::UApplication *app)
    : UVisualControllerWidget(parent, app)
    , ClassName(class_name)
    , componentList(nullptr)
    , ui(nullptr)
{
    // Stub implementation - not used in movement tests
}

UClassFavoritesEditor::~UClassFavoritesEditor()
{
    // Stub implementation
}

void UClassFavoritesEditor::ChangeClass(std::string class_name)
{
    ClassName = class_name;
    // Stub
}

// Note: CreateNewFavorite is a signal, not a method, so MOC generates it automatically
// No implementation needed

void UClassFavoritesEditor::CreateFavorite()
{
    // Stub
}

void UClassFavoritesEditor::ValidatePath()
{
    // Stub
}

void UClassFavoritesEditor::ShowPathPreview()
{
    // Stub
}

bool UClassFavoritesEditor::ValidatePropertyPath(const QString& path, QString& errorMessage)
{
    errorMessage = QString(); // Stub
    return true;
}

QString UClassFavoritesEditor::PreviewResolvedPath(const QString& path)
{
    return QString(); // Stub
}
