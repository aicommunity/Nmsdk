#pragma once

#include <QString>
#include <QStringList>
#include <QHash>
#include <QSet>
#include <vector>
#include <map>
#include <string>

#include "../../Rdk/Core/Engine/UEPtr.h"

namespace RDK {
class UContainer;
class UStorage;
class UNet;
class UIProperty;
}

namespace NeuroModeler {

struct PropertyAliasCandidate
{
    QString aliasName;           // Имя алиаса (например, "LTZoneOutput")
    QString componentPath;       // Путь к компоненту (например, "LTZone")
    QString propertyName;        // Имя свойства (например, "Output")
    QString fullPath;             // Полный путь (например, "LTZone.Output")
    unsigned int propertyType;   // Тип свойства (ptOutput, ptInput, etc.)
    int depth;                   // Глубина вложенности
    int usageFrequency;          // Частота использования в конфигурациях
    int priority;                // Приоритет для генерации (выше = важнее)
    
    PropertyAliasCandidate()
        : propertyType(0), depth(0), usageFrequency(0), priority(0)
    {}
};

struct PropertyAliasAnalyzerOptions
{
    int minDepth = 2;                    // Минимальная глубина для генерации алиаса
    int maxAliasesPerComponent = 20;     // Максимальное количество алиасов на компонент
    QSet<QString> preferredTypes;        // Предпочтительные типы свойств
    QSet<QString> excludePatterns;       // Паттерны для исключения (например, "DataInput*")
    bool analyzeConfigs = true;           // Анализировать конфигурации для частоты использования
    QString configsPath;                  // Путь к конфигурациям
};

class PropertyAliasAnalyzer
{
public:
    PropertyAliasAnalyzer();
    
    // Анализ структуры компонента и генерация кандидатов на алиасы
    std::vector<PropertyAliasCandidate> AnalyzeComponent(
        RDK::UEPtr<RDK::UContainer> component,
        const PropertyAliasAnalyzerOptions& options = PropertyAliasAnalyzerOptions());
    
    // Анализ частоты использования свойств в конфигурациях
    void AnalyzeConfigUsage(const QString& className,
                            const QString& configsPath,
                            QHash<QString, int>& usageFrequency);
    
    // Генерация имени алиаса из пути к свойству
    static QString GenerateAliasName(const QString& componentPath, const QString& propertyName);
    
    // Проверка, следует ли исключить свойство
    static bool ShouldExcludeProperty(const QString& propertyName, const QSet<QString>& excludePatterns);

private:
    // Рекурсивный обход структуры компонента
    void TraverseComponent(
        RDK::UEPtr<RDK::UContainer> component,
        const QString& parentPath,
        int depth,
        const PropertyAliasAnalyzerOptions& options,
        std::vector<PropertyAliasCandidate>& candidates);
    
    // Анализ свойств компонента
    void AnalyzeComponentProperties(
        RDK::UEPtr<RDK::UContainer> component,
        const QString& componentPath,
        int depth,
        const PropertyAliasAnalyzerOptions& options,
        std::vector<PropertyAliasCandidate>& candidates);
    
    // Вычисление приоритета кандидата
    int CalculatePriority(const PropertyAliasCandidate& candidate, const PropertyAliasAnalyzerOptions& options);
    
    // Проверка, является ли свойство важным для алиаса
    bool IsImportantProperty(RDK::UEPtr<RDK::UIProperty> property, const PropertyAliasAnalyzerOptions& options);
    
    // Кэш для частоты использования
    QHash<QString, QHash<QString, int>> usageCache_;
};

} // namespace NeuroModeler

