#pragma once

#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <cstdlib>
#include <stdexcept>

namespace NmsdkTests {

// The historical binary lives in the external archive. The native gate must
// declare its exact bytes and stage them beside its owned native output; tests
// must not depend on a binary having been restored into a source checkout.
inline QByteArray ReadRecordedClassicModelFixture()
{
    const char* output = std::getenv("TIMELEARNER_EXECUTION_OUTPUT");
    if(!output || !*output)
        throw std::runtime_error("recorded_classic_fixture_requires_owned_native_output");
    const auto filename = QDir(QString::fromLocal8Bit(output)).filePath(
        "../native-inputs/classic-package6.qz");
    QFile file(filename);
    if(!file.open(QIODevice::ReadOnly))
        throw std::runtime_error("recorded_classic_fixture_missing: " + filename.toStdString());
    const auto compressed = file.read(323021);
    if(compressed.size() != 323020 ||
       QCryptographicHash::hash(compressed, QCryptographicHash::Sha256).toHex() !=
           QByteArray("d58ce13f3759a9e7c38f65c2cdb3059bb7ddccbd152d7e4144564c1efa36b234"))
        throw std::runtime_error("recorded_classic_fixture_compressed_identity");
    // Check qCompress's advertised allocation before invoking qUncompress.
    const auto byte = [&](int index) { return static_cast<unsigned char>(compressed[index]); };
    const auto expanded = (unsigned(byte(0)) << 24) | (unsigned(byte(1)) << 16) |
                          (unsigned(byte(2)) << 8) | unsigned(byte(3));
    if(expanded != 4812359)
        throw std::runtime_error("recorded_classic_fixture_expanded_size");
    const auto raw = qUncompress(compressed);
    if(raw.size() != 4812359 ||
       QCryptographicHash::hash(raw, QCryptographicHash::Sha256).toHex() !=
           QByteArray("1c8d50628e7eea87c2bad230428526000802ec73e9627bd5d7d7f414bb69e05c"))
        throw std::runtime_error("recorded_classic_fixture_raw_identity");
    return raw;
}

}
