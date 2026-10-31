#include <gtest/gtest.h>
#include "TimeLearner/NativePostTuneConfiguration.h"
#include "TimeLearner/ConfiguredNativeTraining.h"
#include "TimeLearner/ModelIdentity.h"
#include <QDir>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <cstdlib>
#include <limits>
#include <set>

namespace {
using namespace NMSDK::TimeLearner;
QJsonObject Read(const QString& path)
{
    QFile file(path);if(!file.open(QIODevice::ReadOnly))throw std::runtime_error("missing_post_tune_configuration_fixture");
    return ParseStrictNativeJsonObject(file.readAll().toStdString(),256*1024*1024);
}
NativeThresholdGridSpec Grid(const QJsonObject& job)
{
    NativeThresholdGridSpec grid;grid.maximumCandidates=std::size_t(job["maximum_candidates"].toDouble());
    grid.confirmation=DecodeNativeThresholdConfirmationSpec(job["specification"].toObject());
    for(const auto& t:job["thresholds"].toArray())grid.thresholds.push_back(t.toDouble());
    for(const auto& q:job["trials"].toArray())grid.trials.push_back(DecodeNativeCalibrationRequest(q.toObject()));
    return grid;
}
TEST(NativePostTuneConfiguration,AllEighteenPublishedProductionJobs)
{
    const auto directory=std::getenv("TIMELEARNER_POSTTUNE_CONFIG_SOURCE");
    if(!directory)GTEST_SKIP()<<"Requires original 18-job production corpus";
    const QDir root(QString::fromLocal8Bit(directory));const auto controls=Read(root.filePath("controls.json"))["records"].toArray();
    ASSERT_EQ(controls.size(),18);std::set<QString> modes,metrics;
    for(const auto& control:controls)
    {
        const auto name=control.toObject()["name"].toString();SCOPED_TRACE(name.toStdString());
        const auto job=Read(root.filePath(name+"/input/job.json"));auto unsignedJob=job;unsignedJob.remove("sha256");
        ASSERT_EQ(job["sha256"].toString(),NmsdkTools::CanonicalModelDataSha256(unsignedJob));
        const auto grid=Grid(job);
        const auto decoded=DecodeNativePostTuneControls(job["post_tune"].toObject(),grid);
        const auto controlsObject=job["post_tune"].toObject();
        EXPECT_EQ(decoded.canonicalFloor,controlsObject["canonical_floor"].toDouble());
        EXPECT_EQ(decoded.canonicalLast,controlsObject["canonical_last"].toDouble());
        EXPECT_EQ(decoded.minimumPositiveGap,controlsObject["minimum_positive_gap"].toDouble());
        EXPECT_EQ(decoded.searchPasses,unsigned(controlsObject["search_passes"].toDouble()));
        EXPECT_EQ(decoded.maximumCandidates,std::size_t(controlsObject["maximum_candidates"].toDouble()));
        EXPECT_EQ(decoded.maximumRecordedSamples,std::size_t(controlsObject["maximum_recorded_samples"].toDouble()));
        ASSERT_EQ(decoded.resistanceBounds.size(),std::size_t(controlsObject["resistance_bounds"].toArray().size()));
        for(std::size_t i=0;i<decoded.resistanceBounds.size();++i)
        {
            const auto bound=controlsObject["resistance_bounds"].toArray()[int(i)].toObject();
            EXPECT_EQ(decoded.resistanceBounds[i].minimum,bound["minimum"].toDouble());
            EXPECT_EQ(decoded.resistanceBounds[i].maximum,bound["maximum"].toDouble());
        }
        EXPECT_EQ(EncodeNativePostTuneControls(decoded),job["post_tune"].toObject());
        EXPECT_EQ(decoded.calibration.thresholds,grid.thresholds);
        EXPECT_EQ(decoded.calibration.maximumCandidates,grid.maximumCandidates);
        EXPECT_EQ(EncodeNativeThresholdConfirmationSpec(decoded.calibration.confirmation),job["specification"].toObject());
        ASSERT_EQ(decoded.calibration.trials.size(),std::size_t(job["trials"].toArray().size()));
        for(std::size_t i=0;i<grid.trials.size();++i)
            EXPECT_EQ(EncodeNativeCalibrationRequest(decoded.calibration.trials[i]),job["trials"].toArray()[int(i)].toObject());
        modes.insert(job["post_tune"].toObject()["mode"].toString());metrics.insert(job["post_tune"].toObject()["metric"].toString());
    }
    EXPECT_EQ(modes.size(),5u);EXPECT_EQ(metrics.size(),3u);
}
TEST(NativePostTuneConfiguration,RejectsUnknownFieldsEnumsAndTypes)
{
    const auto good=EncodeNativePostTuneControls(NativePostTuneTransactionSpec{});
    for(auto it=good.begin();it!=good.end();++it)
    {
        auto missing=good;missing.remove(it.key());EXPECT_THROW(DecodeNativePostTuneControls(missing,{}),std::invalid_argument);
        auto wrong=good;wrong[it.key()]=QJsonValue(QJsonValue::Null);
        EXPECT_THROW(DecodeNativePostTuneControls(wrong,{}),std::invalid_argument);
    }
    auto extra=good;extra["ignored_factor"]=1.;EXPECT_THROW(DecodeNativePostTuneControls(extra,{}),std::invalid_argument);
    for(const auto* key:{"mode","metric"})
    {auto wrong=good;wrong[key]="unsupported";EXPECT_THROW(DecodeNativePostTuneControls(wrong,{}),std::invalid_argument);}
    for(const auto* key:{"canonical_floor","canonical_last","minimum_positive_gap","search_passes","maximum_candidates","maximum_recorded_samples"})
        for(const auto& value:{QJsonValue(true),QJsonValue("1"),QJsonValue(QJsonArray{})})
        {auto wrong=good;wrong[key]=value;EXPECT_THROW(DecodeNativePostTuneControls(wrong,{}),std::invalid_argument);}
    for(const auto& value:{QJsonValue(1.),QJsonValue(QJsonObject{{"minimum",1.}}),
        QJsonValue(QJsonObject{{"minimum",1.},{"maximum","2"}}),
        QJsonValue(QJsonObject{{"minimum",1.},{"maximum",2.},{"extra",3.}})})
    {auto wrong=good;wrong["resistance_bounds"]=QJsonArray{value};EXPECT_THROW(DecodeNativePostTuneControls(wrong,{}),std::invalid_argument);}
    EXPECT_THROW(ParseStrictNativeJsonObject("{\"post_tune\":{\"mode\":\"off\",\"mode\":\"keep_done\"}}"),std::invalid_argument);
}
TEST(NativePostTuneConfiguration,RejectsUnrepresentableBudgetsAndNonfiniteControls)
{
    const auto good=EncodeNativePostTuneControls(NativePostTuneTransactionSpec{});
    for(const auto* key:{"search_passes","maximum_candidates","maximum_recorded_samples"})
        for(double n:{0.,-1.,1.5,100000001.})
        {auto wrong=good;wrong[key]=n;EXPECT_THROW(DecodeNativePostTuneControls(wrong,{}),std::invalid_argument);}
    NativePostTuneTransactionSpec spec;
    spec.canonicalFloor=std::numeric_limits<double>::quiet_NaN();EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
    spec.canonicalFloor=0.;spec.minimumPositiveGap=std::numeric_limits<double>::infinity();EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
    spec.minimumPositiveGap=0.;spec.resistanceBounds={{1.,std::numeric_limits<double>::infinity()}};
    EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
    spec.resistanceBounds.clear();spec.mode=static_cast<NativePostTuneControllerMode>(99);
    EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
    spec.mode=NativePostTuneControllerMode::Off;spec.metric=static_cast<NativePostTuneMetric>(99);
    EXPECT_THROW(EncodeNativePostTuneControls(spec),std::invalid_argument);
}
}
