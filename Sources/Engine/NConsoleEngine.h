#ifndef NCONSOLEENGINE_H
#define NCONSOLEENGINE_H

#include "UConsoleEngine.h"

namespace NMSDK {

class NConsoleEngine: public MySDK::UConsoleEngine
{
protected: // ������
NEngine* Engine;

public: // ������
// --------------------------
// ������������ � �����������
// --------------------------
NConsoleEngine(void);
virtual ~NConsoleEngine(void);
// --------------------------

// --------------------------
// ������ �������� ����������
// --------------------------
public:

// --------------------------


// --------------------------
// ������ ����������� ����������
// --------------------------
protected:
// ����� ����������� ������, �������� �����������
// ����� ���������� ������ � ���������� ���������
virtual void Parser(const string &command, list<string> &params);
// --------------------------

};

}
#endif
