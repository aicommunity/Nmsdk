#pragma once
#include <QCoreApplication>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <QSaveFile>
#include <QThread>

// Native work has already finished. Keep the owned process alive while its
// parent reads actual /proc mappings; this does not calculate or reset a model.
inline bool AwaitNativeRuntimeCapture(const QString& directory)
{
    if(directory.isEmpty())return true;
#ifdef Q_OS_LINUX
    const QDir folder(directory);
    const QString readyPath=folder.filePath("capture-ready.json"),ackPath=folder.filePath("capture-ack.json");
    if(!folder.exists() || QFileInfo::exists(readyPath) || QFileInfo::exists(ackPath))return false;
    QFile stat("/proc/self/stat");if(!stat.open(QIODevice::ReadOnly))return false;
    const auto text=stat.readAll();const auto end=text.lastIndexOf(") ");if(end<0)return false;
    const auto fields=QString::fromLatin1(text.mid(end+2)).split(' ',Qt::SkipEmptyParts);
    if(fields.size()<=19)return false;
    const auto ticks=fields[19];const double pid=double(QCoreApplication::applicationPid());
    const QJsonObject ready{{"kind","native_runtime_capture_ready"},{"schema_version",1},{"pid",pid},{"start_ticks",ticks}};
    QSaveFile file(readyPath);if(!file.open(QIODevice::WriteOnly))return false;
    const auto bytes=QJsonDocument(ready).toJson(QJsonDocument::Compact);
    if(file.write(bytes)!=bytes.size() || !file.commit())return false;
    QElapsedTimer elapsed;elapsed.start();
    while(elapsed.elapsed()<10000)
    {
        QFile ack(ackPath);
        if(ack.open(QIODevice::ReadOnly))
        {
            const auto value=QJsonDocument::fromJson(ack.readAll()).object();
            return value==QJsonObject{{"kind","native_runtime_capture_ack"},{"schema_version",1},{"pid",pid},{"start_ticks",ticks}};
        }
        QThread::msleep(2);
    }
#endif
    return false;
}
