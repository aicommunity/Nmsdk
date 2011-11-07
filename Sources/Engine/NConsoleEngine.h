#ifndef NCONSOLEENGINE_H
#define NCONSOLEENGINE_H

#include "UConsoleEngine.h"

namespace NMSDK {

class NConsoleEngine: public MySDK::UConsoleEngine
{
protected: // Данные
NEngine* Engine;

public: // Методы
// --------------------------
// Конструкторы и деструкторы
// --------------------------
NConsoleEngine(void);
virtual ~NConsoleEngine(void);
// --------------------------

// --------------------------
// Методы внешнего управления
// --------------------------
public:

// --------------------------


// --------------------------
// Методы внутреннего управления
// --------------------------
protected:
// Метод анализирует запрос, вызывает необходимый
// метод выполнения команд и возвращает результат
virtual void Parser(const string &command, list<string> &params);
// --------------------------

};

}
#endif
