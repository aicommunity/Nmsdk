#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NDataset.h"
#include "../Support/ConsoleLikeInit.h"
#include <QCryptographicHash>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <locale>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace {
using namespace RDK;
using namespace NMSDK;
void Require(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
void Write(const std::string& name,const QByteArray& bytes)
{
    if(const auto directory=std::getenv("TIMELEARNER_EXECUTION_OUTPUT"))
    {
        std::filesystem::create_directories(directory);
        QFile file(QString::fromStdString((std::filesystem::path(directory)/name).string()));
        Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"dataset validation evidence exists/unavailable");
        Require(file.write(bytes)==bytes.size() && file.flush(),"dataset validation evidence write failed");
    }
}
void Check(const std::string& name,const QByteArray& content,bool expected,
           int rows=0,int columns=0,const std::vector<double>& values={},bool missing=false)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();core.environment->DestroyModel();
    struct Cleanup {UEPtr<UEnvironment> environment;~Cleanup(){environment->DestroyModel();}} cleanup{core.environment};
    Require(core.environment->CreateModel("NModel"),"dataset validation model unavailable");
    auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());Require(bool(model),"dataset validation root type differs");
    model->SetEnvironment(core.environment);model->SetGlobalTimeStep(2000);
    auto source=dynamic_pointer_cast<NDataset>(core.storage->TakeObject("NDataset"));
    Require(bool(source),"dataset validation storage image missing");
    QTemporaryDir directory;Require(directory.isValid(),"dataset validation temporary directory unavailable");
    const auto path=directory.filePath("data.txt");
    if(!missing)
    {
        QFile file(path);Require(file.open(QIODevice::WriteOnly|QIODevice::NewOnly),"dataset validation input unavailable");
        Require(file.write(content)==content.size() && file.flush(),"dataset validation input write failed");
    }
    source->Name="Dataset";source->SetEnvironment(core.environment);source->SetGlobalTimeStep(2000);
    source->UseRelativePathFromConfig=false;source->UseRelativePathFromWorkDir=false;
    source->FileName=path.toStdString();source->Activity=true;source->StateGeneration=0;
    UEPtr<UContainer> child=source;Require(model->AddComponent(child)!=ForbiddenId,"dataset validation attach failed");
    const auto marker=source->OperationFailureSequence();
    const bool buildResult=source->Build();
    const bool failed=source->HasOperationFailureSince(marker),ready=source->IsReady();
    const bool accepted=ready && !failed;
    QJsonArray cells;
    for(int row=0;row<source->MatrixData.GetRows();++row)
        for(int column=0;column<source->MatrixData.GetCols();++column)
        {
            // Diagnostic text preserves NaN/Inf in failing baselines without
            // turning them into valid JSON numbers or null measurements.
            std::ostringstream token;token.imbue(std::locale::classic());token<<std::hexfloat<<source->MatrixData(row,column);
            cells.append(QString::fromStdString(token.str()));
        }
    const auto stem="dataset_validation_"+name;
    const QJsonObject record{{"kind","native_dataset_file_validation"},{"schema_version",1},
        {"case_id",QString::fromStdString(name)},{"expected_accepted",expected},{"accepted",accepted},
        {"ready",ready},{"operation_failure",failed},{"build_result",buildResult},{"missing",missing},
        {"rows",source->MatrixData.GetRows()},{"columns",source->MatrixData.GetCols()},
        {"num_samples",source->NumSamples.GetData()},{"num_features",source->NumFeatures.GetData()},
        {"max_spikes",source->MaxSpikesPerFeature.GetData()},{"reload_pending",source->ReloadDataset.GetData()},
        {"generators",source->GetNumComponents()},{"cells_hex",cells},
        {"input_sha256",QString::fromLatin1(QCryptographicHash::hash(content,QCryptographicHash::Sha256).toHex())},
        {"input",QString::fromStdString(stem+".txt")},{"scientific_verdict",QJsonValue(QJsonValue::Null)}};
    Write(stem+".txt",content);Write(stem+".json",QJsonDocument(record).toJson());
    EXPECT_TRUE(buildResult)<<"native Build bool is an interface artifact, including invalid input";
    EXPECT_EQ(accepted,expected)<<"data validity must not follow atoi/atof prefix conversion";
    if(expected)
    {
        ASSERT_EQ(source->MatrixData.GetRows(),rows);ASSERT_EQ(source->MatrixData.GetCols(),columns);
        EXPECT_FALSE(failed);EXPECT_EQ(source->NumFeatures.GetData(),columns);
        EXPECT_EQ(source->GetNumComponents(),columns);
        if(missing){EXPECT_TRUE(source->ReloadDataset.GetData());EXPECT_EQ(source->NumSamples.GetData(),0);}
        else
        {
            EXPECT_FALSE(source->ReloadDataset.GetData());EXPECT_EQ(source->GetSampleClass(0),7);
            ASSERT_EQ(values.size(),std::size_t(rows*columns));
            for(int row=0;row<rows;++row)for(int column=0;column<columns;++column)
                EXPECT_DOUBLE_EQ(source->MatrixData(row,column),values[std::size_t(row*columns+column)]);
        }
    }
    else {EXPECT_FALSE(ready);EXPECT_TRUE(failed);}
}
template<class F> void Run(F operation)
{try{operation();}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
TEST(DatasetFileValidation,ValidLegacySingle){Run([]{Check("legacy","class;f0;f1\n7;0.01;0.02\n",true,1,2,{.01,.02});});}
TEST(DatasetFileValidation,ValidMultiBlankClass){Run([]{Check("multi_blank","#NDataset;MaxSpikes=2\nclass;f0;f1\n7;.01;.02\n;.03;-1\n",true,2,2,{.01,.02,.03,-1});});}
TEST(DatasetFileValidation,ValidMultiNoClass){Run([]{Check("multi_none","# NDataset MaxSpikes=2\nclass;f0;f1\n7;.01;.02\n.03;-1\n",true,2,2,{.01,.02,.03,-1});});}
TEST(DatasetFileValidation,ValidSignedWhitespaceCRLF){Run([]{Check("whitespace","class;f0;f1\r\n +7 ; +1e-2 ; -1 \r\n",true,1,2,{.01,-1});});}
TEST(DatasetFileValidation,MissingFileIdle){Run([]{Check("missing","",true,0,0,{},true);});}
TEST(DatasetFileValidation,RejectGarbageClass){Run([]{Check("class_junk","class;f0\nlabel;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassSuffix){Run([]{Check("class_suffix","class;f0\n7x;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassDecimal){Run([]{Check("class_decimal","class;f0\n7.0;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassOverflow){Run([]{Check("class_overflow","class;f0\n2147483648;.01\n",false);});}
TEST(DatasetFileValidation,RejectGarbageIsi){Run([]{Check("isi_junk","class;f0\n7;bad\n",false);});}
TEST(DatasetFileValidation,RejectIsiSuffix){Run([]{Check("isi_suffix","class;f0\n7;.01ms\n",false);});}
TEST(DatasetFileValidation,RejectNaN){Run([]{Check("nan","class;f0\n7;nan\n",false);});}
TEST(DatasetFileValidation,RejectInf){Run([]{Check("inf","class;f0\n7;inf\n",false);});}
TEST(DatasetFileValidation,RejectOverflowIsi){Run([]{Check("isi_overflow","class;f0\n7;1e999\n",false);});}
TEST(DatasetFileValidation,RejectEmptyIsi){Run([]{Check("empty","class;f0;f1\n7;;.02\n",false);});}
TEST(DatasetFileValidation,RejectExtraIsi){Run([]{Check("extra","class;f0\n7;.01;.02\n",false);});}
TEST(DatasetFileValidation,RejectTrailingDelimiter){Run([]{Check("trailing","class;f0\n7;.01;\n",false);});}
TEST(DatasetFileValidation,RejectWrongHeaderWidth){Run([]{Check("header","f0;f1\n7;.01;.02\n",false);});}
TEST(DatasetFileValidation,RejectMetaSuffix){Run([]{Check("meta_suffix","#NDataset;MaxSpikes=2junk\nclass;f0\n7;.01\n;.02\n",false);});}
TEST(DatasetFileValidation,RejectUnknownMeta){Run([]{Check("meta_unknown","#NDatasetX;MaxSpikes=2\nclass;f0\n7;.01\n;.02\n",false);});}
TEST(DatasetFileValidation,RejectIncompleteBlock){Run([]{Check("block","#NDataset;MaxSpikes=2\nclass;f0\n7;.01\n",false);});}
TEST(DatasetFileValidation,RejectMissingFeature){Run([]{Check("short_row","class;f0;f1\n7;.01\n",false);});}
}
