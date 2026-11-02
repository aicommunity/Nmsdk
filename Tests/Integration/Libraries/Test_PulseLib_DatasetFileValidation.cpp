#include <gtest/gtest.h>
#include "../../../Libraries/Nmsdk-PulseLib/Core/NDataset.h"
#include "../../../Libraries/Nmsdk-PulseLib/Core/NPulseGeneratorTransit.h"
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
template<class F> void ExecuteFileCheck(F operation)
{try{operation();}catch(const RDK::UException& e){FAIL()<<e.what();}catch(const std::exception& e){FAIL()<<e.what();}}
TEST(DatasetFileValidation,ValidLegacySingle){ExecuteFileCheck([]{Check("legacy","class;f0;f1\n7;0.01;0.02\n",true,1,2,{.01,.02});});}
TEST(DatasetFileValidation,ValidMultiBlankClass){ExecuteFileCheck([]{Check("multi_blank","#NDataset;MaxSpikes=2\nclass;f0;f1\n7;.01;.02\n;.03;-1\n",true,2,2,{.01,.02,.03,-1});});}
TEST(DatasetFileValidation,ValidMultiNoClass){ExecuteFileCheck([]{Check("multi_none","# NDataset MaxSpikes=2\nclass;f0;f1\n7;.01;.02\n.03;-1\n",true,2,2,{.01,.02,.03,-1});});}
TEST(DatasetFileValidation,ValidSignedWhitespaceCRLF){ExecuteFileCheck([]{Check("whitespace","class;f0;f1\r\n +7 ; +1e-2 ; -1 \r\n",true,1,2,{.01,-1});});}
TEST(DatasetFileValidation,MissingFileIdle){ExecuteFileCheck([]{Check("missing","",true,0,0,{},true);});}
TEST(DatasetFileValidation,RejectGarbageClass){ExecuteFileCheck([]{Check("class_junk","class;f0\nlabel;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassSuffix){ExecuteFileCheck([]{Check("class_suffix","class;f0\n7x;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassDecimal){ExecuteFileCheck([]{Check("class_decimal","class;f0\n7.0;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassOverflow){ExecuteFileCheck([]{Check("class_overflow","class;f0\n2147483648;.01\n",false);});}
TEST(DatasetFileValidation,RejectGarbageIsi){ExecuteFileCheck([]{Check("isi_junk","class;f0\n7;bad\n",false);});}
TEST(DatasetFileValidation,RejectIsiSuffix){ExecuteFileCheck([]{Check("isi_suffix","class;f0\n7;.01ms\n",false);});}
TEST(DatasetFileValidation,RejectNaN){ExecuteFileCheck([]{Check("nan","class;f0\n7;nan\n",false);});}
TEST(DatasetFileValidation,RejectInf){ExecuteFileCheck([]{Check("inf","class;f0\n7;inf\n",false);});}
TEST(DatasetFileValidation,RejectOverflowIsi){ExecuteFileCheck([]{Check("isi_overflow","class;f0\n7;1e999\n",false);});}
TEST(DatasetFileValidation,RejectEmptyIsi){ExecuteFileCheck([]{Check("empty","class;f0;f1\n7;;.02\n",false);});}
TEST(DatasetFileValidation,RejectExtraIsi){ExecuteFileCheck([]{Check("extra","class;f0\n7;.01;.02\n",false);});}
TEST(DatasetFileValidation,RejectTrailingDelimiter){ExecuteFileCheck([]{Check("trailing","class;f0\n7;.01;\n",false);});}
TEST(DatasetFileValidation,RejectWrongHeaderWidth){ExecuteFileCheck([]{Check("header","f0;f1\n7;.01;.02\n",false);});}
TEST(DatasetFileValidation,RejectMetaSuffix){ExecuteFileCheck([]{Check("meta_suffix","#NDataset;MaxSpikes=2junk\nclass;f0\n7;.01\n;.02\n",false);});}
TEST(DatasetFileValidation,RejectUnknownMeta){ExecuteFileCheck([]{Check("meta_unknown","#NDatasetX;MaxSpikes=2\nclass;f0\n7;.01\n;.02\n",false);});}
TEST(DatasetFileValidation,RejectIncompleteBlock){ExecuteFileCheck([]{Check("block","#NDataset;MaxSpikes=2\nclass;f0\n7;.01\n",false);});}
TEST(DatasetFileValidation,RejectMissingFeature){ExecuteFileCheck([]{Check("short_row","class;f0;f1\n7;.01\n",false);});}
TEST(DatasetFileValidation,RejectClassDoubleSign){ExecuteFileCheck([]{Check("class_sign","class;f0\n+-7;.01\n",false);});}
TEST(DatasetFileValidation,RejectIsiDoubleSign){ExecuteFileCheck([]{Check("isi_sign","class;f0\n7;+-0.01\n",false);});}
TEST(DatasetFileValidation,ValidUtf8Bom){ExecuteFileCheck([]{Check("bom",QByteArray::fromHex("efbbbf")+"#NDataset;MaxSpikes=2\nclass;f0\n7;.01\n;.02\n",true,2,1,{.01,.02});});}
TEST(DatasetFileValidation,ValidBlankWhitespaceLines){ExecuteFileCheck([]{Check("blank_lines","class;f0\n \t\r\n7;.01\n\t\n",true,1,1,{.01});});}

// A valid cold parser is insufficient: reject a corrupt replacement while an
// initialized generator is high, then recover through the native owner path.
void CheckHotReload(unsigned frequency)
{
    const auto& core=NmsdkTests::InitEngineForPulseLibTests();
    struct Cleanup {
        UEPtr<UEnvironment> environment;ULongTime prior;
        ~Cleanup(){environment->DestroyModel();environment->GetTime().SetTime(prior);}
    } cleanup{core.environment,core.environment->GetTime().GetTime()};
    core.environment->DestroyModel();
    Require(core.environment->CreateModel("NModel"),"hot validation model unavailable");
    auto model=dynamic_pointer_cast<UNet>(core.environment->GetModel());
    Require(bool(model),"hot validation model type differs");
    model->SetEnvironment(core.environment);model->SetGlobalTimeStep(frequency);
    auto source=dynamic_pointer_cast<NDataset>(core.storage->TakeObject("NDataset"));
    Require(bool(source),"hot validation storage image unavailable");
    QTemporaryDir directory;Require(directory.isValid(),"hot validation directory unavailable");
    const auto path=directory.filePath("data.txt");
    auto replace=[&](const QByteArray& content) {
        QFile file(path);Require(file.open(QIODevice::WriteOnly|QIODevice::Truncate),"hot input unavailable");
        Require(file.write(content)==content.size() && file.flush(),"hot input write failed");
    };
    const QByteArray original="class;f0\n7;.01\n",corrupt="class;f0\n9;bad\n",recovered="class;f0\n9;.02\n";
    replace(original);
    source->Name="Dataset";source->SetEnvironment(core.environment);source->SetGlobalTimeStep(frequency);
    source->UseRelativePathFromConfig=false;source->UseRelativePathFromWorkDir=false;
    source->FileName=path.toStdString();source->Activity=true;source->StateGeneration=2;source->Delay=0.;
    UEPtr<UContainer> child=source;Require(model->AddComponent(child)!=ForbiddenId,"hot validation attach failed");
    const auto initMarker=model->OperationFailureSequence();model->Init();model->Reset();
    Require(model->IsInit() && model->IsReady() && !model->HasOperationFailureSince(initMarker),"hot initialization failed");
    core.environment->GetTime().SetTime(1000000);
    auto output=[&]() {
        auto generator=source->GetComponentL<NPulseGeneratorTransit>("Generator1",true);
        Require(bool(generator) && generator->IsInit() && generator->IsReady(),"hot generator not initialized");
        Require(generator->Output.GetRows()==1 && generator->Output.GetCols()==1,"hot output shape differs");
        const double value=generator->Output(0,0);Require(std::isfinite(value),"hot output nonfinite");return value;
    };
    std::ostringstream csv;csv.imbue(std::locale::classic());csv<<std::setprecision(17)<<"time,phase,input,ready,reload,operation_failure\n";
    unsigned originalWrong=0,invalidHigh=0,recoveryWrong=0;bool invalidDetected=true,publicResults=true;
    for(unsigned tick=0;tick<=frequency/100;++tick)
    {
        const auto marker=model->OperationFailureSequence();publicResults&=model->Calculate();
        Require(!model->HasOperationFailureSince(marker),"valid original playback failed");
        const double value=output();originalWrong+=(value>0.)!=(tick==frequency/100);
        csv<<core.environment->GetTime().GetDoubleTime()<<",0,"<<value<<','<<source->IsReady()<<','<<source->ReloadDataset.GetData()<<",0\n";
        core.environment->IncreaseModelTimeByStep();
    }
    replace(corrupt);source->ReloadDataset=true;
    for(unsigned tick=0;tick<3;++tick)
    {
        const auto marker=source->OperationFailureSequence();publicResults&=model->Calculate();
        const bool failed=source->HasOperationFailureSince(marker);
        invalidDetected&=failed && !source->IsReady() && source->ReloadDataset.GetData();
        const double value=output();invalidHigh+=value>0.;
        csv<<core.environment->GetTime().GetDoubleTime()<<",1,"<<value<<','<<source->IsReady()<<','<<source->ReloadDataset.GetData()<<','<<failed<<'\n';
        core.environment->IncreaseModelTimeByStep();
    }
    // The rejected parse must not partially replace the old matrix or label.
    EXPECT_EQ(source->GetSampleClass(0),7);ASSERT_EQ(source->MatrixData.GetRows(),1);
    ASSERT_EQ(source->MatrixData.GetCols(),1);EXPECT_DOUBLE_EQ(source->MatrixData(0,0),.01);
    replace(recovered);source->ReloadDataset=true;
    for(unsigned tick=0;tick<=frequency*3/100;++tick)
    {
        const auto marker=model->OperationFailureSequence();publicResults&=model->Calculate();
        Require(!model->HasOperationFailureSince(marker) && source->IsReady() && !source->ReloadDataset.GetData(),"recovery did not complete natively");
        Require(source->GetSampleClass(0)==9,"recovery reused stale label");
        const double value=output();const unsigned onset=frequency/50,width=frequency/1000;
        recoveryWrong+=(value>0.)!=(tick>=onset && tick<onset+width);
        csv<<core.environment->GetTime().GetDoubleTime()<<",2,"<<value<<",1,0,0\n";
        core.environment->IncreaseModelTimeByStep();
    }
    const auto stem="dataset_hot_validation_"+std::to_string(frequency);
    Write(stem+".csv",QByteArray::fromStdString(csv.str()));
    Write(stem+"_original.txt",original);Write(stem+"_corrupt.txt",corrupt);Write(stem+"_recovered.txt",recovered);
    Write(stem+".json",QJsonDocument(QJsonObject{{"kind","native_dataset_hot_validation"},{"schema_version",1},
        {"frequency_hz",int(frequency)},{"original_wrong_samples",int(originalWrong)},
        {"invalid_high_samples",int(invalidHigh)},{"invalid_detected",invalidDetected},
        {"recovery_wrong_samples",int(recoveryWrong)},{"public_results_true",publicResults},
        {"complete",true},{"trace",QString::fromStdString(stem+".csv")},
        {"scientific_verdict",QJsonValue(QJsonValue::Null)}}).toJson());
    EXPECT_TRUE(publicResults);EXPECT_TRUE(invalidDetected);EXPECT_EQ(originalWrong,0u);
    EXPECT_EQ(invalidHigh,0u)<<"invalid replacement must not continue stale stimulus";
    EXPECT_EQ(recoveryWrong,0u)<<"recovery must not shift onset or reuse old schedule";
}
TEST(DatasetHotValidation,CorruptThenRecoverAt2000){ExecuteFileCheck([]{CheckHotReload(2000);});}
TEST(DatasetHotValidation,CorruptThenRecoverAt20000){ExecuteFileCheck([]{CheckHotReload(20000);});}
}
