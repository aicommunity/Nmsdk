#pragma once

#include <QString>
#include <QStringList>
#include <QHash>

#include "../../Rdk/Core/Engine/UELockPtr.h"
#include "../../Rdk/Core/Engine/UStorage.h"
#include "PropertyAliasAnalyzer.h"

namespace NeuroModeler {

struct ClDescGeneratorOptions
{
    QStringList lexiconCandidatePaths;
    bool verbose = false;
    QStringList libraryFilters;
    QStringList classFilters;
    bool forceOverride = false;
};

class ClDescGenerator
{
public:
    struct TextOverride
    {
        QString header;
        QString description;

        bool isEmpty() const { return header.isEmpty() && description.isEmpty(); }
    };

    bool Generate(RDK::UELockPtr<RDK::UStorage> storage,
                  const ClDescGeneratorOptions& options,
                  QString* errorMessage = nullptr);

    bool ensureLexiconLoaded(const QStringList& candidatePaths, QString* errorMessage);
    bool loadLexiconFromFile(const QString& path, QString* errorMessage);

    void applyClassText(const std::string& className,
                        const std::string& libraryName,
                        RDK::UEPtr<RDK::UContainerDescription>& description,
                        bool forceOverride);

    void applyPropertiesText(const std::string& className,
                             const QString& classHeader,
                             RDK::UEPtr<RDK::UContainerDescription>& description,
                             bool forceOverride);

    void generatePropertyAliases(const std::string& className,
                                  RDK::UEPtr<RDK::UContainerDescription>& description,
                                  RDK::UStorage* storage,
                                  const ClDescGeneratorOptions& options);

    QStringList splitIdentifier(const QString& name) const;
    QString tokensToPhrase(const QStringList& tokens,
                           bool capitalizeFirst) const;
    QString buildDefaultClassDescription(const QString& classHeader,
                                         const std::string& className,
                                         const std::string& libraryName) const;
    QString buildDefaultPropertyDescription(const QString& header,
                                            const std::string& propertyName,
                                            const QString& classHeader,
                                            const std::string& className) const;

    TextOverride resolveClassOverride(const QString& className) const;
    TextOverride resolvePropertyOverride(const QString& className,
                                         const QString& propertyName) const;

private:
    bool lexiconLoaded_ = false;
    QString lexiconPathUsed_;
    QHash<QString, QString> tokenMap_; // lower-case token -> translation
    QHash<QString, TextOverride> classOverrides_;
    QHash<QString, TextOverride> propertyFallbacks_;
    QHash<QString, QHash<QString, TextOverride>> propertyOverrides_;
    PropertyAliasAnalyzer aliasAnalyzer_;
};

} // namespace NeuroModeler

