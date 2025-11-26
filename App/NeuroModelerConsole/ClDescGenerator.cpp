#include "ClDescGenerator.h"

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QRegularExpression>
#include <QtDebug>
#include <string>
#include <vector>

#include "../../Rdk/Core/Engine/UContainerDescription.h"
#include "../../Rdk/Core/Engine/ULibrary.h"

namespace NeuroModeler {

namespace {

constexpr const char* kTokensKey = "tokens";
constexpr const char* kClassOverridesKey = "classOverrides";
constexpr const char* kPropertyOverridesKey = "propertyOverrides";
constexpr const char* kPropertyFallbacksKey = "propertyFallbacks";

QString toLowerKey(const QString& value)
{
    return value.trimmed().toLower();
}

QString capitalize(const QString& value)
{
    if (value.isEmpty())
        return value;
    QString result = value;
    result[0] = result.at(0).toUpper();
    return result;
}

NeuroModeler::ClDescGenerator::TextOverride parseTextOverride(const QJsonObject& object)
{
    NeuroModeler::ClDescGenerator::TextOverride override;
    override.header = object.value(QStringLiteral("header")).toString();
    override.description = object.value(QStringLiteral("description")).toString();
    return override;
}

} // namespace

bool ClDescGenerator::Generate(RDK::UELockPtr<RDK::UStorage> storage,
                               const ClDescGeneratorOptions& options,
                               QString* errorMessage)
{
    if (!storage)
    {
        if (errorMessage)
            *errorMessage = QStringLiteral("Не удалось получить ссылку на UStorage.");
        return false;
    }

    if (!lexiconLoaded_ && !ensureLexiconLoaded(options.lexiconCandidatePaths, errorMessage))
    {
        qWarning() << "ClDescGenerator: lexicon not found, будут использованы простые автогенераторы.";
    }

    // Перед началом генерации подгружаем существующие XML, чтобы не потерять ручные описания.
    storage->LoadClassesDescription();

    std::vector<std::string> classNames;
    storage->GetClassNameList(classNames);

    size_t createdCount = 0;
    size_t updatedCount = 0;
    QHash<QString, int> perLibraryStats;

    for (const auto& className : classNames)
    {
        auto description = storage->GetClassDescription(className, true);
        bool createdNow = false;
        if (!description)
        {
            description = new RDK::UContainerDescription();
            createdNow = true;
        }

        auto library = storage->FindCollection(className);
        std::string libraryName = library ? library->GetName() : "Uncategorized";

        if (!options.libraryFilters.isEmpty())
        {
            const QString libName = QString::fromStdString(libraryName);
            bool allowed = false;
            for (const QString& filter : options.libraryFilters)
            {
                if (libName.compare(filter, Qt::CaseInsensitive) == 0)
                {
                    allowed = true;
                    break;
                }
            }
            if (!allowed)
            {
                continue;
            }
        }

        if (!options.classFilters.isEmpty())
        {
            const QString clsName = QString::fromStdString(className);
            bool allowed = false;
            for (const QString& filter : options.classFilters)
            {
                if (clsName.compare(filter, Qt::CaseInsensitive) == 0)
                {
                    allowed = true;
                    break;
                }
            }
            if (!allowed)
            {
                continue;
            }
        }

        description->SetStorage(storage.Get());
        description->SetClassNameValue(className);
        description->CreateProperties();

        applyClassText(className, libraryName, description, options.forceOverride);
        applyPropertiesText(className, QString::fromStdString(description->GetHeader()), description, options.forceOverride);

        storage->SetClassDescription(className, description);
        storage->SaveClassDescriptionToFile(className);

        if (createdNow)
            ++createdCount;
        else
            ++updatedCount;

        perLibraryStats[QString::fromStdString(libraryName)] += 1;
    }

    if (options.verbose)
    {
        qInfo() << "ClDescGenerator: processed" << classNames.size()
                << "классов (новых:" << createdCount << ", обновлено:" << updatedCount << ").";
        if (!lexiconPathUsed_.isEmpty())
        {
            qInfo() << "ClDescGenerator: словарь" << lexiconPathUsed_;
        }
        qInfo() << "ClDescGenerator: статистика по библиотекам:";
        for (auto it = perLibraryStats.constBegin(); it != perLibraryStats.constEnd(); ++it)
        {
            qInfo() << " -" << it.key() << ":" << it.value();
        }
    }

    return true;
}

bool ClDescGenerator::ensureLexiconLoaded(const QStringList& candidatePaths, QString* errorMessage)
{
    if (lexiconLoaded_)
        return true;

    QStringList actualCandidates = candidatePaths;
    if (actualCandidates.isEmpty())
    {
        const QString appDir = QCoreApplication::applicationDirPath();
        actualCandidates << QDir::current().absoluteFilePath(QStringLiteral("Docs/ClDescLexicon.json"))
                         << QDir(appDir).absoluteFilePath(QStringLiteral("../../Docs/ClDescLexicon.json"))
                         << QDir(appDir).absoluteFilePath(QStringLiteral("../Docs/ClDescLexicon.json"))
                         << QStringLiteral("Docs/ClDescLexicon.json");
    }

    for (const QString& path : actualCandidates)
    {
        if (loadLexiconFromFile(path, errorMessage))
        {
            lexiconLoaded_ = true;
            lexiconPathUsed_ = path;
            return true;
        }
    }

    return false;
}

bool ClDescGenerator::loadLexiconFromFile(const QString& path, QString* errorMessage)
{
    QFile file(path);
    if (!file.exists())
        return false;

    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    {
        if (errorMessage)
            *errorMessage = QStringLiteral("Не удалось открыть файл словаря: %1").arg(path);
        return false;
    }

    const auto content = file.readAll();
    file.close();

    const auto doc = QJsonDocument::fromJson(content);
    if (doc.isNull() || !doc.isObject())
    {
        if (errorMessage)
            *errorMessage = QStringLiteral("Некорректный JSON словаря: %1").arg(path);
        return false;
    }

    const auto root = doc.object();

    // Tokens
    const auto tokens = root.value(QString::fromUtf8(kTokensKey)).toObject();
    for (auto it = tokens.begin(); it != tokens.end(); ++it)
    {
        tokenMap_[toLowerKey(it.key())] = it.value().toString();
    }

    // Class overrides
    const auto classOverrides = root.value(QString::fromUtf8(kClassOverridesKey)).toObject();
    for (auto it = classOverrides.begin(); it != classOverrides.end(); ++it)
    {
        classOverrides_[it.key()] = parseTextOverride(it.value().toObject());
    }

    // Property overrides per class
    const auto propertyOverrides = root.value(QString::fromUtf8(kPropertyOverridesKey)).toObject();
    for (auto classIt = propertyOverrides.begin(); classIt != propertyOverrides.end(); ++classIt)
    {
        QHash<QString, TextOverride> overrides;
        const auto propsObject = classIt.value().toObject();
        for (auto propIt = propsObject.begin(); propIt != propsObject.end(); ++propIt)
        {
            overrides.insert(propIt.key(), parseTextOverride(propIt.value().toObject()));
        }
        propertyOverrides_.insert(classIt.key(), overrides);
    }

    // Property fallbacks
    const auto globalProps = root.value(QString::fromUtf8(kPropertyFallbacksKey)).toObject();
    for (auto it = globalProps.begin(); it != globalProps.end(); ++it)
    {
        propertyFallbacks_.insert(it.key(), parseTextOverride(it.value().toObject()));
    }

    if (tokenMap_.isEmpty())
    {
        if (errorMessage)
            *errorMessage = QStringLiteral("Файл словаря %1 не содержит секции tokens.").arg(path);
        return false;
    }

    return true;
}

void ClDescGenerator::applyClassText(const std::string& className,
                                     const std::string& libraryName,
                                     RDK::UEPtr<RDK::UContainerDescription>& description,
                                     bool forceOverride)
{
    const QString classKey = QString::fromStdString(className);
    QString currentHeader = QString::fromStdString(description->GetHeader());
    QString currentDescription = QString::fromStdString(description->GetDescription());

    const auto overrideText = resolveClassOverride(classKey);

    QString header = currentHeader;
    if (forceOverride || header.trimmed().isEmpty())
    {
        header = !overrideText.header.isEmpty() ? overrideText.header : classKey;
        if (header.isEmpty())
            header = QStringLiteral("Компонент");
        description->SetHeader(header.toStdString());
    }

    QString desc = currentDescription;
    if (forceOverride || desc.trimmed().isEmpty())
    {
        QString source = overrideText.description;
        if (source.isEmpty())
            source = buildDefaultClassDescription(header, className, libraryName);
        description->SetDescription(source.toStdString());
    }

    // Обновляем локальные значения для дальнейших вычислений
    description->SetHeader(description->GetHeader());
    description->SetDescription(description->GetDescription());
}

void ClDescGenerator::applyPropertiesText(const std::string& className,
                                          const QString& classHeader,
                                          RDK::UEPtr<RDK::UContainerDescription>& description,
                                          bool forceOverride)
{
    const auto& props = description->GetProperties();
    for (const auto& entry : props)
    {
        const std::string& propertyName = entry.first;
        auto propDesc = entry.second;

        const QString propertyKey = QString::fromStdString(propertyName);
        const auto overrideText = resolvePropertyOverride(QString::fromStdString(className), propertyKey);

        QString header = QString::fromStdString(propDesc.Header);
        if (forceOverride || header.trimmed().isEmpty())
        {
            if (!overrideText.header.isEmpty())
            {
                header = overrideText.header;
            }
            else
            {
                header = tokensToPhrase(splitIdentifier(propertyKey), true);
                if (header.isEmpty())
                    header = QStringLiteral("Свойство %1").arg(propertyKey);
            }
            propDesc.Header = header.toStdString();
        }

        QString desc = QString::fromStdString(propDesc.Description);
        // Старые автогенераторы могли оставить заглушки вида
        // «%1 — параметр компонента %2.» или «%1 — свойство %2.».
        // Если видим такую фразу, считаем описание пустым и перезаписываем его.
        const bool isStubDescription =
            desc.contains(QStringLiteral("— параметр компонента"))
            || desc.contains(QStringLiteral("— свойство "));
        if (forceOverride || desc.trimmed().isEmpty() || isStubDescription)
        {
            QString generated = overrideText.description;
            if (generated.isEmpty())
                generated = buildDefaultPropertyDescription(header, propertyName, classHeader, className);
            propDesc.Description = generated.toStdString();
        }

        description->SetPropertyDescription(propertyName, propDesc, true);
    }
}

QStringList ClDescGenerator::splitIdentifier(const QString& name) const
{
    QString normalized = name;
    normalized.replace(QRegularExpression("([a-z0-9])([A-Z])"), "\\1 \\2");
    normalized.replace(QRegularExpression("([A-Z]+)([A-Z][a-z])"), "\\1 \\2");
    normalized.replace(QRegularExpression("[_\\-]+"), " ");
    const auto rawTokens = normalized.split(QRegularExpression("\\s+"), Qt::SkipEmptyParts);

    QStringList result;
    result.reserve(rawTokens.size());
    for (const QString& token : rawTokens)
    {
        if (!token.isEmpty())
            result.push_back(token);
    }
    return result;
}

QString ClDescGenerator::tokensToPhrase(const QStringList& tokens,
                                        bool capitalizeFirst) const
{
    if (tokens.isEmpty())
        return {};

    QStringList translated;
    translated.reserve(tokens.size());
    for (const QString& token : tokens)
    {
        const QString key = toLowerKey(token);
        translated.push_back(tokenMap_.value(key, token.toLower()));
    }

    QString phrase = translated.join(' ');
    if (capitalizeFirst)
        phrase = capitalize(phrase);
    return phrase;
}

QString ClDescGenerator::buildDefaultClassDescription(const QString& classHeader,
                                                      const std::string& className,
                                                      const std::string& libraryName) const
{
    const QString lib = QString::fromStdString(libraryName.empty() ? "общей библиотеки" : libraryName);
    const QString nativeName = QString::fromStdString(className);
    return QStringLiteral("Компонент %1 относится к библиотеке %2. Описание сформировано автоматически.")
        .arg(nativeName.isEmpty() ? classHeader : nativeName, lib);
}

QString ClDescGenerator::buildDefaultPropertyDescription(const QString& header,
                                                         const std::string& propertyName,
                                                         const QString& classHeader,
                                                         const std::string& className) const
{
    Q_UNUSED(propertyName);

    QString owner = classHeader.trimmed();
    if (owner.isEmpty())
        owner = QString::fromStdString(className);
    if (owner.isEmpty())
        owner = QStringLiteral("компонента");

    return QStringLiteral("%1 — свойство %2.")
        .arg(header, owner);
}

ClDescGenerator::TextOverride ClDescGenerator::resolveClassOverride(const QString& className) const
{
    return classOverrides_.value(className);
}

ClDescGenerator::TextOverride ClDescGenerator::resolvePropertyOverride(const QString& className,
                                                                       const QString& propertyName) const
{
    const auto perClass = propertyOverrides_.value(className);
    if (perClass.contains(propertyName))
        return perClass.value(propertyName);

    if (propertyFallbacks_.contains(propertyName))
        return propertyFallbacks_.value(propertyName);

    return {};
}

} // namespace NeuroModeler

