#include <gtest/gtest.h>
#include "TimeLearner/StrictNativeJson.h"
#include <QJsonDocument>
#include <stdexcept>
#include <vector>

namespace {
TEST(NativeJsonByteInput,OwnedResultAndStringCompatibility)
{
    using namespace NMSDK::TimeLearner;
    QByteArray bytes="{\"text\":\"\\u0410\\u0000\\uD83D\\uDE00\",\"nested\":{\"history\":[1,true,null]},\"padding\":\"";
    bytes+=QByteArray(128*1024,'p');bytes+="\"}";
    const auto expected=QJsonDocument::fromJson(bytes).object();
    ASSERT_FALSE(expected.isEmpty());
    const auto byteResult=ParseStrictNativeJsonBytes(bytes,std::size_t(bytes.size()));
    auto text=bytes.toStdString();
    const auto stringResult=ParseStrictNativeJsonObject(text,text.size());
    EXPECT_EQ(byteResult,expected);EXPECT_EQ(stringResult,expected);
    // Neither entry point may return JSON backed by the caller's raw view.
    bytes.fill('x');text.assign(text.size(),'y');
    EXPECT_EQ(byteResult,expected);EXPECT_EQ(stringResult,expected);
    EXPECT_EQ(byteResult["text"].toString().size(),4);
    EXPECT_EQ(byteResult["text"].toString().at(1),QChar(0));
}

TEST(NativeJsonByteInput,DuplicateKeysRemainRejectedInNestedAndEscapedForms)
{
    using namespace NMSDK::TimeLearner;
    for(const auto& bytes:std::vector<QByteArray>{
        "{\"a\":1,\"a\":2}","{\"a\":1,\"\\u0061\":2}",
        "{\"outer\":[{\"key\":0,\"key\":1}]}",
        "{\"\\u0410\":1,\"\\u0410\":2}"})
    {
        ASSERT_FALSE(QJsonDocument::fromJson(bytes).isNull());
        EXPECT_THROW(ParseStrictNativeJsonBytes(bytes),std::invalid_argument);
        EXPECT_THROW(ParseStrictNativeJsonObject(bytes.toStdString()),std::invalid_argument);
    }
}

TEST(NativeJsonByteInput,Utf8BomDoesNotBypassDuplicateChecks)
{
    using namespace NMSDK::TimeLearner;
    const auto bom=QByteArray::fromHex("efbbbf");
    const auto valid=bom+"{\"outer\":{\"a\":1}}\r\n";
    ASSERT_FALSE(QJsonDocument::fromJson(valid).isNull());
    EXPECT_EQ(ParseStrictNativeJsonBytes(valid),QJsonDocument::fromJson(valid).object());
    for(const auto& bytes:std::vector<QByteArray>{bom+"{\"a\":1,\"a\":2}",
        bom+"{\"outer\":{\"a\":1,\"\\u0061\":2}}"})
    {
        ASSERT_FALSE(QJsonDocument::fromJson(bytes).isNull());
        EXPECT_THROW(ParseStrictNativeJsonBytes(bytes),std::invalid_argument);
        EXPECT_THROW(ParseStrictNativeJsonObject(bytes.toStdString()),std::invalid_argument);
    }
}

TEST(NativeJsonByteInput,ByteLimitsAndInvalidFramingAreRejected)
{
    using namespace NMSDK::TimeLearner;
    const auto valid=QByteArray("{\"x\":\"")+QByteArray::fromHex("c3a9")+"\"}";
    EXPECT_NO_THROW(ParseStrictNativeJsonBytes(valid,std::size_t(valid.size())));
    EXPECT_THROW(ParseStrictNativeJsonBytes(valid,std::size_t(valid.size()-1)),std::invalid_argument);
    EXPECT_THROW(ParseStrictNativeJsonObject(valid.toStdString(),std::size_t(valid.size()-1)),std::invalid_argument);
    for(const auto& bytes:std::vector<QByteArray>{QByteArray{},"[]","null","{\"x\":NaN}",
        "{\"x\":Infinity}","{}{}","{} trailing",valid.left(valid.size()-1),
        valid+QByteArray(1,'\0'),valid+QByteArray(1,'\0')+"{}"})
    {
        EXPECT_THROW(ParseStrictNativeJsonBytes(bytes),std::invalid_argument);
        EXPECT_THROW(ParseStrictNativeJsonObject(bytes.toStdString()),std::invalid_argument);
    }
}

}
