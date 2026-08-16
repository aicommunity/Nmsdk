#include <gtest/gtest.h>

#include "Assembly/UArduinoAssemblySceneBuilder.h"
#include "Catalog/UHardwareCatalog.h"
#include "Catalog/UHardwareSetup.h"

#include <QCoreApplication>
#include <QDir>

namespace {

QString catalogFixtureRoot()
{
    const QByteArray src = qgetenv("NMSDK_SOURCE_DIR");
    if (!src.isEmpty())
        return QDir(QString::fromLocal8Bit(src)).filePath(QStringLiteral("Libraries/Rdk-HardwareLib/Catalog"));
    return QDir(QCoreApplication::applicationDirPath())
        .absoluteFilePath(QStringLiteral("../../../../Libraries/Rdk-HardwareLib/Catalog"));
}

void loadCatalog()
{
    qputenv("RDK_HARDWARE_CATALOG_DIR", catalogFixtureRoot().toUtf8());
    RDK::UHardwareCatalog::instance().unload();
    ASSERT_TRUE(RDK::UHardwareCatalog::instance().load(nullptr));
}

} // namespace

TEST(AssemblySceneBuilder, EmptyBoardOnly)
{
    loadCatalog();
    RDK::UHwSetupDocument doc;
    doc.board = QStringLiteral("uno");
    doc.firmwareId = QStringLiteral("standard_firmata");
    const auto model =
        RDK::UArduinoAssemblySceneBuilder::build(RDK::UHardwareCatalog::instance(), doc, {});
    ASSERT_EQ(model.nodes.size(), 1);
    EXPECT_EQ(model.nodes.first().kind, RDK::UAssemblyNode::Board);
    EXPECT_TRUE(model.wires.isEmpty());
}

TEST(AssemblySceneBuilder, SensorShieldTwoDevices)
{
    loadCatalog();
    const QByteArray json = R"({
      "schemaVersion": 1,
      "board": "uno",
      "firmwareId": "standard_firmata",
      "stack": ["sensor_shield_v5"],
      "devices": [
        {"id": "pot", "module": "potentiometer", "port": "A0", "role": "sensor"},
        {"id": "srv", "module": "servo", "port": "D9", "role": "actuator"}
      ]
    })";
    RDK::UHardwareSetup setup;
    ASSERT_TRUE(setup.loadFromJson(json, nullptr));
    const auto model = RDK::UArduinoAssemblySceneBuilder::build(
        RDK::UHardwareCatalog::instance(), setup.document(), {});
    int shields = 0;
    int modules = 0;
    for (const auto& n : model.nodes) {
        if (n.kind == RDK::UAssemblyNode::Shield)
            ++shields;
        if (n.kind == RDK::UAssemblyNode::Module)
            ++modules;
    }
    EXPECT_EQ(shields, 1);
    EXPECT_EQ(modules, 2);
    EXPECT_EQ(model.wires.size(), 2);
    EXPECT_GE(model.wires.first().conductors.size(), 1);
}

TEST(AssemblySceneBuilder, PinConflictMarksWire)
{
    loadCatalog();
    const QByteArray json = R"({
      "schemaVersion": 1,
      "board": "uno",
      "firmwareId": "standard_firmata",
      "stack": ["sensor_shield_v5"],
      "devices": [
        {"id": "a", "module": "potentiometer", "port": "A0", "role": "sensor"},
        {"id": "b", "module": "potentiometer", "port": "A0", "role": "sensor"}
      ]
    })";
    RDK::UHardwareSetup setup;
    ASSERT_TRUE(setup.loadFromJson(json, nullptr));
    QVector<RDK::UHwIssue> issues;
    setup.validate(RDK::UHardwareCatalog::instance(), &issues);
    const auto model = RDK::UArduinoAssemblySceneBuilder::build(
        RDK::UHardwareCatalog::instance(), setup.document(), issues);
    bool anyConflict = false;
    for (const auto& w : model.wires)
        anyConflict = anyConflict || w.conflict;
    EXPECT_TRUE(anyConflict);
}
