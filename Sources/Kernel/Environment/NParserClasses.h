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

#ifndef NPARSERCLASSES_H
#define NPARSERCLASSES_H

#include "../Kernel/NSupport.h"

/* ************************************************************************************** */
class NParserString
       {
       protected: // General attrubutes
        // Type of content
        int Type;

       public: // Predefined constant for 'Type' attribute
        // Identifier of undefined type
        static const int UndefType;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserString(void);
        virtual ~NParserString(void);
        // --------------------------

        // --------------------------
        // Attributes control methods
        // --------------------------
        virtual int GetType(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserNamedString: public NParserString
       {
       protected: // General attrubutes
        // Name of content
        string Name;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserNamedString(string name);
        virtual ~NParserNamedString(void);
        // --------------------------

        // --------------------------
        // Attributes control methods
        // --------------------------
        virtual string GetName(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserHdr: public NParserNamedString
       {
       protected: // General attrubutes
        // Parent in header description
        string Parent;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserHdr(string name, string parent);
        virtual ~NParserHdr(void);
        // --------------------------

        // --------------------------
        // Attributes control methods
        // --------------------------
        virtual string GetParent(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserClassHdr: public NParserHdr
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of class's header
        static const int ClassHdrType;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserClassHdr(string name, string parent);
        virtual ~NParserClassHdr(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserObjectHdr: public NParserHdr
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of object's header
        static const int ObjectHdrType;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserObjectHdr(string name, string parent);
        virtual ~NParserObjectHdr(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserParameter: public NParserNamedString
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of parameter
        static const int ParameterType;

       protected: // General attrubutes
        // Value of parameter
        string Value;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserParameter(string name, string value);
        virtual ~NParserParameter(void);
        // --------------------------

        // --------------------------
        // Attributes control methods
        // --------------------------
        virtual string GetValue(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */

/* ************************************************************************************** */
class NParserLink: public NParserString
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of link
        static const int LinkType;

       protected: // General attrubutes
        // link output & input;
        string LinkOut,LinkIn;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserLink(string linkout, string linkin);
        virtual ~NParserLink(void);
        // --------------------------

        // --------------------------
        // Attributes control methods
        // --------------------------
        virtual string GetLinkOut(void);

        virtual string GetLinkIn(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */

/* ************************************************************************************** */
class NParserBlockOpen: public NParserString
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of 'block open' symbols sequence
        static const int BlockOpenType;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserBlockOpen(void);
        virtual ~NParserBlockOpen(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */


/* ************************************************************************************** */
class NParserBlockClose: public NParserString
       {
       public: // Predefined constant for 'Type' attribute
        // Identifier of 'block open' symbols sequence
        static const int BlockCloseType;

       public: // Methods
        // --------------------------
        // Constructors & destructors
        // --------------------------
        NParserBlockClose(void);
        virtual ~NParserBlockClose(void);
        // --------------------------

        // ---------
        // Steram IO
        // ---------
        // Load class data from str 'str'
        virtual bool ReadFromString(string &str);

        // Save class data to str 'str'
        virtual void WriteToString(string &str);
        // ---------
       };
/* ************************************************************************************** */

#endif