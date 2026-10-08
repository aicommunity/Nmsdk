#ifndef HARDWARETESTPATHS_H
#define HARDWARETESTPATHS_H

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>

namespace HardwareTestPaths {

inline QString findRepositoryRoot(const QString& startPath)
{
    QDir dir(startPath);
    if (!QFileInfo(startPath).isDir())
        dir = QFileInfo(startPath).dir();
    while (dir.exists()) {
        if (QFile::exists(dir.filePath(QStringLiteral("Libraries/Rdk-HardwareLib/Catalog/catalog.json"))))
            return dir.absolutePath();
        if (!dir.cdUp())
            break;
    }
    return QString();
}

inline void ensureCatalogEnvironment(const char* sourceFile)
{
    const QStringList starts = {
        QString::fromLocal8Bit(qgetenv("NMSDK_SOURCE_DIR")),
        QString::fromLocal8Bit(sourceFile),
        QDir::currentPath(),
        QCoreApplication::applicationDirPath(),
    };
    QString root;
    for (const QString& start : starts) {
        if (start.isEmpty())
            continue;
        root = findRepositoryRoot(start);
        if (!root.isEmpty())
            break;
    }
    if (root.isEmpty())
        return;

    qputenv("NMSDK_SOURCE_DIR", root.toLocal8Bit());
    qputenv("NMSDK_ROOT", root.toLocal8Bit());
    qputenv("RDK_HARDWARE_CATALOG_DIR",
            QDir(root).filePath(QStringLiteral("Libraries/Rdk-HardwareLib/Catalog")).toLocal8Bit());
}

} // namespace HardwareTestPaths

#endif
