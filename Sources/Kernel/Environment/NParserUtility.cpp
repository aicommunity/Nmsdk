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

#ifndef NPARSERUTILITY_CPP
#define NPARSERUTILITY_CPP

#include "NParserUtility.h"

/* ************************************************************************************** */
/* Subsidiary functions                                                                   */
/* ************************************************************************************** */
void NPDelSpaces(string &source)
{
 string::size_type i;
 i=source.find_first_not_of(" \n\t\v\b\r\f\a");
 source.erase(0,i);
 if(source.size() == 0)
  return;
 i=source.find_last_not_of(" \n\t\v\b\r\f\a");
 source.erase(i+1,source.size()-i-1);
}

int NPGetTextObject(string &source, string &result, string &separator, string::size_type sindex)
{
 string::size_type i,li,ki;

 li=source.find_first_not_of(' ',sindex);
 i=source.find_first_of(" :={};",li);
 if(source[i] == ' ')
  {
   ki=source.find_first_not_of(' ',i);
   if(ki != string::npos)
    if(source[ki] == ':' ||
       source[ki] == '=' ||
       source[ki] == '{' ||
       source[ki] == '}' ||
       source[ki] == ';')
     i=ki;
  }
 result=source.substr(li,i-li);
 separator=source.substr(i,1);
 
 i++;
 return i;
}
/* ************************************************************************************** */



#endif