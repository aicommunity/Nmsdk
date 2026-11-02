#include <gtest/gtest.h>
#include "../../../Rdk/Deploy/Include/rdk.h"
#include <sstream>
#include <iomanip>
#include <limits>

namespace {
using namespace RDK;
TEST(MVectorStream, CoordinateDiagnosticUsesPublicElements)
{
    MVector<double,3> value(1.25,-2.5,3.75);
    std::ostringstream stream;stream<<value;
    EXPECT_EQ(stream.str(),"{1.25,-2.5,3.75}");
}
TEST(MVectorStream, CallerFormattingIsPreserved)
{
    MVector<double,3> value(1.25,-2.5,3.75);
    std::ostringstream stream;stream<<std::fixed<<std::setprecision(2)<<value;
    EXPECT_EQ(stream.str(),"{1.25,-2.50,3.75}");EXPECT_EQ(stream.precision(),2);
}
TEST(MVectorStream, FullPrecisionRoundtrip)
{
    MVector<double,3> value(-1.2345678901234567,2.0000000000000004,3.141592653589793);
    std::stringstream stream;stream.imbue(std::locale::classic());stream<<std::setprecision(std::numeric_limits<double>::max_digits10)<<value;
    MVector<double,3> restored;stream>>restored;ASSERT_FALSE(stream.fail());
    for(int i=0;i<3;++i)EXPECT_EQ(value(i),restored(i));
}
TEST(MVectorStream, WideCoordinateRoundtrip)
{
    MVector<double,3> value(1.25,-2.5,3.75),restored;
    std::wstringstream stream;stream<<value;EXPECT_EQ(stream.str(),L"{1.25,-2.5,3.75}");
    stream>>restored;ASSERT_FALSE(stream.fail());for(int i=0;i<3;++i)EXPECT_EQ(restored(i),value(i));
}
TEST(MVectorStream, SpacesAndFollowingToken)
{
    MVector<double,3> value;std::istringstream stream(" { 1.25 , -2.5 , 3.75 } tail");
    stream>>value;ASSERT_FALSE(stream.fail());EXPECT_EQ(value(0),1.25);EXPECT_EQ(value(1),-2.5);EXPECT_EQ(value(2),3.75);
    // Rdk provides a line-preserving string extractor; inspect remaining
    // characters explicitly instead of assuming std::string token extraction.
    std::string tail;std::getline(stream,tail);EXPECT_EQ(tail," tail");
}
TEST(MVectorStream, InvalidInputPreservesAllPreviousCoordinates)
{
    for(const char* text:{"","{}","{1,2}","{1;2,3}","{1,2,3","1,2,3}","{1,2,x}","{1,2,3,4}"})
    {
        SCOPED_TRACE(text);MVector<double,3> value(-7.,-8.,-9.);std::istringstream stream(text);stream>>value;
        EXPECT_TRUE(stream.fail());EXPECT_EQ(value(0),-7.);EXPECT_EQ(value(1),-8.);EXPECT_EQ(value(2),-9.);
    }
}
}
