#ifndef NCONSOLEENGINE_CPP
#define NCONSOLEENGINE_CPP

#include "NConsoleEngine.h"

namespace NMSDK {
// --------------------------
// ������������ � �����������
// --------------------------
NConsoleEngine::NConsoleEngine(void)
: MySDK::UConsoleEngine("Version 0.1")
{
 Engine=0;
}

NConsoleEngine::~NConsoleEngine(void)
{
}
// --------------------------



// --------------------------
// ������ ����������� ����������
// --------------------------
// ����� ����������� ������, �������� �����������
// ����� ���������� ������ � ���������� ���������
void NConsoleEngine::Parser(const string &command, list<string> &params)
{
 if(command == "Start")
 {
  return;
 }

 if(command == "Pause")
 {
  return;
 }

 if(command == "Stop")
 {
  return;
 }

 UConsoleEngine(command,params);
}
// --------------------------

}
#endif

