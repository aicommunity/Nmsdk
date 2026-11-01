#include <gtest/gtest.h>
#include "../../../Rdk/Deploy/Include/rdk.h"
#include <array>
#include <type_traits>

namespace {
using namespace RDK;

TEST(MDMatrixResize, FewerColumnsAndMoreRowsWithinExistingCapacity)
{
 MDMatrix<double> matrix(1,2,0.0);matrix(0,0)=11.;matrix(0,1)=12.;
 auto* allocation=matrix.Data;
 matrix.Resize(3,1,9.0);
 ASSERT_EQ(matrix.GetRows(),3);ASSERT_EQ(matrix.GetCols(),1);
 EXPECT_EQ(matrix.Data,allocation);
 EXPECT_DOUBLE_EQ(matrix(0,0),11.);EXPECT_DOUBLE_EQ(matrix(1,0),9.);EXPECT_DOUBLE_EQ(matrix(2,0),9.);
}

template<class T> class MDMatrixShapeTransitions : public ::testing::Test {};
using MatrixScalars = ::testing::Types<double,int,unsigned char,bool>;
TYPED_TEST_SUITE(MDMatrixShapeTransitions,MatrixScalars);

TYPED_TEST(MDMatrixShapeTransitions, PreservesOnlyExistingIntersectionAndInitializesNewCells)
{
 using T=TypeParam;
 const std::array<std::pair<int,int>,11> shapes{{{0,0},{0,3},{2,0},{1,2},{2,1},{3,1},{1,3},{2,3},{3,2},{4,6},{6,4}}};
 const T fill=std::is_same_v<T,bool>?T(false):T(9);
 const auto value=[](int row,int col) -> T {
  if constexpr(std::is_same_v<T,bool>)return (row+col)%2!=0;
  return T(row*11+col+1);
 };
 for(const bool reserve : {false,true})
  for(const auto& before : shapes)
   for(const auto& after : shapes)
   {
    SCOPED_TRACE(::testing::Message()<<"reserve="<<reserve<<" old="<<before.first<<'x'<<before.second
                 <<" new="<<after.first<<'x'<<after.second);
    MDMatrix<T> matrix;
    if(reserve)matrix.Resize(8,8,T(0));
    matrix.Resize(before.first,before.second,T(0));
    for(int r=0;r<before.first;++r)for(int c=0;c<before.second;++c)matrix(r,c)=value(r,c);
    auto* allocation=matrix.Data;
    matrix.Resize(after.first,after.second,fill);
    ASSERT_EQ(matrix.GetRows(),after.first);ASSERT_EQ(matrix.GetCols(),after.second);
    if(reserve)EXPECT_EQ(matrix.Data,allocation);
    for(int r=0;r<after.first;++r)for(int c=0;c<after.second;++c)
     EXPECT_EQ(matrix(r,c),(r<before.first && c<before.second)?value(r,c):fill);
   }
}

TYPED_TEST(MDMatrixShapeTransitions, ScalarAssignmentAfterShapeChangeFillsEveryCell)
{
 MDMatrix<TypeParam> matrix(1,2,TypeParam(1));auto* allocation=matrix.Data;
 matrix.Assign(3,1,TypeParam(0));
 EXPECT_EQ(matrix.Data,allocation);
 for(int r=0;r<3;++r)EXPECT_EQ(matrix(r,0),TypeParam(0));
}

TEST(MDMatrixResize, SameShapeAndNegativeRequestsKeepExistingValues)
{
 MDMatrix<double> matrix(2,3,7.);auto* allocation=matrix.Data;
 matrix.Resize(2,3,9.);matrix.Resize(-1,3);matrix.Resize(2,-1);
 ASSERT_EQ(matrix.GetRows(),2);ASSERT_EQ(matrix.GetCols(),3);EXPECT_EQ(matrix.Data,allocation);
 for(int r=0;r<2;++r)for(int c=0;c<3;++c)EXPECT_DOUBLE_EQ(matrix(r,c),7.);
}
}
