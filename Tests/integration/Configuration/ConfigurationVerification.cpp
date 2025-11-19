#include "ConfigurationVerification.h"
#include "../../../Rdk/Core/Engine/UEngine.h"
#include "../../../Rdk/Core/Engine/UEnvironment.h"
#include "../../../Rdk/Core/Engine/UItem.h"
#include "../../../Rdk/Core/Engine/UEnvSupport.h"
#include "../../../Rdk/Core/Engine/UContainer.h"
#include <filesystem>
#include <algorithm>
#include <functional>
#include <map>

namespace RDK {
namespace TestHelpers {

ReferenceConfiguration ParseModelXML(const std::string& xmlFilePath) {
    ReferenceConfiguration refConfig;
    
    if (!std::filesystem::exists(xmlFilePath)) {
        LOG(ERROR) << "XML file not found: " << xmlFilePath;
        return refConfig;
    }
    
    // Читаем файл
    std::ifstream file(xmlFilePath);
    if (!file.is_open()) {
        LOG(ERROR) << "Failed to open XML file: " << xmlFilePath;
        return refConfig;
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string xmlContent = buffer.str();
    file.close();
    
    // Парсим XML
    USerStorageXML xmlStorage;
    if (!xmlStorage.Load(xmlContent.c_str(), "Save")) {
        LOG(ERROR) << "Failed to parse XML file: " << xmlFilePath;
        return refConfig;
    }
    
    // Получаем имя модели
    refConfig.modelName = xmlStorage.GetNodeAttribute("ModelName");
    if (refConfig.modelName.empty()) {
        refConfig.modelName = "Model";  // Значение по умолчанию
    }
    
    // Находим узел Model
    if (!xmlStorage.SelectNode("Model")) {
        LOG(ERROR) << "Model node not found in XML";
        return refConfig;
    }
    
    // Парсим компоненты и связи
    int numNodes = xmlStorage.GetNumNodes();
    for (int i = 0; i < numNodes; ++i) {
        if (xmlStorage.SelectNode(i)) {
            std::string nodeName = xmlStorage.GetNodeName();
            if (nodeName == "Components") {
                // Парсим компоненты рекурсивно
                int numComponents = xmlStorage.GetNumNodes();
                for (int j = 0; j < numComponents; ++j) {
                    if (xmlStorage.SelectNode(j)) {
                        ParseComponentRecursive(xmlStorage, refConfig.modelName, refConfig);
                        xmlStorage.SelectUp();
                    }
                }
            } else if (nodeName == "Links") {
                ParseLinks(xmlStorage, refConfig);
            }
            xmlStorage.SelectUp();
        }
    }
    
    refConfig.componentCount = refConfig.components.size();
    refConfig.linkCount = refConfig.links.size();
    
    LOG(INFO) << "Parsed reference configuration: " << refConfig.componentCount 
              << " components, " << refConfig.linkCount << " links";
    
    return refConfig;
}

void ParseComponentRecursive(USerStorageXML& xmlStorage, const std::string& parentPath, ReferenceConfiguration& refConfig) {
    // Получаем имя текущего узла (это имя компонента)
    std::string nodeName = xmlStorage.GetNodeName();
    
    // Пропускаем узлы Parameters и Links
    if (nodeName == "Parameters" || nodeName == "Links") {
        return;
    }
    
    // Это должен быть компонент
    ComponentInfo compInfo;
    compInfo.name = nodeName;
    compInfo.className = xmlStorage.GetNodeAttribute("Class");
    if (compInfo.className.empty()) {
        compInfo.className = nodeName;  // Если класс не указан, используем имя узла
    }
    
    // Формируем путь
    if (parentPath.empty()) {
        compInfo.fullPath = compInfo.name;
        compInfo.parentName = "";
    } else {
        compInfo.fullPath = parentPath + "." + compInfo.name;
        compInfo.parentName = parentPath;
    }
    
    // Добавляем компонент
    refConfig.components.insert(compInfo);
    
    // Рекурсивно обрабатываем вложенные компоненты
    int numNodes = xmlStorage.GetNumNodes();
    for (int i = 0; i < numNodes; ++i) {
        if (xmlStorage.SelectNode(i)) {
            std::string subNodeName = xmlStorage.GetNodeName();
            if (subNodeName == "Components") {
                // Обрабатываем дочерние компоненты
                int numComponents = xmlStorage.GetNumNodes();
                for (int j = 0; j < numComponents; ++j) {
                    if (xmlStorage.SelectNode(j)) {
                        ParseComponentRecursive(xmlStorage, compInfo.fullPath, refConfig);
                        xmlStorage.SelectUp();
                    }
                }
            }
            xmlStorage.SelectUp();
        }
    }
}

void ParseLinks(USerStorageXML& xmlStorage, ReferenceConfiguration& refConfig) {
    // Парсим каждую связь
    int numLinks = xmlStorage.GetNumNodes();
    for (int i = 0; i < numLinks; ++i) {
        if (xmlStorage.SelectNode(i)) {
            std::string nodeName = xmlStorage.GetNodeName();
            if (nodeName != "elem") {
                xmlStorage.SelectUp();
                continue;
            }
            
            LinkInfo linkInfo;
            
            // Ищем узел Item (Output)
            int numChildNodes = xmlStorage.GetNumNodes();
            for (int j = 0; j < numChildNodes; ++j) {
                if (xmlStorage.SelectNode(j)) {
                    std::string itemName = xmlStorage.GetNodeName();
                    if (itemName == "Item") {
                        std::string nameAttr = xmlStorage.GetNodeAttribute("Name");
                        if (nameAttr == "Output") {
                            linkInfo.outputName = "Output";
                            // Получаем текст узла (имя компонента)
                            std::string outputText = xmlStorage.GetNodeText();
                            if (!outputText.empty()) {
                                linkInfo.outputComponent = outputText;
                            }
                        }
                        xmlStorage.SelectUp();
                        break;
                    }
                    xmlStorage.SelectUp();
                }
            }
            
            // Ищем узлы Connector (Inputs)
            for (int j = 0; j < numChildNodes; ++j) {
                if (xmlStorage.SelectNode(j)) {
                    std::string connectorName = xmlStorage.GetNodeName();
                    if (connectorName == "Connector") {
                        std::string nameAttr = xmlStorage.GetNodeAttribute("Name");
                        std::string inputText = xmlStorage.GetNodeText();
                        if (!nameAttr.empty() && !inputText.empty()) {
                            linkInfo.inputs.push_back(std::make_pair(inputText, nameAttr));
                        }
                    }
                    xmlStorage.SelectUp();
                }
            }
            
            if (!linkInfo.outputComponent.empty() && !linkInfo.inputs.empty()) {
                refConfig.links.insert(linkInfo);
            }
            
            xmlStorage.SelectUp();
        }
    }
}

VerificationResult VerifyModelStructure(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference) {
    VerificationResult result;
    
    if (!app) {
        result.AddError("Application pointer is null");
        return result;
    }
    
    // Проверяем, что проект открыт
    if (!app->GetProjectOpenFlag()) {
        result.AddError("Project is not open");
        return result;
    }
    
    // Получаем Environment через GetEnvironment() для первого канала
    auto environment = app->GetEnvironment(0);
    
    auto model = environment->GetModel();
    if (!model) {
        result.AddError("Model is null");
        return result;
    }
    
    // Проверяем имя модели
    std::string modelName = model->GetName();
    if (modelName != reference.modelName) {
        result.AddError("Model name mismatch: expected '" + reference.modelName + "', got '" + modelName + "'");
    }
    
    return result;
}

VerificationResult VerifyComponents(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference) {
    VerificationResult result;
    
    if (!app) {
        result.AddError("Application pointer is null");
        return result;
    }
    
    if (!app->GetProjectOpenFlag()) {
        result.AddError("Project is not open");
        return result;
    }
    
    // Получаем Environment через GetEnvironment() для первого канала
    auto environment = app->GetEnvironment(0);
    if (!environment) {
        result.AddError("Environment is null");
        return result;
    }
    
    // Получаем Storage из Environment
    UStorage* storage = environment->GetStorage();
    if (!storage) {
        result.AddError("Storage is null");
        return result;
    }
    
    // Получаем модель
    auto model = environment->GetModel();
    if (!model) {
        result.AddError("Model is null");
        return result;
    }
    
    // Получаем список компонентов из загруженной модели
    std::set<std::string> loadedComponents;
    std::map<std::string, std::string> componentClasses;  // fullPath -> className
    
    // Рекурсивно собираем все компоненты
    std::function<void(std::shared_ptr<UContainer>, const std::string&)> collectComponents = 
        [&](std::shared_ptr<UContainer> container, const std::string& parentPath) {
            if (!container) return;
            
            std::string compName = container->GetName();
            std::string fullPath = parentPath.empty() ? compName : parentPath + "." + compName;
            
            // Получаем класс компонента через Storage::FindClassName
            UId classId = container->GetClass();
            NameT className = storage->FindClassName(classId);
            if (className.empty()) {
                className = "Unknown";
            }
            
            loadedComponents.insert(fullPath);
            componentClasses[fullPath] = className;
            
            // Рекурсивно обрабатываем дочерние компоненты
            try {
                // Получаем дочерние компоненты через GetComponentsNameByClassType
                std::vector<NameT> componentNames;
                container->template GetComponentsNameByClassType<UContainer>(componentNames, std::shared_ptr<UContainer>(), false);
                
                for (const auto& childName : componentNames) {
                    try {
                        // Получаем ID компонента по имени, затем сам компонент
                        UId childId = container->GetComponentId(childName, true);
                        if (childId != ForbiddenId) {
                            ULongId childLongId;
                            childLongId.Add(childId);
                            std::weak_ptr<UContainer> child_weak = container->GetComponentL(childLongId, true);
                            if (!child_weak.expired()) {
                                std::shared_ptr<UContainer> child = child_weak.lock();
                                if (child) {
                                    collectComponents(child, fullPath);
                                }
                            }
                        }
                    } catch (...) {
                        // Игнорируем ошибки при получении компонента
                    }
                }
            } catch (...) {
                // Игнорируем ошибки при получении списка компонентов
            }
        };
    
    collectComponents(model, reference.modelName);
    
    // Сравниваем с эталоном
    for (const auto& refComp : reference.components) {
        if (loadedComponents.find(refComp.fullPath) == loadedComponents.end()) {
            result.missingComponents.push_back(refComp.fullPath + " (class: " + refComp.className + ")");
            result.success = false;
        } else {
            // Проверяем класс
            auto it = componentClasses.find(refComp.fullPath);
            if (it != componentClasses.end() && it->second != refComp.className) {
                result.componentClassMismatches.push_back(
                    refComp.fullPath + ": expected class '" + refComp.className + 
                    "', got '" + it->second + "'");
                result.success = false;
            }
        }
    }
    
    // Находим лишние компоненты
    for (const auto& loadedComp : loadedComponents) {
        bool found = false;
        for (const auto& refComp : reference.components) {
            if (refComp.fullPath == loadedComp) {
                found = true;
                break;
            }
        }
        if (!found) {
            result.extraComponents.push_back(loadedComp);
            result.success = false;
        }
    }
    
    return result;
}

VerificationResult VerifyLinks(std::shared_ptr<UApplication> app, const ReferenceConfiguration& reference) {
    VerificationResult result;
    
    if (!app) {
        result.AddError("Application pointer is null");
        return result;
    }
    
    if (!app->GetProjectOpenFlag()) {
        result.AddError("Project is not open");
        return result;
    }
    
    // Получаем Environment через GetEnvironment() для первого канала
    auto environment = app->GetEnvironment(0);
    
    // Получаем модель
    auto model = environment->GetModel();
    if (!model) {
        result.AddError("Model is null");
        return result;
    }
    
    // Получаем связи из модели
    std::set<LinkInfo> loadedLinks;
    
    try {
        auto net = std::dynamic_pointer_cast<UNet>(model);
        if (net) {
            // Получаем все связи через GetLinks
            ULinksList linksList;
            net->GetLinks(linksList, net, false);
            
            // Создаем карту ID -> имя компонента для быстрого поиска
            std::map<ULongId, std::string> idToName;
            std::function<void(std::shared_ptr<UContainer>, const std::string&)> collectNames = 
                [&](std::shared_ptr<UContainer> container, const std::string& parentPath) {
                    if (!container) return;
                    
                    std::string compName = container->GetName();
                    std::string fullPath = parentPath.empty() ? compName : parentPath + "." + compName;
                    // GetLongId требует mainowner, используем модель как mainowner
                    ULongId compId = container->GetLongId(model);
                    idToName[compId] = fullPath;
                    
                    // Рекурсивно обрабатываем дочерние компоненты
                    try {
                        std::vector<NameT> componentNames;
                        container->template GetComponentsNameByClassType<UContainer>(componentNames, std::shared_ptr<UContainer>(), false);
                        
                        for (const auto& childName : componentNames) {
                            try {
                                // Получаем ID компонента по имени, затем сам компонент
                                UId childId = container->GetComponentId(childName, true);
                                if (childId != ForbiddenId) {
                                    ULongId childLongId;
                                    childLongId.Add(childId);
                                    std::weak_ptr<UContainer> child_weak = container->GetComponentL(childLongId, true);
                                    if (!child_weak.expired()) {
                                        std::shared_ptr<UContainer> child = child_weak.lock();
                                        if (child) {
                                            collectNames(child, fullPath);
                                        }
                                    }
                                }
                            } catch (...) {
                                // Игнорируем ошибки
                            }
                        }
                    } catch (...) {
                        // Игнорируем ошибки
                    }
                };
            collectNames(model, reference.modelName);
            
            // Преобразуем в LinkInfo
            for (int i = 0; i < linksList.GetSize(); ++i) {
                const ULinkT<ULongId>& link = linksList[i];
                LinkInfo linkInfo;
                
                // Получаем имя выходного компонента
                auto it = idToName.find(link.Item.Id);
                if (it != idToName.end()) {
                    linkInfo.outputComponent = it->second;
                    linkInfo.outputName = link.Item.Name.empty() ? "Output" : link.Item.Name;
                } else {
                    // Если не нашли по ID, пропускаем эту связь
                    continue;
                }
                
                // Получаем входные компоненты
                for (const auto& connector : link.Connector) {
                    auto connIt = idToName.find(connector.Id);
                    if (connIt != idToName.end()) {
                        std::string inputName = connector.Name.empty() ? "Input" : connector.Name;
                        linkInfo.inputs.push_back(std::make_pair(connIt->second, inputName));
                    }
                }
                
                // Sort inputs for consistent comparison
                std::sort(linkInfo.inputs.begin(), linkInfo.inputs.end());
                
                if (!linkInfo.outputComponent.empty() && !linkInfo.inputs.empty()) {
                    loadedLinks.insert(linkInfo);
                }
            }
        }
    } catch (const std::exception& e) {
        result.AddError("Exception while getting links: " + std::string(e.what()));
        return result;
    }
    
    // Сравниваем с эталоном
    for (const auto& refLink : reference.links) {
        if (loadedLinks.find(refLink) == loadedLinks.end()) {
            result.missingLinks.push_back(refLink.ToString());
            result.success = false;
        }
    }
    
    // Находим лишние связи
    for (const auto& loadedLink : loadedLinks) {
        if (reference.links.find(loadedLink) == reference.links.end()) {
            result.extraLinks.push_back(loadedLink.ToString());
            result.success = false;
        }
    }
    
    return result;
}

VerificationResult CompareConfigurations(const ReferenceConfiguration& original, const ReferenceConfiguration& saved) {
    VerificationResult result;
    
    // Сравниваем компоненты
    for (const auto& origComp : original.components) {
        bool found = false;
        for (const auto& savedComp : saved.components) {
            if (origComp.fullPath == savedComp.fullPath) {
                found = true;
                if (origComp.className != savedComp.className) {
                    result.componentClassMismatches.push_back(
                        origComp.fullPath + ": original class '" + origComp.className + 
                        "', saved class '" + savedComp.className + "'");
                    result.success = false;
                }
                break;
            }
        }
        if (!found) {
            result.missingComponents.push_back(origComp.fullPath);
            result.success = false;
        }
    }
    
    // Находим лишние компоненты
    for (const auto& savedComp : saved.components) {
        bool found = false;
        for (const auto& origComp : original.components) {
            if (savedComp.fullPath == origComp.fullPath) {
                found = true;
                break;
            }
        }
        if (!found) {
            result.extraComponents.push_back(savedComp.fullPath);
            result.success = false;
        }
    }
    
    // Сравниваем связи
    for (const auto& origLink : original.links) {
        if (saved.links.find(origLink) == saved.links.end()) {
            result.missingLinks.push_back(origLink.ToString());
            result.success = false;
        }
    }
    
    for (const auto& savedLink : saved.links) {
        if (original.links.find(savedLink) == original.links.end()) {
            result.extraLinks.push_back(savedLink.ToString());
            result.success = false;
        }
    }
    
    return result;
}

std::string GenerateVerificationReport(const VerificationResult& result, const ReferenceConfiguration& reference) {
    std::ostringstream report;
    
    report << "=== Configuration Verification Report ===\n\n";
    report << "Reference Configuration:\n";
    report << "  Model Name: " << reference.modelName << "\n";
    report << "  Components: " << reference.componentCount << "\n";
    report << "  Links: " << reference.linkCount << "\n\n";
    
    report << result.ToString();
    
    return report.str();
}

} // namespace TestHelpers
} // namespace RDK

