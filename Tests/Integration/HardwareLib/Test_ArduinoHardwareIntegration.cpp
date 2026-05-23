#include <gtest/gtest.h>

#include <functional>

#include <QCoreApplication>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QThread>

#include <QtSerialPort/QSerialPort>

#include "../../../Libraries/Rdk-HardwareLib/Core/UArduinoFirmata.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoPinMap.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoFlasher.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/Transport/UArduinoSerialPortUtil.h"
#include "../../../Libraries/Rdk-HardwareLib/Core/UFirmwareManifest.h"

namespace {

void EnsureQtApp()
{
    static int argc = 1;
    static char arg0[] = "arduino_hw_integration";
    static char* argv[] = {arg0, nullptr};
    if (!QCoreApplication::instance())
        new QCoreApplication(argc, argv);
}

QString resolveSdkRoot()
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

void EnsureSdkEnv()
{
    const QString root = resolveSdkRoot();
    if (qgetenv("NMSDK_SOURCE_DIR").isEmpty())
        qputenv("NMSDK_SOURCE_DIR", root.toLocal8Bit());
    if (qgetenv("NMSDK_ROOT").isEmpty())
        qputenv("NMSDK_ROOT", root.toLocal8Bit());
}

bool envFlagEnabled(const char* name)
{
    const QByteArray v = qgetenv(name);
    if (v.isEmpty())
        return false;
    return v == "1" || v.toLower() == "true" || v.toLower() == "yes";
}

bool shouldSkipFirmwareUpload()
{
    return envFlagEnabled("ARDUINO_SKIP_UPLOAD");
}

bool shouldForceFirmwareUpload()
{
    return envFlagEnabled("ARDUINO_FORCE_UPLOAD");
}

bool canRunAvrdudeUpload()
{
    return !shouldSkipFirmwareUpload()
           && !RDK::UArduinoFlasher::locateAvrdudeBinary().isEmpty();
}

bool uploadFailureLooksLikeRunningSketch(const std::string& msg)
{
    const QString text = QString::fromStdString(msg);
    return text.contains(QStringLiteral("not in sync"), Qt::CaseInsensitive)
           || text.contains(QStringLiteral("programmer is not responding"), Qt::CaseInsensitive);
}

int boardProfileFromEnv()
{
    bool ok = false;
    const int profile = QString::fromLocal8Bit(qgetenv("ARDUINO_BOARD_PROFILE")).toInt(&ok);
    return ok ? profile : 0;
}

bool serialPortAccessible(const QString& port)
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

QString detectArduinoPort()
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

class FirmataHarness : public RDK::UArduinoFirmata {
public:
    void initDefaults() { ADefault(); }
    void prepareForPort() { PortChanged = false; }
    using RDK::UArduinoBoard::ProcessBoardEdges;
    using RDK::UArduinoBoard::EnsureConnected;
    using RDK::UArduinoBoard::SyncDerivedStates;
    using RDK::UArduinoFirmata::CloseConnection;
    using RDK::UArduinoFirmata::ACalculate;
};

void waitForPort(const QString& port, int timeout_ms = 15000)
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

void disconnectBoard(FirmataHarness& board)
{
    board.CloseConnection();
    board.SyncDerivedStates();
    QThread::msleep(300);
}

bool pumpCalculate(FirmataHarness& board, int timeout_ms, const std::function<bool()>& done)
{
    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < timeout_ms) {
        board.ACalculate();
        QCoreApplication::processEvents(QEventLoop::AllEvents, 20);
        QThread::msleep(5);
        if (done())
            return true;
    }
    return done();
}

bool tryConnectSerial(FirmataHarness& board, int timeout_ms = 10000)
{
    disconnectBoard(board);

    QElapsedTimer timer;
    timer.start();
    while (timer.elapsed() < timeout_ms) {
        if (board.EnsureConnected()) {
            board.SyncDerivedStates();
            return true;
        }
        QThread::msleep(300);
        QCoreApplication::processEvents(QEventLoop::AllEvents, 20);
    }
    board.SyncDerivedStates();
    return static_cast<bool>(board.IsConnected);
}

bool connectAndWaitHandshake(FirmataHarness& board, int timeout_ms = 20000)
{
    if (!tryConnectSerial(board, timeout_ms)) {
        const std::string err = *board.LastError;
        ADD_FAILURE() << "Serial connect failed: "
                      << (err.empty() ? "(no error text; check port busy or board profile)"
                                      : err);
        return false;
    }

    QThread::msleep(1500);

    const bool ready = pumpCalculate(board, timeout_ms, [&board]() {
        return static_cast<bool>(board.FirmataReady);
    });
    if (!ready) {
        ADD_FAILURE() << "Firmata handshake timeout: stage=" << static_cast<int>(board.HandshakeStage)
                      << " fw=" << *board.FirmataFirmwareVersion
                      << " linkReady=" << static_cast<bool>(board.IsLinkReady);
    }
    return ready;
}

bool probeFirmataOnPort(const QString& port, int board_profile, int timeout_ms = 15000)
{
    FirmataHarness board;
    board.initDefaults();
    board.PortName = port.toStdString();
    board.prepareForPort();
    board.BoardProfile = board_profile;
    board.BaudRate = 57600;
    board.AutoReconnect = false;
    board.ConnectOnBuild = false;
    board.HeartbeatEnabled = false;
    if (!tryConnectSerial(board, 5000))
        return false;
    const bool ready = pumpCalculate(board, timeout_ms, [&board]() {
        return static_cast<bool>(board.FirmataReady);
    });
    disconnectBoard(board);
    return ready;
}

int digitalFromPinStatusJson(const std::string& json, const QString& pin_id)
{
    const QJsonObject root = QJsonDocument::fromJson(QByteArray::fromStdString(json)).object();
    const QJsonArray pins = root.value(QStringLiteral("pins")).toArray();
    for (const QJsonValue& value : pins) {
        const QJsonObject pin = value.toObject();
        if (pin.value(QStringLiteral("id")).toString() == pin_id)
            return pin.value(QStringLiteral("digital")).toInt(-2);
    }
    return -2;
}

class ArduinoHardwareIntegration : public ::testing::Test {
protected:
    static QString s_port;
    static int s_boardProfile;
    static bool s_uploadedThisRun;

    static void SetUpTestSuite()
    {
        EnsureQtApp();
        EnsureSdkEnv();
        s_boardProfile = boardProfileFromEnv();
        s_port = detectArduinoPort();
        s_uploadedThisRun = false;
    }

    void SetUp() override
    {
        if (s_port.isEmpty()) {
            GTEST_SKIP() << "No serial port detected; set ARDUINO_TEST_PORT or connect Arduino";
        }
    }


    void configureBoard(FirmataHarness& board) const
    {
        board.initDefaults();
        board.PortName = s_port.toStdString();
        board.prepareForPort();
        board.BoardProfile = s_boardProfile;
        board.BaudRate = 57600;
        board.AutoReconnect = false;
        board.ConnectOnBuild = false;
        board.HeartbeatEnabled = false;
        board.ShowDebug = envFlagEnabled("ARDUINO_TEST_DEBUG");
        board.StreamLogEnable = board.ShowDebug;
    }

    bool ensureStandardFirmata(FirmataHarness& board)
    {
        waitForPort(s_port);
        if (!shouldForceFirmwareUpload()
            && probeFirmataOnPort(s_port, s_boardProfile, 15000)) {
            s_uploadedThisRun = false;
            return true;
        }

        if (!canRunAvrdudeUpload()) {
            if (shouldSkipFirmwareUpload()) {
                ADD_FAILURE() << "Firmata probe failed and ARDUINO_SKIP_UPLOAD is set. "
                                 "Unset it or flash standard_firmata manually.";
            } else {
                ADD_FAILURE() << "Firmata probe failed and avrdude was not found on PATH.";
            }
            return false;
        }

        const QString hex =
            RDK::UFirmwareManifest::resolveBundledHex(QStringLiteral("standard_firmata"),
                                                      s_boardProfile);
        if (hex.isEmpty() || !QFile::exists(hex)) {
            ADD_FAILURE() << "standard_firmata hex not found";
            return false;
        }

        board.BundledFirmwareId = "standard_firmata";
        board.FirmwarePath = "";
        board.UploadFirmware = true;
        board.ProcessBoardEdges();
        board.SyncDerivedStates();

        EXPECT_FALSE(board.UploadFirmware);
        const std::string upload_msg = *board.UploadLastResult;
        if (!board.UploadComplete && uploadFailureLooksLikeRunningSketch(upload_msg)) {
            waitForPort(s_port, 20000);
            if (probeFirmataOnPort(s_port, s_boardProfile))
                return true;
        }

        EXPECT_TRUE(board.UploadComplete)
            << "Upload failed: " << upload_msg
            << " progress=" << static_cast<int>(board.UploadProgress)
            << " (tip: double-press RESET before upload, or set ARDUINO_BOARD_PROFILE)";
        s_uploadedThisRun = board.UploadComplete;
        waitForPort(s_port, 20000);
        QThread::msleep(1500);
        return static_cast<bool>(board.UploadComplete)
               || probeFirmataOnPort(s_port, s_boardProfile);
    }
};

QString ArduinoHardwareIntegration::s_port;
int ArduinoHardwareIntegration::s_boardProfile = 0;
bool ArduinoHardwareIntegration::s_uploadedThisRun = false;

#define REQUIRE_ARDUINO_PORT_OPEN()                                                       \
    do {                                                                                  \
        if (!serialPortAccessible(s_port)) {                                              \
            GTEST_SKIP() << "Cannot open " << s_port.toStdString()                        \
                         << " (permission denied?). Add user to dialout: "                \
                            "sudo usermod -aG dialout $USER && newgrp dialout";           \
        }                                                                                 \
    } while (0)

} // namespace

TEST_F(ArduinoHardwareIntegration, 01_PortAutoDetection)
{
    EXPECT_FALSE(s_port.isEmpty());
    const QList<RDK::UArduinoSerialPortEntry> ports =
        RDK::UArduinoSerialPortUtil::listPortsSorted();
    EXPECT_FALSE(ports.isEmpty());

    bool found = false;
    for (const RDK::UArduinoSerialPortEntry& entry : ports) {
        if (entry.DevicePath == s_port) {
            found = true;
            break;
        }
    }
    EXPECT_TRUE(found) << "Selected port " << s_port.toStdString()
                       << " not in enumerated list";
}

TEST_F(ArduinoHardwareIntegration, 02_EnsureStandardFirmata)
{
    REQUIRE_ARDUINO_PORT_OPEN();

    FirmataHarness board;
    configureBoard(board);
    ASSERT_TRUE(ensureStandardFirmata(board));
    disconnectBoard(board);
}

TEST_F(ArduinoHardwareIntegration, 03_FirmataHandshake)
{
    REQUIRE_ARDUINO_PORT_OPEN();
    FirmataHarness board;
    configureBoard(board);
    ASSERT_TRUE(connectAndWaitHandshake(board));
    EXPECT_FALSE(board.FirmataFirmwareVersion->empty());
    EXPECT_GE(board.HandshakeStage, 1);
    EXPECT_TRUE(board.IsLinkReady);
    disconnectBoard(board);
}

TEST_F(ArduinoHardwareIntegration, 04_FirmataDigitalPin13)
{
    REQUIRE_ARDUINO_PORT_OPEN();
    FirmataHarness board;
    configureBoard(board);
    ASSERT_TRUE(connectAndWaitHandshake(board));

    board.SelectedPin = 13;
    board.SelectedPinMode = 1;
    board.DigitalPinValue = 1;
    board.SetPinMode = true;
    board.WriteDigital = true;
    board.RefreshPins = true;

    ASSERT_TRUE(pumpCalculate(board, 5000, [&board]() {
        return digitalFromPinStatusJson(*board.PinStatusJson, QStringLiteral("D13")) == 1;
    })) << "D13 did not read HIGH; PinStatusJson=" << *board.PinStatusJson;

    board.DigitalPinValue = 0;
    board.WriteDigital = true;
    board.RefreshPins = true;
    ASSERT_TRUE(pumpCalculate(board, 5000, [&board]() {
        return digitalFromPinStatusJson(*board.PinStatusJson, QStringLiteral("D13")) == 0;
    })) << "D13 did not read LOW";

    disconnectBoard(board);
}

TEST_F(ArduinoHardwareIntegration, 05_FirmataAnalogA0)
{
    REQUIRE_ARDUINO_PORT_OPEN();
    FirmataHarness board;
    configureBoard(board);
    ASSERT_TRUE(connectAndWaitHandshake(board));

    const int a0_pin =
        RDK::UArduinoPinMap::firmataPinForLabel(QStringLiteral("A0"), s_boardProfile);
    board.SelectedPin = a0_pin;
    board.SelectedPinMode = 2;
    board.SetPinMode = true;
    board.ReadAnalog = true;
    board.ReportAnalogEnable = true;
    board.RefreshPins = true;

    const bool got_sample = pumpCalculate(board, 8000, [&board]() {
        return board.AnalogSamples->GetRows() > 0
               || static_cast<int>(board.AnalogPinValue) >= 0;
    });
    EXPECT_TRUE(got_sample) << "No analog sample for A0; AnalogPinValue="
                            << static_cast<int>(board.AnalogPinValue);

    disconnectBoard(board);
}

TEST_F(ArduinoHardwareIntegration, 06_FirmataRestartHandshake)
{
    REQUIRE_ARDUINO_PORT_OPEN();
    FirmataHarness board;
    configureBoard(board);
    ASSERT_TRUE(connectAndWaitHandshake(board));

    board.RestartFirmata = true;
    board.ACalculate();
    ASSERT_TRUE(pumpCalculate(board, 20000, [&board]() {
        return static_cast<bool>(board.FirmataReady);
    })) << "Handshake after RestartFirmata failed; stage="
         << static_cast<int>(board.HandshakeStage);

    disconnectBoard(board);
}
