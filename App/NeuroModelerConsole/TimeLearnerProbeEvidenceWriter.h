#pragma once
#include "TimeLearnerJobSupport.h"
#include "TimeLearner/ProbeEvidenceJson.h"
#include <iomanip>
#include <locale>
#include <sstream>

namespace NmsdkWorker {
// Streams every native sample; only one row is formatted in memory at a time.
// No trace is treated as complete merely because its file was closed.
class EvidenceWriter {
    QString directory;
    std::size_t channels,count=0,sampledFrames=0;
    QFile csv;
    bool pending=false;
    std::vector<std::pair<QString,QString>> files;
    void Open()
    {
        Require(!pending,"training_trace_already_open");pending=true;++count;
        const QString stem="raw-trial-"+QString::number(qulonglong(count));csv.setFileName(QDir(directory).filePath(stem+".csv"));
        Require(csv.open(QIODevice::WriteOnly|QIODevice::NewOnly),"training_trace_open_failed");
        QByteArray header="time,stimulus";for(std::size_t i=0;i<channels;++i)header+=",soma"+QByteArray::number(qulonglong(i));header+='\n';
        Require(csv.write(header)==header.size(),"training_trace_write_failed");
    }
public:
    EvidenceWriter(QString directory,std::size_t channels):directory(std::move(directory)),channels(channels){}
    void Prepared(const NMSDK::TimeLearner::PreparedVerificationProbe&,const NMSDK::TimeLearner::ProbeSpec&){Open();}
    void Sample(const NMSDK::TimeLearner::NativeProbeSample& sample)
    {
        Require(pending && sample.potentials.size()==channels,"training_trace_shape_or_order_changed");
        std::ostringstream row;row.imbue(std::locale::classic());row<<std::setprecision(17)<<sample.time<<','<<sample.stimulus;
        for(double value:sample.potentials)row<<','<<value;row<<'\n';const auto bytes=QByteArray::fromStdString(row.str());
        Require(csv.write(bytes)==bytes.size(),"training_trace_write_failed");++sampledFrames;
    }
    std::size_t NativeTrials() const {return count;}
    std::size_t SampledFrames() const {return sampledFrames;}
    void Observation(const NMSDK::TimeLearner::NativeProbeResult& result)
    {
        if(!pending)Open(); // An unarmed cancellation still has a declared empty CSV.
        Require(csv.flush(),"training_trace_flush_failed");csv.close();
        const QString stem="raw-trial-"+QString::number(qulonglong(count));
        Write(directory,stem+".json",NMSDK::TimeLearner::EncodeNativeProbeEvidence(result));
        files.emplace_back(stem+".json",stem+".csv");pending=false;
    }
    QJsonArray Finalize(bool stopped)
    {return FinalizeWithPrefix(stopped?"train_stopped_trial_":"train_state_trial_");}
    QJsonArray FinalizeWithPrefix(const QString& prefix)
    {
        Require(!pending,"training_observation_not_closed");QJsonArray records;std::size_t index=0;
        for(const auto& pair:files)
        {
            const QString stem=prefix+QString::number(qulonglong(++index));
            for(const auto& entry:{std::make_pair(pair.first,stem+".json"),std::make_pair(pair.second,stem+".csv")})
            {
                QFile source(QDir(directory).filePath(entry.first));Require(source.rename(QDir(directory).filePath(entry.second)),"training_trace_finalize_failed");
                Require(source.open(QIODevice::ReadOnly),"training_trace_readback_failed");const auto size=source.size();
                QCryptographicHash hash(QCryptographicHash::Sha256);Require(hash.addData(&source),"training_trace_readback_failed");source.close();
                records.append(QJsonObject{{"path",entry.second},{"bytes",double(size)},
                    {"sha256",QString::fromLatin1(hash.result().toHex())}});
            }
        }
        return records;
    }
};
}
