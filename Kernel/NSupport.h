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

using namespace std;
using namespace RDK;
using RDK::UId;
using RDK::ULongId;
using RDK::NameT;

typedef RDK::UAContainer NAContainer;

typedef RDK::UAConnector NAConnector;

typedef RDK::UAItem NAItem;

typedef RDK::UADItem NADItem;

typedef RDK::UANet NANet;

typedef double real;
typedef vector<real> Real;
typedef vector<real>::iterator RealIterator;
typedef vector<real>::const_iterator RealCIterator;

//typedef long int IndexT;
//typedef int TimeT;

typedef RDK::UVariableData NVariableData;

// Константы
//extern const TimeT DefaultTimeStep;

// Буферы
//extern ULongId LongIdTemp;
//extern NameT NameTemp;

}

#endif

