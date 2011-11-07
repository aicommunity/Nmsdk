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

#ifndef NPARSERCLASSES_CPP
#define NPARSERCLASSES_CPP

#include "NParserClasses.h"

// ----------------------------------------
// Predefined constant for 'Type' attribute
// ----------------------------------------
// Identifier of undefined type
const int NParserString::UndefType=0;

// Identifier of class's header
const int NParserClassHdr::ClassHdrType=1;

// Identifier of object's header
const int NParserObjectHdr::ObjectHdrType=2;

// Identifier of parameter
const int NParserParameter::ParameterType=3;

// Identifier of link
const int NParserLink::LinkType=4;

// Identifier of 'block open' symbols sequence
const int NParserBlockOpen::BlockOpenType=8;

// Identifier of 'block close' symbols sequence
const int NParserBlockClose::BlockCloseType=9;
// ----------------------------------------


/* ************************************************************************************** *
 class NParserString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserString::NParserString(void)
{
 Type=UndefType;
}

NParserString::~NParserString(void)
{
}
// --------------------------

// --------------------------
// Attributes control methods
// --------------------------
int NParserString::GetType(void)
{
 return Type;
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserString::ReadFromString(string &str)
{
 int i=str.find_first_of(' ');
 int type;

 type=atoi((str.substr(0,i)).c_str());
 if(type != Type)
  return false;

 str=str.substr(i+1,str.size()-i);
 return true;
}

// Save class data to str 'str'
void NParserString::WriteToString(string &str)
{
 char s[33]="";
 sprintf(s,"%i",Type);

 str+=s;
}
// ---------
/* ************************************************************************************** */


/* ************************************************************************************** * 
 class NParserNamedString: public NParserString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserNamedString::NParserNamedString(string name)
{
 Name=name;
}

NParserNamedString::~NParserNamedString(void)
{
}
// --------------------------

// --------------------------
// Attributes control methods
// --------------------------
string NParserNamedString::GetName(void)
{
 return Name;
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserNamedString::ReadFromString(string &str)
{
 if(!NParserString::ReadFromString(str))
  return false;

 int i=str.find_first_of(' ');
 Name=str.substr(0,i);
 str=str.substr(i+1,str.size()-i);
 return true;
}

// Save class data to str 'str'
void NParserNamedString::WriteToString(string &str)
{
 NParserString::WriteToString(str);

 str+=" ";
 str+=Name;
}
// ---------
/* ************************************************************************************** */



/* ************************************************************************************** * 
 class NParserHdr: public NParserNamedString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserHdr::NParserHdr(string name, string parent)
 : NParserNamedString(name)
{
 Parent=parent;
}

NParserHdr::~NParserHdr(void)
{
}
// --------------------------

// --------------------------
// Attributes control methods
// --------------------------
string NParserHdr::GetParent(void)
{
 return Parent;
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserHdr::ReadFromString(string &str)
{
 if(!NParserNamedString::ReadFromString(str))
  return false;

 int i=str.find_first_of(' ');
 Parent=str.substr(0,i);
 str=str.substr(i+1,str.size()-i);
 return true;
}

// Save class data to str 'str'
void NParserHdr::WriteToString(string &str)
{
 NParserNamedString::WriteToString(str);

 str+=" ";
 str+=Parent;
}
// ---------
/* ************************************************************************************** */



/* ************************************************************************************** *
 class NParserClassHdr: public NParserHdr
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserClassHdr::NParserClassHdr(string name, string parent)
 : NParserHdr(name,parent)
{
 Type=ClassHdrType;
}

NParserClassHdr::~NParserClassHdr(void)
{
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserClassHdr::ReadFromString(string &str)
{
 if(!NParserHdr::ReadFromString(str))
  return false;
 return true;
}

// Save class data to str 'str'
void NParserClassHdr::WriteToString(string &str)
{
 NParserHdr::WriteToString(str);
}
// ---------
/* ************************************************************************************** */



/* ************************************************************************************** *
 class NParserObjectHdr: public NParserHdr
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserObjectHdr::NParserObjectHdr(string name, string parent)
 : NParserHdr(name,parent)
{
 Type=ObjectHdrType;
}

NParserObjectHdr::~NParserObjectHdr(void)
{
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserObjectHdr::ReadFromString(string &str)
{
 if(!NParserHdr::ReadFromString(str))
  return false;

 return true;
}

// Save class data to str 'str'
void NParserObjectHdr::WriteToString(string &str)
{
 NParserHdr::WriteToString(str);
}
// ---------
/* ************************************************************************************** */



/* ************************************************************************************** *
 class NParserParameter: public NParserNamedString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserParameter::NParserParameter(string name, string value)
 : NParserNamedString(name)
{
 Type=ParameterType;
 Value=value;
}

NParserParameter::~NParserParameter(void)
{
}
// --------------------------

// --------------------------
// Attributes control methods
// --------------------------
string NParserParameter::GetValue(void)
{
 return Value;
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserParameter::ReadFromString(string &str)
{
 if(!NParserNamedString::ReadFromString(str))
  return false;

 int i=str.find_first_of(' ');
 Value=str.substr(0,i);
 str=str.substr(i+1,str.size()-i);
 return true;
}

// Save class data to str 'str'
void NParserParameter::WriteToString(string &str)
{
 NParserNamedString::WriteToString(str);

 str+=" ";
 str+=Value;
}
// ---------
/* ************************************************************************************** */

/* ************************************************************************************** 
 class NParserLink: public NParserString
 ************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserLink::NParserLink(string linkout, string linkin)
{
 Type=LinkType;
 LinkOut=linkout;
 LinkIn=linkin;
}

NParserLink::~NParserLink(void)
{
}
// --------------------------

// --------------------------
// Attributes control methods
// --------------------------
string NParserLink::GetLinkOut(void)
{
 return LinkOut;
}

string NParserLink::GetLinkIn(void)
{
 return LinkIn;
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserLink::ReadFromString(string &str)
{
 if(!NParserString::ReadFromString(str))
  return false;

 int i=str.find_first_of(' ');

 LinkIn=str.substr(0,i);
 str=str.substr(i+1,str.size()-i);

 i=str.find_first_of(' ');

 LinkOut=str.substr(0,i);
 str=str.substr(i+1,str.size()-i);
 return true;
}

// Save class data to str 'str'
void NParserLink::WriteToString(string &str)
{
 NParserString::WriteToString(str);

 str+=" ";
 str+=LinkIn;
 str+=" ";
 str+=LinkOut;
}
// ---------
/* ************************************************************************************** */

/* ************************************************************************************** *
 class NParserBlockOpen: public NParserString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserBlockOpen::NParserBlockOpen(void)
{
 Type=BlockOpenType;
}

NParserBlockOpen::~NParserBlockOpen(void)
{
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserBlockOpen::ReadFromString(string &str)
{
 if(!NParserString::ReadFromString(str))
  return false;

 return true;
}

// Save class data to str 'str'
void NParserBlockOpen::WriteToString(string &str)
{
 NParserString::WriteToString(str);
}
// ---------
/* ************************************************************************************** */



/* ************************************************************************************** * 
 class NParserBlockClose: public NParserString
 **************************************************************************************** */
// --------------------------
// Constructors & destructors
// --------------------------
NParserBlockClose::NParserBlockClose(void)
{
 Type=BlockCloseType;
}

NParserBlockClose::~NParserBlockClose(void)
{
}
// --------------------------

// ---------
// Steram IO
// ---------
// Load class data from str 'str'
bool NParserBlockClose::ReadFromString(string &str)
{
 if(!NParserString::ReadFromString(str))
  return false;

 return true;
}

// Save class data to str 'str'
void NParserBlockClose::WriteToString(string &str)
{
 NParserString::WriteToString(str);
}
// ---------
/* ************************************************************************************** */

#endif