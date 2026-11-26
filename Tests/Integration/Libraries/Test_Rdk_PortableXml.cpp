#include <gtest/gtest.h>
#include <rdk.h>
#include <array>
#include <string>

namespace {
bool Same(const std::string& first,const std::string& second)
{
    RDK::USerStorageXML left,right;
    if(!left.Load(first,"Root") || !right.Load(second,"Root"))return false;
    return left.SamePortableSerialization(right) && right.SamePortableSerialization(left);
}
}

TEST(PortableNativeXml,KnownScalarSpellingsMatchInAllThreeTypeAttributes)
{
    const std::array<std::pair<const char*,const char*>,15> types{{
        {"b","bool"},{"c","char"},{"a","signed char"},{"h","unsigned char"},
        {"s","short"},{"t","unsigned short"},{"i","int"},{"j","unsigned int"},
        {"l","long"},{"m","unsigned long"},{"x","__int64"},{"y","unsigned __int64"},
        {"f","float"},{"d","double"},{"e","long double"}}};
    for(const auto& type:types)
        for(const auto* attribute:{"Type","elemType","elemVecType"})
        {
            const auto xml=[&](const char* value){return std::string("<Root><value ")+attribute+"=\""+value+"\">1</value></Root>";};
            EXPECT_TRUE(Same(xml(type.first),xml(type.second)))<<attribute<<":"<<type.first;
        }
}

TEST(PortableNativeXml,NativeScalarSerializationMatchesOtherCompilerSpellingWithoutMutation)
{
    RDK::USerStorageXML native,other;
    ASSERT_TRUE(native.Create("Root"));ASSERT_TRUE(native.AddNode("value"));native<<1.25;
    const auto local=native.GetNodeAttribute("Type");ASSERT_TRUE(local=="d" || local=="double");
    ASSERT_TRUE(other.Load(std::string("<Root><value Type=\"")+(local=="d"?"double":"d")+"\">1.25</value></Root>","Root"));
    std::string before,after;ASSERT_TRUE(native.Save(before));
    EXPECT_TRUE(native.SamePortableSerialization(other));
    EXPECT_EQ(native.GetNodeName(),"value");EXPECT_EQ(native.GetNodeAttribute("Type"),local);
    ASSERT_TRUE(native.Save(after));EXPECT_EQ(before,after);
}

TEST(PortableNativeXml,TypesValuesDimensionsClassesLinksAndUnknownAttributesStayDistinct)
{
    const std::string xml="<Root Class=\"Neuron\"><matrix Type=\"MDMatrix\" elemType=\"d\" Rows=\"1\" Cols=\"1\"><elem Type=\"d\">1.25</elem></matrix><link>$.Soma:Input</link></Root>";
    const auto changed=[&](const std::string& old,const std::string& replacement){auto copy=xml;const auto where=copy.find(old);EXPECT_NE(where,std::string::npos);copy.replace(where,old.size(),replacement);return copy;};
    EXPECT_FALSE(Same(xml,changed("elemType=\"d\"","elemType=\"i\"")));
    EXPECT_FALSE(Same(xml,changed("Type=\"d\"","Type=\"int\"")));
    EXPECT_FALSE(Same(xml,changed("1.25","1.26")));
    EXPECT_FALSE(Same(xml,changed("Rows=\"1\"","Rows=\"2\"")));
    EXPECT_FALSE(Same(xml,changed("Neuron","Synapse")));
    EXPECT_FALSE(Same(xml,changed("$.Soma:Input","$.Tip:Input")));
    EXPECT_FALSE(Same(xml,changed("Rows=\"1\"","Rows=\"1\" Unknown=\"d\"")));
    EXPECT_FALSE(Same("<Root><p Type=\"i\"/></Root>","<Root><p Type=\"long\"/></Root>"));
    EXPECT_FALSE(Same("<Root><p Type=\"f\"/></Root>","<Root><p Type=\"double\"/></Root>"));
    EXPECT_FALSE(Same("<Root><p Type=\"class Private\"/></Root>","<Root><p Type=\"Private\"/></Root>"));
    EXPECT_FALSE(Same("<Root><p Type=\"d\"/><p Type=\"i\"/></Root>","<Root><p Type=\"int\"/><p Type=\"double\"/></Root>"));
}

TEST(PortableNativeXml,AttributeOrderIsImmaterialButTextAndMixedContentRemainExact)
{
    EXPECT_TRUE(Same("<Root A=\"1\" B=\"2\"><p Type=\"d\">1</p></Root>",
                    "<Root B=\"2\" A=\"1\"><p Type=\"double\">1</p></Root>"));
    EXPECT_FALSE(Same("<Root>before<p Type=\"d\"/>after</Root>",
                     "<Root>after<p Type=\"double\"/>before</Root>"));
    EXPECT_FALSE(Same("<Root><!--Type=d--><p Type=\"d\"/></Root>",
                     "<Root><!--Type=double--><p Type=\"double\"/></Root>"));
    EXPECT_FALSE(Same("<Root><p Type=\"d\">d</p></Root>",
                     "<Root><p Type=\"double\">double</p></Root>"));
    RDK::USerStorageXML empty;
    EXPECT_FALSE(empty.SamePortableSerialization(empty));
}
