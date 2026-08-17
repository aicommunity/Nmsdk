#ifndef ARDUINOLIVETESTSUPPORT_H
#define ARDUINOLIVETESTSUPPORT_H

#include <QCoreApplication>
#include <QDir>
#include <QElapsedTimer>
#include <QEventLoop>
#include <QFile>
#include <QFileInfo>
#include <QThread>
#include <cstring>

#include <QtSerialPort/QSerialPort>

#include "../../../Libraries/Rdk-HardwareLib/Core/Board/UFirmwareManifest.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoBoardProfile.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoFlasher.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialPortUtil.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialSession.h"

namespace ArduinoLiveTest {

inline void EnsureQtApp(const char* argv0)
{
    static int argc = 1;
    static char arg0_storage[64];
    static char* argv[] = {arg0_storage, nullptr};
    if (!QCoreApplication::instance()) {
        std::strncpy(arg0_storage, argv0, sizeof(arg0_storage) - 1);
        arg0_storage[sizeof(arg0_storage) - 1] = '\0';
        new QCoreApplication(argc, argv);
    }
}

inline QString resolveSdkRoot()
{
    QString root = QString::fromLocal8Bit(qgetenv("NMSDK_ROOT"));
    if (root.isEmpty())
        root = QString::fromLocal8Bit(qgetenv("NMSDK_SOURCE_DIR"));
    if (root.isEmpty()) {
        const QFileInfo testFile(QString::fromUtf8(__FILE__));
        root = QDir(testFile.absolutePath()).filePath(QStringLiteral("../../.."));
    }
    return QDir(root).absolutePath();
}

inline void EnsureSdkEnv()
{
    const QString root = resolveSdkRoot();
    if (qgetenv("NMSDK_SOURCE_DIR").isEmpty())
        qputenv("NMSDK_SOURCE_DIR", root.toLocal8Bit());
    if (qgetenv("NMSDK_ROOT").isEmpty())
        qputenv("NMSDK_ROOT", root.toLocal8Bit());
    if (qgetenv("ARDUINO_SYNC_UPLOAD").isEmpty())
        qputenv("ARDUINO_SYNC_UPLOAD", "1");

    const QString firmwareDir =
        QDir(root).filePath(QStringLiteral("Bin/ArduinoFirmware"));
    if (QFile::exists(firmwareDir + QStringLiteral("/manifest.json"))
        && qgetenv("RDK_HARDWARE_FIRMWARE_DIR").isEmpty()) {
        qputenv("RDK_HARDWARE_FIRMWARE_DIR", firmwareDir.toLocal8Bit());
    }

    const QString avrdudeWin =
        QDir(root).filePath(QStringLiteral("Bin/Platform/Win/ArduinoTools/bin/avrdude.exe"));
    if (QFileInfo::exists(avrdudeWin) && qgetenv("AVRDUDE").isEmpty())
        qputenv("AVRDUDE", avrdudeWin.toLocal8Bit());
}

inline bool envFlagEnabled(const char* name)
{
    const QByteArray v = qgetenv(name);
    if (v.isEmpty())
        return false;
    return v == "1" || v.toLower() == "true" || v.toLower() == "yes";
}

inline int boardProfileFromEnv()
{
    bool ok = false;
    const int profile = QString::fromLocal8Bit(qgetenv("ARDUINO_BOARD_PROFILE")).toInt(&ok);
    return ok ? profile : 0;
}

inline bool serialPortAccessible(const QString& port)
{
    if (port.isEmpty())
        return false;
    QSerialPort serial;
    serial.setPortName(RDK::UArduinoSerialPortUtil::preferredOpenName(port));
    if (!serial.open(QIODevice::ReadWrite))
        return false;
    serial.close();
    return true;
}

inline QString detectArduinoPort()
{
    const QByteArray forced = qgetenv("ARDUINO_TEST_PORT");
    if (!forced.isEmpty()) {
        return RDK::UArduinoSerialPortUtil::normalizeDevicePath(
            QString::fromUtf8(forced));
    }

    const QList<RDK::UArduinoSerialPortEntry> ports =
        RDK::UArduinoSerialPortUtil::listPortsSorted();
    for (const RDK::UArduinoSerialPortEntry& entry : ports) {
        if (entry.LikelyAttachedDevice)
            return entry.DevicePath;
    }
    for (const RDK::UArduinoSerialPortEntry& entry : ports) {
        if (!entry.DevicePath.isEmpty())
            return entry.DevicePath;
    }
    return {};
}

inline void waitForPort(const QString& port, int timeout_ms = 20000)
{
    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < timeout_ms) {
        if (serialPortAccessible(port))
            return;
        QThread::msleep(200);
        QCoreApplication::processEvents(QEventLoop::AllEvents, 20);
    }
}

inline bool flashBundledFirmware(const QString& port, int board_profile, const QString& bundled_id,
                                 QString* error_out)
{
    const QString hex = RDK::UFirmwareManifest::resolveBundledHex(bundled_id, board_profile);
    if (hex.isEmpty() || !QFile::exists(hex)) {
        if (error_out)
            *error_out = QStringLiteral("HEX not found for %1 profile %2 (resolved='%3')")
                             .arg(bundled_id)
                             .arg(board_profile)
                             .arg(hex);
        return false;
    }
    if (RDK::UArduinoFlasher::locateAvrdudeBinary().isEmpty()) {
        if (error_out)
            *error_out = QStringLiteral("avrdude not found");
        return false;
    }

    waitForPort(port);
    RDK::UArduinoFlasher flasher;
    QString flash_error;
    const RDK::UArduinoBoardProfile profile =
        RDK::UArduinoBoardProfileUtil::profileForKind(board_profile);
    const bool ok = flasher.flash(profile, port, hex, &flash_error);
    if (!ok) {
        if (error_out)
            *error_out = flash_error;
        return false;
    }
    waitForPort(port, 20000);
    QThread::msleep(2500);
    return true;
}

} // namespace ArduinoLiveTest

#endif
