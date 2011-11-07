#ifndef NENGINE_CPP
#define NENGINE_CPP

#include "NEngine.h"

namespace NMSDK{

// --------------------------
// ������������ � �����������
// --------------------------
NEngine::NEngine(void)
: MySDK::UConsoleEngine("Version 0.1")
{
// Runned=-1;
// Storage=0;
// Environment=0;
}

NEngine::~NEngine(void)
{
// Stop();
}
// --------------------------

// --------------------------
// ������ ������� � ���������� ���������
// --------------------------
// ���� ������ �������
/*int NEngine::IsRunned(void)
{
 return Runned;
} */
// --------------------------


// --------------------------
// ������ ������� � ������
// --------------------------
// ���������� ��������� �� �����
NEnvironment* NEngine::GetEnvironment(void)
{
 return static_cast<NEnvironment*>(Environment);
}
// --------------------------

// --------------------------
// ������ ���������� ������
// --------------------------
// �������������� ������ ������
bool NEngine::Init(void)
{
 if(!MySDK::UEngine::Init())
 {
  ResultBuffer.push_back("Engine: init FAILED!");
  return false;
 }
 else
 {
  ResultBuffer.push_back("Engine: successfuly init.");
  return true;
 }
}

// ���������������� ������ ������
// � ��������� ������� ���������
bool NEngine::UnInit(void)
{
 return MySDK::UEngine::UnInit();
}

// ��������� �������
bool NEngine::Start(void)
{
 if(!MySDK::UEngine::Start())
 {
   ResultBuffer.push_back("Engine: Reset FAILED!");
   return false;
 }
 else
 {
  ResultBuffer.push_back("Engine: successful started.");
  return true;
 }
}

// ���������������� �������
bool NEngine::Pause(void)
{
 if(!MySDK::UEngine::Pause())
 {
  ResultBuffer.push_back("Engine: Reset FAILED!");
  return false;
 }
 else
 {
  ResultBuffer.push_back("Engine: successful paused.");
  return true;
 }
}

// ������������� �������
bool NEngine::Stop(void)
{
 MySDK::UEngine::Stop();
 ResultBuffer.push_back("Engine: successful stopped.");
 return true;
}
// --------------------------

// --------------------------
// ������ ���������� ������
// ������ ����� � ��� �� �������������
// --------------------------
// ������� ������
bool NEngine::CreateModel(list<string> &params)
{
 if(params.size() < 1)
 {
  ResultBuffer.push_back("Environment->CreateModel: please select model class!");
  return false;
 }

 if(!Environment->CreateModel(params.front()))
 {
  ResultBuffer.push_back("Environment->CreateModel: model creation error!");
  return false;
 }

  ResultBuffer.push_back("Environment->CreateModel: model successfuly created.");
  return true;
}

// ������� ������
bool NEngine::List(list<string> &params)
{
 if(params.size() < 1)
 {
  ResultBuffer.push_back("Environment->List: please select list! (libs, classes)");
  return false;
 }

 if(params.front() == "libs")
 {
  for(size_t i=0;i<Environment->GetNumClassLibraries();i++)
  {
   ResultBuffer.push_back(Environment->GetClassLibrary(i)->GetName());
  }

  return true;
 }

 if(params.front() == "classes")
 {
  vector<string> buffer;
  Environment->GetStorage()->GetClassNameList(buffer);
  for(size_t i=0;i<buffer.size();i++)
  {
   string result=buffer[i]+string(" (")+MySDK::sntoa(Environment->GetStorage()->CalcNumObjects(buffer[i]))+string(")");
   size_t classobjsize=static_cast<NAContainer*>(Environment->GetStorage()->GetClass(Environment->GetStorage()->GetClassId(buffer[i])))->GetNumAllComponents();
   result+=string(" objsize=")+MySDK::sntoa(classobjsize);
   ResultBuffer.push_back(result);
  }

  ResultBuffer.push_back(string("Total Objects: ")+MySDK::sntoa(Environment->GetStorage()->CalcNumObjects()));
  return true;
 }

 ResultBuffer.push_back("Environment->List: unknown param!");
 return false;
}
// --------------------------


// --------------------------
// ������ ����������� ���������� �������
// --------------------------
// ��������� ����� ��������� � ��������� ��������� �� ��� � ������ external_libs
// ���������� 0 � ������ ������
// ������ ���� ��������� ������� �� ini-����� 'inifile', ������ 'section'
/*int NEngine::LoadNLibraries(void)
{
 vector<string> variables;
 int res=0;
 NLibrary *library;

 Options.GetVariableList(ComponentLibrariesSectionName, variables);

 LibrariesList.clear();
 for(size_t i=0;i<variables.size();i++)
 {
  library=LoadNLibrary(Options(ComponentLibrariesSectionName,variables[i],""),variables[i]);
  if(!library)
   res|=1;
  LibrariesList.push_back(library);
 }
 return res;
}            */
// --------------------------

// --------------------------
// ������ ����������� ���������� ��������
// --------------------------
// ����� ����������� ������, �������� �����������
// ����� ���������� ������ � ���������� ���������
void NEngine::Parser(const string &command, list<string> &params)
{
 if(command == "Start")
 {
  Start();
  return;
 }

 if(command == "Pause")
 {
  Pause();
  return;
 }

 if(command == "Stop")
 {
  Stop();
  return;
 }

 if(command == "CreateModel")
 {
  CreateModel(params);
  return;
 }

 if(command == "List")
 {
  List(params);
  return;
 }

 MySDK::UConsoleEngine::Parser(command,params);
}
// --------------------------

// --------------------------
// ������� ������ ���������� ������
// --------------------------
// �������������� �������� �� ��������� � ����� �������� �����
bool NEngine::ADefault(void)
{
/*
 // ��� ����� �������������
 OptionsFileName="options.ini";

 // ��� ������ ������ �������� ����������
 MainLibrarySectionName="MainDLL";

 // ��� ���������� �������� ����������
 MainLibraryName="NMSDK";
 Options(MainLibrarySectionName,MainLibraryName,string("nmsdk.dll"));

 // ��� ������ ������ ��������� ���������
 ComponentLibrariesSectionName="ComponentLibraries";

 // ������ ������������� ��������� � ����������
 // ���� < 0, �� ����� ��������� ����� �������
 StorageIndex=-1;
 Options("General","StorageIndex",MySDK::sntoa(StorageIndex));

 // ������ ������������ ����� � ����������
 // ���� < 0, �� ����� ����� ����� �������
 EnvironmentIndex=-1;
 Options("General","EnvironmentIndex",MySDK::sntoa(EnvironmentIndex));
		  */
 return MySDK::UEngine::ADefault();
}

// ������������ ������ ���������� ��������� �������
// ����� ��������� ����������
// ������������� �������� ����� Reset() � ���������� Ready � true
// � ������ �������� ������
bool NEngine::ABuild(void)
{
 return MySDK::UEngine::ABuild();
}

// ����� �������� �����.
bool NEngine::AReset(void)
{
 return MySDK::UEngine::AReset();
}

// ��������� ������ ����� �������
bool NEngine::ACalculate(void)
{
 return MySDK::UEngine::ACalculate();
}
// --------------------------

}
#endif
