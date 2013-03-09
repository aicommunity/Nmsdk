#ifndef TNSupportH
#define TNSupportH

#include "../../Kernel/NBios.h"
#include "WatchFrameUnit.h"

namespace NMSDK {

// Добавляем объект в окно наблюдений (график по времени)
void AddWatch(TWatchFrame *watch, RDK::UContainer *item, int output, int outindex, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// Добавляем посторонний объект в окно наблюдений (график по времени)
void AddWatch(TWatchFrame *watch, NameT name, real *y, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

// Добавляем объект в окно наблюдений (график по частоте)
void AddFrequencyWatch(TWatchFrame *watch, RDK::UContainer* item, real watchinterval, real yshift=0, TPenStyle style=psSolid, TColor color=TColor(0));

}
#endif
