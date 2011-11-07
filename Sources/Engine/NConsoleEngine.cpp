#ifndef NCONSOLEENGINE_CPP
#define NCONSOLEENGINE_CPP

#include "NConsoleEngine.h"

namespace NMSDK {
// --------------------------
// Конструкторы и деструкторы
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
// Методы внутреннего управления
// --------------------------
// Метод анализирует запрос, вызывает необходимый
// метод выполнения команд и возвращает результат
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

