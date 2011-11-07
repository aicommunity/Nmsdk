#include "TNCRLibSupport.h"

namespace NMSDK{

// «аполн€ет данными обучающей выборки заданный StringGrid
void CRSampleToStringGrid(const NCRSample *sample,TStringGrid *grid)
{
 if(!sample || !grid)
  return;

 grid->RowCount=sample->SampleSize+1;
 grid->ColCount=sample->VectorSize+1;

 String value;

 const vector<pair<NIOData,int> > &data=sample->GetSampleData();
 for(size_t j=0;j<data[0].first.GetSize();j++)
 {
  grid->Cells[j+1][0]=IntToStr(int(j));
 }

 for(size_t i=0;i<data.size();i++)
 {
  value=String("[")+IntToStr(data[i].second)+String("] ");
  grid->Cells[0][i+1]=value+IntToStr(int(i));
  for(size_t j=0;j<data[i].first.GetSize();j++)
  {
   grid->Cells[j+1][i+1]=FloatToStrF(data[i].first.Double[j],ffFixed,3,3);
  }
 }

}


}
