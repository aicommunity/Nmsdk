#ifndef CONFIGURATION_VERIFICATION_H
#define CONFIGURATION_VERIFICATION_H

#include <string>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <fstream>
#include <sstream>
#include "../../../Rdk/Core/Serialize/USerStorageXML.h"
#include "../../../Rdk/Core/Engine/UContainer.h"
#include "../../../Rdk/Core/Engine/UNet.h"
#include "../../../Rdk/Core/Engine/UEnvSupport.h"
#include "../../../Rdk/Core/Application/UApplication.h"
#include <glog/logging.h>

namespace RDK {
namespace TestHelpers {

// Структура для хранения информации о компоненте
struct ComponentInfo {
    std::string name;
    std::string className;
    std::string parentName;  // Путь к родителю (например, "Model.IaFNeuron")
    std::string fullPath;     // Полный путь (например, "Model.IaFNeuron.Soma1.ExcSynapse1")
    
    bool operator<(const ComponentInfo& other) const {
        return fullPath < other.fullPath;
    }
    
    bool operator==(const ComponentInfo& other) const {
        return fullPath == other.fullPath && className == other.className;
    }
};

// Структура для хранения информации о связи
struct LinkInfo {
    std::string outputComponent;      // Компонент-источник (например, "PGenerator")
    std::string outputName;          // Имя выхода (например, "Output")
    std::vector<std::pair<std::string, std::string>> inputs;  // Пары (компонент, имя входа)
    
    std::string ToString() const {
        std::ostringstream oss;
        oss << outputComponent << "." << outputName << " -> ";
        for (size_t i = 0; i < inputs.size(); ++i) {
            if (i > 0) oss << ", ";
            oss << inputs[i].first << "." << inputs[i].second;
        }
        return oss.str();
    }
    
    bool operator<(const LinkInfo& other) const {
        return ToString() < other.ToString();
    }
    
    bool operator==(const LinkInfo& other) const {
        return outputComponent == other.outputComponent &&
               outputName == other.outputName &&
               inputs == other.inputs;
    }
};

// Структура для хранения эталонной конфигурации
struct ReferenceConfiguration {
    std::string modelName;
    std::set<ComponentInfo> components;
    std::set<LinkInfo> links;
    size_t componentCount;
    size_t linkCount;
    
    ReferenceConfiguration() : componentCount(0), linkCount(0) {}
};

// Структура для хранения результатов проверки
struct VerificationResult {
    bool success;
    std::vector<std::string> missingComponents;
    std::vector<std::string> extraComponents;
    std::vector<std::string> missingLinks;
    std::vector<std::string> extraLinks;
    std::vector<std::string> componentClassMismatches;
    std::vector<std::string> errors;
    
    VerificationResult() : success(true) {}
    
    void AddError(const std::string& error) {
        errors.push_back(error);
        success = false;
    }
    
    std::string ToString() const {
        std::ostringstream oss;
        oss << "Verification Result:\n";
        oss << "  Success: " << (success ? "Yes" : "No") << "\n";
        if (!missingComponents.empty()) {
            oss << "  Missing Components (" << missingComponents.size() << "):\n";
            for (const auto& comp : missingComponents) {
                oss << "    - " << comp << "\n";
            }
        }
        if (!extraComponents.empty()) {
            oss << "  Extra Components (" << extraComponents.size() << "):\n";
            for (const auto& comp : extraComponents) {
                oss << "    - " << comp << "\n";
            }
        }
        if (!missingLinks.empty()) {
            oss << "  Missing Links (" << missingLinks.size() << "):\n";
            for (const auto& link : missingLinks) {
                oss << "    - " << link << "\n";
            }
        }
        if (!extraLinks.empty()) {
            oss << "  Extra Links (" << extraLinks.size() << "):\n";
            for (const auto& link : extraLinks) {
                oss << "    - " << link << "\n";
            }
        }
        if (!componentClassMismatches.empty()) {
            oss << "  Component Class Mismatches (" << componentClassMismatches.size() << "):\n";
            for (const auto& mismatch : componentClassMismatches) {
                oss << "    - " << mismatch << "\n";
            }
        }
        if (!errors.empty()) {
            oss << "  Errors (" << errors.size() << "):\n";
            for (const auto& error : errors) {
                oss << "    - " << error << "\n";
            }
        }
        return oss.str();
    }
};

// Функция парсинга XML файла для извлечения компонентов
ReferenceConfiguration ParseModelXML(const std::string& xmlFilePath);

// Функция парсинга компонента рекурсивно
void ParseComponentRecursive(USerStorageXML& xmlStorage, const std::string& parentPath, ReferenceConfiguration& refConfig);

// Функция парсинга связей
void ParseLinks(USerStorageXML& xmlStorage, ReferenceConfiguration& refConfig);

// Функция проверки модели после загрузки
VerificationResult VerifyModelStructure(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference);

// Функция проверки компонентов
VerificationResult VerifyComponents(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference);

// Функция проверки связей
VerificationResult VerifyLinks(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference);

// Функция сравнения двух конфигураций
VerificationResult CompareConfigurations(const ReferenceConfiguration& original, const ReferenceConfiguration& saved);

// Функция генерации отчета
std::string GenerateVerificationReport(const VerificationResult& result, const ReferenceConfiguration& reference);

} // namespace TestHelpers
} // namespace RDK

#endif // CONFIGURATION_VERIFICATION_H

