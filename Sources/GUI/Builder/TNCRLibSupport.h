#ifndef TNCRLibSupportH
#define TNCRLibSupportH

#include <Grids.hpp>
#include "NCRSample.h"

namespace NMSDK{

// «аполн€ет данными обучающей выборки заданный StringGrid
void CRSampleToStringGrid(const NCRSample *sample, TStringGrid *grid);

}
#endif
