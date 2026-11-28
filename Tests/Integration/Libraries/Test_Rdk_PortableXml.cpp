#include <gtest/gtest.h>
#include <rdk.h>
#include <array>
#include <string>
#include <typeinfo>
#include <vector>

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

namespace {
std::string VectorSpelling(std::string element,unsigned depth)
{
    for(unsigned i=0;i<depth;++i)
        element="class std::vector<"+element+",class std::allocator<"+element+"> >";
    return element;
}
}

TEST(PortableNativeXml,ObservedRdkContainersAndItaniumSubstitutionsRetainTheirStructure)
{
    for(const auto& pair:std::vector<std::pair<std::string,std::string>>{
        {"MVector<d>","MVector<double>"},
        {"MDMatrix<d>","MDMatrix<double>"},{"MDMatrix<i>","MDMatrix<int>"},
        {"N3RDK8MDMatrixIdEE","class RDK::MDMatrix<double>"},
        {"St6vectorIiSaIiEE",VectorSpelling("int",1)},
        {"St6vectorIS_IiSaIiEESaIS1_EE",VectorSpelling("int",2)},
        {"St6vectorIS_IS_IiSaIiEESaIS1_EESaIS3_EE",VectorSpelling("int",3)},
        {"St6vectorIS_IS_IS_IiSaIiEESaIS1_EESaIS3_EESaIS5_EE",VectorSpelling("int",4)},
        {"A2_A3_i","int[2][3]"}})
    {
        EXPECT_TRUE(RDK::SamePortableXmlType(pair.first,pair.second))<<pair.first;
        EXPECT_TRUE(RDK::SamePortableXmlType(pair.second,pair.first))<<pair.second;
    }
    EXPECT_FALSE(RDK::SamePortableXmlType("MDMatrix<d>","MVector<double>"));
    EXPECT_FALSE(RDK::SamePortableXmlType("MDMatrix<d>","MDMatrix<float>"));
    EXPECT_FALSE(RDK::SamePortableXmlType("A2_A3_i","int[3][2]"));
    EXPECT_FALSE(RDK::SamePortableXmlType(VectorSpelling("int",3),VectorSpelling("int",4)));
}

TEST(PortableNativeXml,NativeNestedVectorAndMatrixTypesUseTheProductionSerializer)
{
    using V1=std::vector<int>;using V2=std::vector<V1>;using V3=std::vector<V2>;using V4=std::vector<V3>;
    EXPECT_TRUE(RDK::SamePortableXmlType(typeid(V3).name(),VectorSpelling("int",3)));
    EXPECT_TRUE(RDK::SamePortableXmlType(typeid(V4).name(),VectorSpelling("int",4)));
    EXPECT_TRUE(RDK::SamePortableXmlType(typeid(RDK::MDMatrix<double>).name(),"class RDK::MDMatrix<double>"));
    RDK::USerStorageXML xml;ASSERT_TRUE(xml.Create("Root"));ASSERT_TRUE(xml.AddNode("value"));
    const V4 value{{{{1,2},{3}},{{4}}}};xml<<value;
    EXPECT_TRUE(RDK::SamePortableXmlType(xml.GetNodeAttribute("elemType"),VectorSpelling("int",3)));
    EXPECT_TRUE(RDK::SamePortableXmlType(xml.GetNodeAttribute("elemVecType"),VectorSpelling("int",2)));
    const auto originalCursor=xml.GetNodeName();std::string before,after;ASSERT_TRUE(xml.Save(before));
    RDK::USerStorageXML roundtrip;ASSERT_TRUE(roundtrip.Load(before,"Root"));
    EXPECT_TRUE(xml.SamePortableSerialization(roundtrip));
    EXPECT_EQ(xml.GetNodeName(),originalCursor);ASSERT_TRUE(xml.Save(after));EXPECT_EQ(before,after);
}

TEST(PortableNativeXml,MalformedOrUnknownTypeExpressionsNeverAcquireKnownMeanings)
{
    for(const auto& bad:{"class int","struct double","std::vector<int,std::allocator<double> >",
                         "St6vectorIS9_SaIiEE","St6vectorIiSaIdEE","MDMatrix<double,int>",
                         "RDK::OtherMatrix<double>","int[0]","A0_i","MDMatrix<double>suffix"})
    {
        EXPECT_FALSE(RDK::SamePortableXmlType(bad,"int"))<<bad;
        EXPECT_FALSE(RDK::SamePortableXmlType(bad,VectorSpelling("int",1)))<<bad;
        EXPECT_FALSE(RDK::SamePortableXmlType(bad,"MDMatrix<double>"))<<bad;
    }
    EXPECT_TRUE(RDK::SamePortableXmlType("PrivateABIType","PrivateABIType"));
    EXPECT_FALSE(RDK::SamePortableXmlType("PrivateABIType","class PrivateABIType"));
}

TEST(PortableNativeXml,LogicalIntegerDomainsAreExplicitValueBoundedAndSigned)
{
    using D=RDK::UXmlIntegralDomain;
    EXPECT_FALSE(RDK::SamePortableXmlType("m","unsigned __int64"));
    EXPECT_TRUE(RDK::SamePortableXmlType("m","unsigned __int64",D::UnsignedValue,"1"));
    EXPECT_TRUE(RDK::SamePortableXmlType("m","unsigned __int64",D::UnsignedValue,"4294967295"));
    EXPECT_FALSE(RDK::SamePortableXmlType("m","unsigned __int64",D::UnsignedValue,"4294967296"));
    EXPECT_FALSE(RDK::SamePortableXmlType("m","__int64",D::UnsignedValue,"1"));
    EXPECT_FALSE(RDK::SamePortableXmlType("m","unsigned __int64",D::UnsignedValue,"-1"));
    EXPECT_TRUE(RDK::SamePortableXmlType("x","long",D::SignedValue,"-2147483648"));
    EXPECT_FALSE(RDK::SamePortableXmlType("x","long",D::SignedValue,"2147483648"));
    EXPECT_TRUE(RDK::SamePortableXmlType("y","unsigned __int64",D::UnsignedValue,"18446744073709551615"));
    for(const auto& bad:{"","+1","1x","NaN","18446744073709551616"})
        EXPECT_FALSE(RDK::SamePortableXmlType("m","unsigned __int64",D::UnsignedValue,bad))<<bad;
    EXPECT_FALSE(RDK::SamePortableXmlType("d","double",D::UnsignedValue,"1"));
}

TEST(PortableNativeXml,ValueDomainOnlyAppliesToTheDeclaredScalarField)
{
    RDK::USerStorageXML a,b;
    ASSERT_TRUE(a.Load("<Root><p Type=\"m\">1</p><q Type=\"m\">1</q></Root>","Root"));
    ASSERT_TRUE(b.Load("<Root><p Type=\"unsigned __int64\">1</p><q Type=\"m\">1</q></Root>","Root"));
    EXPECT_FALSE(a.SamePortableSerialization(b));
    const RDK::USerStorageXML::PortableIntegralFields fields{{{"Root","p"},RDK::UXmlIntegralDomain::UnsignedValue}};
    EXPECT_TRUE(a.SamePortableSerialization(b,fields));
    ASSERT_TRUE(b.SelectNode("q"));ASSERT_TRUE(b.SetNodeAttribute("Type","unsigned __int64"));
    EXPECT_FALSE(a.SamePortableSerialization(b,fields));
}
