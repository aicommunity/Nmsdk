/* ***********************************************************
@Copyright Alexander V. Bakhshiev, 2002-2009.
E-mail:			alexab@ailab.ru
url:			http://ailab.ru
Version:		1.2.1

This file - part of the project: Neuro Modeler

File License:		BSD License
Project License:	GNU GPLv3 License
See file license.txt for more information
*********************************************************** */

#ifndef NPARSERUTILITY_H
#define NPARSERUTILITY_H

#include "../Kernel/NSupport.h"

/* ************************************************************************************** */
/* Subsidiary functions                                                                   */
/* ************************************************************************************** */
void NPDelSpaces(string &source);

int NPGetTextObject(string &source, string &result, string &separator, string::size_type sindex=0);
/* ************************************************************************************** */


#endif