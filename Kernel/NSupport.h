// ===========================================================
// Version:        3.0.3
// ===========================================================
/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002.
E-mail:		alexab@ailab.ru
url:            http://ailab.ru

This file - part of the project: Neuro Modeler Software Developer Kit (NMSDK)

File License:        BSD License
Project License:     BSD License
See file license.txt for more information
*********************************************************** */

#ifndef NSUPPORT_H
#define NSUPPORT_H

// Отключение предупреждений в VS
#pragma warning( disable : 4355)
#pragma warning( disable : 4800)

//#pragma warning( disable: 4786 )

#include <list>
#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <functional>
#include "rdk.h"

namespace NMSDK {

using namespace RDK;

//typedef double double;
typedef vector<double> Real;
typedef vector<double>::iterator RealIterator;
typedef vector<double>::const_iterator RealCIterator;


}

#endif

