#include <gtest/gtest.h>
#include "../../../Tests/TestHelpers.h"
#include "ConfigurationVerification.h"
#include "../../../Rdk/Core/Application/UApplication.h"
#include "../../../Rdk/Deploy/Include/rdk.h"
#include "../../../Libraries/Libraries.h"
#include <QCoreApplication>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <memory>

#ifndef CMAKE_SOURCE_DIR
#define CMAKE_SOURCE_DIR "."
#endif

using namespace RDK;
using namespace RDK::TestHelpers;
namespace fs = std::filesystem;

class ConfigurationVerificationTest : public ::testing::Test {
protected:
    void SetUp() override {
        InitTestLogging();
        configPath = std::string(CMAKE_SOURCE_DIR) + "/Bin/Configs/Samples/LIF-Neuron";
        modelXmlPath = configPath + "/Model_00.xml";
        projectIniPath = configPath + "/project.ini";
    }

    std::string configPath;
    std::string modelXmlPath;
    std::string projectIniPath;
};

// Тест парсинга исходного Model_00.xml
TEST_F(ConfigurationVerificationTest, ParseOriginalModelXML) {
    if (!fs::exists(modelXmlPath)) {
        GTEST_SKIP() << "Model XML file not found: " << modelXmlPath;
        return;
    }
    
    ReferenceConfiguration refConfig = ParseModelXML(modelXmlPath);
    
    EXPECT_GT(refConfig.componentCount, 0) << "Should parse at least some components";
    EXPECT_GT(refConfig.linkCount, 0) << "Should parse at least some links";
    EXPECT_FALSE(refConfig.modelName.empty()) << "Should have model name";
    
    LOG(INFO) << "Parsed " << refConfig.componentCount << " components and " 
              << refConfig.linkCount << " links from " << modelXmlPath;
}

// Тест загрузки и проверки модели
TEST_F(ConfigurationVerificationTest, VerifyModelStructure) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found: " << projectIniPath;
        return;
    }
    
    // Парсим эталонную конфигурацию
    ReferenceConfiguration refConfig = ParseModelXML(modelXmlPath);
    if (refConfig.componentCount == 0) {
        GTEST_SKIP() << "Failed to parse reference configuration";
        return;
    }
    
    // Инициализируем Qt приложение для тестов
    static int argc = 1;
    static char* argv[] = {(char*)"test"};
    if (!QCoreApplication::instance()) {
        new QCoreApplication(argc, argv);
    }
    
    // Создаем приложение
    auto app = std::make_shared<UApplication>();
    if (!app) {
        GTEST_SKIP() << "Failed to create application";
        return;
    }
    
    bool initResult = app->Init();
    EXPECT_TRUE(initResult) << "Application initialization should succeed";
    
    if (!initResult) {
        return;
    }
    
    // Загружаем проект
    bool openResult = app->OpenProject(projectIniPath);
    EXPECT_TRUE(openResult) << "Project should open successfully";
    
    if (!openResult) {
        app->UnInit();
        return;
    }
    
    // Проверяем структуру модели
    VerificationResult result = VerifyModelStructure(app, refConfig);
    
    EXPECT_TRUE(result.success) << "Model structure verification failed: " << result.ToString();
    
    if (!result.success) {
        LOG(ERROR) << "Verification errors:\n" << result.ToString();
    }
    
    app->UnInit();
}

// Тест проверки компонентов
TEST_F(ConfigurationVerificationTest, VerifyComponents) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found: " << projectIniPath;
        return;
    }
    
    // Парсим эталонную конфигурацию
    ReferenceConfiguration refConfig = ParseModelXML(modelXmlPath);
    if (refConfig.componentCount == 0) {
        GTEST_SKIP() << "Failed to parse reference configuration";
        return;
    }
    
    // Инициализируем Qt приложение для тестов
    static int argc = 1;
    static char* argv[] = {(char*)"test"};
    if (!QCoreApplication::instance()) {
        new QCoreApplication(argc, argv);
    }
    
    // Создаем приложение
    auto app = std::make_shared<UApplication>();
    if (!app) {
        GTEST_SKIP() << "Failed to create application";
        return;
    }
    
    bool initResult = app->Init();
    EXPECT_TRUE(initResult) << "Application initialization should succeed";
    
    if (!initResult) {
        return;
    }
    
    // Загружаем проект
    bool openResult = app->OpenProject(projectIniPath);
    EXPECT_TRUE(openResult) << "Project should open successfully";
    
    if (!openResult) {
        app->UnInit();
        return;
    }
    
    // Проверяем компоненты
    VerificationResult result = VerifyComponents(app, refConfig);
    
    EXPECT_TRUE(result.success) << "Components verification failed: " << result.ToString();
    
    if (!result.success) {
        LOG(ERROR) << "Verification errors:\n" << result.ToString();
        LOG(ERROR) << "Missing components: " << result.missingComponents.size();
        LOG(ERROR) << "Extra components: " << result.extraComponents.size();
        LOG(ERROR) << "Class mismatches: " << result.componentClassMismatches.size();
    }
    
    app->UnInit();
}

// Тест проверки связей
TEST_F(ConfigurationVerificationTest, VerifyLinks) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found: " << projectIniPath;
        return;
    }
    
    // Парсим эталонную конфигурацию
    ReferenceConfiguration refConfig = ParseModelXML(modelXmlPath);
    if (refConfig.linkCount == 0) {
        GTEST_SKIP() << "Failed to parse reference configuration or no links found";
        return;
    }
    
    // Инициализируем Qt приложение для тестов
    static int argc = 1;
    static char* argv[] = {(char*)"test"};
    if (!QCoreApplication::instance()) {
        new QCoreApplication(argc, argv);
    }
    
    // Создаем приложение
    auto app = std::make_shared<UApplication>();
    if (!app) {
        GTEST_SKIP() << "Failed to create application";
        return;
    }
    
    bool initResult = app->Init();
    EXPECT_TRUE(initResult) << "Application initialization should succeed";
    
    if (!initResult) {
        return;
    }
    
    // Загружаем проект
    bool openResult = app->OpenProject(projectIniPath);
    EXPECT_TRUE(openResult) << "Project should open successfully";
    
    if (!openResult) {
        app->UnInit();
        return;
    }
    
    // Проверяем связи
    VerificationResult result = VerifyLinks(app, refConfig);
    
    EXPECT_TRUE(result.success) << "Links verification failed: " << result.ToString();
    
    if (!result.success) {
        LOG(ERROR) << "Verification errors:\n" << result.ToString();
        LOG(ERROR) << "Missing links: " << result.missingLinks.size();
        LOG(ERROR) << "Extra links: " << result.extraLinks.size();
    }
    
    app->UnInit();
}

// Тест полной проверки конфигурации
TEST_F(ConfigurationVerificationTest, FullVerification) {
    if (!fs::exists(projectIniPath)) {
        GTEST_SKIP() << "project.ini not found: " << projectIniPath;
        return;
    }
    
    // Парсим эталонную конфигурацию
    ReferenceConfiguration refConfig = ParseModelXML(modelXmlPath);
    if (refConfig.componentCount == 0 || refConfig.linkCount == 0) {
        GTEST_SKIP() << "Failed to parse reference configuration";
        return;
    }
    
    // Инициализируем Qt приложение для тестов
    static int argc = 1;
    static char* argv[] = {(char*)"test"};
    if (!QCoreApplication::instance()) {
        new QCoreApplication(argc, argv);
    }
    
    // Создаем приложение
    auto app = std::make_shared<UApplication>();
    if (!app) {
        GTEST_SKIP() << "Failed to create application";
        return;
    }
    
    bool initResult = app->Init();
    EXPECT_TRUE(initResult) << "Application initialization should succeed";
    
    if (!initResult) {
        return;
    }
    
    // Загружаем проект
    bool openResult = app->OpenProject(projectIniPath);
    EXPECT_TRUE(openResult) << "Project should open successfully";
    
    if (!openResult) {
        app->UnInit();
        return;
    }
    
    // Проверяем структуру модели
    VerificationResult modelResult = VerifyModelStructure(app, refConfig);
    EXPECT_TRUE(modelResult.success) << "Model structure verification failed";
    
    // Проверяем компоненты
    VerificationResult componentsResult = VerifyComponents(app, refConfig);
    EXPECT_TRUE(componentsResult.success) << "Components verification failed";
    
    // Проверяем связи
    VerificationResult linksResult = VerifyLinks(app, refConfig);
    EXPECT_TRUE(linksResult.success) << "Links verification failed";
    
    // Генерируем отчет
    std::string report = GenerateVerificationReport(componentsResult, refConfig);
    LOG(INFO) << "Verification Report:\n" << report;
    
    // Общий результат
    bool overallSuccess = modelResult.success && componentsResult.success && linksResult.success;
    EXPECT_TRUE(overallSuccess) << "Full verification failed";
    
    if (!overallSuccess) {
        LOG(ERROR) << "Model verification: " << (modelResult.success ? "PASS" : "FAIL");
        LOG(ERROR) << "Components verification: " << (componentsResult.success ? "PASS" : "FAIL");
        LOG(ERROR) << "Links verification: " << (linksResult.success ? "PASS" : "FAIL");
    }
    
    app->UnInit();
}

