#include <gtest/gtest.h>
#include "../../../App/NeuroModelerConsole/RuntimeCapture.h"
#include <QTemporaryDir>
#include <atomic>
#include <thread>

namespace {
bool PublishAcknowledgement(const QString& directory, unsigned delayMilliseconds, bool wrongIdentity)
{
    const QDir folder(directory);
    QElapsedTimer waiting;waiting.start();QJsonObject ready;
    while(waiting.elapsed()<5000)
    {
        QFile file(folder.filePath("capture-ready.json"));
        if(file.open(QIODevice::ReadOnly))
        {
            ready=QJsonDocument::fromJson(file.readAll()).object();
            if(!ready.isEmpty())break;
        }
        QThread::msleep(2);
    }
    if(ready.isEmpty())return false;
    QThread::msleep(delayMilliseconds);
    ready["kind"]="native_runtime_capture_ack";
    if(wrongIdentity)ready["pid"]=ready["pid"].toDouble()+1;
    QSaveFile file(folder.filePath("capture-ack.json"));
    if(!file.open(QIODevice::WriteOnly))return false;
    const auto bytes=QJsonDocument(ready).toJson(QJsonDocument::Compact);
    return file.write(bytes)==bytes.size() && file.commit();
}

TEST(NativeRuntimeCapture,AcceptsSameProcessAfterFormerTenSecondDeadline)
{
    QTemporaryDir temporary;ASSERT_TRUE(temporary.isValid());
    std::atomic<bool> published{false};
    std::thread supervisor([&]{published=PublishAcknowledgement(temporary.path(),11000,false);});
    const bool accepted=AwaitNativeRuntimeCapture(temporary.path());
    supervisor.join();EXPECT_TRUE(published);EXPECT_TRUE(accepted);
}

TEST(NativeRuntimeCapture,RejectsAcknowledgementForAnotherProcess)
{
    QTemporaryDir temporary;ASSERT_TRUE(temporary.isValid());
    std::atomic<bool> published{false};
    std::thread supervisor([&]{published=PublishAcknowledgement(temporary.path(),0,true);});
    const bool accepted=AwaitNativeRuntimeCapture(temporary.path());
    supervisor.join();EXPECT_TRUE(published);EXPECT_FALSE(accepted);
}

TEST(NativeRuntimeCapture,MissingAcknowledgementRemainsBoundedAndNegative)
{
    QTemporaryDir temporary;ASSERT_TRUE(temporary.isValid());
    QElapsedTimer waiting;waiting.start();
    EXPECT_FALSE(AwaitNativeRuntimeCapture(temporary.path(),50));
    EXPECT_GE(waiting.elapsed(),50);EXPECT_LT(waiting.elapsed(),5000);
    EXPECT_TRUE(QFileInfo::exists(QDir(temporary.path()).filePath("capture-ready.json")));
    EXPECT_FALSE(QFileInfo::exists(QDir(temporary.path()).filePath("capture-ack.json")));
}
}
