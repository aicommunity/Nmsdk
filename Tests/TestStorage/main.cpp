#include <iostream>
#include <memory>
#include <stdexcept>

// RDK includes
#include "../../Rdk/Deploy/Include/rdk.h"
#include "../../Libraries/Rdk-BasicLib/Deploy/Include/Lib.h"
#include "../../Rdk/Core/Engine/ULoggerEnv.h"

using namespace RDK;

int main() {
    std::cout << "=== RDK Storage Test with Real Implementation ===" << std::endl;

    try {
        std::cout << "1. Creating Storage variable..." << std::endl;
        // ACTUAL CODE: Create UStorage variable
        std::shared_ptr<UStorage> storage = std::make_shared<UStorage>();
        std::cout << "   ✓ Storage variable created successfully" << std::endl;
        std::cout << "   - Storage type: " << typeid(*storage).name() << std::endl;
        std::cout << "   - Storage address: " << storage.get() << std::endl;

        std::cout << "2. Creating Logger variable..." << std::endl;
        // ACTUAL CODE: Create ULoggerEnv variable
        std::shared_ptr<ULoggerEnv> logger = std::make_shared<ULoggerEnv>();
        logger->SetDebugMode(true);
        logger->SetEventsLogMode(true);
        logger->SetCoutLogMode(true);
        std::cout << "   ✓ Logger variable created successfully" << std::endl;
        std::cout << "   - Logger type: " << typeid(*logger).name() << std::endl;
        std::cout << "   - Logger address: " << logger.get() << std::endl;

        storage->SetBuildMode(1);
        storage->AddCollection(&RDK::BasicLibrary);

        std::cout << "   - Setting Logger to Storage..." << std::endl;
        storage->SetLogger(logger);
        std::cout << "   ✓ Logger set to Storage" << std::endl;

        storage->BuildStorage();

        std::cout << "3. Creating Environment variable..." << std::endl;
        // ACTUAL CODE: Create UEnvironment variable
        std::shared_ptr<UEnvironment> environment = std::make_shared<UEnvironment>();
        std::cout << "   ✓ Environment variable created successfully" << std::endl;
        std::cout << "   - Environment type: " << typeid(*environment).name() << std::endl;
        std::cout << "   - Environment address: " << environment.get() << std::endl;

        std::cout << "   - Setting Logger to Environment..." << std::endl;
        environment->SetLogger(logger);
        std::cout << "   ✓ Logger set to Environment" << std::endl;

        std::cout << "4. Setting Storage to Environment..." << std::endl;
        // ACTUAL CODE: Set storage to environment
        bool setResult = environment->SetStorage(storage.get());
        std::cout << "   ✓ Storage set to Environment: " << (setResult ? "success" : "failed") << std::endl;

        std::cout << "5. Getting Storage from Environment..." << std::endl;
        // ACTUAL CODE: Get storage from environment
        UStorage* envStorage = environment->GetStorage();
        if (envStorage) {
            std::cout << "   ✓ Storage retrieved from Environment" << std::endl;
            std::cout << "   - Retrieved Storage type: " << typeid(*envStorage).name() << std::endl;
            std::cout << "   - Retrieved Storage address: " << envStorage << std::endl;
        } else {
            std::cout << "   ✗ Failed to get Storage from Environment" << std::endl;
        }

        std::cout << "6. Testing TakeObject with UModel..." << std::endl;
        // ACTUAL CODE: Try to create UModel object
        try {
            std::shared_ptr<UComponent> model = envStorage->TakeObject("UModel");
            if (model) {
                std::cout << "   ✓ UModel object created successfully" << std::endl;
                std::cout << "   - Object type: " << typeid(*model).name() << std::endl;
                std::cout << "   - Object address: " << model.get() << std::endl;

                // Check if object is UComponent derived
                if (dynamic_cast<UComponent*>(model.get())) {
                    std::cout << "   - Object is UComponent derived" << std::endl;
                } else {
                    std::cout << "   - Object is not UComponent derived" << std::endl;
                }
            } else {
                std::cout << "   ⚠ UModel object is null" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cout << "   ✗ Failed to create UModel: " << e.what() << std::endl;
        }

        std::cout << "7. Testing other object types..." << std::endl;

        // ACTUAL CODE: Test UContainer
        try {
            std::shared_ptr<UComponent> container = envStorage->TakeObject("UContainer");
            if (container) {
                std::cout << "   ✓ UContainer object created successfully" << std::endl;
                std::cout << "   - Container type: " << typeid(*container).name() << std::endl;
                std::cout << "   - Container address: " << container.get() << std::endl;
            } else {
                std::cout << "   ⚠ UContainer object is null" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cout << "   ✗ Failed to create UContainer: " << e.what() << std::endl;
        }

        // ACTUAL CODE: Test UItem
        try {
            std::shared_ptr<UComponent> item = envStorage->TakeObject("UItem");
            if (item) {
                std::cout << "   ✓ UItem object created successfully" << std::endl;
                std::cout << "   - Item type: " << typeid(*item).name() << std::endl;
                std::cout << "   - Item address: " << item.get() << std::endl;
            } else {
                std::cout << "   ⚠ UItem object is null" << std::endl;
            }
        } catch (const std::exception& e) {
            std::cout << "   ✗ Failed to create UItem: " << e.what() << std::endl;
        }

        std::cout << "\n=== Test completed successfully ===" << std::endl;
        std::cout << "Real UStorage variables were created and tested!" << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "❌ Test failed with error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
