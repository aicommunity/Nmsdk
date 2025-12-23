#include "PropertyAliasAnalyzer.h"

#include <QCoreApplication>
#include <QDir>
#include <QDirIterator>
#include <QFile>
#include <QFileInfo>
#include <QRegularExpression>
#include <QXmlStreamReader>
#include <QtDebug>
#include <algorithm>

#include "../../Rdk/Core/Engine/UContainer.h"
#include "../../Rdk/Core/Engine/UNet.h"
#include "../../Rdk/Core/Engine/UStorage.h"
#include "../../Rdk/Core/Engine/UComponent.h"
#include "../../Rdk/Core/Engine/UProperty.h"

namespace NeuroModeler {

PropertyAliasAnalyzer::PropertyAliasAnalyzer()
{
}

std::vector<PropertyAliasCandidate> PropertyAliasAnalyzer::AnalyzeComponent(
    RDK::UEPtr<RDK::UContainer> component,
    const PropertyAliasAnalyzerOptions& options)
{
    std::vector<PropertyAliasCandidate> candidates;
    
    if (!component)
        return candidates;
    
    // Анализируем частоту использования, если нужно
    QHash<QString, int> usageFrequency;
    if (options.analyzeConfigs && !options.configsPath.isEmpty())
    {
        QString className = QString::fromStdString(component->GetCompClassName());
        AnalyzeConfigUsage(className, options.configsPath, usageFrequency);
    }
    
    // Рекурсивно обходим структуру компонента
    TraverseComponent(component, QString(), 0, options, candidates);
    
    // Применяем частоту использования к кандидатам
    for (auto& candidate : candidates)
    {
        QString fullPathKey = candidate.fullPath;
        if (usageFrequency.contains(fullPathKey))
        {
            candidate.usageFrequency = usageFrequency[fullPathKey];
        }
        candidate.priority = CalculatePriority(candidate, options);
    }
    
    // Сортируем по приоритету (выше = важнее)
    std::sort(candidates.begin(), candidates.end(),
              [](const PropertyAliasCandidate& a, const PropertyAliasCandidate& b) {
                  return a.priority > b.priority;
              });
    
    // Ограничиваем количество
    if (candidates.size() > static_cast<size_t>(options.maxAliasesPerComponent))
    {
        candidates.resize(options.maxAliasesPerComponent);
    }
    
    return candidates;
}

void PropertyAliasAnalyzer::TraverseComponent(
    RDK::UEPtr<RDK::UContainer> component,
    const QString& parentPath,
    int depth,
    const PropertyAliasAnalyzerOptions& options,
    std::vector<PropertyAliasCandidate>& candidates)
{
    if (!component)
        return;
    
    try
    {
        // Анализируем свойства текущего компонента
        AnalyzeComponentProperties(component, parentPath, depth, options, candidates);
    }
    catch (...)
    {
        // Игнорируем ошибки при анализе свойств
        // Продолжаем обход вложенных компонентов
    }
    
    // Если это UNet, обходим вложенные компоненты
    RDK::UEPtr<RDK::UNet> net = dynamic_pointer_cast<RDK::UNet>(component);
    if (!net)
        return;
    
    try
    {
        std::vector<std::string> childNames;
        component->GetComponentsList(childNames);
        
        for (const auto& childName : childNames)
        {
            try
            {
                RDK::UEPtr<RDK::UContainer> child = component->GetComponent(childName, true);
                if (!child)
                    continue;
                
                QString childPath = parentPath.isEmpty() 
                    ? QString::fromStdString(childName)
                    : parentPath + "." + QString::fromStdString(childName);
                
                TraverseComponent(child, childPath, depth + 1, options, candidates);
            }
            catch (...)
            {
                // Игнорируем ошибки при доступе к отдельным дочерним компонентам
                // Продолжаем обход остальных компонентов
                continue;
            }
        }
    }
    catch (...)
    {
        // Игнорируем ошибки при получении списка компонентов
    }
}

void PropertyAliasAnalyzer::AnalyzeComponentProperties(
    RDK::UEPtr<RDK::UContainer> component,
    const QString& componentPath,
    int depth,
    const PropertyAliasAnalyzerOptions& options,
    std::vector<PropertyAliasCandidate>& candidates)
{
    if (!component || depth < options.minDepth)
        return;
    
    try
    {
        // Получаем список свойств компонента
        const auto& properties = component->GetPropertiesList();
    
    for (const auto& propEntry : properties)
    {
        const std::string& propName = propEntry.first;
        QString propNameQ = QString::fromStdString(propName);
        
        // Проверяем исключения
        if (ShouldExcludeProperty(propNameQ, options.excludePatterns))
            continue;
        
        RDK::UEPtr<RDK::UIProperty> property = propEntry.second.Property;
        if (!property)
            continue;
        
        // Проверяем, является ли свойство важным
        if (!IsImportantProperty(property, options))
            continue;
        
        // Определяем тип свойства через UVariable (имеет CheckMask)
        unsigned int propType = 0;
        if (propEntry.second.CheckMask(ptPubOutput | ptOutput))
            propType = ptPubOutput | ptOutput;
        else if (propEntry.second.CheckMask(ptPubInput | ptInput))
            propType = ptPubInput | ptInput;
        else if (propEntry.second.CheckMask(ptPubParameter | ptParameter))
            propType = ptPubParameter | ptParameter;
        else if (propEntry.second.CheckMask(ptPubState | ptState))
            propType = ptPubState | ptState;
        
        if (propType == 0)
            continue;
        
        // Создаем кандидата
        PropertyAliasCandidate candidate;
        candidate.componentPath = componentPath;
        candidate.propertyName = propNameQ;
        candidate.fullPath = componentPath.isEmpty() 
            ? propNameQ
            : componentPath + "." + propNameQ;
        candidate.propertyType = propType;
        candidate.depth = depth;
        candidate.aliasName = GenerateAliasName(componentPath, propNameQ);
        
        candidates.push_back(candidate);
    }
    }
    catch (...)
    {
        // Игнорируем ошибки при анализе свойств компонента
    }
}

bool PropertyAliasAnalyzer::IsImportantProperty(
    RDK::UEPtr<RDK::UIProperty> property,
    const PropertyAliasAnalyzerOptions& options)
{
    if (!property)
        return false;
    
    // Проверяем, является ли свойство публичным
    // Проверяем, является ли свойство публичным (через Type из UVariable)
    // Для этого нужно получить доступ к UVariable, но у нас только UIProperty
    // Пока пропускаем эту проверку
    // TODO: Передавать UVariable вместо UIProperty
    if (false) // Временно отключено
        return false;
    
    // Проверяем предпочтительные типы (нужно получить UVariable из property)
    // Для этого нужно найти свойство в компоненте
    // Пока пропускаем эту проверку, так как у нас нет прямого доступа к UVariable
    // TODO: Передавать UVariable вместо UIProperty в IsImportantProperty
    
    // Исключаем системные свойства
    QString propName = QString::fromStdString(property->GetName());
    if (propName.startsWith("DataInput") || propName.startsWith("DataOutput"))
        return false;
    
    return true;
}

int PropertyAliasAnalyzer::CalculatePriority(
    const PropertyAliasCandidate& candidate,
    const PropertyAliasAnalyzerOptions& options)
{
    int priority = 0;
    
    // Приоритет по типу свойства
    if (candidate.propertyType & (ptPubOutput | ptOutput))
        priority += 100;
    else if (candidate.propertyType & (ptPubInput | ptInput))
        priority += 80;
    else if (candidate.propertyType & (ptPubParameter | ptParameter))
        priority += 60;
    else if (candidate.propertyType & (ptPubState | ptState))
        priority += 40;
    
    // Приоритет по глубине (более глубокие = важнее, так как их сложнее найти)
    priority += candidate.depth * 10;
    
    // Приоритет по частоте использования
    priority += candidate.usageFrequency * 5;
    
    // Штраф за длинные пути (предпочитаем более короткие имена)
    int pathLength = candidate.fullPath.length();
    priority -= pathLength / 10;
    
    return priority;
}

QString PropertyAliasAnalyzer::GenerateAliasName(const QString& componentPath, const QString& propertyName)
{
    // Генерируем имя алиаса из пути компонента и имени свойства
    // Например: "LTZone.Output" -> "LTZoneOutput"
    // "Soma1.ExcChannel.Output" -> "Soma1ExcChannelOutput"
    
    QString alias = componentPath;
    if (!alias.isEmpty())
    {
        // Убираем точки и заменяем на заглавные буквы
        alias.replace(".", "");
        // Делаем первую букву заглавной
        if (!alias.isEmpty())
            alias[0] = alias[0].toUpper();
    }
    
    // Добавляем имя свойства
    QString prop = propertyName;
    if (!prop.isEmpty())
        prop[0] = prop[0].toUpper();
    
    return alias + prop;
}

bool PropertyAliasAnalyzer::ShouldExcludeProperty(
    const QString& propertyName,
    const QSet<QString>& excludePatterns)
{
    for (const QString& pattern : excludePatterns)
    {
        QRegularExpression regex(pattern, QRegularExpression::CaseInsensitiveOption);
        if (regex.match(propertyName).hasMatch())
            return true;
    }
    return false;
}

void PropertyAliasAnalyzer::AnalyzeConfigUsage(
    const QString& className,
    const QString& configsPath,
    QHash<QString, int>& usageFrequency)
{
    // Проверяем кэш
    QString cacheKey = className + ":" + configsPath;
    if (usageCache_.contains(cacheKey))
    {
        usageFrequency = usageCache_[cacheKey];
        return;
    }
    
    QDir configDir(configsPath);
    if (!configDir.exists())
        return;
    
    // Ищем все XML файлы в конфигурациях (рекурсивно)
    QStringList filters;
    filters << "*.xml";
    
    QFileInfoList files = configDir.entryInfoList(filters, QDir::Files | QDir::Readable | QDir::NoDotAndDotDot, QDir::Name);
    
    // Рекурсивно ищем в подпапках
    QDirIterator it(configDir.absolutePath(), filters, QDir::Files | QDir::Readable, QDirIterator::Subdirectories);
    while (it.hasNext())
    {
        files.append(QFileInfo(it.next()));
    }
    
    for (const QFileInfo& fileInfo : files)
    {
        QFile file(fileInfo.absoluteFilePath());
        if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
            continue;
        
        QXmlStreamReader xml(&file);
        QString currentPath;
        
        while (!xml.atEnd())
        {
            xml.readNext();
            
            if (xml.isStartElement())
            {
                QString elementName = xml.name().toString();
                
                // Ищем атрибуты и текстовые значения, которые могут быть путями к свойствам
                QXmlStreamAttributes attrs = xml.attributes();
                for (const QXmlStreamAttribute& attr : attrs)
                {
                    QString attrValue = attr.value().toString();
                    // Проверяем, похоже ли значение на путь к свойству (содержит точку)
                    if (attrValue.contains(".") && attrValue.length() > 3)
                    {
                        usageFrequency[attrValue]++;
                    }
                }
                
                // Также проверяем текстовое содержимое элементов
                QString text = xml.readElementText();
                if (text.contains(".") && text.length() > 3)
                {
                    usageFrequency[text]++;
                }
            }
        }
        
        file.close();
    }
    
    // Сохраняем в кэш
    usageCache_[cacheKey] = usageFrequency;
}

} // namespace NeuroModeler

